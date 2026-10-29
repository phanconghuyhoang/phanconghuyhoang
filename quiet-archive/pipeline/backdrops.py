"""Cartoon stage backdrops (2560x1440) for v3 videos: flat colours, clear floor line for the stick-figure cast.

render(name, **kw) -> PIL RGB image. FLOOR[name] = fraction of height where feet stand.
Run `python3 backdrops.py <outdir> name1 name2 ...` to write PNGs.
"""
import math, random, sys, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import visuals as V

BW, BH = 2560, 1440
FLOOR = {}


def vgrad(top, bottom, w=BW, h=BH):
    im = Image.new("RGB", (w, h)); d = ImageDraw.Draw(im)
    for y in range(h):
        u = y / (h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * u) for i in range(3)))
    return im


def soft_clouds(im, n, seed, color=(255, 255, 255), alpha=170, ymax=0.4):
    rng = random.Random(seed)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for _ in range(n):
        cx, cy = rng.uniform(0, BW), rng.uniform(60, BH * ymax)
        for k in range(5):
            r = rng.uniform(60, 130)
            d.ellipse((cx + k * 70 - r, cy - r * 0.6, cx + k * 70 + r, cy + r * 0.6), fill=color + (alpha,))
    lay = lay.filter(ImageFilter.GaussianBlur(6))
    im.paste(lay, (0, 0), lay)


