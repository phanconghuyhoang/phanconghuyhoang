"""Renderer v3: host-driven animated stick-figure videos (long-form 16:9 or vertical Shorts).

usage: render3.py <ep_dir> [--vertical] [--part i n] [--parallel n] [--mood dread]
Inputs : <ep_dir>/audio/{scenes.json, voice_full.wav} from narrate3.py
Output : <ep_dir>/final.mp4  (+ captions from audio/narration.srt)

Scene backgrounds: "room" (the host's archive set), "card:Title|line|line", or an image path relative to the
project root (append "#fit" to show the whole picture). Layouts: "host" (Archie big, centre) or "story"
(background picture, cast on stage, Archie small in the corner).
"""
import json, math, os, random, re, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import visuals as V
import character as C
import sfx as SFX

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 25
W, H = 1920, 1080
VERT = False
SS = 2


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------ backgrounds

def room_bg():
    """The host's set: a dim archive with shelves of boxes and a warm desk lamp."""
    BW, BH = 2560, 1440
    im = Image.new("RGB", (BW, BH), (26, 27, 32))
    d = ImageDraw.Draw(im)
    rng = random.Random(7)
    # back wall gradient
    for y in range(BH):
        c = int(24 + 10 * (y / BH))
        d.line([(0, y), (BW, y)], fill=(c, c + 1, c + 6))
    # shelves
    for sx in (60, 700, 1660, 2200):
        w = 520 if sx in (60, 1660) else 300
        d.rectangle((sx, 120, sx + w, 1060), fill=(38, 32, 28))
        for k in range(6):
            y = 180 + k * 150
            d.rectangle((sx, y + 110, sx + w, y + 124), fill=(70, 54, 40))
            x = sx + 14
            while x < sx + w - 60:
                bw = rng.randint(48, 110); bh = rng.randint(70, 104)
                col = rng.choice([(120, 96, 70), (140, 118, 86), (96, 80, 62), (150, 132, 100), (110, 88, 60)])
                d.rectangle((x, y + 110 - bh, x + bw - 6, y + 110), fill=col)
                d.rectangle((x + bw * 0.2, y + 110 - bh * 0.6, x + bw * 0.7, y + 110 - bh * 0.45), fill=(225, 214, 190))
                x += bw
    # floor
    d.rectangle((0, 1060, BW, BH), fill=(44, 36, 30))
    for k in range(14):
        d.line([(k * 200, 1060), (k * 200 - 300, BH)], fill=(52, 42, 35), width=4)
    # desk at right with lamp
    d.rectangle((1900, 900, 2420, 940), fill=(92, 64, 44)); d.rectangle((1930, 940, 1960, 1200), fill=(70, 50, 36)); d.rectangle((2360, 940, 2390, 1200), fill=(70, 50, 36))
    d.line([(2250, 900), (2230, 760), (2300, 700)], fill=(30, 30, 30), width=10)
    d.polygon([(2270, 690), (2350, 670), (2370, 740), (2300, 760)], fill=(200, 150, 60))
    d.rectangle((1980, 850, 2120, 900), fill=(150, 130, 100)); d.rectangle((2000, 820, 2100, 850), fill=(200, 186, 160))
    # warm lamp glow + vignette
    glow = Image.new("L", (BW, BH), 0); g = ImageDraw.Draw(glow)
    g.ellipse((1650, 500, 2700, 1300), fill=110); g.ellipse((700, 300, 1860, 1300), fill=60)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    warm = Image.new("RGB", (BW, BH), (255, 190, 110))
    im = Image.composite(warm, im, glow.point(lambda v: int(v * 0.45)))
    vig = Image.new("L", (BW, BH), 0); ImageDraw.Draw(vig).ellipse((-300, -200, BW + 300, BH + 200), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(220))
    im = Image.composite(im, Image.new("RGB", (BW, BH), (8, 8, 10)), vig)
    return im


