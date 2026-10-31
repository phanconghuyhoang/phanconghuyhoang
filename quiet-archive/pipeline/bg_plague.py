"""Backdrops for the Dancing Plague of 1518 (Strasbourg). Flat cartoon, 2560x1440, floor line ~0.84-0.88.

usage: python3 bg_plague.py <outdir>
"""
import os, random, sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
import visuals as V
import backdrops as B

BW, BH = B.BW, B.BH


def timber_house(d, x, w, h, base, wall, beam=(70, 46, 30), roof=(150, 70, 50), seed=0):
    rng = random.Random(seed)
    top = base - h
    d.rectangle((x, top, x + w, base), fill=wall)
    d.polygon([(x - 30, top), (x + w // 2, top - int(w * 0.7)), (x + w + 30, top)], fill=roof)
    for k in range(3):  # storeys
        y = top + k * h // 3
        d.rectangle((x, y - 8, x + w, y + 8), fill=beam)
    for k in range(0, w + 1, w // 4):
        d.rectangle((x + k - 7, top, x + k + 7, base), fill=beam)
    for k in range(2):  # diagonal braces
        y0 = top + k * h // 3
        d.line([(x, y0), (x + w // 4, y0 + h // 3)], fill=beam, width=12)
        d.line([(x + w, y0), (x + w - w // 4, y0 + h // 3)], fill=beam, width=12)
    for k in range(3):  # windows
        for j in range(2):
            wx = x + w // 8 + k * w // 4 + 10; wy = top + j * h // 3 + 50
            if wx + 60 < x + w:
                lit = rng.random() < 0.4
                d.rectangle((wx, wy, wx + 60, wy + 80), fill=(250, 210, 120) if lit else (60, 70, 90), outline=beam, width=6)
    d.rectangle((x + w // 2 - 50, base - 200, x + w // 2 + 50, base), fill=(90, 58, 36), outline=beam, width=6)


def cobbles(d, y0, col=(150, 140, 126), dark=(120, 110, 98), seed=5):
    d.rectangle((0, y0, BW, BH), fill=col)
    rng = random.Random(seed)
    for _ in range(500):
        x, y = rng.uniform(0, BW), rng.uniform(y0 + 10, BH)
        r = rng.uniform(16, 30)
        d.ellipse((x - r, y - r * 0.55, x + r, y + r * 0.55), outline=dark, width=3)


def cathedral(d, x, base, col=(176, 110, 96)):
    d.rectangle((x, base - 700, x + 360, base), fill=col)
    d.rectangle((x + 120, base - 1180, x + 240, base - 700), fill=col)
    d.polygon([(x + 110, base - 1180), (x + 180, base - 1400), (x + 250, base - 1180)], fill=col)
    d.ellipse((x + 110, base - 600, x + 250, base - 460), fill=(120, 70, 60), outline=(150, 90, 76), width=10)
    for k in range(4):
        d.rectangle((x + 30 + k * 85, base - 380, x + 70 + k * 85, base - 200), fill=(120, 70, 60))


def bg_street(night=False):
    im = B.vgrad((40, 50, 90), (90, 80, 110)) if night else B.vgrad((150, 196, 230), (236, 226, 200))
    if not night:
        B.soft_clouds(im, 5, 31)
    d = ImageDraw.Draw(im)
    if night:
        d.ellipse((2100, 120, 2260, 280), fill=(240, 236, 210))
    cathedral(d, 1100, 1190, (120, 80, 80) if night else (186, 118, 100))
    walls = [(232, 220, 190), (220, 200, 160), (236, 214, 180), (210, 196, 170), (226, 206, 170)]
    xs = [-60, 380, 1560, 2000]
    for i, x in enumerate(xs):
        timber_house(d, x, 400 if i % 2 else 440, 640, 1220, walls[i % len(walls)], seed=i + (10 if night else 0))
    cobbles(d, 1180, (110, 104, 110) if night else (150, 140, 126), (90, 84, 92) if night else (120, 110, 98))
    if night:
        lay = Image.new("RGBA", im.size, (10, 10, 40, 90)); im = Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")
    return im


def bg_square(stage=False, crowd=False):
    im = B.vgrad((170, 206, 236), (240, 230, 206)); B.soft_clouds(im, 4, 41)
    d = ImageDraw.Draw(im)
    cathedral(d, 1700, 980)
    for i, x in enumerate([-80, 360, 2200]):
        timber_house(d, x, 380, 560, 1000, [(230, 214, 184), (214, 196, 160), (232, 210, 176)][i], seed=20 + i)
    cobbles(d, 960, seed=7)
    if stage:  # wooden dance platform with musicians' bench
        d.rectangle((700, 900, 1900, 1010), fill=(150, 104, 62), outline=(100, 66, 40), width=10)
        for x in range(740, 1900, 160):
            d.rectangle((x, 1010, x + 30, 1100), fill=(110, 74, 46))
        for x, c in ((1300, (160, 40, 40)), (1440, (40, 70, 140)), (1580, (220, 180, 60))):  # banners
            d.rectangle((x, 600, x + 8, 900), fill=(90, 60, 40)); d.polygon([(x + 8, 610), (x + 120, 650), (x + 8, 700)], fill=c)
        dr = (1760, 840)  # drum
        d.ellipse((dr[0] - 60, dr[1] - 30, dr[0] + 60, dr[1] + 10), fill=(200, 170, 120), outline=(90, 60, 40), width=6)
        d.rectangle((dr[0] - 60, dr[1] - 10, dr[0] + 60, dr[1] + 60), fill=(170, 40, 40))
    if crowd:
        rng = random.Random(77)
        for _ in range(70):
            x = rng.uniform(80, BW - 80); y = rng.uniform(1040, 1300); s = 0.6 + (y - 1040) / 600
            col = rng.choice([(70, 60, 80), (90, 70, 60), (60, 70, 90), (100, 60, 60)])
            d.ellipse((x - 26 * s, y - 150 * s, x + 26 * s, y - 98 * s), fill=col)
            d.line([(x, y - 98 * s), (x, y - 30 * s)], fill=col, width=int(12 * s))
            a = rng.choice([-1, 1])
            d.line([(x, y - 80 * s), (x + 50 * s * a, y - 140 * s)], fill=col, width=int(10 * s))
            d.line([(x, y - 80 * s), (x - 40 * s * a, y - 40 * s)], fill=col, width=int(10 * s))
            d.line([(x, y - 30 * s), (x - 30 * s, y + 10 * s)], fill=col, width=int(10 * s))
            d.line([(x, y - 30 * s), (x + 34 * s, y)], fill=col, width=int(10 * s))
    return im


def bg_guildhall():
    im = Image.new("RGB", (BW, BH), (120, 84, 56)); d = ImageDraw.Draw(im)
    for x in range(0, BW, 320):
        d.rectangle((x, 0, x + 50, 1080), fill=(84, 56, 36))
    d.rectangle((0, 120, BW, 170), fill=(84, 56, 36)); d.rectangle((0, 1040, BW, 1080), fill=(84, 56, 36))
    for x, c in ((420, (160, 40, 40)), (1100, (40, 80, 130)), (1780, (60, 110, 60))):  # guild banners
        d.polygon([(x, 200), (x + 260, 200), (x + 260, 560), (x + 130, 500), (x, 560)], fill=c)
        d.ellipse((x + 80, 280, x + 180, 380), fill=(230, 200, 110))
    for x in (300, 2200):  # candles chandelier hint
        d.line([(x, 170), (x, 300)], fill=(50, 40, 30), width=6); d.rectangle((x - 80, 300, x + 80, 316), fill=(50, 40, 30))
        for k in (-70, 0, 70):
            d.rectangle((x + k - 8, 260, x + k + 8, 300), fill=(240, 230, 200)); d.ellipse((x + k - 10, 236, x + k + 10, 262), fill=(255, 200, 80))
    d.rectangle((0, 1080, BW, BH), fill=(150, 112, 70))
    for x in range(0, BW, 140):
        d.line([(x, 1080), (x - 200, BH)], fill=(130, 96, 60), width=6)
    d.rectangle((2000, 860, 2500, 1080), fill=(100, 66, 40))  # musicians' bench
    return im


def bg_shrine():
    im = Image.new("RGB", (BW, BH), (70, 64, 70)); d = ImageDraw.Draw(im)
    d.polygon([(800, 1060), (800, 400), (1280, 120), (1760, 400), (1760, 1060)], fill=(96, 88, 92))
    d.polygon([(1100, 380), (1280, 240), (1460, 380), (1460, 760), (1100, 760)], fill=(200, 160, 90))  # alcove glow
    d.ellipse((1240, 300, 1320, 380), fill=(150, 104, 66)); d.rectangle((1250, 380, 1310, 640), fill=(150, 104, 66))  # wooden saint
    d.line([(1250, 420), (1180, 520)], fill=(150, 104, 66), width=24); d.line([(1310, 420), (1380, 520)], fill=(150, 104, 66), width=24)
    d.ellipse((1220, 270, 1340, 300), outline=(250, 220, 120), width=8)  # halo
    for x in (900, 1000, 1560, 1660):
        d.rectangle((x - 10, 880, x + 10, 1000), fill=(240, 232, 210)); d.ellipse((x - 12, 850, x + 12, 884), fill=(255, 196, 80))
    for k, x in enumerate((1120, 1260, 1400)):  # red shoes on the altar step
        d.ellipse((x, 1000, x + 110, 1050), fill=(200, 30, 40)); d.rectangle((x, 990, x + 50, 1030), fill=(200, 30, 40))
    d.rectangle((0, 1060, BW, BH), fill=(110, 100, 96))
    lay = Image.new("L", (BW, BH), 0); ImageDraw.Draw(lay).ellipse((900, 100, 1700, 900), fill=110)
    lay = lay.filter(ImageFilter.GaussianBlur(140))
    return Image.composite(Image.new("RGB", (BW, BH), (255, 220, 150)), im, lay)


def bg_map():
    im = Image.new("RGB", (BW, BH), (214, 206, 176)); d = ImageDraw.Draw(im)
    pts = [(1500, 0), (1460, 300), (1520, 600), (1480, 900), (1560, 1200), (1600, BH)]
    d.line(pts, fill=(70, 130, 180), width=40, joint="curve")
    d.line([(0, 380), (500, 420), (900, 300), (1480, 280)], fill=(70, 130, 180), width=24, joint="curve")  # Moselle-ish
    for x, y in ((1050, 760), (1130, 720), (1000, 820)):  # Vosges hills
        d.polygon([(x - 120, y + 80), (x, y - 60), (x + 120, y + 80)], fill=(150, 160, 120))
    f = V.font(V.SANS_B, 56); fs = V.font(V.SANS, 40)
    for name, x, y in (("Strasbourg", 1410, 860), ("Saverne", 950, 900), ("Aachen", 700, 80)):
        d.ellipse((x - 20, y - 20, x + 20, y + 20), fill=(200, 40, 40))
        d.text((x - d.textlength(name, font=f) / 2, y + 30), name, font=f, fill=(50, 40, 30))
    d.text((1560, 420), "Rhine", font=fs, fill=(40, 90, 140)); d.text((200, 330), "Moselle", font=fs, fill=(40, 90, 140))
    d.line([(1390, 860), (970, 900)], fill=(200, 40, 40), width=8)
    d.text((1080, 800), "~30 miles", font=fs, fill=(150, 40, 40))
    d.text((60, BH - 70), "Schematic map, not to scale", font=fs, fill=(90, 80, 60))
    return im


def bg_famine():
    im = B.vgrad((120, 120, 130), (190, 180, 160)); d = ImageDraw.Draw(im)
    d.rectangle((0, 960, BW, BH), fill=(150, 130, 90))
    rng = random.Random(9)
    for row in range(8):
        y = 980 + row * 56
        for x in range(0, BW, 70):
            h = rng.uniform(20, 70)
            d.line([(x + row * 9, y), (x + row * 9 + rng.uniform(-14, 14), y - h)], fill=(120, 100, 60), width=6)
    d.polygon([(1800, 960), (1800, 760), (2000, 640), (2200, 760), (2200, 960)], fill=(120, 96, 70))  # barn
    d.rectangle((1950, 840, 2050, 960), fill=(60, 44, 30))
    for x in range(200, 1500, 260):  # hail / rain streaks
        for k in range(10):
            yy = rng.uniform(0, 900); d.line([(x + k * 20, yy), (x + k * 20 - 20, yy + 60)], fill=(200, 210, 220), width=4)
    return im


SCENES = {
    "street": bg_street, "street_night": lambda: bg_street(night=True), "square": bg_square,
    "square_crowd": lambda: bg_square(crowd=True), "stage": lambda: bg_square(stage=True, crowd=True),
    "guildhall": bg_guildhall, "shrine": bg_shrine, "map": bg_map, "famine": bg_famine,
    "board": lambda: B.bg_board("THEORIES"),
}

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    names = sys.argv[2:] or list(SCENES)
    for n in names:
        SCENES[n]().save(os.path.join(out, n + ".png"))
        print(n)