def waves(im, y0, color, line, seed=3, rows=14):
    d = ImageDraw.Draw(im)
    d.rectangle((0, y0, BW, BH), fill=color)
    rng = random.Random(seed)
    for r in range(rows):
        y = y0 + 18 + r * (BH - y0) / rows
        amp = 4 + r * 1.2
        pts = [(x, y + math.sin(x / (40 + r * 6) + r) * amp) for x in range(0, BW + 20, 20)]
        d.line(pts, fill=line, width=2 + r // 5)


def sailing_ship(d, x, base, s=1.0, hull=(70, 44, 30), sail=(240, 232, 214), masts=2, damaged=False, flag=None):
    L = 760 * s
    d.polygon([(x - L / 2, base - 70 * s), (x + L / 2 + 60 * s, base - 80 * s), (x + L / 2 - 20 * s, base + 30 * s), (x - L / 2 + 40 * s, base + 30 * s)], fill=hull)
    d.rectangle((x - L / 2 + 20 * s, base - 70 * s, x + L / 2 + 20 * s, base - 58 * s), fill=(200, 170, 110))
    for k in range(masts):
        mx = x - L * 0.22 + k * L * 0.42
        top = base - 640 * s
        d.line([(mx, base - 70 * s), (mx, top)], fill=(60, 40, 28), width=int(12 * s))
        for j in range(3):
            y1 = top + 40 * s + j * 170 * s
            wdt = (150 + j * 30) * s
            if damaged and (j + k) % 2 == 0:
                d.polygon([(mx - wdt, y1), (mx + wdt, y1), (mx + wdt * 0.2, y1 + 120 * s), (mx - wdt * 0.6, y1 + 80 * s)], fill=sail)
            else:
                d.polygon([(mx - wdt, y1), (mx + wdt, y1), (mx + wdt * 1.05, y1 + 140 * s), (mx - wdt * 1.05, y1 + 140 * s)], fill=sail, outline=(150, 140, 120))
        if flag and k == 0:
            d.polygon([(mx, top), (mx + 70 * s, top + 22 * s), (mx, top + 44 * s)], fill=flag)
    d.polygon([(x + L / 2 + 60 * s, base - 80 * s), (x + L / 2 + 260 * s, base - 300 * s)], fill=(60, 40, 28))
    d.line([(x + L / 2 + 40 * s, base - 76 * s), (x + L / 2 + 260 * s, base - 260 * s)], fill=(60, 40, 28), width=int(8 * s))


def bg_sea_day(ship=True, ship2=False):
    im = vgrad((120, 180, 225), (205, 228, 240)); soft_clouds(im, 9, 4)
    hz = int(BH * 0.58)
    waves(im, hz, (46, 104, 150), (90, 150, 190), rows=16)
    d = ImageDraw.Draw(im)
    if ship:
        sailing_ship(d, 1300, hz + 60, 1.0, damaged=True)
    if ship2:
        sailing_ship(d, 380, hz + 20, 0.45, hull=(40, 40, 50), flag=(200, 40, 40))
    return im


def bg_sea_storm():
    im = vgrad((60, 66, 80), (120, 126, 136)); soft_clouds(im, 14, 8, (40, 44, 54), 220, 0.5)
    hz = int(BH * 0.6)
    waves(im, hz, (30, 52, 70), (70, 100, 120), seed=8, rows=10)
    d = ImageDraw.Draw(im)
    d.line([(1700, 0), (1660, 300), (1720, 330), (1640, 700)], fill=(255, 245, 200), width=10)
    return im


def bg_harbor():
    im = vgrad((240, 196, 150), (250, 226, 196))
    d = ImageDraw.Draw(im)
    rng = random.Random(2)
    x = 0
    while x < BW:   # city skyline
        w = rng.randint(80, 200); h = rng.randint(160, 420)
        d.rectangle((x, 780 - h, x + w, 780), fill=(150, 120, 120))
        for wy in range(780 - h + 20, 770, 40):
            for wx in range(x + 12, x + w - 12, 30):
                if rng.random() < 0.4:
                    d.rectangle((wx, wy, wx + 12, wy + 18), fill=(250, 220, 150))
        x += w + 6
    waves(im, 780, (70, 120, 150), (110, 160, 185), rows=6)
    d.rectangle((0, 1040, BW, BH), fill=(120, 86, 56))
    for k in range(0, BW, 120):
        d.line([(k, 1040), (k, BH)], fill=(100, 70, 46), width=4)
    sailing_ship(d, 1500, 960, 0.8)
    for cx in (300, 420, 2200):
        d.rectangle((cx, 940, cx + 110, 1040), fill=(170, 120, 70), outline=(110, 76, 44), width=6)
        d.line([(cx, 940), (cx + 110, 1040)], fill=(110, 76, 44), width=5)
    FLOOR["harbor"] = 0.80
    return im


def bg_deck(hatch_open=True):
    im = vgrad((150, 196, 230), (210, 230, 240)); soft_clouds(im, 6, 3)
    d = ImageDraw.Draw(im)
    waves(im, 760, (46, 104, 150), (90, 150, 190), rows=5)
    d.rectangle((0, 980, BW, BH), fill=(150, 108, 66))
    for k in range(0, BW, 90):
        d.line([(k, 980), (k - 60, BH)], fill=(128, 90, 54), width=3)
    d.rectangle((0, 900, BW, 980), fill=(110, 76, 46))   # rail
    for k in range(0, BW, 160):
        d.rectangle((k, 860, k + 22, 980), fill=(96, 66, 40))
    d.rectangle((0, 850, BW, 872), fill=(120, 84, 50))
    d.rectangle((1180, 0, 1240, 980), fill=(96, 66, 40))   # mast
    d.polygon([(1240, 60), (1900, 120), (1880, 760), (1240, 720)], fill=(240, 232, 214), outline=(170, 160, 140))
    # hatch
    if hatch_open:
        d.rectangle((1500, 1080, 1840, 1180), fill=(30, 22, 16)); d.rectangle((1860, 1110, 2200, 1190), fill=(170, 124, 76), outline=(100, 70, 44), width=6)
    else:
        d.rectangle((1500, 1080, 1840, 1180), fill=(170, 124, 76), outline=(100, 70, 44), width=6)
    # wheel
    cx, cy = 480, 900
    d.ellipse((cx - 120, cy - 120, cx + 120, cy + 120), outline=(90, 60, 36), width=18)
    for a in range(0, 360, 45):
        r = math.radians(a)
        d.line([(cx, cy), (cx + math.cos(r) * 150, cy + math.sin(r) * 150)], fill=(90, 60, 36), width=10)
    d.rectangle((cx - 20, cy, cx + 20, 1080), fill=(90, 60, 36))
    FLOOR["deck"] = 0.86
    return im


def bg_cabin():
    im = Image.new("RGB", (BW, BH), (112, 78, 52)); d = ImageDraw.Draw(im)
    for k in range(0, BH, 70):
        d.line([(0, k), (BW, k)], fill=(98, 68, 44), width=4)
    d.rectangle((0, 1120, BW, BH), fill=(80, 56, 38))
    # porthole with sea
    d.ellipse((1980, 260, 2280, 560), fill=(60, 40, 28)); d.ellipse((2010, 290, 2250, 530), fill=(120, 180, 220))
    d.rectangle((2010, 420, 2250, 530), fill=(46, 104, 150))
    # bed with sword
    d.rectangle((180, 820, 980, 1000), fill=(90, 60, 40)); d.rectangle((200, 760, 960, 830), fill=(220, 214, 200)); d.rectangle((200, 740, 380, 800), fill=(240, 240, 236))
    d.line([(400, 1040), (900, 1010)], fill=(200, 200, 210), width=12); d.rectangle((370, 1025, 410, 1060), fill=(170, 130, 50))
    # table with sewing machine and bottle of ink
    d.rectangle((1300, 860, 1800, 900), fill=(130, 90, 56)); d.rectangle((1330, 900, 1360, 1120), fill=(110, 76, 46)); d.rectangle((1740, 900, 1770, 1120), fill=(110, 76, 46))
    d.rectangle((1380, 760, 1580, 860), fill=(30, 30, 34)); d.arc((1380, 700, 1560, 860), 180, 270, fill=(30, 30, 34), width=30)
    d.rectangle((1640, 800, 1690, 860), fill=(40, 50, 90))
    # picture frame
    d.rectangle((700, 240, 1040, 520), fill=(170, 130, 60)); d.rectangle((730, 270, 1010, 490), fill=(200, 210, 200))
    FLOOR["cabin"] = 0.86
    return im


def bg_hold():
    im = Image.new("RGB", (BW, BH), (46, 34, 26)); d = ImageDraw.Draw(im)
    for k in range(0, BW, 220):
        d.arc((k - 300, -500, k + 300, 600), 30, 150, fill=(70, 50, 36), width=14)
    d.rectangle((0, 1150, BW, BH), fill=(36, 26, 20))
    rng = random.Random(5)
    for row in range(3):
        for k in range(12):
            x = 120 + k * 200 + (row % 2) * 100; y = 1080 - row * 180
            d.ellipse((x - 90, y - 85, x + 90, y + 85), fill=(150, 96, 52), outline=(90, 56, 30), width=8)
            for r in (40, 70):
                d.ellipse((x - r, y - r * 0.95, x + r, y + r * 0.95), outline=(110, 70, 38), width=6)
    # light from hatch
    lay = Image.new("L", (BW, BH), 0); ImageDraw.Draw(lay).polygon([(1100, 0), (1500, 0), (1800, BH), (800, BH)], fill=90)
    lay = lay.filter(ImageFilter.GaussianBlur(40))
    im = Image.composite(Image.new("RGB", (BW, BH), (255, 230, 170)), im, lay)
    FLOOR["hold"] = 0.88
    return im


def bg_court():
    im = Image.new("RGB", (BW, BH), (140, 110, 84)); d = ImageDraw.Draw(im)
    for x in range(0, BW, 260):
        d.rectangle((x + 20, 120, x + 60, 900), fill=(160, 130, 100))
    d.rectangle((0, 1000, BW, BH), fill=(110, 80, 56))
    d.rectangle((900, 620, 1660, 1000), fill=(96, 62, 38)); d.rectangle((880, 600, 1680, 640), fill=(120, 80, 50))
    d.ellipse((1180, 200, 1380, 400), fill=(200, 170, 80)); d.ellipse((1210, 230, 1350, 370), fill=(150, 120, 60))
    FLOOR["court"] = 0.86
    return im


def bg_study():
    im = Image.new("RGB", (BW, BH), (60, 70, 62)); d = ImageDraw.Draw(im)
    for x in range(0, BW, 90):
        d.line([(x, 0), (x, 1060)], fill=(66, 78, 68), width=30)
    d.rectangle((0, 1060, BW, BH), fill=(96, 62, 40))
    d.rectangle((300, 200, 900, 1060), fill=(70, 46, 32))
    rng = random.Random(9)
    for row in range(5):
        x = 320
        while x < 870:
            w = rng.randint(24, 46); col = rng.choice([(150, 40, 40), (40, 70, 120), (60, 110, 60), (190, 160, 90)])
            d.rectangle((x, 240 + row * 160, x + w - 4, 380 + row * 160), fill=col); x += w
    d.rectangle((1300, 820, 2200, 860), fill=(110, 70, 44)); d.rectangle((1340, 860, 1380, 1100), fill=(90, 58, 36)); d.rectangle((2120, 860, 2160, 1100), fill=(90, 58, 36))
    d.rectangle((1500, 780, 1800, 820), fill=(240, 236, 220)); d.line([(1820, 700), (1860, 810)], fill=(30, 30, 30), width=8)
    d.line([(2000, 820), (2000, 620)], fill=(40, 40, 40), width=12); d.polygon([(1930, 640), (2070, 640), (2040, 560), (1960, 560)], fill=(60, 120, 70))
    lay = Image.new("L", (BW, BH), 0); ImageDraw.Draw(lay).ellipse((1700, 400, 2300, 1000), fill=120)
    lay = lay.filter(ImageFilter.GaussianBlur(120))
    im = Image.composite(Image.new("RGB", (BW, BH), (255, 220, 150)), im, lay)
    FLOOR["study"] = 0.86
    return im


def bg_board(title="THEORIES"):
    im = Image.new("RGB", (BW, BH), (60, 56, 52)); d = ImageDraw.Draw(im)
    d.rectangle((240, 120, 2320, 1080), fill=(176, 136, 92), outline=(110, 80, 50), width=24)
    rng = random.Random(4)
    for k in range(400):
        x, y = rng.uniform(260, 2300), rng.uniform(140, 1060)
        d.point((x, y), fill=(150, 112, 74))
    f = V.font(V.SANS_B, 80)
    w = d.textlength(title, font=f); d.text(((BW - w) / 2, 150), title, font=f, fill=(250, 245, 230))
    d.rectangle((0, 1100, BW, BH), fill=(80, 70, 60))
    FLOOR["board"] = 0.92
    return im


def bg_reef():
    im = vgrad((110, 190, 230), (240, 230, 200)); soft_clouds(im, 6, 11)
    d = ImageDraw.Draw(im)
    d.polygon([(0, 700), (500, 560), (900, 640), (1300, 600), (1300, 760), (0, 760)], fill=(70, 130, 80))
    waves(im, 760, (40, 150, 170), (110, 200, 210), rows=10)
    d = ImageDraw.Draw(im)
    for k in range(20):
        x = 900 + k * 70
        d.ellipse((x, 960 + (k % 3) * 20, x + 120, 1010 + (k % 3) * 20), fill=(200, 180, 140))
    # wrecked ship tilted
    d.polygon([(1200, 980), (1900, 860), (1950, 950), (1260, 1060)], fill=(70, 44, 30))
    d.line([(1500, 930), (1380, 500)], fill=(60, 40, 28), width=14); d.line([(1750, 890), (1700, 560)], fill=(60, 40, 28), width=14)
    d.polygon([(1380, 520), (1560, 560), (1500, 760)], fill=(230, 220, 200))
    FLOOR["reef"] = 0.8
    return im


def bg_map_mc(stage=0):
    """North Atlantic schematic: New York -> Azores -> found position -> Gibraltar. stage controls markers shown."""
    im = Image.new("RGB", (BW, BH), (70, 120, 160)); d = ImageDraw.Draw(im)
    for k in range(0, BW, 160):
        d.line([(k, 0), (k, BH)], fill=(80, 130, 170), width=2)
    for k in range(0, BH, 160):
        d.line([(0, k), (BW, k)], fill=(80, 130, 170), width=2)
    land = (214, 196, 150)
    d.polygon([(0, 0), (520, 0), (560, 260), (460, 420), (380, 520), (300, 760), (180, 980), (0, 1100)], fill=land)  # North America
    d.polygon([(2060, 0), (2560, 0), (2560, 1200), (2300, 1260), (2180, 1000), (2140, 760), (2080, 560), (2100, 360)], fill=land)  # Europe/Africa
    for ax, ay in ((1500, 620), (1560, 650), (1620, 600), (1700, 700)):
        d.ellipse((ax - 18, ay - 12, ax + 18, ay + 12), fill=land)
    f = V.font(V.SANS_B, 46); fs = V.font(V.SANS, 38)
    pts = {"ny": (430, 470), "az": (1640, 690), "found": (1980, 610), "gib": (2170, 800)}
    d.ellipse((pts["ny"][0] - 16, pts["ny"][1] - 16, pts["ny"][0] + 16, pts["ny"][1] + 16), fill=(200, 50, 40))
    d.text((pts["ny"][0] + 30, pts["ny"][1] - 60), "New York", font=f, fill=(30, 30, 30))
    d.text((1560, 740), "Azores", font=fs, fill=(250, 250, 250))
    if stage >= 1:
        d.line([pts["ny"], (1000, 640), pts["az"]], fill=(250, 220, 120), width=10, joint="curve")
        d.text((pts["az"][0] - 260, pts["az"][1] - 120), "Last log entry", font=f, fill=(255, 235, 170))
        d.text((pts["az"][0] - 260, pts["az"][1] - 70), "25 Nov 1872", font=fs, fill=(255, 235, 170))
    if stage >= 2:
        for k in range(12):
            u = k / 12
            x = pts["az"][0] + (pts["found"][0] - pts["az"][0]) * u; y = pts["az"][1] + (pts["found"][1] - pts["az"][1]) * u
            d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(255, 255, 255))
        d.ellipse((pts["found"][0] - 22, pts["found"][1] - 22, pts["found"][0] + 22, pts["found"][1] + 22), outline=(200, 40, 40), width=10)
        d.text((pts["found"][0] - 330, pts["found"][1] - 150), "Found, 4 Dec 1872", font=f, fill=(255, 255, 255))
        d.text((pts["found"][0] - 330, pts["found"][1] - 98), "~400 nautical miles later", font=fs, fill=(255, 255, 255))
    if stage >= 3:
        d.line([pts["found"], pts["gib"]], fill=(255, 255, 255), width=6)
        d.text((pts["gib"][0] - 120, pts["gib"][1] + 40), "Gibraltar", font=f, fill=(30, 30, 30))
    d.text((60, BH - 90), "Schematic map, not to scale", font=fs, fill=(220, 230, 240))
    return im