def card_bg(spec):
    BW, BH = 2560, 1440
    parts = spec.split("|")
    im = Image.new("RGB", (BW, BH), (24, 25, 30))
    d = ImageDraw.Draw(im)
    pw, ph = 1700, 980
    x0, y0 = (BW - pw) // 2, (BH - ph) // 2
    d.rectangle((x0 + 20, y0 + 24, x0 + pw + 20, y0 + ph + 24), fill=(10, 10, 12))
    d.rectangle((x0, y0, x0 + pw, y0 + ph), fill=(234, 224, 200))
    ft = ImageFont.truetype(V.SERIF_B, 92); fb = ImageFont.truetype(V.SERIF, 64)
    d.text((x0 + 90, y0 + 80), parts[0], font=ft, fill=(30, 28, 26))
    d.line([(x0 + 90, y0 + 210), (x0 + pw - 90, y0 + 210)], fill=(120, 110, 96), width=4)
    y = y0 + 260
    for ln in parts[1:]:
        stamp = ln.startswith("!")
        ln = ln.lstrip("!")
        for w in V.wrap(d, ln, fb, pw - 180):
            d.text((x0 + 90, y), w, font=fb, fill=(170, 50, 40) if stamp else (40, 38, 34)); y += 84
        y += 26
    return im


_bg_cache = {}


def load_bg(spec):
    if spec in _bg_cache:
        return _bg_cache[spec]
    fit = spec.endswith("#fit")
    s = spec[:-4] if fit else spec
    if s == "room":
        im = room_bg()
    elif s.startswith("card:"):
        im = card_bg(s[5:]); fit = True
    else:
        im = Image.open(os.path.join(ROOT, s)).convert("RGB")
        if im.size != (2560, 1440):
            im = im.resize((2560, 1440), Image.LANCZOS)
    if VERT and fit:
        CW, CH = int(W * 1.5), int(H * 1.5)
        bg = im.resize((int(CH * im.width / im.height), CH)).crop((0, 0, CW, CH)).filter(ImageFilter.GaussianBlur(50))
        bg = Image.eval(bg, lambda v: int(v * 0.45))
        fg = im.resize((CW, int(CW * im.height / im.width)), Image.LANCZOS)
        bg.paste(fg, (0, int(CH * 0.2)))
        im = bg
    _bg_cache[spec] = (im, fit)
    return _bg_cache[spec]


def cam(src, fr, u):
    cx, cy, z0, z1, dx, dy = fr
    e = ease(u)
    z = z0 + (z1 - z0) * e
    if src.width / src.height > W / H:
        vh = src.height / z; vw = vh * W / H
    else:
        vw = src.width / z; vh = vw * H / W
    cxp = (cx + dx * e) * src.width; cyp = (cy + dy * e) * src.height
    x0 = min(max(cxp - vw / 2, 0), src.width - vw); y0 = min(max(cyp - vh / 2, 0), src.height - vh)
    s = vw / W
    return src.transform((W, H), Image.AFFINE, (s, 0, x0, 0, s, y0), resample=Image.BILINEAR)


DEFAULT_CAMS = [(0.5, 0.5, 1.0, 1.08, 0.0, 0.0), (0.45, 0.5, 1.12, 1.04, 0.05, 0.0), (0.55, 0.48, 1.04, 1.14, -0.03, 0.02)]

# ------------------------------------------------------------------ text

