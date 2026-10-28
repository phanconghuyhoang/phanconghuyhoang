"""Procedural illustration kit for The Quiet Archive. Every image is drawn from code (no stock, no third-party art)."""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H = 2560, 1440
BG = (21, 23, 28); PAPER = (232, 220, 196); AMBER = (217, 164, 65); GREY = (107, 111, 120)
INK = (40, 34, 28); RED = (178, 58, 48)
F = "/usr/share/fonts/truetype/"
SERIF_B = F + "liberation/LiberationSerif-Bold.ttf"
SERIF = F + "liberation/LiberationSerif-Regular.ttf"
SERIF_I = F + "liberation/LiberationSerif-Italic.ttf"
MONO = F + "dejavu/DejaVuSansMono.ttf"
SANS = F + "dejavu/DejaVuSans.ttf"
SANS_B = F + "dejavu/DejaVuSans-Bold.ttf"


def font(p, s):
    return ImageFont.truetype(p, s)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def grad(top, bottom, w=W, h=H):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        d.line((0, y, w, y), fill=lerp(top, bottom, y / h))
    return im


GRAIN_ON = False


def grain(im, amt=10, seed=1):
    if not GRAIN_ON:
        return im
    random.seed(seed)
    n = Image.effect_noise((im.width // 2, im.height // 2), amt).resize(im.size).convert("RGB")
    return ImageChops.add(im, n, scale=1.0, offset=-128) if amt else im


def vignette(im, strength=0.55):
    m = Image.new("L", (im.width // 8, im.height // 8), 0)
    d = ImageDraw.Draw(m)
    w, h = m.size
    for i in range(40):
        t = i / 40
        d.ellipse((-w * 0.3 + w * 0.3 * t, -h * 0.4 + h * 0.4 * t, w * 1.3 - w * 0.3 * t, h * 1.4 - h * 0.4 * t), fill=int(255 * t))
    m = m.resize(im.size).filter(ImageFilter.GaussianBlur(60))
    dark = Image.new("RGB", im.size, (0, 0, 0))
    mask = m.point(lambda v: int(255 - (255 - v) * strength))
    return Image.composite(im, dark, mask)


def stars(im, n=260, seed=3, maxy=0.55):
    random.seed(seed)
    d = ImageDraw.Draw(im)
    for _ in range(n):
        x, y = random.randint(0, W), random.randint(0, int(H * maxy))
        r = random.choice([1, 1, 1, 2, 2, 3])
        c = random.randint(150, 235)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(c, c, int(c * 0.95)))


def clouds(im, color, n=14, seed=5, ymax=0.45, alpha=110, blur=70):
    random.seed(seed)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        cx, cy = random.randint(-200, W + 200), random.randint(0, int(H * ymax))
        rw, rh = random.randint(300, 900), random.randint(60, 180)
        d.ellipse((cx - rw, cy - rh, cx + rw, cy + rh), fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    im.paste(layer, (0, 0), layer)


def sea(im, horizon, top, bottom, line, seed=7, rough=1.0):
    d = ImageDraw.Draw(im)
    for y in range(horizon, H):
        d.line((0, y, W, y), fill=lerp(top, bottom, (y - horizon) / (H - horizon)))
    random.seed(seed)
    y = horizon + 6
    k = 0
    while y < H:
        amp = (2 + (y - horizon) * 0.02) * rough
        ph = random.random() * 6.28
        wl = 90 + (y - horizon) * 0.8
        pts = [(x, y + amp * math.sin(x / wl * 6.28 + ph)) for x in range(0, W + 20, 20)]
        c = lerp(line, top, 0.3 + 0.5 * random.random())
        d.line(pts, fill=c, width=max(1, int(1 + (y - horizon) / 220)))
        y += int(10 + (y - horizon) * 0.06)
        k += 1


def island(im, base_y, x0, x1, peak, color=(10, 11, 14), seed=11):
    random.seed(seed)
    pts = [(x0, base_y)]
    n = 14
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        hgt = peak * (math.sin(t * math.pi) ** 0.55) * (0.85 + 0.15 * random.random())
        pts.append((x, base_y - hgt))
    pts.append((x1, base_y))
    ImageDraw.Draw(im).polygon(pts, fill=color)
    return pts


def lighthouse(im, x, ground, h=360, lit=True, beam_angle=-12, color=(14, 15, 19)):
    d = ImageDraw.Draw(im)
    w0, w1 = h * 0.16, h * 0.11
    d.polygon([(x - w0, ground), (x + w0, ground), (x + w1, ground - h), (x - w1, ground - h)], fill=color)
    d.rectangle((x - w1 * 1.35, ground - h - 12, x + w1 * 1.35, ground - h), fill=color)
    lw = w1 * 0.9
    lamp_y = ground - h - 12 - h * 0.1
    if lit:
        d.rectangle((x - lw, lamp_y, x + lw, ground - h - 12), fill=(250, 220, 140))
        beam = Image.new("RGBA", im.size, (0, 0, 0, 0))
        bd = ImageDraw.Draw(beam)
        cy = (lamp_y + ground - h - 12) / 2
        for side in (1, -1):
            a = math.radians(beam_angle if side == 1 else 180 - beam_angle)
            L = W * 1.2
            spread = 0.07
            p1 = (x + L * math.cos(a - spread), cy + L * math.sin(a - spread))
            p2 = (x + L * math.cos(a + spread), cy + L * math.sin(a + spread))
            bd.polygon([(x, cy), p1, p2], fill=(255, 225, 150, 60 if side == 1 else 30))
        beam = beam.filter(ImageFilter.GaussianBlur(18))
        im.paste(beam, (0, 0), beam)
        glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((x - 120, cy - 120, x + 120, cy + 120), fill=(255, 220, 140, 120))
        glow = glow.filter(ImageFilter.GaussianBlur(50))
        im.paste(glow, (0, 0), glow)
    else:
        d.rectangle((x - lw, lamp_y, x + lw, ground - h - 12), fill=(34, 36, 42))
    d.polygon([(x - lw * 1.2, lamp_y), (x + lw * 1.2, lamp_y), (x, lamp_y - h * 0.12)], fill=color)


def ship(im, x, y, s=1.0, color=(8, 9, 12), light=True):
    d = ImageDraw.Draw(im)
    L = 520 * s
    d.polygon([(x - L / 2, y), (x + L / 2, y), (x + L / 2 - 40 * s, y + 46 * s), (x - L / 2 + 30 * s, y + 46 * s)], fill=color)
    d.rectangle((x - 110 * s, y - 70 * s, x + 70 * s, y), fill=color)
    d.rectangle((x - 30 * s, y - 170 * s, x + 10 * s, y - 70 * s), fill=color)
    d.line((x - 220 * s, y, x - 220 * s, y - 230 * s), fill=color, width=int(8 * s))
    d.line((x + 180 * s, y, x + 180 * s, y - 200 * s), fill=color, width=int(8 * s))
    if light:
        for lx in (-80, -40, 20):
            d.rectangle((x + lx * s, y - 50 * s, x + (lx + 14) * s, y - 36 * s), fill=(240, 200, 120))


def rain(im, n=1600, seed=9, alpha=70):
    random.seed(seed)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        x, y = random.randint(-200, W), random.randint(-100, H)
        l = random.randint(40, 110)
        d.line((x, y, x + l * 0.35, y + l), fill=(200, 210, 225, alpha), width=2)
    im.paste(layer, (0, 0), layer)


def paper(w, h, seed=2, tone=PAPER):
    im = Image.new("RGB", (w, h), tone)
    im = grain(im, 14, seed)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), outline=lerp(tone, INK, 0.25), width=3)
    return im


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(d, xy, text, f, fill, maxw, spacing=1.35):
    x, y = xy
    for ln in wrap(d, text, f, maxw):
        d.text((x, y), ln, font=f, fill=fill)
        y += int(f.size * spacing)
    return y


def stamp(im, text, center, angle=-12, color=RED, size=90):
    f = font(SANS_B, size)
    tw = int(ImageDraw.Draw(im).textlength(text, font=f)) + 80
    layer = Image.new("RGBA", (tw, size + 70), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle((6, 6, tw - 6, size + 64), outline=color + (210,), width=8)
    d.text((40, 26), text, font=f, fill=color + (210,))
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    im.paste(layer, (int(center[0] - layer.width / 2), int(center[1] - layer.height / 2)), layer)


def night_base(seed=1, horizon=0.66, lit=True, clouds_on=True):
    im = grad((10, 13, 22), (28, 34, 48))
    stars(im, seed=seed)
    if clouds_on:
        clouds(im, (40, 46, 60), seed=seed + 2)
    hz = int(H * horizon)
    sea(im, hz, (20, 26, 38), (6, 8, 12), (70, 84, 104), seed=seed)
    return im, hz


def center_text(d, y, text, f, fill):
    d.text(((W - d.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)


# ----------------------------------------------------------------- scenes

def sc_lighthouse(lit=True, dawn=False, seed=1):
    if dawn:
        im = grad((48, 58, 78), (196, 150, 110))
        clouds(im, (120, 110, 120), seed=seed, alpha=90)
        hz = int(H * 0.66)
        sea(im, hz, (70, 80, 96), (18, 22, 30), (150, 140, 140), seed=seed)
    else:
        im, hz = night_base(seed)
    pts = island(im, hz + 8, W * 0.34, W * 0.82, 260, seed=seed)
    lighthouse(im, W * 0.58, hz + 8 - 250, h=300, lit=lit)
    return vignette(grain(im, 8, seed))


def sc_title(title, sub):
    im, hz = night_base(4, horizon=0.72)
    island(im, hz + 6, W * 0.62, W * 0.92, 180, seed=4)
    lighthouse(im, W * 0.77, hz + 6 - 172, h=220, lit=False)
    d = ImageDraw.Draw(im)
    center_text(d, H * 0.30, title, font(SERIF_B, 150), PAPER)
    d.rectangle((W / 2 - 200, H * 0.30 + 190, W / 2 + 200, H * 0.30 + 196), fill=AMBER)
    center_text(d, H * 0.30 + 230, sub, font(SERIF_I, 64), PAPER)
    return vignette(grain(im, 8, 4))


def sc_map():
    im = paper(W, H, 5, tone=(226, 214, 190))
    d = ImageDraw.Draw(im)
    sea_c = (196, 202, 198)
    d.rectangle((60, 60, W - 60, H - 60), fill=sea_c)
    random.seed(12)
    # Lewis & Harris: stylised landmass on the right
    pts = []
    cx, cy = W * 0.78, H * 0.52
    for i in range(48):
        a = i / 48 * 6.28
        r = 1 + 0.12 * math.sin(a * 3) + 0.08 * random.random()
        pts.append((cx + 330 * r * math.cos(a) * 0.9, cy + 520 * r * math.sin(a)))
    d.polygon(pts, fill=(214, 200, 168), outline=INK)
    d.text((cx - 150, cy - 40), "LEWIS", font=font(SERIF_B, 70), fill=INK)
    d.text((cx - 150, cy + 40), "Outer Hebrides", font=font(SERIF_I, 44), fill=INK)
    # Flannan Isles: cluster on the left
    fx, fy = W * 0.26, H * 0.40
    for (ox, oy, r) in [(0, 0, 34), (70, 40, 16), (-60, 60, 14), (110, -30, 12), (-20, -70, 12), (40, 100, 10), (-100, -20, 9)]:
        d.ellipse((fx + ox - r, fy + oy - r * 0.7, fx + ox + r, fy + oy + r * 0.7), fill=(214, 200, 168), outline=INK, width=3)
    d.text((fx - 210, fy - 200), "FLANNAN ISLES", font=font(SERIF_B, 64), fill=INK)
    d.text((fx - 210, fy - 125), "“the Seven Hunters”", font=font(SERIF_I, 44), fill=INK)
    d.text((fx + 60, fy - 20), "Eilean Mòr", font=font(SERIF, 40), fill=RED)
    # distance line
    x0, x1, y = fx + 140, cx - 330, H * 0.47
    for x in range(int(x0), int(x1), 46):
        d.line((x, y, min(x + 26, x1), y), fill=INK, width=5)
    d.text(((x0 + x1) / 2 - 170, y + 20), "about 20 miles", font=font(SERIF_B, 56), fill=INK)
    d.text((W * 0.08, H * 0.70), "ATLANTIC OCEAN", font=font(SERIF_I, 64), fill=(90, 96, 100))
    # compass
    ccx, ccy = W * 0.12, H * 0.2
    d.polygon([(ccx, ccy - 90), (ccx + 26, ccy), (ccx, ccy + 90), (ccx - 26, ccy)], outline=INK, width=4)
    d.polygon([(ccx, ccy - 90), (ccx + 26, ccy), (ccx - 26, ccy)], fill=INK)
    d.text((ccx - 16, ccy - 160), "N", font=font(SERIF_B, 56), fill=INK)
    d.text((W - 640, H - 130), "Schematic — not to scale", font=font(SERIF_I, 40), fill=GREY)
    return im


def sc_construction():
    im = grad((30, 36, 46), (70, 76, 84))
    clouds(im, (110, 112, 118), seed=21, alpha=120)
    hz = int(H * 0.7)
    sea(im, hz, (44, 54, 66), (14, 18, 24), (120, 130, 140), seed=21)
    island(im, hz + 8, W * 0.2, W * 0.9, 340, color=(22, 22, 24), seed=21)
    d = ImageDraw.Draw(im)
    x, g = W * 0.55, hz + 8 - 330
    # scaffolded tower
    for i in range(8):
        y = g - i * 40
        d.rectangle((x - 60 + i * 2, y - 40, x + 60 - i * 2, y), outline=(150, 140, 120), width=4)
    for k in (-80, 80):
        d.line((x + k, g, x + k * 0.7, g - 360), fill=(120, 110, 95), width=6)
    # steps down the cliff
    for i in range(16):
        sx, sy = W * 0.32 + i * 18, hz + 8 - 20 - i * 18
        d.line((sx, sy, sx + 18, sy), fill=(160, 150, 130), width=4)
        d.line((sx + 18, sy, sx + 18, sy - 18), fill=(160, 150, 130), width=4)
    return vignette(grain(im, 10, 21))


def card(lines, title=None, foot=None, w=1700, h=1000, seed=3, mono=False, tone=PAPER):
    bg = grad((18, 20, 25), (30, 33, 40))
    p = paper(w, h, seed, tone)
    d = ImageDraw.Draw(p)
    y = 90
    if title:
        d.text((100, y), title, font=font(SERIF_B, 76), fill=INK)
        y += 120
        d.line((100, y, w - 100, y), fill=lerp(tone, INK, 0.5), width=3)
        y += 50
    f = font(MONO if mono else SERIF, 54 if mono else 60)
    for ln in lines:
        y = text_block(d, (100, y), ln, f, INK, w - 200) + 26
    if foot:
        d.text((100, h - 110), foot, font=font(SERIF_I, 44), fill=lerp(tone, INK, 0.6))
    shadow = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle((40, 40, w + 40, h + 40), fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    ox, oy = (W - w) // 2, (H - h) // 2
    bg.paste(shadow, (ox - 20, oy - 10), shadow)
    bg.paste(p, (ox, oy))
    return bg, (ox, oy)


def sc_keepers():
    im = grad((18, 20, 25), (30, 33, 40))
    names = [("JAMES DUCAT", "Principal keeper", "Wife, four children"),
             ("THOMAS MARSHALL", "Assistant keeper", ""),
             ("DONALD McARTHUR", "Occasional keeper", "Wife, two children")]
    cw, ch = 700, 860
    for i, (n, r, f_) in enumerate(names):
        p = paper(cw, ch, 30 + i)
        d = ImageDraw.Draw(p)
        d.text((60, 60), "NORTHERN LIGHTHOUSE BOARD", font=font(SANS, 30), fill=lerp(PAPER, INK, 0.6))
        d.rectangle((60, 130, cw - 60, 470), outline=lerp(PAPER, INK, 0.4), width=3)
        # anonymous silhouette (no likeness)
        cx = cw / 2
        d.ellipse((cx - 80, 180, cx + 80, 340), fill=lerp(PAPER, INK, 0.35))
        d.pieslice((cx - 170, 330, cx + 170, 640), 180, 360, fill=lerp(PAPER, INK, 0.35))
        d.rectangle((60, 470, cw - 60, 480), fill=PAPER)
        d.text((60, 520), n, font=font(SERIF_B, 54), fill=INK)
        d.text((60, 600), r, font=font(SERIF_I, 46), fill=INK)
        if f_:
            d.text((60, 670), f_, font=font(SERIF, 40), fill=lerp(PAPER, INK, 0.7))
        d.text((60, ch - 100), "Flannan Isles · Dec. 1900", font=font(SERIF, 36), fill=lerp(PAPER, INK, 0.6))
        rot = [-3, 1.5, -1][i]
        layer = p.convert("RGBA").rotate(rot, expand=True, resample=Image.BICUBIC)
        im.paste(layer, (int(220 + i * 740), int(260 + [0, 30, -10][i])), layer)
    return vignette(grain(im, 6, 30))


def sc_ship_night():
    im, hz = night_base(8, horizon=0.62, clouds_on=True)
    clouds(im, (30, 34, 44), seed=81, alpha=160, ymax=0.6)
    island(im, hz + 6, W * 0.06, W * 0.26, 140, seed=8)
    lighthouse(im, W * 0.16, hz + 6 - 132, h=170, lit=False)
    ship(im, W * 0.66, hz + 40, s=1.15)
    rain(im, 900, 8, 40)
    return vignette(grain(im, 10, 8))


def sc_storm():
    im = grad((20, 22, 28), (44, 48, 56))
    clouds(im, (60, 64, 72), n=24, seed=71, alpha=170, ymax=0.7)
    hz = int(H * 0.6)
    sea(im, hz, (36, 42, 52), (10, 12, 16), (150, 160, 170), seed=71, rough=4.0)
    rain(im, 2400, 71, 85)
    d = ImageDraw.Draw(im)
    # harbour post with moored steamer silhouette
    ship(im, W * 0.35, hz + 70, s=0.9, light=True)
    d.rectangle((W * 0.12, hz - 40, W * 0.135, hz + 260), fill=(8, 9, 11))
    return vignette(grain(im, 12, 71))


def sc_landing(east=True):
    im = grad((34, 40, 52), (80, 84, 92))
    clouds(im, (110, 114, 122), seed=41, alpha=110)
    hz = int(H * 0.58)
    sea(im, hz, (40, 50, 62), (12, 16, 22), (130, 140, 150), seed=41, rough=1.5)
    d = ImageDraw.Draw(im)
    cliff = [(W * 0.35, H), (W * 0.42, hz - 80), (W * 0.5, hz - 300), (W * 0.72, hz - 420), (W, hz - 460), (W, H)]
    d.polygon(cliff, fill=(26, 26, 28))
    # stairs
    for i in range(22):
        sx, sy = W * 0.44 + i * 26, hz - 70 - i * 15
        d.line((sx, sy, sx + 26, sy), fill=(120, 116, 108), width=5)
    # empty flagpole on top
    d.line((W * 0.84, hz - 455, W * 0.84, hz - 760), fill=(10, 10, 12), width=10)
    lighthouse(im, W * 0.93, hz - 455, h=260, lit=False)
    ship(im, W * 0.2, hz + 80, s=0.8, light=False)
    return vignette(grain(im, 10, 41))


def sc_doorway():
    im = grad((26, 24, 22), (44, 40, 36))
    d = ImageDraw.Draw(im)
    # wall + panelling
    d.rectangle((0, H * 0.72, W, H), fill=(34, 30, 27))
    # door frame
    d.rectangle((W * 0.08, H * 0.12, W * 0.3, H * 0.72), fill=(18, 16, 14))
    d.rectangle((W * 0.1, H * 0.15, W * 0.28, H * 0.72), fill=(52, 42, 34))
    # coat hooks: one oilskin, two empty
    hy = H * 0.26
    for i, hx in enumerate([W * 0.45, W * 0.58, W * 0.71]):
        d.rectangle((hx - 10, hy - 10, hx + 10, hy + 26), fill=(150, 140, 120))
        if i == 1:
            coat = [(hx - 30, hy + 20), (hx + 30, hy + 20), (hx + 140, hy + 120), (hx + 120, hy + 640), (hx - 120, hy + 640), (hx - 140, hy + 120)]
            d.polygon(coat, fill=(150, 126, 40))
            d.line((hx, hy + 30, hx, hy + 630), fill=(110, 92, 30), width=6)
        else:
            d.text((hx - 60, hy + 120), "empty", font=font(SERIF_I, 52), fill=(120, 110, 96))
    # stopped clock
    cx, cy, r = W * 0.88, H * 0.3, 150
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(220, 208, 182), outline=(90, 70, 50), width=12)
    for k in range(12):
        a = k / 12 * 6.28
        d.line((cx + (r - 30) * math.sin(a), cy - (r - 30) * math.cos(a), cx + (r - 12) * math.sin(a), cy - (r - 12) * math.cos(a)), fill=INK, width=6)
    d.line((cx, cy, cx + 70 * math.sin(2.2), cy - 70 * math.cos(2.2)), fill=INK, width=10)
    d.line((cx, cy, cx + 110 * math.sin(5.5), cy - 110 * math.cos(5.5)), fill=INK, width=6)
    d.text((cx - 120, cy + r + 30), "stopped", font=font(SERIF_I, 52), fill=(160, 146, 120))
    # light from the door
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).polygon([(W * 0.1, H * 0.15), (W * 0.28, H * 0.15), (W * 0.6, H), (W * 0.0, H)], fill=(220, 210, 190, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    im.paste(glow, (0, 0), glow)
    return vignette(grain(im, 10, 51))


def sc_cliff_diagram(wave=False):
    im = grad((16, 18, 23), (26, 29, 36))
    d = ImageDraw.Draw(im)
    base = H * 0.80
    px = lambda m: base - m * 15.5   # 1 metre = 15.5 px
    # sea
    d.rectangle((0, px(0), W, H), fill=(28, 44, 62))
    # cliff profile
    prof = [(W * 0.36, H), (W * 0.36, px(0)), (W * 0.42, px(8)), (W * 0.46, px(20)), (W * 0.5, px(33)), (W * 0.56, px(40)),
            (W * 0.62, px(55)), (W * 0.68, px(62)), (W, px(64)), (W, H)]
    d.polygon(prof, fill=(46, 44, 42))
    # height guides
    for m, label in [(0, "sea level"), (33, "rope box — about 33 m (110 ft)"), (60, "clifftop turf torn up — over 60 m")]:
        y = px(m)
        for x in range(120, int(W * 0.95), 40):
            d.line((x, y, x + 20, y), fill=(120, 124, 132), width=3)
        d.text((120, y - 70), label, font=font(SANS_B if m else SANS, 50), fill=AMBER if m else (170, 176, 184))
    # rope box
    bx, by = W * 0.5, px(33)
    d.rectangle((bx - 40, by - 50, bx + 40, by), fill=(130, 100, 60), outline=PAPER, width=3)
    # landing steps
    for i in range(14):
        sx, sy = W * 0.37 + i * 22, px(0) - i * 22 * 0.75
        d.line((sx, sy, sx + 22, sy), fill=(150, 146, 138), width=4)
    # person scale
    hx, hy = bx + 90, by
    d.line((hx, hy, hx, hy - 28), fill=PAPER, width=6)
    d.ellipse((hx - 8, hy - 44, hx + 8, hy - 28), fill=PAPER)
    if wave:
        w_ = Image.new("RGBA", im.size, (0, 0, 0, 0))
        wd = ImageDraw.Draw(w_)
        pts = [(0, H), (0, px(4))]
        for i in range(60):
            t = i / 59
            x = W * 0.52 * t
            y = px(4 + 36 * (t ** 2.2))
            pts.append((x, y))
        pts += [(W * 0.55, px(36)), (W * 0.56, px(30)), (W * 0.36, px(0)), (W * 0.36, H)]
        wd.polygon(pts, fill=(170, 200, 220, 150))
        w_ = w_.filter(ImageFilter.GaussianBlur(6))
        im.paste(w_, (0, 0), w_)
        d.text((W * 0.06, px(46)), "A sea far larger than expected", font=font(SERIF_B, 70), fill=PAPER)
    d.text((W - 900, H - 90), "Heights from the 1901 report · diagram", font=font(SERIF_I, 40), fill=GREY)
    return grain(im, 6, 61)


def sc_sea_calm():
    im = grad((60, 70, 86), (150, 150, 150))
    clouds(im, (170, 170, 175), seed=91, alpha=70)
    hz = int(H * 0.55)
    sea(im, hz, (70, 82, 96), (22, 28, 36), (140, 150, 160), seed=91, rough=0.6)
    return vignette(grain(im, 8, 91), 0.4)


def sc_fog_text(text):
    im, hz = night_base(101, horizon=0.6, clouds_on=True)
    fog = Image.new("RGBA", im.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    random.seed(101)
    for _ in range(30):
        x, y = random.randint(-300, W), random.randint(int(H * 0.45), int(H * 0.85))
        fd.ellipse((x, y, x + random.randint(600, 1400), y + random.randint(80, 200)), fill=(160, 170, 185, 50))
    fog = fog.filter(ImageFilter.GaussianBlur(60))
    im.paste(fog, (0, 0), fog)
    d = ImageDraw.Draw(im)
    center_text(d, H * 0.36, text, font(SERIF_I, 110), PAPER)
    return vignette(grain(im, 10, 101))


def sc_logbook():
    bg, (ox, oy) = card([
        "12 Dec — storm for days ........................",
        "            a keeper is said to be weeping .........",
        "13 Dec — the men are said to be praying ..........",
        "15 Dec — “storm ended, sea calm, God is over all”",
    ], title="The ‘famous’ logbook entries", foot="As retold in later accounts (paraphrased)", mono=True, w=1900, h=980, seed=42)
    stamp(bg, "NOT IN THE REAL RECORDS", (W / 2 + 330, H / 2 + 330), angle=-8, size=80)
    return bg


def sc_poem():
    bg, (ox, oy) = card([
        "In the 1912 ballad, the relief crew find:",
        "• a meal set out, but never eaten",
        "• a chair knocked over",
        "Joseph Moore’s actual report: the kitchen was clean.",
    ], title="‘Flannan Isle’ — W. W. Gibson, 1912", foot="Poetry, not testimony", w=1900, h=960, seed=43)
    stamp(bg, "NOT REPORTED", (ox + 1480, oy + 790), angle=-10, size=80)
    return bg


def sc_tiles(items, verdict, color):
    im = grad((18, 20, 25), (30, 33, 40))
    d = ImageDraw.Draw(im)
    n = len(items)
    tw, th, gap = (2200 - (n - 1) * 60) / n, 620, 60
    x0 = (W - (tw * n + gap * (n - 1))) / 2
    for i, (head, sub) in enumerate(items):
        x = x0 + i * (tw + gap)
        p = paper(int(tw), th, 60 + i)
        pd = ImageDraw.Draw(p)
        y = text_block(pd, (50, 60), head, font(SERIF_B, 64), INK, tw - 100)
        text_block(pd, (50, y + 30), sub, font(SERIF_I, 44), lerp(PAPER, INK, 0.7), tw - 100)
        im.paste(p, (int(x), int(H * 0.22)))
    center_text(d, H * 0.22 + th + 90, verdict, font(SANS_B, 80), color)
    return vignette(grain(im, 6, 60), 0.4)


def sc_verdict():
    im = grad((18, 20, 25), (30, 33, 40))
    d = ImageDraw.Draw(im)
    cols = [("DOCUMENTED", AMBER, ["Light out on the night of 15 Dec 1900", "Station work finished that day",
                                   "Two oilskins gone, one left behind", "Storm damage at the west landing, 33 m up",
                                   "Three men lost; no bodies recovered"]),
            ("LEGEND", (150, 156, 166), ["The dramatic logbook entries", "The uneaten meal", "The overturned chair",
                                          "Sea serpent, spies, ghost ship"])]
    for i, (head, c, items) in enumerate(cols):
        x = 240 + i * 1180
        d.text((x, 200), head, font=font(SANS_B, 90), fill=c)
        d.rectangle((x, 320, x + 980, 326), fill=c)
        y = 390
        for it in items:
            d.text((x, y), ("✓  " if i == 0 else "✕  ") + it, font=font(SERIF, 58), fill=PAPER if i == 0 else (150, 156, 166))
            y += 130
    return vignette(grain(im, 6, 70), 0.4)


def sc_investigator():
    bg, (ox, oy) = card([
        "Report on the disappearance of the three keepers,",
        "Flannan Islands Lighthouse.",
        "Investigation on the island from 29 December 1900.",
        "Submitted 8 January 1901.",
    ], title="Superintendent Robert Muirhead", foot="Northern Lighthouse Board · summary card", w=1900, h=920, seed=44)
    return bg


def sc_telegram():
    bg, (ox, oy) = card([
        "A DREADFUL ACCIDENT HAS HAPPENED AT FLANNANS.",
        "THE THREE KEEPERS HAVE DISAPPEARED FROM THE ISLAND.",
        "CLOCKS STOPPED AND OTHER SIGNS INDICATE ACCIDENT ABOUT A WEEK AGO.",
        "BLOWN OVER CLIFFS OR DROWNED SECURING A CRANE.",
    ], title="TELEGRAM · 26 DEC 1900", foot="Paraphrased from Captain Harvie’s telegram", mono=True, w=2000, h=1000, seed=45, tone=(222, 214, 188))
    return bg


def caption(im, text):
    if not text:
        return im
    im = im.copy()
    d = ImageDraw.Draw(im)
    f = font(SANS, 46)
    tw = d.textlength(text, font=f)
    x, y = 150, H - 200
    bar = Image.new("RGBA", (int(tw + 90), 96), (10, 11, 14, 175))
    im.paste(bar, (x - 45, y - 24), bar)
    d.rectangle((x - 45, y - 24, x - 37, y + 72), fill=AMBER)
    d.text((x, y), text, font=f, fill=PAPER)
    return im


def render(visual, cap):
    v = visual
    if v == "lighthouse_night": im = sc_lighthouse(lit=False)
    elif v == "lighthouse_dawn": im = sc_lighthouse(lit=True, dawn=True, seed=2)
    elif v == "title": im = sc_title("THE FLANNAN ISLES", "December 1900")
    elif v == "map": im = sc_map()
    elif v == "construction": im = sc_construction()
    elif v == "keepers": im = sc_keepers()
    elif v == "ship_night": im = sc_ship_night()
    elif v == "storm": im = sc_storm()
    elif v == "landing_east": im = sc_landing(True)
    elif v == "doorway": im = sc_doorway()
    elif v == "telegram": im = sc_telegram()
    elif v == "investigator": im = sc_investigator()
    elif v == "landing_west": im = sc_cliff_diagram(False)
    elif v == "wave": im = sc_cliff_diagram(True)
    elif v == "sea_calm": im = sc_sea_calm()
    elif v == "legend": im = sc_fog_text("Where the legend begins")
    elif v == "logbook": im = sc_logbook()
    elif v == "poem": im = sc_poem()
    elif v == "theories": im = sc_tiles([("Sea serpent", "A creature from the deep"), ("Foreign spies", "Keepers kidnapped"),
                                          ("Ghost boat", "The Phantom of the Seven Hunters"), ("A new life", "Three men faked their deaths")],
                                         "NO EVIDENCE FOR ANY OF THESE", RED)
    elif v == "theories_real": im = sc_tiles([("Saving the gear", "McArthur lost trying to help the other two"),
                                               ("A rescue gone wrong", "One swept off, two lost going after him"),
                                               ("A quarrel", "Rests on gossip, not on evidence")],
                                              "REFINEMENTS OF MUIRHEAD’S ACCOUNT", AMBER)
    elif v == "verdict": im = sc_verdict()
    else: raise ValueError(v)
    return caption(im, cap)