def bg_newspaper(headline, sub):
    im = Image.new("RGB", (BW, BH), (40, 40, 44)); d = ImageDraw.Draw(im)
    d.rectangle((420, 80, 2140, 1360), fill=(236, 230, 214))
    d.text((520, 120), "THE DAILY ARCHIVE", font=V.font(V.SERIF_B, 110), fill=(30, 30, 30))
    d.line([(500, 270), (2060, 270)], fill=(30, 30, 30), width=6)
    y = 320
    for ln in V.wrap(d, headline, V.font(V.SERIF_B, 120), 1560):
        d.text((520, y), ln, font=V.font(V.SERIF_B, 120), fill=(20, 20, 20)); y += 140
    for ln in V.wrap(d, sub, V.font(V.SERIF_I, 60), 1560):
        d.text((520, y + 20), ln, font=V.font(V.SERIF_I, 60), fill=(60, 60, 60)); y += 76
    for k in range(10):
        d.line([(520, y + 120 + k * 50), (2040 - (k % 3) * 200, y + 120 + k * 50)], fill=(150, 146, 136), width=10)
    return im


SCENES = dict(sea_day=bg_sea_day, sea_storm=bg_sea_storm, harbor=bg_harbor, deck=bg_deck, cabin=bg_cabin, hold=bg_hold,
              court=bg_court, study=bg_study, board=bg_board, reef=bg_reef)


