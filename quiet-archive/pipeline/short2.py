"""Shorts builder v2: Kokoro voice, smooth vertical camera, word-chunk captions, ambient bed with ducking.

usage: short2.py <spec.json> <out_dir>
spec: {
  "mood": "sea" | "dread",
  "hook": "BIG TEXT shown for the first 2.6 s",
  "beats": [{"img": "ep02/frames/s09_0.png", "text": "One narrated sentence.",
             "cam": [cx, cy, z0, z1, dx, dy]}   # cam optional
           ...]
}
Output: <out_dir>/final.mp4 (1080x1920, 25 fps), <out_dir>/captions.srt
"""
import json, os, re, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import visuals as V
import render2 as R
from kokoro_tts import synth

SW, SH, FPS = 1080, 1920, 25
SR = 24000
GAP = 0.28
XF = 0.35
LEAD = 0.25


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def cam(src, fr, u):
    cx, cy, z0, z1, dx, dy = fr
    e = ease(u)
    z = z0 + (z1 - z0) * e
    vh = src.height / z
    vw = vh * SW / SH
    cxp = (cx + dx * e) * src.width
    cyp = (cy + dy * e) * src.height
    x0 = min(max(cxp - vw / 2, 0), src.width - vw)
    y0 = min(max(cyp - vh / 2, 0), src.height - vh)
    s = vw / SW
    return src.transform((SW, SH), Image.AFFINE, (s, 0, x0, 0, s, y0), resample=Image.BILINEAR)


def chunks(text, n=3):
    words = text.split()
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= n or re.search(r"[.,;:!?]$", w):
            out.append(" ".join(cur)); cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def fmt(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def main(spec_path, out):
    spec = json.load(open(spec_path))
    os.makedirs(os.path.join(out, "audio"), exist_ok=True)
    beats = spec["beats"]
    # ---- voice
    pieces, t, cues, srt = [np.zeros(int(SR * LEAD), np.float32)], LEAD, [], []
    for i, b in enumerate(beats):
        a = synth(b["text"])
        nz = np.where(np.abs(a) > 0.01)[0]
        if len(nz):
            a = a[max(0, nz[0] - 240): nz[-1] + 2400]
        d = len(a) / SR
        b["t0"], b["t1"] = t, t + d
        ch = chunks(b["text"])
        tot = sum(len(c) for c in ch)
        tc = t
        for c in ch:
            dc = d * len(c) / tot
            cues.append((tc, tc + dc, c)); tc += dc
        srt.append((t, t + d, b["text"]))
        pieces += [a, np.zeros(int(SR * GAP), np.float32)]
        t += d + GAP
    voice = np.concatenate(pieces + [np.zeros(int(SR * 0.9), np.float32)])
    total = len(voice) / SR
    with wave.open(os.path.join(out, "audio", "voice_full.wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(voice, -1, 1) * 32767).astype(np.int16).tobytes())
    with open(os.path.join(out, "captions.srt"), "w") as f:
        for k, (a, b2, s) in enumerate(srt, 1):
            f.write(f"{k}\n{fmt(a)} --> {fmt(b2)}\n{s}\n\n")
    # beat windows: each beat shows from its t0 (first from 0) to next beat's t0 (+XF overlap)
    for i, b in enumerate(beats):
        b["s0"] = 0.0 if i == 0 else b["t0"] - XF / 2
        b["s1"] = total if i == len(beats) - 1 else beats[i + 1]["t0"] + XF / 2
    defaults = [(0.5, 0.5, 1.0, 1.12, 0.06, 0.0), (0.45, 0.5, 1.15, 1.05, -0.05, 0.0),
                (0.55, 0.45, 1.05, 1.2, 0.0, 0.03), (0.4, 0.5, 1.1, 1.18, 0.08, 0.0)]
    stills = {}
    for i, b in enumerate(beats):
        key = b["img"] + ("#fit" if b.get("fit") else "")
        if key not in stills:
            src = Image.open(b["img"]).convert("RGB")
            if b.get("fit"):
                # whole 16:9 picture on a blurred vertical canvas, so baked-in text is never cut
                from PIL import ImageFilter
                CW, CH = int(SW * 1.5), int(SH * 1.5)
                bg = src.resize((int(CH * src.width / src.height), CH)).crop((0, 0, CW, CH)).filter(ImageFilter.GaussianBlur(50))
                bg = Image.eval(bg, lambda v: int(v * 0.45))
                fg = src.resize((CW, int(CW * src.height / src.width)), Image.LANCZOS)
                bg.paste(fg, (0, int(CH * 0.24)))
                src = bg
            stills[key] = src
        b["key"] = key
        b["fr"] = tuple(b.get("cam") or ((0.5, 0.5, 1.0, 1.06, 0.0, 0.0) if b.get("fit") else defaults[i % len(defaults)]))
    f_cap = ImageFont.truetype(V.SANS_B, 92)
    f_tag = ImageFont.truetype(V.SANS_B, 40)
    f_hook = ImageFont.truetype(V.SERIF_B, 120)
    hook = spec.get("hook", "")
    vid = os.path.join(out, "video_nosound.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SW}x{SH}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                           "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    nfr = int(total * FPS)
    for n in range(nfr):
        tt = n / FPS
        act = [b for b in beats if b["s0"] <= tt < b["s1"]] or [beats[-1]]
        def bf(b):
            return cam(stills[b["key"]], b["fr"], (tt - b["s0"]) / max(b["s1"] - b["s0"], 0.1))
        im = bf(act[0])
        if len(act) > 1:
            a = ease((tt - act[1]["s0"]) / XF)
            im = Image.blend(im, bf(act[1]), a)
        # darken edges for legibility
        im = im.convert("RGBA")
        lay = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rectangle((0, 0, SW, 260), fill=(0, 0, 0, 90))
        # channel tag
        tw = d.textlength("THE QUIET ARCHIVE", font=f_tag)
        d.rectangle((60, 130, 60 + tw + 36, 192), fill=V.AMBER + (235,))
        d.text((78, 138), "THE QUIET ARCHIVE", font=f_tag, fill=V.BG)
        # hook
        if hook and tt < 2.8:
            al = ease(tt / 0.35) * (1 - ease((tt - 2.4) / 0.4))
            lines = V.wrap(d, hook, f_hook, SW - 140)
            y = int(SH * 0.30)
            for ln in lines:
                w = d.textlength(ln, font=f_hook)
                d.text(((SW - w) / 2, y), ln, font=f_hook, fill=V.PAPER + (int(255 * al),),
                       stroke_width=6, stroke_fill=(0, 0, 0, int(220 * al)))
                y += 140
        # word-chunk caption
        cur = [c for c in cues if c[0] <= tt < c[1] + 0.12]
        if cur:
            c0, c1, txt = cur[-1]
            pop = 0.9 + 0.1 * ease((tt - c0) / 0.12)
            fs = ImageFont.truetype(V.SANS_B, int(92 * pop))
            lines = V.wrap(d, txt.upper(), fs, SW - 160)
            y = int(SH * 0.64) - len(lines) * 60
            for ln in lines:
                w = d.textlength(ln, font=fs)
                d.text(((SW - w) / 2, y), ln, font=fs, fill=(255, 255, 255, 255), stroke_width=7, stroke_fill=(0, 0, 0, 255))
                y += 118
        im = Image.alpha_composite(im, lay).convert("RGB")
        ff.stdin.write(im.tobytes())
    ff.stdin.close(); ff.wait()
    R.mix(out, total, spec.get("mood", "sea"))
    print("FINAL", os.path.join(out, "final.mp4"), f"{total:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
