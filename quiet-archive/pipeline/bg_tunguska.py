"""Backdrops for the Tunguska event (Siberia, 30 June 1908). Flat cartoon, 2560x1440.

usage: python3 bg_tunguska.py <outdir> [names]
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
import visuals as V
import backdrops as B

BW, BH = B.BW, B.BH


def pine(d, x, base, h, col=(40, 86, 58)):
    d.rectangle((x - 8, base - h * 0.25, x + 8, base), fill=(90, 62, 40))
    for k in range(4):
        w = h * (0.32 - k * 0.06); y = base - h * 0.2 - k * h * 0.2
        d.polygon([(x - w, y), (x, y - h * 0.38), (x + w, y)], fill=col)


def forest(d, y, seed, n=60, hmin=160, hmax=320, col=(40, 86, 58)):
    rng = random.Random(seed)
    for _ in range(n):
        pine(d, rng.uniform(-40, BW + 40), y + rng.uniform(0, 40), rng.uniform(hmin, hmax), col)


def glow(im, cx, cy, r, color, alpha=200):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color + (alpha,))
    lay = lay.filter(ImageFilter.GaussianBlur(r * 0.45))
    return Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")


def bg_taiga():
    im = B.vgrad((150, 196, 230), (226, 232, 220)); B.soft_clouds(im, 5, 11); d = ImageDraw.Draw(im)
    d.rectangle((0, 1040, BW, BH), fill=(110, 130, 80))
    forest(d, 820, 3, 40, 200, 340, (60, 104, 72)); forest(d, 1000, 4, 50, 260, 420)
    d.polygon([(0, 1150), (BW, 1110), (BW, 1200), (0, 1240)], fill=(80, 130, 170))  # river
    return im


def bg_fireball():
    im = B.vgrad((120, 170, 220), (240, 220, 190)); d = ImageDraw.Draw(im)
    d.rectangle((0, 1040, BW, BH), fill=(110, 130, 80)); forest(d, 1000, 7, 60, 200, 360)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for k in range(40):  # smoke trail
        t = k / 40; x = 2500 - t * 1500; y = 40 + t * 520; r = 30 + t * 50
        ld.ellipse((x - r, y - r, x + r, y + r), fill=(250, 240, 220, 140))
    lay = lay.filter(ImageFilter.GaussianBlur(20)); im = Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")
    im = glow(im, 1000, 560, 260, (255, 230, 150), 255); im = glow(im, 1000, 560, 120, (255, 255, 240), 255)
    return im


def bg_blast():
    im = B.vgrad((250, 220, 160), (255, 160, 80)); d = ImageDraw.Draw(im)
    d.rectangle((0, 1040, BW, BH), fill=(120, 100, 60))
    im = glow(im, 1280, 700, 700, (255, 250, 220), 255)
    d = ImageDraw.Draw(im)
    rng = random.Random(9)
    for _ in range(70):  # trees bending away from the centre
        x = rng.uniform(0, BW); side = 1 if x > 1280 else -1
        d.line([(x, 1060), (x + side * 140, 900)], fill=(70, 50, 30), width=14)
    return im


def bg_flattened(center=False):
    im = B.vgrad((170, 190, 210), (220, 220, 214)); d = ImageDraw.Draw(im)
    d.rectangle((0, 900, BW, BH), fill=(150, 140, 100))
    rng = random.Random(21); cx, cy = 1280, 1160
    for _ in range(260):  # fallen trunks pointing away from the centre
        a = rng.uniform(math.pi, 2 * math.pi) if rng.random() < 0.5 else rng.uniform(0, math.pi)
        r = rng.uniform(260, 1500); x = cx + math.cos(a) * r; y = cy + math.sin(a) * r * 0.28
        if y < 910 or y > BH:
            continue
        L = rng.uniform(60, 140)
        d.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L * 0.28)], fill=(96, 72, 48), width=9)
    if center:
        for x in range(1080, 1500, 70):  # standing, stripped trunks at the epicentre
            d.rectangle((x, 640, x + 16, 1160), fill=(90, 70, 50))
            d.line([(x + 8, 700), (x + 40, 670)], fill=(90, 70, 50), width=5)
    return im


def bg_post():
    im = B.vgrad((160, 200, 230), (232, 232, 220)); B.soft_clouds(im, 4, 31); d = ImageDraw.Draw(im)
    d.rectangle((0, 1040, BW, BH), fill=(120, 140, 86)); forest(d, 900, 33, 30, 200, 320, (60, 104, 72))
    x0 = 1300  # log trading-post house
    for k in range(12):
        d.rectangle((x0, 640 + k * 34, x0 + 760, 640 + k * 34 + 30), fill=(150, 106, 64), outline=(110, 76, 44), width=3)
    d.polygon([(x0 - 40, 640), (x0 + 380, 420), (x0 + 800, 640)], fill=(110, 76, 50))
    d.rectangle((x0 + 120, 760, x0 + 260, 900), fill=(200, 220, 236), outline=(90, 60, 40), width=10)
    d.rectangle((x0 + 500, 860, x0 + 620, 1048), fill=(90, 60, 40))
    d.rectangle((x0 + 420, 1040, x0 + 700, 1070), fill=(130, 96, 60))  # porch
    return im


def bg_camp():
    im = B.vgrad((150, 196, 230), (230, 230, 220)); d = ImageDraw.Draw(im)
    d.rectangle((0, 1040, BW, BH), fill=(116, 136, 84)); forest(d, 900, 41, 40, 200, 340, (56, 100, 70))
    for x in (700, 1500):  # conical tents (chum)
        d.polygon([(x - 220, 1060), (x, 600), (x + 220, 1060)], fill=(170, 140, 100), outline=(120, 96, 66))
        d.line([(x - 40, 560), (x, 600)], fill=(90, 66, 40), width=8); d.line([(x + 40, 560), (x, 600)], fill=(90, 66, 40), width=8)
        d.polygon([(x - 50, 1060), (x, 900), (x + 50, 1060)], fill=(80, 60, 40))
    for x in (1050, 1150, 1950, 2100):  # reindeer
        d.ellipse((x, 960, x + 120, 1010), fill=(120, 100, 80))
        for lx in (x + 15, x + 95):
            d.line([(lx, 1000), (lx, 1060)], fill=(100, 80, 60), width=8)
        d.line([(x + 110, 970), (x + 140, 930)], fill=(100, 80, 60), width=10)
        d.line([(x + 140, 930), (x + 160, 880)], fill=(160, 140, 110), width=5); d.line([(x + 140, 930), (x + 120, 880)], fill=(160, 140, 110), width=5)
    return im


def bg_night_city():
    im = B.vgrad((60, 70, 120), (220, 190, 160)); d = ImageDraw.Draw(im)
    rng = random.Random(51)
    for x in range(0, BW, 140):
        h = rng.uniform(260, 520); d.rectangle((x, 1100 - h, x + 120, 1100), fill=(40, 44, 60))
        for wy in range(int(1100 - h) + 30, 1080, 70):
            if rng.random() < 0.5:
                d.rectangle((x + 30, wy, x + 60, wy + 30), fill=(250, 220, 140))
    d.rectangle((0, 1100, BW, BH), fill=(50, 50, 60))
    return im


def bg_swamp():
    im = B.vgrad((170, 196, 210), (220, 226, 214)); d = ImageDraw.Draw(im)
    d.rectangle((0, 980, BW, BH), fill=(100, 116, 70))
    rng = random.Random(61)
    for _ in range(30):
        x, y = rng.uniform(0, BW), rng.uniform(1040, BH); w = rng.uniform(120, 300)
        d.ellipse((x, y, x + w, y + w * 0.25), fill=(90, 120, 130))
    forest(d, 960, 63, 25, 140, 260, (70, 100, 70))
    for x in range(400, 2200, 260):  # broken stumps
        d.rectangle((x, 900, x + 20, 1000), fill=(110, 84, 56))
    return im


def bg_map():
    im = Image.new("RGB", (BW, BH), (214, 206, 176)); d = ImageDraw.Draw(im)
    d.polygon([(0, 0), (BW, 0), (BW, 160), (1900, 240), (1300, 180), (700, 260), (0, 200)], fill=(110, 160, 200))  # Arctic Ocean
    d.line([(1400, 260), (1420, 600), (1350, 900), (1380, 1440)], fill=(70, 130, 180), width=22)  # Yenisei
    d.line([(1380, 820), (1700, 800), (1900, 760)], fill=(70, 130, 180), width=14)  # Podkamennaya Tunguska
    f = V.font(V.SANS_B, 56); fs = V.font(V.SANS, 40)
    d.ellipse((1880, 700, 1920, 740), fill=(220, 40, 40)); d.text((1800, 620), "Tunguska 1908", font=f, fill=(150, 30, 30))
    d.ellipse((1950, 790, 1980, 820), fill=(60, 60, 60)); d.text((1990, 790), "Vanavara (~65 km)", font=fs, fill=(60, 50, 40))
    d.text((1430, 420), "Yenisei", font=fs, fill=(40, 90, 140)); d.text((200, 80), "Arctic Ocean", font=fs, fill=(240, 246, 250))
    d.text((300, 700), "RUSSIAN EMPIRE (Siberia)", font=f, fill=(90, 80, 60))
    d.text((60, BH - 70), "Schematic map, not to scale", font=fs, fill=(90, 80, 60))
    return im


def bg_seismo():
    im = Image.new("RGB", (BW, BH), (236, 230, 214)); d = ImageDraw.Draw(im)
    rng = random.Random(71)
    for row in range(6):
        y = 220 + row * 170; pts = []
        for x in range(120, 2440, 12):
            amp = 6
            if row in (2, 3) and 1100 < x < 1500:
                amp = 90 * math.exp(-((x - 1220) / 120) ** 2) + 10
            pts.append((x, y + rng.uniform(-amp, amp)))
        d.line(pts, fill=(40, 40, 60), width=4)
    d.text((140, 80), "Barograph / seismograph traces (illustration)", font=V.font(V.SANS_B, 48), fill=(80, 60, 50))
    return im


SCENES = {"taiga": bg_taiga, "fireball": bg_fireball, "blast": bg_blast, "flattened": bg_flattened,
          "epicentre": lambda: bg_flattened(center=True), "post": bg_post, "camp": bg_camp,
          "night_city": bg_night_city, "swamp": bg_swamp, "map": bg_map, "seismo": bg_seismo,
          "board": lambda: B.bg_board("THEORIES")}

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for n in (sys.argv[2:] or list(SCENES)):
        SCENES[n]().save(os.path.join(out, n + ".png")); print(n)