if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for name in sys.argv[2:]:
        SCENES[name]().save(os.path.join(out, name + ".png"))


def bg_forest(carving=None, post=False):
    """Coastal forest clearing; carving='CRO' on a tree trunk, post=True adds a palisade post with CROATOAN."""
    im = vgrad((150, 196, 220), (220, 232, 210)); soft_clouds(im, 5, 21)
    d = ImageDraw.Draw(im)
    rng = random.Random(12)
    for k in range(40):  # back trees
        x = rng.uniform(-100, BW); h = rng.uniform(500, 800)
        d.polygon([(x, 1000 - h), (x - 140, 1000), (x + 140, 1000)], fill=(46, 90, 60))
    d.rectangle((0, 1000, BW, BH), fill=(120, 140, 80))
    for k in range(0, BW, 60):
        d.line([(k, 1000), (k + 20, 980)], fill=(100, 124, 66), width=4)
    if carving:
        d.rectangle((300, 200, 520, 1080), fill=(110, 80, 56)); d.ellipse((150, 0, 670, 420), fill=(40, 84, 52))
        d.rectangle((330, 560, 490, 720), fill=(196, 160, 110))
        d.text((345, 590), carving, font=V.font(V.SERIF_B, 80), fill=(70, 46, 30))
    if post:
        for k in range(14):
            x = 1100 + k * 100
            d.polygon([(x, 1000), (x, 600), (x + 40, 560), (x + 80, 600), (x + 80, 1000)], fill=(140, 104, 66), outline=(90, 64, 40))
        d.rectangle((1500, 640, 1580, 1000), fill=(176, 136, 90))
        f = V.font(V.SERIF_B, 54)
        for i, ch in enumerate("CROATOAN"):
            d.text((1520, 650 + i * 42), ch, font=f, fill=(60, 40, 24))
    FLOOR["forest"] = 0.84
    return im


