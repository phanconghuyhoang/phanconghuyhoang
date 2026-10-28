"""Thumbnail with Archie: thumb3.py <bg.png> <out.jpg> "<TEXT>" [pose] [expr] [cast_look]"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
sys.path.insert(0, os.path.dirname(__file__))
import visuals as V
import character as C

bg, out, text = sys.argv[1], sys.argv[2], sys.argv[3]
pose = sys.argv[4] if len(sys.argv) > 4 else "point_l"
expr = sys.argv[5] if len(sys.argv) > 5 else "shocked"
cast = sys.argv[6] if len(sys.argv) > 6 else None
W, H = 1280, 720
im = Image.open(bg).convert("RGB").resize((W, H), Image.LANCZOS)
im = ImageEnhance.Color(im).enhance(1.35); im = ImageEnhance.Contrast(im).enhance(1.15)
im = im.convert("RGBA")
# darken left for text
grad = Image.new("L", (W, 1)); [grad.putpixel((x, 0), int(170 * max(0, 1 - x / (W * 0.62)))) for x in range(W)]
im.alpha_composite(Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [grad.resize((W, H))]))
SS = 2
lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
if cast:
    C.draw_figure(lay, 820 * SS, 610 * SS, 38 * SS, C.pose("scared"), "scared", 0, 0, C.Look(cast))
C.draw_figure(lay, 1080 * SS, 560 * SS, 78 * SS, C.pose(pose), expr, 0.6, 0, C.Look("archie"))
lay = lay.resize((W, H), Image.LANCZOS)
im.alpha_composite(lay)
d = ImageDraw.Draw(im)
size = 128
f = ImageFont.truetype(V.SANS_B, size)
lines = V.wrap(d, text, f, 700)
while len(lines) > 3:
    size -= 8; f = ImageFont.truetype(V.SANS_B, size); lines = V.wrap(d, text, f, 700)
y = (H - len(lines) * size * 1.08) / 2
for i, ln in enumerate(lines):
    col = (255, 214, 90) if i == len(lines) - 1 else (255, 255, 255)
    d.text((48, y), ln, font=f, fill=col, stroke_width=10, stroke_fill=(0, 0, 0))
    y += size * 1.08
im.convert("RGB").save(out, quality=92)