def kinetic(frame, text, age, dur=2.6):
    if age < 0 or age > dur:
        return
    a = ease(age / 0.25) * (1 - ease((age - (dur - 0.4)) / 0.4))
    pop = 1.0 + 0.25 * (1 - ease(age / 0.22))
    d = ImageDraw.Draw(frame)
    size = int((120 if not VERT else 110) * pop)
    font = ImageFont.truetype(V.SANS_B, size)
    lines = V.wrap(d, text, font, W - 200)
    while len(lines) > 3 and size > 60:
        size -= 8; font = ImageFont.truetype(V.SANS_B, size); lines = V.wrap(d, text, font, W - 200)
    y = H * (0.18 if VERT else 0.14)
    for ln in lines:
        w = d.textlength(ln, font=font)
        d.text(((W - w) / 2, y), ln, font=font, fill=(255, 214, 120, int(255 * a)), stroke_width=max(4, size // 14), stroke_fill=(10, 10, 12, int(255 * a)))
        y += size * 1.12


def chunk_words(text, n=3):
    out, cur = [], []
    for w in text.split():
        cur.append(w)
        if len(cur) >= n or re.search(r"[.,;:!?]$", w):
            out.append(" ".join(cur)); cur = []
    if cur:
        out.append(" ".join(cur))
    return out


# ------------------------------------------------------------------ figures

def paste_figure(frame, actor, t, x, y, r, mouth=0.0, facing=1, alpha=255):
    """Draw an actor on a local supersampled canvas and composite it at hip (x, y)."""
    cw, ch = int(r * 9), int(r * 9.5)
    lay = Image.new("RGBA", (cw * SS, ch * SS), (0, 0, 0, 0))
    hx, hy = cw * SS / 2, ch * SS * 0.62
    actor.draw(lay, hx, hy, r * SS, t, mouth, facing, alpha)
    lay = lay.resize((cw, ch), Image.LANCZOS)
    frame.alpha_composite(lay, (int(x - cw / 2), int(y - ch * 0.62)))


class Cast:
    def __init__(self, cid, look, x, y, r, seed):
        self.id = cid
        self.actor = C.Actor(C.Look(look), seed=seed, talk_gestures=False)
        self.x0 = self.x = x; self.y = y; self.r = r
        self.facing = 1; self.alpha_t = None; self.enter_t = None
        self.walk = None   # (t0, t1, xa, xb)
        self.talk = []     # (t0, t1)

    def pos(self, t):
        if self.walk and self.walk[0] <= t:
            t0, t1, xa, xb = self.walk
            u = ease((t - t0) / max(t1 - t0, 0.1))
            return xa + (xb - xa) * u, self.walk[1] > t
        return self.x, False


def parse_cast_cmd(v):
    # "id=look@x,y,r" | "id pose/expr" | "id walk>x" | "id face<" | "id face>" | "id exit" | "id talk"
    m = re.match(r"(\w+)=(\w+)@([\d.]+),([\d.]+)(?:,([\d.]+))?", v)
    if m:
        return ("new", m.group(1), m.group(2), float(m.group(3)), float(m.group(4)), float(m.group(5) or 0.045))
    p = v.split()
    return ("cmd", p[0], " ".join(p[1:]))


# ------------------------------------------------------------------ main render

def build_timeline(ep):
    scenes = json.load(open(os.path.join(ep, "audio", "scenes.json")))
    t0 = 0.0
    for sc in scenes:
        sc["t0"] = t0
        for s in sc["sentences"]:
            s["t"] = t0 + s["start"]; s["te"] = t0 + s["end"]
        t0 += sc["duration"]
        sc["t1"] = t0
    return scenes, t0


def render(ep, part=None, mood="sea"):
    scenes, total = build_timeline(ep)
    # voice envelope for lip-sync
    with wave.open(os.path.join(ep, "audio", "voice_full.wav")) as w:
        sr = w.getframerate(); pcm = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    mouth = C.mouth_track(pcm, sr, FPS)

    host = C.Actor(C.Look("archie"), seed=11)
    cast = {}
    kin, sfx_cues, zooms, bgs, words = [], [], [], [], []
    seed = 100
    for sc in scenes:
        host.key(sc["t0"], "talk", "neutral")
        bgs.append([sc["t0"], sc["bg"], None, sc["layout"]])
        if sc["layout"] == "host" and sc is not scenes[0]:
            sfx_cues.append((sc["t0"], "whoosh"))
        for s in sc["sentences"]:
            t = s["t"]
            for k, v in s["tags"]:
                if k == "a":
                    pz, _, ex = v.partition("/")
                    host.key(t, pz or "talk", ex or None)
                elif k == "t":
                    kin.append((t, v)); sfx_cues.append((t, "pop"))
                elif k == "s":
                    sfx_cues.append((t, v))
                elif k == "z":
                    zooms.append((t, s["te"]))
                elif k == "bg":
                    bgs.append([t, v, None, sc["layout"]])
                elif k == "cam":
                    bgs[-1][2] = tuple(float(x) for x in v.split(","))
                elif k == "c":
                    for cmd in v.split(";"):
                        c = parse_cast_cmd(cmd.strip())
                        if c[0] == "new":
                            seed += 1
                            cast[c[1]] = Cast(c[1], c[2], c[3], c[4], c[5], seed)
                            cast[c[1]].enter_t = t
                            cast[c[1]].actor.key(0, "idle", "neutral")
                        else:
                            a = cast.get(c[1])
                            if not a:
                                continue
                            arg = c[2]
                            if arg.startswith("walk>"):
                                x, _ = a.pos(t)
                                a.walk = (t, t + 1.6, x, float(arg[5:])); a.x = float(arg[5:])
                                a.actor.key(t, "walk_a", None); a.actor.key(t + 1.6, "idle", None)
                            elif arg == "face<":
                                a.facing = -1
                            elif arg == "face>":
                                a.facing = 1
                            elif arg == "exit":
                                a.alpha_t = t
                            elif arg == "talk":
                                a.talk.append((s["t"], s["te"]))
                            elif arg.startswith("jump"):
                                a.actor.key(t, "jump", None); a.actor.key(t + 0.6, "idle", None)
                            else:
                                pz, _, ex = arg.partition("/")
                                a.actor.key(t, pz or "idle", ex or None)
            if s["text"]:
                if VERT:
                    ch = chunk_words(s["text"])
                    tot = sum(len(c) for c in ch); tc = s["t"]
                    for c in ch:
                        dc = (s["te"] - s["t"]) * len(c) / tot
                        words.append((tc, tc + dc, c)); tc += dc
        # cast present only within their scene
        for a in cast.values():
            if a.alpha_t is None and a.enter_t is not None and sc["t0"] <= a.enter_t < sc["t1"]:
                a.alpha_t = sc["t1"]
    cast_list = list(cast.values())

    nfr = int(total * FPS)
    fr0, fr1 = 0, nfr
    if part:
        i, n = part
        fr0, fr1 = nfr * i // n, nfr * (i + 1) // n
    out = os.path.join(ep, f"v3_part{part[0]}.mp4" if part else "v3_nosound.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    fcap = ImageFont.truetype(V.SANS_B, 84)
    ftag = ImageFont.truetype(V.SANS_B, 34)
    for n in range(fr0, fr1):
        t = n / FPS
        seg = [b for b in bgs if b[0] <= t][-1]
        k = bgs.index(seg)
        seg_end = bgs[k + 1][0] if k + 1 < len(bgs) else total
        img, fit = load_bg(seg[1])
        fr = seg[2] or ((0.5, 0.5, 1.0, 1.05, 0, 0) if fit else DEFAULT_CAMS[k % len(DEFAULT_CAMS)])
        if seg[1] == "room":
            fr = (0.5, 0.55, 1.08, 1.12, 0, 0)
        frame = cam(img, fr, (t - seg[0]) / max(seg_end - seg[0], 0.5)).convert("RGBA")
        layout = seg[3]
        m = float(mouth[min(n, len(mouth) - 1)])
        # cast
        for a in cast_list:
            if a.enter_t is None or t < a.enter_t or (a.alpha_t is not None and t > a.alpha_t + 0.3):
                continue
            al = ease((t - a.enter_t) / 0.3)
            if a.alpha_t is not None and t > a.alpha_t:
                al *= 1 - ease((t - a.alpha_t) / 0.3)
            x, _ = a.pos(t)
            talking = any(t0 <= t <= t1 for t0, t1 in a.talk)
            paste_figure(frame, a.actor, t, x * W, a.y * H - 2.35 * a.r * min(W, H), a.r * min(W, H),
                         m if talking else 0.0, a.facing, int(255 * al))
        # host
        if layout == "host":
            hr = H * 0.085 if not VERT else W * 0.1
            hx, hy = W * 0.5, H * 0.965 - 2.35 * hr
        else:
            hr = H * 0.052 if not VERT else W * 0.07
            hx, hy = W * (0.89 if not VERT else 0.82), H * 0.975 - 2.35 * hr
            # soft shadow pad so the corner host reads over any picture
            pad = Image.new("RGBA", (int(hr * 8), int(hr * 8)), (0, 0, 0, 0))
            ImageDraw.Draw(pad).ellipse((hr * 1.3, hr * 1.3, pad.width - hr * 1.3, pad.height - hr * 1.3), fill=(0, 0, 0, 110))
            pad = pad.filter(ImageFilter.GaussianBlur(hr))
            frame.alpha_composite(pad, (int(hx - pad.width / 2), int(hy - pad.height * 0.62)))
        paste_figure(frame, host, t, hx, hy, hr, m)
        # comedic zoom on the host's face
        for z0, z1 in zooms:
            if z0 <= t <= z1 + 0.15:
                u = ease((t - z0) / 0.18) * (1 - ease((t - z1) / 0.15))
                zf = 1 + 0.6 * u if layout == "host" else 1 + 1.4 * u
                fx, fy = hx, hy - hr * 4.6
                vw, vh = W / zf, H / zf
                x0 = min(max(fx - vw / 2, 0), W - vw); y0 = min(max(fy - vh / 2, 0), H - vh)
                frame = frame.transform((W, H), Image.AFFINE, (vw / W, 0, x0, 0, vh / H, y0), resample=Image.BILINEAR)
        # kinetic titles
        for tk, txt in kin:
            kinetic(frame, txt, t - tk)
        d = ImageDraw.Draw(frame)
        if VERT:
            cur = [c for c in words if c[0] <= t < c[1] + 0.1]
            if cur:
                c0, c1, txt = cur[-1]
                pop = 0.9 + 0.1 * ease((t - c0) / 0.12)
                fs = ImageFont.truetype(V.SANS_B, int(84 * pop))
                lines = V.wrap(d, txt.upper(), fs, W - 160)
                y = H * 0.6 - len(lines) * 50
                for ln in lines:
                    w = d.textlength(ln, font=fs)
                    d.text(((W - w) / 2, y), ln, font=fs, fill=(255, 255, 255), stroke_width=7, stroke_fill=(0, 0, 0))
                    y += 104
            tw = d.textlength("THE QUIET ARCHIVE", font=ftag)
            d.rectangle((54, 120, 54 + tw + 30, 172), fill=V.AMBER)
            d.text((69, 126), "THE QUIET ARCHIVE", font=ftag, fill=V.BG)
        ff.stdin.write(frame.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    return out, total, sfx_cues


def mix(ep, total, sfx_cues, mood):
    amb = os.path.join(ep, "ambient.wav")
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "ambient.py"), f"{total + 1:.2f}", amb, "3", mood], check=True, capture_output=True)
    fxw = os.path.join(ep, "sfx.wav")
    tr = SFX.track(sfx_cues, total)
    with wave.open(fxw, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SFX.SR)
        w.writeframes((np.clip(tr, -1, 1) * 32767).astype(np.int16).tobytes())
    voice = os.path.join(ep, "audio", "voice_full.wav")
    final = os.path.join(ep, "final.mp4")
    fc = ("[1:a]aresample=48000:resampler=soxr,highpass=f=70,equalizer=f=250:t=q:w=1:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=2,"
          "deesser=i=0.3,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=7,"
          "aformat=channel_layouts=stereo,asplit=2[v][vsc];"
          "[2:a]volume=0.5[bed];[bed][vsc]sidechaincompress=threshold=0.02:ratio=6:attack=40:release=600[ducked];"
          "[3:a]volume=0.8[fx];"
          "[v][ducked][fx]amix=inputs=3:duration=first:weights='1 0.3 0.6':normalize=0,loudnorm=I=-14:TP=-1.0:LRA=9[a]")
    subprocess.run(["ffmpeg", "-y", "-i", os.path.join(ep, "v3_nosound.mp4"), "-i", voice, "-i", amb, "-i", fxw,
                    "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-ar", "48000", "-movflags", "+faststart", final], check=True, capture_output=True)
    return final


def main():
    global W, H, VERT
    a = sys.argv[1:]
    ep = a[0]
    if "--vertical" in a:
        VERT = True; W, H = 1080, 1920
    mood = a[a.index("--mood") + 1] if "--mood" in a else "sea"
    if "--part" in a:
        i = a.index("--part"); render(ep, (int(a[i + 1]), int(a[i + 2])), mood); return
    n = int(a[a.index("--parallel") + 1]) if "--parallel" in a else 1
    if n > 1:
        base = [sys.executable, __file__, ep] + (["--vertical"] if VERT else [])
        ps = [subprocess.Popen(base + ["--part", str(i), str(n)]) for i in range(n)]
        if any(p.wait() for p in ps):
            print("part failed"); sys.exit(1)
        lst = os.path.join(ep, "v3_parts.txt")
        open(lst, "w").write("".join(f"file 'v3_part{i}.mp4'\n" for i in range(n)))
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", os.path.join(ep, "v3_nosound.mp4")], check=True)
        _, total = build_timeline(ep)
        # sfx cues are deterministic: rebuild cheaply by parsing tags
        cues = sfx_from_scenes(ep)
    else:
        _, total, cues = render(ep, None, mood)
        os.replace(os.path.join(ep, "v3_nosound.mp4"), os.path.join(ep, "v3_nosound.mp4"))
    print("FINAL", mix(ep, total, cues, mood), f"{total:.1f}s")


def sfx_from_scenes(ep):
    scenes, _ = build_timeline(ep)
    cues = []
    for sc in scenes:
        if sc["layout"] == "host" and sc is not scenes[0]:
            cues.append((sc["t0"], "whoosh"))
        for s in sc["sentences"]:
            for k, v in s["tags"]:
                if k == "t":
                    cues.append((s["t"], "pop"))
                elif k == "s":
                    cues.append((s["t"], v))
    return cues


if __name__ == "__main__":
    main()