def bg_map_roanoke(stage=0):
    """Outer Banks schematic: Roanoke Island, Croatoan (Hatteras) to the south, Chesapeake Bay to the north."""
    im = Image.new("RGB", (BW, BH), (70, 130, 170)); d = ImageDraw.Draw(im)
    land = (214, 196, 150)
    d.polygon([(0, 0), (1500, 0), (1450, 200), (1300, 260), (1250, 500), (1100, 700), (1000, 1000), (900, 1440), (0, 1440)], fill=land)
    d.polygon([(1620, 300), (1660, 300), (1760, 900), (2050, 1250), (2030, 1270), (1720, 920)], fill=land)  # banks
    d.ellipse((1380, 640, 1500, 860), fill=land)  # Roanoke Island
    d.polygon([(1100, 0), (1350, 0), (1300, 160), (1150, 200)], fill=(70, 130, 170))  # Chesapeake
    f = V.font(V.SANS_B, 52); fs = V.font(V.SANS, 40)
    d.text((1150, 40), "Chesapeake Bay", font=f, fill=(255, 255, 255))
    d.text((1200, 880), "Roanoke Island", font=f, fill=(30, 30, 30))
    d.text((1840, 1180), "Croatoan", font=f, fill=(30, 30, 30)); d.text((1840, 1236), "(today Hatteras Island)", font=fs, fill=(40, 40, 40))
    d.text((300, 600), "Mainland", font=f, fill=(90, 80, 60))
    if stage >= 1:
        d.line([(1440, 640), (1300, 150)], fill=(250, 220, 120), width=8)
        d.text((1500, 380), "Planned: Chesapeake", font=fs, fill=(255, 240, 180))
    if stage >= 2:
        for k in range(10):
            u = k / 10; x = 1480 + (1900 - 1480) * u; y = 800 + (1150 - 800) * u
            d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(255, 255, 255))
        d.text((1560, 1000), "~50 miles", font=fs, fill=(255, 255, 255))
    d.text((60, BH - 90), "Schematic map, not to scale", font=fs, fill=(220, 230, 240))
    return im


