"""Renderer v2: smooth sub-pixel camera moves, multi-shot scenes, animated overlays, kinetic text.

usage: render2.py <ep_dir> <scenes_module> [--fps 25] [--only s03]
Inputs : <ep_dir>/audio/scenes.json (from narrate2.py), <ep_dir>/script.md, scene module with render(visual, caption)
Output : <ep_dir>/video_nosound.mp4, then mixed with voice + ambient bed into <ep_dir>/final.mp4

Script extras understood here:
  a paragraph starting with  [[TEXT]]  shows TEXT as a large kinetic title when that paragraph begins.
"""
import importlib, json, math, os, random, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import visuals as V

OW, OH = 1920, 1080
FPS = 25
XF = 0.7          # crossfade seconds between shots
SHOT = 7.5        # target shot length (s)

# ---------------------------------------------------------------- effects (drawn on RGBA overlays)

def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


class Rain:
    """Seamless 1-second loop, pre-rendered once (each drop travels a whole number of screen heights per loop)."""
    L = 25

    def __init__(self, seed, n=600, alpha=60, slant=0.32, speed=None):
        r = random.Random(seed)
        self.drops = [(r.random() * (OW + 400) - 200, r.random() * (OH + 120), r.uniform(30, 90), r.choice((1, 1, 2))) for _ in range(n)]
        self.alpha, self.slant = alpha, slant
        self.loop = None

    def layer(self, t):
        if self.loop is None:
            self.loop = []
            for k in range(self.L):
                lay = Image.new("RGBA", (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
                for x, y, l, m in self.drops:
                    yy = (y + (k / self.L) * m * (OH + 120)) % (OH + 120) - 60
                    xx = x + yy * self.slant * 0.25
                    d.line((xx, yy, xx + l * self.slant, yy + l), fill=(210, 220, 235, self.alpha), width=2)
                self.loop.append(lay)
        return self.loop[int(round(t * FPS)) % self.L]


class Dust:
    def __init__(self, seed, n=90, color=(255, 236, 200)):
        r = random.Random(seed)
        self.p = [(r.random() * OW, r.random() * OH, r.uniform(1.5, 4), r.uniform(0, 6.28), r.uniform(6, 22)) for _ in range(n)]
        self.c = color

    def draw(self, d, t):
        for x, y, s, ph, sp in self.p:
            xx = (x + math.sin(t * 0.3 + ph) * 40 + t * sp) % OW
            yy = (y - t * sp * 0.6) % OH
            a = int(60 + 60 * math.sin(t * 0.8 + ph))
            d.ellipse((xx - s, yy - s, xx + s, yy + s), fill=self.c + (max(0, a),))


class Fog:
    def __init__(self, seed, y0=0.45, y1=0.9, alpha=40):
        r = random.Random(seed)
        self.blobs = [(r.random() * OW * 1.6 - OW * 0.3, r.uniform(y0, y1) * OH, r.uniform(400, 900), r.uniform(60, 160), r.uniform(8, 25)) for _ in range(18)]
        self.alpha = alpha
        self._cache = {}

    def layer(self, t):
        key = int(t * 5)  # fog moves slowly: rebuild 5x per second, blur is the costly part
        if key not in self._cache:
            lay = Image.new("RGBA", (OW // 4, OH // 4), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            for x, y, w, h, sp in self.blobs:
                xx = ((x + key / 5 * sp) % (OW * 1.6)) - OW * 0.3
                d.ellipse(((xx - w) / 4, (y - h) / 4, (xx + w) / 4, (y + h) / 4), fill=(190, 200, 214, self.alpha))
            self._cache = {key: lay.filter(ImageFilter.GaussianBlur(14)).resize((OW, OH), Image.BILINEAR)}
        return self._cache[key]


class Beam:
    """Rotating lighthouse beam pivoting at a point given in output coordinates."""
    def __init__(self, cx, cy, period=9.0):
        self.cx, self.cy, self.period = cx, cy, period

    def layer(self, t):
        lay = Image.new("RGBA", (OW // 2, OH // 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        a = (t / self.period) * 2 * math.pi
        sx = math.cos(a)
        for side in (1, -1):
            L = 1600 * abs(sx) + 120
            ang = 0.08
            dx = side * sx
            p0 = (self.cx / 2, self.cy / 2)
            p1 = (p0[0] + dx * L, p0[1] - L * 0.05 * math.sin(ang * 3) - 18)
            p2 = (p0[0] + dx * L, p0[1] + L * 0.05 + 18)
            alpha = int(85 * (0.35 + 0.65 * max(0, side * math.sin(a) * 0 + abs(sx))))
            d.polygon([p0, p1, p2], fill=(255, 226, 150, alpha if side * sx > 0 else alpha // 3))
        d.ellipse((self.cx / 2 - 40, self.cy / 2 - 40, self.cx / 2 + 40, self.cy / 2 + 40), fill=(255, 225, 150, 110))
        return lay.filter(ImageFilter.GaussianBlur(10)).resize((OW, OH), Image.BILINEAR)


class Flicker:
    def __init__(self, seed, color=(255, 170, 80), strength=0.07):
        self.r = random.Random(seed); self.c = color; self.s = strength

    def tint(self, t):
        v = 0.5 + 0.5 * math.sin(t * 7.3) * math.sin(t * 3.1 + 1) + 0.2 * math.sin(t * 19)
        return int(255 * self.s * max(0, v))


# ---------------------------------------------------------------- camera framings per visual

# Each framing: (cx, cy, zoom_start, zoom_end, dx, dy) in fractions of the 2560x1440 still.
DEFAULT_FRAMES = [(0.5, 0.5, 1.00, 1.08, 0.00, 0.0), (0.42, 0.45, 1.25, 1.35, 0.03, 0.0),
                  (0.6, 0.55, 1.30, 1.22, -0.03, 0.0), (0.5, 0.48, 1.12, 1.02, 0.0, -0.02)]


def framings(visual, extra):
    return extra.get(visual, DEFAULT_FRAMES)


def effects_for(visual, fx_map, seed):
    out = []
    for name in fx_map.get(visual, []):
        if name == "rain": out.append(Rain(seed))
        elif name == "rain_heavy": out.append(Rain(seed, n=1100, alpha=75, slant=0.45))
        elif name == "dust": out.append(Dust(seed))
        elif name == "fog": out.append(Fog(seed))
        elif name == "fog_high": out.append(Fog(seed, 0.2, 0.7, 35))
        elif name.startswith("beam"):
            _, x, y = name.split(":"); out.append(Beam(float(x) * OW, float(y) * OH))
        elif name == "flicker": out.append(Flicker(seed))
    return out


# ---------------------------------------------------------------- kinetic title

FONT_K = None


def kinetic(frame, text, age, dur=3.2):
    if age < 0 or age > dur:
        return frame
    a = ease(age / 0.5) * (1 - ease((age - (dur - 0.6)) / 0.6))
    lay = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    size = 120
    font = ImageFont.truetype(V.SERIF_B, size)
    while d.textlength(text, font=font) > OW - 260 and size > 56:
        size -= 6; font = ImageFont.truetype(V.SERIF_B, size)
    FONT_K = font
    w = d.textlength(text, font=FONT_K)
    x = (OW - w) / 2
    y = OH * 0.40 - 20 * (1 - ease(age / 0.6))
    pad = 50
    hb = size + 40
    d.rectangle((x - pad, y - 30, x + w + pad, y + hb), fill=(10, 11, 14, int(170 * a)))
    d.rectangle((x - pad, y + hb, x + w + pad, y + hb + 8), fill=V.AMBER + (int(255 * a),))
    d.text((x, y), text, font=FONT_K, fill=V.PAPER + (int(255 * a),))
    return Image.alpha_composite(frame, lay)


def lower_third(frame, text, age, dur=4.5):
    a = ease(age / 0.4) * (1 - ease((age - (dur - 0.5)) / 0.5))
    if a <= 0:
        return frame
    lay = Image.new("RGBA", (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = ImageFont.truetype(V.SANS, 34)
    w = d.textlength(text, font=f)
    x, y = 96 - 30 * (1 - ease(age / 0.5)), OH - 150
    d.rectangle((x - 30, y - 18, x + w + 30, y + 52), fill=(10, 11, 14, int(175 * a)))
    d.rectangle((x - 30, y - 18, x - 24, y + 52), fill=V.AMBER + (int(255 * a),))
    d.text((x, y), text, font=f, fill=V.PAPER + (int(255 * a),))
    return Image.alpha_composite(frame, lay)


# ---------------------------------------------------------------- frame renderer

def cam_frame(src, fr, u):
    """Render one camera frame from still `src` (2560x1440 RGB) for framing fr at progress u (0..1)."""
    cx, cy, z0, z1, dx, dy = fr
    e = ease(u)
    z = z0 + (z1 - z0) * e
    cxp = (cx + dx * e) * src.width
    cyp = (cy + dy * e) * src.height
    vw, vh = src.width / z, src.height / z
    x0 = min(max(cxp - vw / 2, 0), src.width - vw)
    y0 = min(max(cyp - vh / 2, 0), src.height - vh)
    sx = vw / OW
    # affine: output (X, Y) -> source (x0 + X*sx, y0 + Y*sx); floats, so no pixel snapping
    return src.transform((OW, OH), Image.AFFINE, (sx, 0, x0, 0, sx, y0), resample=Image.BILINEAR)


def build_shots(scenes, frames_dir, frame_extra):
    """Split each scene into shots of ~SHOT seconds, cycling that visual's framings."""
    shots, t = [], 0.0
    for si, sc in enumerate(scenes):
        d = sc["duration"]
        n = max(1, round(d / SHOT))
        fl = framings(sc["visual"], frame_extra)
        import glob
        imgs = sorted(glob.glob(os.path.join(frames_dir, sc["id"] + "_*.png"))) or [os.path.join(frames_dir, sc["id"] + ".png")]
        if len(imgs) > 1:
            n = max(n, min(len(imgs), int(d // 4)))  # make sure every variant gets screen time
        for k in range(n):
            s0 = t + d * k / n
            s1 = t + d * (k + 1) / n
            shots.append({"scene": si, "img": imgs[k % len(imgs)], "visual": sc["visual"], "caption": sc.get("caption", ""),
                          "scene_t0": t, "fr": fl[(k + si) % len(fl)], "t0": s0, "t1": s1})
        t += d
    return shots, t


def kinetic_cues(script_path, scenes):
    """Map [[TEXT]] paragraph markers to absolute times using sentence timings."""
    cues = []
    paras_by_scene = []
    cur = None
    for line in open(script_path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("## "):
            cur = []; paras_by_scene.append(cur)
        elif cur is not None and line.strip() and not line.startswith(("#", "<!--")):
            cur.append(line.strip())
    t = 0.0
    for sc, paras in zip(scenes, paras_by_scene):
        sents = sc["sentences"]
        si = 0
        for p in paras:
            m = re.match(r"^\[\[(.+?)\]\]\s*(.*)$", p)
            body = m.group(2) if m else p
            if m and si < len(sents):
                cues.append((t + sents[si]["start"], m.group(1)))
            # advance sentence index by the number of sentences in this paragraph
            n = len([s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'])", body) if s.strip()])
            si += n
        t += sc["duration"]
    return cues


def render(ep, mod_name, frame_extra=None, fx_map=None, only=None, part=None):
    mod = importlib.import_module(mod_name)
    frame_extra = frame_extra or getattr(mod, "FRAMES", {})
    fx_map = fx_map or getattr(mod, "FX", {})
    scenes = json.load(open(os.path.join(ep, "audio", "scenes.json")))
    shots, total = build_shots(scenes, os.path.join(ep, "frames"), frame_extra)
    cues = kinetic_cues(os.path.join(ep, "script.md"), scenes)
    if only:
        shots = [s for s in shots if scenes[s["scene"]]["id"] == only]
        t_start, t_end = shots[0]["t0"], shots[-1]["t1"]
    else:
        t_start, t_end = 0.0, total
    if part:
        i, n = part
        span = (t_end - t_start) / n
        t_start, t_end = t_start + span * i, t_start + span * (i + 1) if i < n - 1 else t_end
        t_start = round(t_start * FPS) / FPS; t_end = round(t_end * FPS) / FPS
    out = os.path.join(ep, f"part{part[0]}.mp4" if part else ("video_nosound.mp4" if not only else f"preview_{only}.mp4"))
    enc = subprocess.Popen(["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
                            "-g", "50", out], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    cache, fx_cache = {}, {}

    def still(p):
        if p not in cache:
            if len(cache) > 4:
                cache.pop(next(iter(cache)))
            cache[p] = Image.open(p).convert("RGB")
        return cache[p]

    def shot_frame(sh, t):
        u = (t - sh["t0"]) / max(0.01, sh["t1"] - sh["t0"])
        img = cam_frame(still(sh["img"]), sh["fr"], u).convert("RGBA")
        key = (sh["scene"], sh["visual"])
        if key not in fx_cache:
            fx_cache[key] = effects_for(sh["visual"], fx_map, sh["scene"] * 7 + 3)
        for fx in fx_cache[key]:
            if isinstance(fx, Rain):
                img = Image.alpha_composite(img, fx.layer(t))
            elif isinstance(fx, Dust):
                lay = Image.new("RGBA", (OW, OH), (0, 0, 0, 0)); fx.draw(ImageDraw.Draw(lay), t); img = Image.alpha_composite(img, lay)
            elif isinstance(fx, (Fog, Beam)):
                img = Image.alpha_composite(img, fx.layer(t))
            elif isinstance(fx, Flicker):
                v = fx.tint(t)
                if v:
                    img = Image.alpha_composite(img, Image.new("RGBA", (OW, OH), fx.c + (v,)))
        return img

    n_frames = int(round((t_end - t_start) * FPS))
    si = 0
    for f in range(n_frames):
        t = t_start + f / FPS
        while si < len(shots) - 1 and t >= shots[si]["t1"]:
            si += 1
        sh = shots[si]
        img = shot_frame(sh, t)
        # crossfade into the next shot during the last XF seconds
        if si < len(shots) - 1 and t > sh["t1"] - XF:
            nxt = shots[si + 1]
            a = ease((t - (sh["t1"] - XF)) / XF)
            img = Image.blend(img, shot_frame(nxt, t), a)
        # fade from/to black at very start and end
        edge = min(t / 1.2, (total - t) / 1.5, 1.0)
        if edge < 1:
            img = Image.blend(Image.new("RGBA", (OW, OH), (0, 0, 0, 255)), img, max(0.0, edge))
        cap = sh.get("caption")
        age = t - sh["scene_t0"]
        if cap and 0.3 <= age <= 4.8:
            img = lower_third(img, cap, age - 0.3)
        for ct, txt in cues:
            if ct - 0.2 <= t <= ct + 3.4:
                img = kinetic(img, txt, t - ct)
        enc.stdin.write(img.convert("RGB").tobytes())
        if f % (FPS * 30) == 0:
            print(f"{t:7.1f}s / {t_end:.1f}s", flush=True)
    enc.stdin.close(); enc.wait()
    return out, total


def mix(ep, total, mood="sea", seed=1):
    """Voice chain + ambient bed with sidechain ducking -> final.mp4"""
    amb = os.path.join(ep, "ambient.wav")
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "ambient.py"), f"{total + 1:.2f}", amb, str(seed), mood], check=True, capture_output=True)
    voice = os.path.join(ep, "audio", "voice_full.wav")
    final = os.path.join(ep, "final.mp4")
    fc = ("[1:a]aresample=48000:resampler=soxr,highpass=f=70,equalizer=f=250:t=q:w=1:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=2,"
          "deesser=i=0.3,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=7,"
          "aformat=channel_layouts=stereo,asplit=2[v][vsc];"
          "[2:a]volume=0.55[bed];[bed][vsc]sidechaincompress=threshold=0.02:ratio=6:attack=40:release=600[ducked];"
          "[v][ducked]amix=inputs=2:duration=first:weights='1 0.35':normalize=0,loudnorm=I=-14:TP=-1.0:LRA=9[a]")
    subprocess.run(["ffmpeg", "-y", "-i", os.path.join(ep, "video_nosound.mp4"), "-i", voice, "-i", amb,
                    "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-ar", "48000", "-movflags", "+faststart", final], check=True, capture_output=True)
    return final


def parallel(ep, mod, n=2, mood="sea"):
    procs = [subprocess.Popen([sys.executable, __file__, ep, mod, "--part", str(i), str(n)]) for i in range(n)]
    for p in procs:
        p.wait()
        if p.returncode:
            raise SystemExit("part failed")
    with open(os.path.join(ep, "parts.txt"), "w") as f:
        for i in range(n):
            f.write(f"file '{os.path.abspath(os.path.join(ep, f'part{i}.mp4'))}'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(ep, "parts.txt"), "-c", "copy",
                    os.path.join(ep, "video_nosound.mp4")], check=True, capture_output=True)
    scenes = json.load(open(os.path.join(ep, "audio", "scenes.json")))
    total = sum(s["duration"] for s in scenes)
    print("FINAL", mix(ep, total, mood))


if __name__ == "__main__":
    ep, mod = sys.argv[1], sys.argv[2]
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    mood = sys.argv[sys.argv.index("--mood") + 1] if "--mood" in sys.argv else "sea"
    if "--part" in sys.argv:
        k = sys.argv.index("--part")
        render(ep, mod, part=(int(sys.argv[k + 1]), int(sys.argv[k + 2])))
    elif "--parallel" in sys.argv:
        parallel(ep, mod, int(sys.argv[sys.argv.index("--parallel") + 1]), mood)
    else:
        out, total = render(ep, mod, only=only)
        print("VIDEO", out)
        if not only:
            print("FINAL", mix(ep, total, mood))
