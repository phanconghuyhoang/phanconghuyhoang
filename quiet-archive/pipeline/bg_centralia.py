"""Backdrops for Centralia, Pennsylvania (underground mine fire since 1962). Flat cartoon, 2560x1440.

usage: python3 bg_centralia.py <outdir> [names]
"""
import os, random, sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
import visuals as V
import backdrops as B

BW, BH = B.BW, B.BH


def house(d, x, base, w=360, h=300, wall=(210, 200, 180), roof=(110, 70, 60)):
    d.rectangle((x, base - h, x + w, base), fill=wall)
    d.polygon([(x - 30, base - h), (x + w // 2, base - h - 170), (x + w + 30, base - h)], fill=roof)
    for k in range(2):
        d.rectangle((x + 40 + k * 180, base - h + 60, x + 130 + k * 180, base - h + 150), fill=(120, 150, 180), outline=(240, 240, 240), width=8)
    d.rectangle((x + w // 2 - 40, base - 150, x + w // 2 + 40, base), fill=(90, 60, 40))
    d.rectangle((x - 20, base - 40, x + w + 20, base), fill=(160, 150, 136))  # porch


def church(d, x, base):
    d.rectangle((x, base - 300, x + 260, base), fill=(236, 232, 222))
    d.polygon([(x - 20, base - 300), (x + 130, base - 420), (x + 280, base - 300)], fill=(90, 110, 140))
    d.rectangle((x + 90, base - 560, x + 170, base - 380), fill=(236, 232, 222))
    d.polygon([(x + 80, base - 560), (x + 130, base - 680), (x + 180, base - 560)], fill=(90, 110, 140))
    d.ellipse((x + 110, base - 520, x + 150, base - 480), fill=(110, 90, 60))
    d.rectangle((x + 125, base - 720, x + 135, base - 680), fill=(240, 220, 120)); d.rectangle((x + 112, base - 708, x + 148, base - 698), fill=(240, 220, 120))


def steam(im, spots, seed=1, strength=150):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rng = random.Random(seed)
    for (x, y) in spots:
        for k in range(14):
            r = 40 + k * 18; yy = y - k * 45 + rng.uniform(-10, 10); xx = x + rng.uniform(-30, 30) + k * 6
            d.ellipse((xx - r, yy - r * 0.6, xx + r, yy + r * 0.6), fill=(235, 235, 240, max(10, strength - k * 10)))
    lay = lay.filter(ImageFilter.GaussianBlur(24))
    return Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")


def hills(d, y, col):
    d.polygon([(0, y), (500, y - 160), (1100, y - 60), (1700, y - 200), (2300, y - 80), (BW, y - 140), (BW, BH), (0, BH)], fill=col)


def bg_town():
    im = B.vgrad((150, 190, 226), (230, 232, 222)); B.soft_clouds(im, 5, 51); d = ImageDraw.Draw(im)
    hills(d, 900, (110, 130, 100))
    church(d, 1900, 820)
    for i, x in enumerate((80, 520, 960, 1400)):
        house(d, x, 1060, wall=[(214, 200, 176), (190, 196, 206), (222, 212, 190), (200, 180, 170)][i])
    d.rectangle((0, 1060, BW, BH), fill=(90, 90, 96)); d.rectangle((0, 1060, BW, 1100), fill=(170, 166, 156))
    for x in range(0, BW, 220):
        d.rectangle((x, 1240, x + 120, 1256), fill=(230, 210, 100))
    return im


def bg_pit():
    im = B.vgrad((150, 180, 210), (220, 214, 200)); d = ImageDraw.Draw(im)
    hills(d, 760, (120, 130, 100))
    d.polygon([(300, 760), (2260, 760), (1900, 1200), (660, 1200)], fill=(80, 64, 50))
    rng = random.Random(4)
    for _ in range(90):  # trash
        x, y = rng.uniform(700, 1860), rng.uniform(900, 1180)
        d.rectangle((x, y, x + rng.uniform(20, 60), y + rng.uniform(14, 34)), fill=rng.choice([(150, 140, 120), (110, 120, 130), (170, 150, 110), (90, 80, 70)]))
    for x in range(800, 1800, 120):  # flames
        h = rng.uniform(90, 200)
        d.polygon([(x, 1000), (x + 40, 1000 - h), (x + 80, 1000)], fill=(240, 120, 40)); d.polygon([(x + 20, 1000), (x + 40, 1000 - h * 0.55), (x + 60, 1000)], fill=(255, 210, 90))
    d.ellipse((1980, 1060, 2080, 1140), fill=(20, 16, 14))  # the hole in the pit wall
    d.rectangle((0, 1200, BW, BH), fill=(110, 100, 80))
    return steam(im, [(1100, 900), (1500, 920)], 3, 110)


def bg_mine():
    im = Image.new("RGB", (BW, BH), (100, 80, 60)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, BW, 260), fill=(150, 190, 220)); d.rectangle((0, 240, BW, 300), fill=(90, 110, 70))
    for x in (300, 700, 1100, 1700, 2100):
        d.rectangle((x, 140, x + 160, 250), fill=(210, 200, 180)); d.polygon([(x - 10, 140), (x + 80, 80), (x + 170, 140)], fill=(110, 70, 60))
    for i, y in enumerate((560, 860, 1160)):  # coal seams with tunnels
        d.rectangle((0, y - 60, BW, y + 60), fill=(36, 32, 30))
        for x in range(80, BW, 300):
            d.rectangle((x, y - 40, x + 200, y + 40), fill=(60, 54, 48))
    for x in (900, 1900):
        d.rectangle((x, 300, x + 60, 1220), fill=(60, 54, 48))  # shafts
    rng = random.Random(8)
    for y in (860, 1160):  # glowing fire front
        for x in range(1200, BW, 70):
            c = rng.choice([(240, 110, 40), (255, 170, 60), (220, 70, 30)])
            d.ellipse((x - 30, y - 34, x + 30, y + 34), fill=c)
    f = V.font(V.SANS_B, 50)
    d.text((80, 320), "Town", font=f, fill=(250, 250, 250)); d.text((80, 1300), "Abandoned coal mines (cross-section, not to scale)", font=V.font(V.SANS, 40), fill=(240, 230, 210))
    d.text((1700, 1000), "FIRE", font=V.font(V.SANS_B, 80), fill=(255, 200, 90))
    return im


def bg_gas():
    im = B.vgrad((160, 196, 226), (236, 230, 216)); B.soft_clouds(im, 4, 61); d = ImageDraw.Draw(im)
    hills(d, 880, (120, 136, 104))
    d.rectangle((1300, 520, 2300, 1000), fill=(236, 236, 230)); d.rectangle((1300, 480, 2300, 560), fill=(200, 50, 40))
    d.text((1420, 488), "GAS", font=V.font(V.SANS_B, 70), fill=(255, 255, 255))
    d.rectangle((1400, 640, 1700, 860), fill=(120, 160, 190))
    for x in (600, 900):  # pumps
        d.rectangle((x, 760, x + 120, 1000), fill=(200, 50, 40)); d.rectangle((x + 20, 790, x + 100, 850), fill=(250, 250, 240))
    d.rectangle((0, 1000, BW, BH), fill=(110, 110, 114))
    d.rectangle((1100, 1150, 1500, 1400), fill=(70, 70, 76), outline=(40, 40, 44), width=8)  # underground tank cap / thermometer
    d.rectangle((1950, 1060, 1990, 1380), fill=(240, 240, 240), outline=(60, 60, 60), width=6); d.rectangle((1956, 1100, 1984, 1374), fill=(220, 40, 30))
    d.ellipse((1930, 1340, 2010, 1420), fill=(220, 40, 30))
    return im


def bg_yard():
    im = B.vgrad((150, 186, 220), (230, 230, 220)); B.soft_clouds(im, 4, 71); d = ImageDraw.Draw(im)
    house(d, 1700, 1000, w=520, h=380)
    for x in range(0, BW, 60):
        d.rectangle((x, 880, x + 14, 1000), fill=(240, 240, 236))
    d.rectangle((0, 900, BW, 914), fill=(240, 240, 236))
    d.rectangle((0, 1000, BW, BH), fill=(110, 150, 80))
    d.rectangle((300, 600, 360, 1000), fill=(100, 70, 50)); d.ellipse((140, 360, 520, 700), fill=(70, 120, 60))  # tree
    d.ellipse((900, 1120, 1260, 1220), fill=(30, 24, 20))  # sinkhole
    for k in range(6):
        d.line([(960 + k * 50, 1130), (940 + k * 56, 1200)], fill=(90, 66, 40), width=6)  # roots
    return steam(im, [(1080, 1140)], 5, 170)


def bg_field():
    im = B.vgrad((170, 196, 220), (230, 228, 214)); B.soft_clouds(im, 3, 81); d = ImageDraw.Draw(im)
    hills(d, 900, (120, 134, 100))
    church(d, 1950, 880)
    d.rectangle((0, 960, BW, BH), fill=(130, 150, 90))
    d.polygon([(1100, 960), (1300, 960), (1700, BH), (700, BH)], fill=(100, 100, 104))  # empty street
    d.rectangle((0, 1120, BW, 1180), fill=(100, 100, 104))
    house(d, 300, 1000, w=320, h=260, wall=(214, 206, 190))
    d.rectangle((2200, 1050, 2420, 1180), fill=(240, 200, 40)); d.text((2215, 1080), "DANGER", font=V.font(V.SANS_B, 48), fill=(30, 30, 30))
    d.rectangle((2300, 1180, 2320, 1300), fill=(60, 60, 60))
    return im


def bg_road():
    im = B.vgrad((150, 160, 180), (220, 214, 204)); d = ImageDraw.Draw(im)
    hills(d, 820, (110, 124, 96))
    d.polygon([(1000, 820), (1560, 820), (2400, BH), (160, BH)], fill=(80, 80, 86))
    rng = random.Random(91)
    for _ in range(40):  # abstract paint marks (no text)
        x, y = rng.uniform(400, 2100), rng.uniform(900, 1400); w = rng.uniform(80, 260)
        d.ellipse((x, y, x + w, y + w * 0.3), fill=rng.choice([(220, 60, 120), (60, 160, 220), (240, 200, 40), (80, 200, 120), (240, 120, 40)]))
    for x0, y0 in ((1200, 950), (900, 1150), (1500, 1250)):  # cracks
        pts = [(x0, y0)]
        for k in range(6):
            pts.append((pts[-1][0] + rng.uniform(20, 80), pts[-1][1] + rng.uniform(-30, 30)))
        d.line(pts, fill=(30, 30, 32), width=10)
    return steam(im, [(1260, 960), (980, 1160), (1560, 1260)], 9, 140)


def bg_smoke():
    im = B.vgrad((120, 130, 150), (200, 196, 190)); d = ImageDraw.Draw(im)
    hills(d, 900, (100, 110, 90))
    d.rectangle((0, 960, BW, BH), fill=(140, 130, 100))
    rng = random.Random(3)
    for _ in range(120):
        x, y = rng.uniform(0, BW), rng.uniform(980, BH)
        d.line([(x, y), (x + rng.uniform(-8, 8), y - rng.uniform(20, 50))], fill=(110, 100, 70), width=5)
    for x in (600, 1300, 2000):
        d.ellipse((x - 70, 1080, x + 70, 1120), fill=(60, 50, 40))
    return steam(im, [(600, 1090), (1300, 1090), (2000, 1090)], 11, 170)


SCENES = {"town": bg_town, "pit": bg_pit, "mine": bg_mine, "gas": bg_gas, "yard": bg_yard, "field": bg_field,
          "road": bg_road, "smoke": bg_smoke,
          "news": lambda: B.bg_newspaper("Town to be relocated: $42 million approved", "Congress funds buyout of Centralia homes above the mine fire (1983)")}

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for n in (sys.argv[2:] or list(SCENES)):
        SCENES[n]().save(os.path.join(out, n + ".png")); print(n)