def bg_dig():
    """Archaeology dig: trench, grid strings, sieve, finds tray."""
    im = vgrad((160, 200, 230), (230, 236, 220)); soft_clouds(im, 5, 31)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 820, BW, BH), fill=(170, 140, 96))
    d.polygon([(700, 960), (1860, 960), (1760, 1240), (800, 1240)], fill=(120, 90, 60))
    for k in range(6):
        x = 760 + k * 200
        d.line([(x, 960), (x - 30, 1240)], fill=(240, 240, 240), width=3)
    d.line([(740, 1100), (1820, 1100)], fill=(240, 240, 240), width=3)
    d.rectangle((2000, 900, 2300, 940), fill=(90, 70, 50)); d.rectangle((2020, 940, 2040, 1060), fill=(80, 60, 44)); d.rectangle((2260, 940, 2280, 1060), fill=(80, 60, 44))
    for k, c in enumerate([(180, 180, 190), (150, 90, 50), (60, 60, 64)]):
        d.ellipse((2040 + k * 80, 860, 2100 + k * 80, 900), fill=c)
    d.ellipse((300, 900, 520, 980), outline=(90, 70, 50), width=10)
    FLOOR["dig"] = 0.8
    return im


def bg_armada():
    im = bg_sea_storm(); d = ImageDraw.Draw(im)
    for x, s in ((500, 0.5), (1100, 0.6), (1800, 0.55), (2300, 0.45)):
        sailing_ship(d, x, 900, s, hull=(60, 40, 30), flag=(200, 160, 40) if x < 1500 else (190, 40, 40))
    for x in (800, 1500, 2000):
        d.ellipse((x - 60, 760, x + 60, 860), fill=(200, 200, 200))
    return im


def bg_queen():
    """Tudor throne room."""
    im = Image.new("RGB", (BW, BH), (120, 40, 44)); d = ImageDraw.Draw(im)
    for x in range(0, BW, 200):
        d.rectangle((x, 0, x + 100, 1060), fill=(130, 46, 50))
    d.rectangle((0, 1060, BW, BH), fill=(80, 60, 50))
    d.rectangle((1100, 380, 1460, 1060), fill=(200, 160, 60)); d.rectangle((1140, 420, 1420, 760), fill=(150, 30, 40))
    d.polygon([(1180, 380), (1280, 250), (1380, 380)], fill=(220, 180, 70))
    FLOOR["queen"] = 0.86
    return im


