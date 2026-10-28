"""Build a vertical Short (1080x1920) from a list of (visual_key, sentence) beats.

usage: short.py <spec.json> <out_dir>
spec: {"beats": [{"visual": "wave", "text": "..."}, ...], "crop_x": {"wave": 0.45}}
Each beat: one narrated sentence over a 9:16 crop of the scene, big centred caption, slow push-in.
"""
import json, os, subprocess, sys, wave
sys.path.insert(0, os.path.dirname(__file__))
import visuals as V
from PIL import Image, ImageDraw

PIPER = "/home/claude/tts/piper/piper"
MODEL = "/home/claude/tts/en-us-ryan-high.onnx"
SW, SH, FPS = 1080, 1920, 30
FIT = {"landing_west", "wave", "map", "telegram", "investigator", "logbook", "poem", "verdict", "theories", "theories_real"}


def run(c):
    subprocess.run(c, check=True, capture_output=True)


def tts(text, path):
    subprocess.run([PIPER, "--model", MODEL, "--output_file", path, "--length_scale", "1.0"],
                   input=text.replace("ò", "o").encode(), check=True, capture_output=True)
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def frame(visual, text, cx, cache):
    if visual not in cache:
        cache[visual] = V.render(visual, "")
    src = cache[visual]
    if visual in FIT:
        # diagrams and cards: show the whole 16:9 picture over a blurred fill so no label is cut
        from PIL import ImageFilter
        bg = src.resize((int(SH * V.W / V.H), SH)).crop((0, 0, SW, SH)).filter(ImageFilter.GaussianBlur(40))
        bg = Image.eval(bg, lambda v: int(v * 0.45))
        fg = src.resize((SW, int(SW * V.H / V.W)), Image.LANCZOS)
        bg.paste(fg, (0, 330))
        im = bg
    else:
        cw = int(V.H * SW / SH)  # 810 px wide crop of the 1440-high scene
        x0 = int(max(0, min(V.W - cw, cx * V.W - cw / 2)))
        im = src.crop((x0, 0, x0 + cw, V.H)).resize((SW, SH), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    f = V.font(V.SANS_B, 78)
    lines = V.wrap(d, text, f, SW - 160)
    lh = 100
    y = int(SH * 0.62) - len(lines) * lh // 2
    pad = 36
    box = Image.new("RGBA", (SW - 100, len(lines) * lh + pad * 2), (10, 11, 14, 170))
    im.paste(box, (50, y - pad), box)
    for ln in lines:
        w = d.textlength(ln, font=f)
        d.text(((SW - w) / 2, y), ln, font=f, fill=V.PAPER)
        y += lh
    # channel tag
    tf = V.font(V.SANS_B, 44)
    d.rectangle((60, 120, 60 + d.textlength("THE QUIET ARCHIVE", font=tf) + 40, 190), fill=V.AMBER)
    d.text((80, 128), "THE QUIET ARCHIVE", font=tf, fill=V.BG)
    return im


def main(spec_path, out):
    spec = json.load(open(spec_path))
    os.makedirs(out, exist_ok=True)
    cache, parts = {}, []
    for i, b in enumerate(spec["beats"]):
        wav = os.path.join(out, f"b{i:02}.wav")
        dur = tts(b["text"], wav) + 0.25
        png = os.path.join(out, f"b{i:02}.png")
        frame(b["visual"], b["text"], spec.get("crop_x", {}).get(b["visual"], 0.5), cache).save(png)
        n = int(dur * FPS) + 1
        mp4 = os.path.join(out, f"b{i:02}.mp4")
        run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", png, "-i", wav,
             "-vf", f"scale=1296:2304,zoompan=z='min(1+0.06*on/{n},1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={SW}x{SH}:fps={FPS},format=yuv420p",
             "-af", "apad=pad_dur=0.25", "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "24",
             "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2", mp4])
        parts.append(f"file '{os.path.abspath(mp4)}'")
    open(os.path.join(out, "list.txt"), "w").write("\n".join(parts))
    body = os.path.join(out, "body.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(out, "list.txt"), "-c", "copy", body])
    final = os.path.join(out, "short.mp4")
    run(["ffmpeg", "-y", "-i", body, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart", final])
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", final],
                             capture_output=True, text=True).stdout)
    print("SHORT", final, round(d, 1), "s", os.path.getsize(final))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
