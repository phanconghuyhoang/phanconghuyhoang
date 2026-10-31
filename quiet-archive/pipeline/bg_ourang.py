"""Backdrops for the Ourang Medan legend (Strait of Malacca, 1940s). Flat cartoon, 2560x1440.

usage: python3 bg_ourang.py <outdir> [names]
"""
import os, random, sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
import visuals as V
import backdrops as B

BW, BH = B.BW, B.BH


def freighter(d, x, base, s=1.0, hull=(50, 56, 66), deck=(210, 206, 196)):
    w = int(1300 * s)
    d.polygon([(x, base - 120 * s), (x + w, base - 120 * s), (x + w - 80 * s, base), (x + 60 * s, base)], fill=hull)
    d.rectangle((x + w * 0.62, base - 330 * s, x + w * 0.82, base - 120 * s), fill=deck)
    d.rectangle((x + w * 0.66, base - 420 * s, x + w * 0.74, base - 330 * s), fill=(160, 60, 50))
    for k in range(4):
        d.rectangle((x + w * 0.64 + k * 50 * s, base - 300 * s, x + w * 0.64 + k * 50 * s + 30 * s, base - 270 * s), fill=(110, 150, 180))
    for mx in (0.18, 0.42):
        d.rectangle((x + w * mx, base - 380 * s, x + w * mx + 12 * s, base - 120 * s), fill=(80, 80, 86))
        d.line([(x + w * mx, base - 360 * s), (x + w * mx - 120 * s, base - 140 * s)], fill=(80, 80, 86), width=int(5 * s))


def bg_ship():
    im = B.vgrad((150, 196, 230), (230, 236, 236)); B.soft_clouds(im, 5, 3); d = ImageDraw.Draw(im)
    B.waves(im, 900, (40, 110, 150), (80, 150, 190), rows=10); d = ImageDraw.Draw(im)
    freighter(d, 600, 960)
    return im


def bg_ship_fire():
    im = B.vgrad((60, 50, 70), (200, 120, 80)); d = ImageDraw.Draw(im)
    B.waves(im, 900, (30, 50, 70), (60, 80, 100), rows=10); d = ImageDraw.Draw(im)
    freighter(d, 600, 960, hull=(30, 30, 36), deck=(120, 110, 100))
    rng = random.Random(7)
    for x in range(900, 1500, 60):
        h = rng.uniform(120, 300)
        d.polygon([(x, 850), (x + 30, 850 - h), (x + 60, 850)], fill=(250, 130, 40)); d.polygon([(x + 15, 850), (x + 30, 850 - h * 0.5), (x + 45, 850)], fill=(255, 220, 100))
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for k in range(18):
        r = 80 + k * 30; ld.ellipse((1200 - r + k * 40, 600 - k * 50 - r * 0.6, 1200 + r + k * 40, 600 - k * 50 + r * 0.6), fill=(40, 36, 40, 150))
    lay = lay.filter(ImageFilter.GaussianBlur(30))
    return Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")


def bg_bridge():
    im = Image.new("RGB", (BW, BH), (120, 124, 130)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, BW, 600), fill=(96, 100, 108))
    for x in range(200, 2400, 440):  # windows to the sea
        d.rectangle((x, 140, x + 360, 520), fill=(150, 196, 220), outline=(60, 64, 70), width=14)
        d.rectangle((x + 14, 380, x + 346, 506), fill=(60, 120, 160))
    d.rectangle((0, 1060, BW, BH), fill=(90, 84, 76))
    d.ellipse((1180, 720, 1380, 920), outline=(120, 90, 60), width=26)  # ship's wheel
    for k in range(8):
        import math
        a = k * math.pi / 4; d.line([(1280, 820), (1280 + math.cos(a) * 130, 820 + math.sin(a) * 130)], fill=(120, 90, 60), width=12)
    d.rectangle((1240, 920, 1320, 1060), fill=(80, 70, 60))
    d.rectangle((1700, 860, 2100, 1060), fill=(110, 90, 66)); d.rectangle((1720, 820, 2080, 870), fill=(230, 220, 190))  # chart table
    d.ellipse((600, 1080, 720, 1110), fill=(40, 40, 50)); d.rectangle((620, 1050, 700, 1086), fill=(40, 40, 50))  # a dropped cap
    return im


def bg_register():
    im = Image.new("RGB", (BW, BH), (60, 46, 36)); d = ImageDraw.Draw(im)
    d.rectangle((300, 140, 2260, 1320), fill=(230, 222, 200)); d.line([(1280, 140), (1280, 1320)], fill=(170, 160, 140), width=8)
    f = V.font(V.SERIF_B, 54); fs = V.font(V.SERIF, 40)
    d.text((380, 200), "SHIP REGISTER (illustration)", font=f, fill=(60, 40, 30))
    names = ["Orion", "Orita", "Ormonde", "Oronsay", "Orsova", "———", "Otaio", "Otranto"]
    for i, n in enumerate(names):
        d.text((400, 330 + i * 110), n, font=fs, fill=(70, 60, 50))
        d.line([(400, 380 + i * 110), (1200, 380 + i * 110)], fill=(190, 180, 160), width=3)
    d.text((1360, 520), "Ourang Medan?", font=f, fill=(170, 40, 40))
    d.text((1360, 620), "no entry found", font=fs, fill=(170, 40, 40))
    return im


SCENES = {"ship": bg_ship, "ship_fire": bg_ship_fire, "bridge": bg_bridge, "register": bg_register,
          "news": lambda: B.bg_newspaper("Death ship found in Malacca Strait", "Crew dead, cause unknown, says sailor's story (as later retold)"),
          "board": lambda: B.bg_board("THEORIES")}

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for n in (sys.argv[2:] or list(SCENES)):
        SCENES[n]().save(os.path.join(out, n + ".png")); print(n)