def bg_hoax_stone():
    im = Image.new("RGB", (BW, BH), (40, 40, 44)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((900, 300, 1660, 1100), radius=80, fill=(150, 146, 136), outline=(100, 96, 90), width=10)
    f = V.font(V.SERIF_B, 54)
    for i, ln in enumerate(["ANANIAS DARE &", "VIRGINIA WENT", "HENCE VNTO", "HEAVEN 1591 . . ."]):
        d.text((980, 400 + i * 90), ln, font=f, fill=(80, 76, 70))
    V.stamp(im, "HOAX", (1280, 900), angle=-12, size=150)
    return im


SCENES.update(dict(forest=bg_forest, dig=bg_dig, armada=bg_armada, queen=bg_queen))


def avenger(d, x, y, s=1.0, col=(70, 86, 110)):
    """Side view of a WWII torpedo bomber (stylised)."""
    L = 420 * s
    d.polygon([(x - L / 2, y), (x + L / 2 - 40 * s, y - 20 * s), (x + L / 2, y + 10 * s), (x + L / 2 - 30 * s, y + 40 * s), (x - L / 2 + 20 * s, y + 40 * s)], fill=col)
    d.ellipse((x - 40 * s, y - 50 * s, x + 110 * s, y + 5 * s), fill=(160, 200, 220))  # canopy
    d.polygon([(x - L / 2, y), (x - L / 2 - 30 * s, y - 70 * s), (x - L / 2 + 40 * s, y)], fill=col)  # tail
    d.polygon([(x - 60 * s, y + 25 * s), (x + 120 * s, y + 25 * s), (x + 60 * s, y + 60 * s), (x - 90 * s, y + 60 * s)], fill=(56, 70, 92))  # wing
    d.ellipse((x + L / 2 - 10 * s, y - 30 * s, x + L / 2 + 20 * s, y + 60 * s), fill=(200, 200, 200))  # prop disc
    d.ellipse((x - 120 * s, y + 8 * s, x - 90 * s, y + 30 * s), fill=(240, 240, 240)); d.ellipse((x - 112 * s, y + 13 * s, x - 98 * s, y + 25 * s), fill=(30, 50, 120))


def bg_airbase():
    im = vgrad((150, 200, 235), (230, 236, 230)); soft_clouds(im, 6, 41)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 900, BW, BH), fill=(150, 156, 140)); d.rectangle((0, 980, BW, 1100), fill=(90, 92, 96))
    for k in range(0, BW, 220):
        d.rectangle((k, 1036, k + 120, 1044), fill=(240, 240, 230))
    d.rectangle((80, 600, 700, 900), fill=(120, 120, 110)); d.arc((80, 420, 700, 780), 180, 360, fill=(100, 100, 92), width=180)
    d.rectangle((2200, 520, 2280, 900), fill=(200, 196, 180)); d.rectangle((2160, 440, 2320, 520), fill=(90, 120, 140))
    for i, x in enumerate((900, 1250, 1600, 1950)):
        avenger(d, x, 900 - (i % 2) * 10, 0.75)
    FLOOR["airbase"] = 0.82
    return im


def bg_sky_formation(dusk=False):
    im = vgrad((240, 170, 120) if dusk else (110, 170, 220), (60, 70, 100) if dusk else (200, 225, 240)); soft_clouds(im, 10, 43, (255, 230, 210) if dusk else (255, 255, 255))
    d = ImageDraw.Draw(im)
    waves(im, 1100, (30, 70, 110) if dusk else (46, 104, 150), (60, 100, 140) if dusk else (90, 150, 190), rows=6)
    d = ImageDraw.Draw(im)
    for x, y in ((700, 520), (1050, 460), (1400, 520), (1750, 460), (2100, 520)):
        avenger(d, x, y, 0.6)
    return im


def bg_islands():
    im = Image.new("RGB", (BW, BH), (40, 130, 170)); d = ImageDraw.Draw(im)
    rng = random.Random(51)
    for k in range(9):
        x, y = rng.uniform(200, 2300), rng.uniform(200, 1240); w = rng.uniform(120, 360)
        d.ellipse((x - w * 1.3, y - w * 0.5, x + w * 1.3, y + w * 0.5), fill=(90, 190, 200))
        d.ellipse((x - w, y - w * 0.32, x + w, y + w * 0.32), fill=(226, 210, 160))
        d.ellipse((x - w * 0.7, y - w * 0.2, x + w * 0.7, y + w * 0.2), fill=(90, 150, 80))
    return im


