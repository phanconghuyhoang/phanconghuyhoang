"""Backdrops for Kaspar Hauser (Nuremberg 1828 – Ansbach 1833). Flat cartoon, 2560x1440.

usage: python3 bg_hauser.py <outdir> [names]
"""
import os, random, sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
import visuals as V
import backdrops as B

BW, BH = B.BW, B.BH


def bg_cell():
    im = Image.new("RGB", (BW, BH), (46, 42, 40)); d = ImageDraw.Draw(im)
    rng = random.Random(3)
    for y in range(0, 1080, 90):
        off = 0 if (y // 90) % 2 else 70
        for x in range(-70 + off, BW, 140):
            c = rng.randint(52, 66); d.rectangle((x + 4, y + 4, x + 136, y + 86), fill=(c, c - 4, c - 8))
    d.rectangle((0, 1080, BW, BH), fill=(70, 60, 48))
    for k in range(80):  # straw
        x, y = rng.uniform(300, 1100), rng.uniform(1100, 1300)
        d.line([(x, y), (x + rng.uniform(-40, 40), y + rng.uniform(-10, 10))], fill=(190, 160, 90), width=4)
    d.rectangle((1640, 980, 1720, 1060), fill=(150, 110, 70))  # bread
    d.ellipse((1760, 980, 1860, 1060), fill=(90, 110, 130))  # water jug
    for x in (1960, 2120):  # wooden toy horses
        d.rectangle((x, 990, x + 110, 1030), fill=(170, 120, 70)); d.rectangle((x + 90, 950, x + 120, 1000), fill=(170, 120, 70))
        for lx in (x + 10, x + 90):
            d.rectangle((lx, 1030, lx + 12, 1070), fill=(140, 96, 56))
        d.rectangle((x - 10, 1066, x + 130, 1080), fill=(120, 84, 50))
    lay = Image.new("L", (BW, BH), 0); ImageDraw.Draw(lay).polygon([(1200, 0), (1360, 0), (1700, 1440), (900, 1440)], fill=90)
    lay = lay.filter(ImageFilter.GaussianBlur(60))
    im = Image.composite(Image.new("RGB", (BW, BH), (210, 196, 160)), im, lay)
    d = ImageDraw.Draw(im); d.rectangle((1220, 80, 1340, 220), fill=(20, 18, 16))
    for x in range(1240, 1340, 30):
        d.rectangle((x, 80, x + 8, 220), fill=(80, 76, 70))
    return im


def bg_letter():
    im = Image.new("RGB", (BW, BH), (60, 46, 36)); d = ImageDraw.Draw(im)
    d.polygon([(560, 160), (2000, 120), (2040, 1300), (520, 1340)], fill=(232, 220, 190))
    f = V.font(V.SERIF_I, 54)
    lines = ["To the Captain of the 4th Squadron,", "Nuremberg, 1828", "", "I send you a boy who wishes", "to serve his king…", "", "(illustration — wording paraphrased)"]
    for i, ln in enumerate(lines):
        d.text((660, 260 + i * 110), ln, font=f, fill=(70, 50, 40))
    return im


def bg_palace():
    im = B.vgrad((150, 190, 226), (230, 228, 220)); B.soft_clouds(im, 4, 21); d = ImageDraw.Draw(im)
    d.rectangle((0, 1040, BW, BH), fill=(120, 150, 90))
    d.rectangle((600, 560, 1960, 1040), fill=(236, 226, 196))
    d.polygon([(560, 560), (1280, 360), (2000, 560)], fill=(100, 110, 130))
    d.rectangle((1180, 260, 1380, 560), fill=(236, 226, 196)); d.polygon([(1160, 260), (1280, 140), (1400, 260)], fill=(100, 110, 130))
    for row in range(2):
        for x in range(660, 1920, 120):
            d.rectangle((x, 640 + row * 180, x + 60, 760 + row * 180), fill=(120, 150, 180))
    d.rectangle((1220, 860, 1340, 1040), fill=(110, 80, 50))
    d.rectangle((1260, 60, 1266, 150), fill=(80, 80, 80)); d.polygon([(1266, 60), (1360, 80), (1266, 100)], fill=(220, 190, 60))
    return im


def bg_garden():
    im = B.vgrad((180, 190, 206), (236, 236, 236)); d = ImageDraw.Draw(im)
    d.rectangle((0, 1000, BW, BH), fill=(232, 234, 238))  # snow
    rng = random.Random(41)
    for x in range(100, BW, 300):  # bare trees
        d.rectangle((x, 520, x + 30, 1010), fill=(80, 66, 56))
        for k in range(5):
            y = 560 + k * 80; s = 1 if k % 2 else -1
            d.line([(x + 15, y), (x + 15 + s * 140, y - 90)], fill=(80, 66, 56), width=10)
    d.rectangle((0, 1160, BW, 1220), fill=(200, 196, 190))  # path
    d.polygon([(1700, 1000), (1700, 820), (1820, 760), (1940, 820), (1940, 1000)], fill=(200, 196, 186))  # monument
    for _ in range(200):
        x, y = rng.uniform(0, BW), rng.uniform(0, 1000); d.ellipse((x, y, x + 6, y + 6), fill=(250, 250, 252))
    return im


def bg_map():
    im = Image.new("RGB", (BW, BH), (214, 206, 176)); d = ImageDraw.Draw(im)
    d.line([(300, 0), (420, 500), (360, 1000), (460, 1440)], fill=(70, 130, 180), width=24)  # Rhine
    f = V.font(V.SANS_B, 56); fs = V.font(V.SANS, 40)
    for name, x, y in (("Nuremberg", 1700, 520), ("Ansbach", 1450, 760), ("Karlsruhe (Baden)", 520, 980)):
        d.ellipse((x - 20, y - 20, x + 20, y + 20), fill=(200, 40, 40)); d.text((x + 30, y - 30), name, font=f, fill=(50, 40, 30))
    d.text((1300, 200), "Kingdom of Bavaria", font=f, fill=(110, 90, 60)); d.text((500, 1180), "Grand Duchy of Baden", font=f, fill=(110, 90, 60))
    d.text((440, 300), "Rhine", font=fs, fill=(40, 90, 140))
    d.text((60, BH - 70), "Schematic map, not to scale", font=fs, fill=(90, 80, 60))
    return im


SCENES = {"cell": bg_cell, "letter": bg_letter, "palace": bg_palace, "garden": bg_garden, "map": bg_map,
          "board": lambda: B.bg_board("THEORIES")}

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for n in (sys.argv[2:] or list(SCENES)):
        SCENES[n]().save(os.path.join(out, n + ".png")); print(n)
