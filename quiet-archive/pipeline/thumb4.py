"""Thumbnail styles for A/B testing. Each style looks clearly different so tests teach us something.

usage: thumb4.py <style> <out.jpg> <bg.png> <cx,cy,zoom> "<TEXT>" [extra]
styles:
  reaction   bright burst background, framed photo of the subject, big shocked Archie, red arrow, bold text
  cinematic  dark colour-graded close-up of the subject, red circle on the detail, 2-3 words, no mascot
  evidence   aged case-file paper, polaroid of the subject, red marker text, stamp, Archie peeking
  question   near-black, glowing subject silhouette, giant red question mark, one or two words
cx,cy = focus point as fractions of the 2560x1440 background, zoom = how tight the crop is (1 = whole frame).
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, os.path.dirname(__file__))
import visuals as V
import character as C

W, H = 1280, 720
SS = 2


def crop(bg, cx, cy, zoom, w, h):
    im = Image.open(bg).convert("RGB")
    cw = im.width / zoom; ch = cw * h / w
    if ch > im.height:
        ch = im.height; cw = ch * w / h
    x0 = min(max(cx * im.width - cw / 2, 0), im.width - cw); y0 = min(max(cy * im.height - ch / 2, 0), im.height - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((w, h), Image.LANCZOS)


def text(d, xy, s, size, fill=(255, 255, 255), stroke=10, font=V.SANS_B, maxw=None, anchor="la"):
    f = ImageFont.truetype(font, size)
    if maxw:
        while d.textlength(s, font=f) > maxw and size > 40:
            size -= 4; f = ImageFont.truetype(font, size)
    d.text(xy, s, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0), anchor=anchor)
    return size


def archie(im, x, y, r, pose="lean_in", expr="shocked", mouth=0.8):
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    C.draw_figure(lay, x * SS, y * SS, r * SS, C.pose(pose), expr, mouth, 0, C.Look("archie"))
    im.alpha_composite(lay.resize((W, H), Image.LANCZOS))


def arrow(d, p0, p1, col=(230, 30, 30), w=22):
    d.line([p0, p1], fill=col, width=w)
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    L = w * 2.6
    pts = [p1, (p1[0] - L * math.cos(a - 0.5), p1[1] - L * math.sin(a - 0.5)), (p1[0] - L * math.cos(a + 0.5), p1[1] - L * math.sin(a + 0.5))]
    d.polygon(pts, fill=col)


def reaction(bg, focus, txt):
    im = Image.new("RGBA", (W, H), (255, 196, 40, 255))
    d = ImageDraw.Draw(im)
    for k in range(24):  # burst
        a0 = k * math.pi / 12; a1 = a0 + math.pi / 24
        d.polygon([(900, 360), (900 + 1600 * math.cos(a0), 360 + 1600 * math.sin(a0)), (900 + 1600 * math.cos(a1), 360 + 1600 * math.sin(a1))], fill=(255, 168, 20, 255))
    photo = crop(bg, *focus, 620, 400)
    photo = ImageEnhance.Color(photo).enhance(1.4)
    card = ImageOps.expand(photo, border=14, fill="white").convert("RGBA").rotate(-4, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
    im.alpha_composite(card.convert("RGBA"), (40, 270))
    archie(im, 1060, 690, 120, "lean_in", "shocked", 0.9)
    d = ImageDraw.Draw(im)
    arrow(d, (905, 470), (690, 450))
    f = ImageFont.truetype(V.SANS_B, 112)
    lines = V.wrap(d, txt, f, 860)
    y = 24
    for i, ln in enumerate(lines[:2]):
        d.text((48, y), ln, font=f, fill=(255, 255, 255) if i == 0 else (230, 30, 30), stroke_width=12, stroke_fill=(0, 0, 0)); y += 118
    return im


def cinematic(bg, focus, txt):
    im = crop(bg, *focus, W, H)
    im = ImageEnhance.Contrast(im).enhance(1.35); im = ImageEnhance.Brightness(im).enhance(0.7)
    r, g, b = im.split()  # teal-orange grade
    im = Image.merge("RGB", (r.point(lambda v: min(255, int(v * 1.08 + 8))), g, b.point(lambda v: min(255, int(v * 1.12 + 10)))))
    vig = Image.new("L", (W, H), 0); ImageDraw.Draw(vig).ellipse((-200, -150, W + 200, H + 150), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(140))
    im = Image.composite(im, Image.new("RGB", (W, H), (0, 0, 0)), vig).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.ellipse((W * 0.5 - 190, H * 0.45 - 150, W * 0.5 + 190, H * 0.45 + 150), outline=(235, 30, 30), width=14)
    text(d, (W / 2, H - 70), txt, 110, (255, 214, 60), 10, maxw=W - 120, anchor="ms")
    return im


def evidence(bg, focus, txt):
    im = Image.new("RGBA", (W, H), (214, 196, 160, 255))
    d = ImageDraw.Draw(im)
    rng = random.Random(3)
    for _ in range(3000):
        x, y = rng.uniform(0, W), rng.uniform(0, H); c = rng.randint(170, 200)
        d.point((x, y), fill=(c, c - 18, c - 50, 255))
    for y in range(90, H, 46):
        d.line([(0, y), (W, y)], fill=(170, 186, 210, 255), width=2)
    photo = ImageEnhance.Color(crop(bg, *focus, 560, 420)).enhance(0.55)
    pol = ImageOps.expand(photo, border=(18, 18, 18, 80), fill=(246, 244, 236)).convert("RGBA").rotate(6, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
    im.alpha_composite(pol.convert("RGBA"), (640, 90))
    d = ImageDraw.Draw(im)
    lines = txt.split("|")
    y = 120
    for ln in lines:
        text(d, (60, y), ln, 104, (200, 20, 20), 0, font=V.SERIF_B, maxw=560); y += 128
    V.stamp(im, "UNSOLVED", (330, 600), angle=-10, size=70)
    archie(im, 1180, 900, 95, "think", "suspicious", 0.0)
    return im


def question(bg, focus, txt):
    sub = crop(bg, *focus, 700, 500).convert("L")
    sub = ImageOps.autocontrast(sub)
    glow = Image.new("RGB", (W, H), (6, 8, 14))
    d = ImageDraw.Draw(glow)
    lay = Image.new("L", (W, H), 0); ImageDraw.Draw(lay).ellipse((300, 100, 1000, 640), fill=200)
    lay = lay.filter(ImageFilter.GaussianBlur(90))
    glow = Image.composite(Image.new("RGB", (W, H), (40, 70, 110)), glow, lay)
    tint = ImageOps.colorize(sub, (6, 8, 14), (170, 210, 255)).resize((700, 500))
    mask = Image.new("L", (700, 500), 0); ImageDraw.Draw(mask).ellipse((60, 40, 640, 460), fill=255); mask = mask.filter(ImageFilter.GaussianBlur(50))
    glow.paste(tint, (300, 110), mask)
    im = glow.convert("RGBA"); d = ImageDraw.Draw(im)
    text(d, (1090, 600), "?", 620, (230, 30, 30), 14, anchor="ms")
    text(d, (60, 640), txt, 100, (255, 255, 255), 10, maxw=760, anchor="ls")
    return im


STYLES = dict(reaction=reaction, cinematic=cinematic, evidence=evidence, question=question)

if __name__ == "__main__":
    style, out, bg, focus, txt = sys.argv[1:6]
    f = tuple(float(x) for x in focus.split(","))
    STYLES[style](bg, f, txt).convert("RGB").save(out, quality=92)