def bg_radio_room():
    im = Image.new("RGB", (BW, BH), (70, 80, 76)); d = ImageDraw.Draw(im)
    d.rectangle((0, 1060, BW, BH), fill=(60, 56, 50))
    d.rectangle((500, 500, 2060, 900), fill=(50, 56, 54)); d.rectangle((480, 900, 2080, 940), fill=(110, 86, 60))
    for k in range(6):
        x = 560 + k * 250
        d.rectangle((x, 540, x + 200, 860), fill=(30, 34, 34), outline=(90, 96, 92), width=6)
        for j in range(3):
            d.ellipse((x + 30 + j * 55, 600, x + 70 + j * 55, 640), fill=(200, 190, 140))
        d.rectangle((x + 30, 700, x + 170, 760), fill=(40, 120, 70))
    d.rectangle((1200, 150, 1360, 300), fill=(230, 226, 210)); d.line([(1280, 225), (1280, 170)], fill=(30, 30, 30), width=6); d.line([(1280, 225), (1320, 240)], fill=(30, 30, 30), width=6)
    FLOOR["radio"] = 0.86
    return im


def bg_night_fireball():
    im = vgrad((14, 18, 34), (30, 40, 60)); d = ImageDraw.Draw(im)
    rng = random.Random(61)
    for _ in range(200):
        x, y = rng.uniform(0, BW), rng.uniform(0, 700); d.point((x, y), fill=(220, 220, 240))
    waves(im, 900, (14, 26, 44), (30, 46, 70), rows=8)
    lay = Image.new("L", (BW, BH), 0); ImageDraw.Draw(lay).ellipse((1500, 600, 1900, 1000), fill=255)
    lay = lay.filter(ImageFilter.GaussianBlur(60))
    im = Image.composite(Image.new("RGB", (BW, BH), (255, 160, 60)), im, lay)
    d = ImageDraw.Draw(im)
    d.polygon([(300, 980), (900, 960), (880, 1020), (320, 1030)], fill=(30, 30, 34)); d.rectangle((560, 880, 640, 965), fill=(30, 30, 34))
    return im


def bg_map_f19(stage=0):
    im = Image.new("RGB", (BW, BH), (70, 140, 180)); d = ImageDraw.Draw(im)
    land = (214, 196, 150)
    d.polygon([(200, 0), (700, 0), (760, 500), (720, 900), (640, 1200), (520, 1300), (420, 1100), (360, 700)], fill=land)  # Florida
    for k in range(10):  # Keys
        d.ellipse((420 - k * 40, 1300 + k * 8, 470 - k * 40, 1320 + k * 8), fill=land)
    for x, y, w in ((1200, 520, 160), (1350, 640, 120), (1500, 900, 220), (1700, 1100, 180), (1300, 1000, 90)):
        d.ellipse((x - w, y - w * 0.35, x + w, y + w * 0.35), fill=land)
    f = V.font(V.SANS_B, 50); fs = V.font(V.SANS, 38)
    d.text((300, 120), "Florida", font=f, fill=(60, 50, 40)); d.text((560, 380), "Fort Lauderdale", font=fs, fill=(30, 30, 30))
    d.ellipse((740, 440, 770, 470), fill=(200, 40, 40))
    d.text((1150, 400), "Grand Bahama", font=fs, fill=(30, 30, 30)); d.text((1500, 1000), "Bahamas", font=f, fill=(30, 30, 30))
    d.text((80, 1360), "Florida Keys", font=fs, fill=(30, 30, 30))
    if stage >= 1:
        d.line([(760, 455), (1150, 470), (1450, 470), (1250, 380), (760, 420)], fill=(255, 230, 120), width=8)
        d.text((900, 500), "Planned training route (approx.)", font=fs, fill=(255, 240, 180))
    if stage >= 2:
        d.ellipse((1350, 60, 1950, 380), outline=(255, 255, 255), width=8)
        d.text((1400, 200), "Last estimated area", font=f, fill=(255, 255, 255))
    d.text((60, BH - 70), "Schematic map, not to scale", font=fs, fill=(220, 230, 240))
    return im
