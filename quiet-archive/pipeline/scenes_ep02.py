"""Scenes for EP02 (Carroll A. Deering). Procedural art only."""
import math, random
from PIL import Image, ImageDraw, ImageFilter
import visuals as V
from visuals import W, H, PAPER, AMBER, GREY, INK, RED, BG


def schooner(im, x, base, s=1.0, color=(12, 13, 16), sails=True, tilt=0.0, sail_color=(205, 198, 182)):
    """Five-masted schooner silhouette, bow to the right."""
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    L = 1100 * s
    hull = [(x - L / 2, base - 40 * s), (x + L / 2 + 60 * s, base - 70 * s), (x + L / 2 - 20 * s, base + 30 * s),
            (x - L / 2 + 40 * s, base + 30 * s)]
    d.polygon(hull, fill=color + (255,))
    d.line((x + L / 2 + 50 * s, base - 70 * s, x + L / 2 + 260 * s, base - 150 * s), fill=color + (255,), width=int(8 * s))
    for i in range(5):
        mx = x - L / 2 + 140 * s + i * (L - 220 * s) / 4
        top = base - (520 - abs(i - 2) * 25) * s
        d.line((mx, base - 40 * s, mx, top), fill=color + (255,), width=int(9 * s))
        if sails:
            d.polygon([(mx + 6 * s, top + 20 * s), (mx + 6 * s, base - 70 * s), (mx + 170 * s, base - 70 * s),
                       (mx + 120 * s, top + 60 * s)], fill=sail_color + (235,))
            d.polygon([(mx + 6 * s, top + 20 * s), (mx + 120 * s, top + 60 * s), (mx + 6 * s, top - 40 * s)],
                      fill=tuple(int(c * 0.9) for c in sail_color) + (235,))
    if sails:
        d.polygon([(x + L / 2 + 40 * s, base - 80 * s), (x + L / 2 + 250 * s, base - 150 * s),
                   (x + L / 2 - 20 * s, base - 420 * s)], fill=sail_color + (220,))
    if tilt:
        lay = lay.rotate(tilt, center=(x, base), resample=Image.BICUBIC)
    im.paste(lay, (0, 0), lay)


def surf(im, y, seed=3, n=40):
    random.seed(seed)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        cx, cy = random.randint(0, W), y + random.randint(-30, 120)
        rw, rh = random.randint(80, 260), random.randint(10, 30)
        d.ellipse((cx - rw, cy - rh, cx + rw, cy + rh), fill=(230, 235, 240, 140))
    lay = lay.filter(ImageFilter.GaussianBlur(8))
    im.paste(lay, (0, 0), lay)


def sc_ghost_aground(dawn=False):
    if dawn:
        im = V.grad((52, 60, 80), (190, 150, 120))
        V.clouds(im, (130, 120, 130), seed=12, alpha=80)
    else:
        im = V.grad((44, 52, 66), (120, 126, 134))
        V.clouds(im, (150, 152, 160), seed=11, alpha=120)
    hz = int(H * 0.6)
    V.sea(im, hz, (60, 74, 90), (16, 22, 30), (150, 160, 170), seed=11, rough=2.5)
    schooner(im, W * 0.48, hz + 40, s=1.15, tilt=-4)
    surf(im, hz + 60)
    return V.vignette(V.grain(im, 8, 11))


def sc_title2():
    im = V.grad((20, 24, 32), (40, 46, 58))
    V.clouds(im, (60, 66, 80), seed=21, alpha=140)
    hz = int(H * 0.74)
    V.sea(im, hz, (30, 38, 50), (8, 10, 14), (90, 100, 118), seed=21)
    schooner(im, W * 0.72, hz + 20, s=0.75, color=(10, 11, 14), sail_color=(120, 122, 130))
    d = ImageDraw.Draw(im)
    V.center_text(d, H * 0.22, "THE CARROLL A. DEERING", V.font(V.SERIF_B, 140), PAPER)
    d.rectangle((W / 2 - 200, H * 0.22 + 180, W / 2 + 200, H * 0.22 + 186), fill=AMBER)
    V.center_text(d, H * 0.22 + 220, "January 1921", V.font(V.SERIF_I, 64), PAPER)
    return V.vignette(im)


def sc_schooner_sail():
    im = V.grad((96, 130, 170), (200, 210, 214))
    V.clouds(im, (235, 238, 240), seed=31, alpha=120)
    hz = int(H * 0.66)
    V.sea(im, hz, (60, 92, 120), (24, 40, 58), (150, 180, 200), seed=31, rough=1.2)
    schooner(im, W * 0.46, hz + 30, s=1.2, color=(26, 24, 22), sail_color=(236, 228, 210))
    return V.vignette(im, 0.35)


def _coast(d, pts, fill):
    d.polygon(pts, fill=fill, outline=INK)


def sc_route_map():
    im = V.paper(W, H, 41, tone=(226, 214, 190))
    d = ImageDraw.Draw(im)
    d.rectangle((60, 60, W - 60, H - 60), fill=(196, 202, 198))
    land = (214, 200, 168)
    # North America east coast (schematic)
    _coast(d, [(60, 60), (900, 60), (980, 200), (930, 330), (1010, 420), (880, 560), (760, 640), (700, 760), (560, 760),
               (420, 700), (60, 700)], land)
    # South America (schematic)
    _coast(d, [(1300, 960), (1700, 900), (2050, 980), (2200, 1150), (2150, H - 60), (1350, H - 60), (1250, 1120)], land)
    # Caribbean arc
    for (x, y, r) in [(1400, 820, 18), (1460, 840, 14), (1520, 860, 12), (1580, 880, 14)]:
        d.ellipse((x - r, y - r, x + r, y + r), fill=land, outline=INK, width=2)
    pts = {"Norfolk / Hampton Roads": (930, 360), "Lewes, Delaware": (960, 250), "Cape Lookout": (880, 520),
           "Cape Hatteras": (930, 450), "Barbados": (1640, 880), "Rio de Janeiro": (2080, 1240)}
    f = V.font(V.SERIF_B, 46)
    for name, (x, y) in pts.items():
        d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=RED)
        off = {"Cape Hatteras": (-330, -26), "Cape Lookout": (-320, 0), "Lewes, Delaware": (-400, -30),
               "Norfolk / Hampton Roads": (30, -26)}.get(name, (30, -20))
        d.text((x + off[0], y + off[1]), name, font=f, fill=INK)
    # outbound and return routes (dashed)
    def dash(a, b, col, w=6):
        n = int(math.dist(a, b) / 30)
        for i in range(0, n, 2):
            t0, t1 = i / n, min((i + 1) / n, 1)
            d.line((a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0, a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1), fill=col, width=w)
    dash((960, 380), (2060, 1210), INK)
    dash((2060, 1230), (1650, 900), AMBER, 8)
    dash((1630, 870), (950, 470), AMBER, 8)
    d.text((1200, 560), "Return, January 1921", font=V.font(V.SERIF_I, 52), fill=(140, 96, 20))
    d.text((1560, 1040), "Outbound with coal, 1920", font=V.font(V.SERIF_I, 48), fill=INK)
    d.text((W - 640, H - 130), "Schematic — not to scale", font=V.font(V.SERIF_I, 40), fill=GREY)
    return im


def sc_quote_card():
    bg, (ox, oy) = V.card(["“I'll get the captain before we get to Norfolk. I will.”"],
                          title="First mate Charles McLellan, Barbados", foot="As reported by witnesses to the later investigation",
                          w=1900, h=760, seed=51)
    return bg


def sc_lightship():
    im = V.grad((70, 78, 92), (150, 150, 150))
    V.clouds(im, (170, 170, 176), seed=61, alpha=90)
    hz = int(H * 0.62)
    V.sea(im, hz, (70, 82, 96), (20, 26, 34), (150, 160, 170), seed=61, rough=1.8)
    d = ImageDraw.Draw(im)
    # lightship hull with mast lantern
    x, y = W * 0.24, hz + 40
    d.polygon([(x - 260, y - 40), (x + 280, y - 50), (x + 240, y + 30), (x - 230, y + 30)], fill=(120, 30, 26))
    d.text((x - 150, y - 36), "CAPE LOOKOUT", font=V.font(V.SANS_B, 34), fill=(235, 228, 210))
    d.line((x, y - 40, x, y - 360), fill=(20, 20, 22), width=12)
    d.ellipse((x - 34, y - 400, x + 34, y - 330), fill=(250, 220, 140))
    schooner(im, W * 0.68, hz + 30, s=0.85, color=(18, 18, 20), sail_color=(200, 196, 186))
    # megaphone figure (anonymous)
    fx, fy = W * 0.6, hz - 10
    d.rectangle((fx - 8, fy - 70, fx + 8, fy), fill=(18, 18, 20))
    d.ellipse((fx - 14, fy - 100, fx + 14, fy - 72), fill=(160, 70, 40))
    d.polygon([(fx - 14, fy - 86), (fx - 70, fy - 110), (fx - 70, fy - 60)], fill=(18, 18, 20))
    return V.vignette(im, 0.45)


def sc_ship_night2():
    im, hz = V.night_base(71, horizon=0.62)
    V.clouds(im, (30, 34, 44), seed=72, alpha=160, ymax=0.6)
    schooner(im, W * 0.5, hz + 30, s=0.8, color=(8, 9, 12), sail_color=(46, 50, 60))
    return V.vignette(im)


def sc_shoals_map():
    im = V.paper(W, H, 81, tone=(226, 214, 190))
    d = ImageDraw.Draw(im)
    d.rectangle((60, 60, W - 60, H - 60), fill=(190, 200, 202))
    land = (214, 200, 168)
    # Outer Banks barrier island hooking at Cape Hatteras
    pts = [(300, 60), (360, 60), (900, 620), (1180, 760), (1150, 800), (860, 680), (300, 160)]
    d.polygon(pts, fill=land, outline=INK)
    pts2 = [(1150, 790), (1180, 760), (1300, 860), (1900, 1200), (1880, 1240), (1250, 900)]
    d.polygon(pts2, fill=land, outline=INK)
    # shoals: stippled bands extending SE from the cape
    random.seed(8)
    for i in range(2200):
        t = random.random()
        x = 1180 + t * 900 + random.gauss(0, 40)
        y = 760 - t * 120 + random.gauss(0, 50 * (1 - t * 0.5))
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(170, 140, 90))
    d.text((1250, 150), "DIAMOND SHOALS", font=V.font(V.SERIF_B, 70), fill=INK)
    d.text((1250, 240), "“Graveyard of the Atlantic”", font=V.font(V.SERIF_I, 52), fill=INK)
    d.line((1250, 320, 1500, 700), fill=INK, width=3)
    d.text((780, 840), "Cape Hatteras", font=V.font(V.SERIF_B, 52), fill=INK)
    d.ellipse((1160, 750, 1190, 780), fill=RED)
    # currents
    for k, (col, lab, y0) in enumerate([((190, 90, 60), "Gulf Stream (warm)", 1150), ((70, 110, 160), "Labrador Current (cold)", 300)]):
        pts = [(2400 - i * 40, y0 - k * 0 + math.sin(i / 3) * 20 - (i * 18 if k == 0 else -i * 14)) for i in range(30)]
        d.line(pts, fill=col, width=10)
        d.text((pts[0][0] - 520, pts[0][1] + (40 if k == 0 else -70)), lab, font=V.font(V.SANS_B, 40), fill=col)
    d.text((W - 640, H - 130), "Schematic — not to scale", font=V.font(V.SERIF_I, 40), fill=GREY)
    return im


def sc_boarding_list():
    bg, _ = V.card(["• Wheel smashed, compass stand broken, rudder loose",
                    "• Ship's log, navigation instruments, crew's belongings: gone",
                    "• Both lifeboats: gone",
                    "• Galley: food apparently prepared for the next day's meal"],
                   title="Boarding report · 4 February 1921", foot="Summary of the boarding party's findings", w=2000, h=980, seed=91)
    return bg


def sc_galley():
    im = V.grad((30, 26, 22), (52, 44, 36))
    d = ImageDraw.Draw(im)
    d.rectangle((0, H * 0.7, W, H), fill=(40, 32, 26))
    # iron stove
    sx, sy = W * 0.36, H * 0.42
    d.rectangle((sx - 320, sy, sx + 320, sy + 420), fill=(22, 22, 24))
    d.rectangle((sx - 340, sy - 20, sx + 340, sy + 10), fill=(34, 34, 36))
    d.rectangle((sx + 230, sy - 520, sx + 290, sy - 20), fill=(26, 26, 28))
    # pot and coffee pot
    d.rectangle((sx - 230, sy - 150, sx - 30, sy - 20), fill=(70, 70, 74))
    d.polygon([(sx + 60, sy - 20), (sx + 190, sy - 20), (sx + 165, sy - 190), (sx + 85, sy - 190)], fill=(90, 84, 70))
    # faint steam
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for i in range(10):
        ld.ellipse((sx - 160 + i * 6, sy - 220 - i * 50, sx - 80 + i * 6, sy - 170 - i * 50), fill=(220, 220, 220, 30))
    lay = lay.filter(ImageFilter.GaussianBlur(14))
    im.paste(lay, (0, 0), lay)
    # porthole light
    d.ellipse((W * 0.72, H * 0.2, W * 0.86, H * 0.45), fill=(150, 160, 170), outline=(120, 100, 70), width=24)
    d.text((W * 0.66, H * 0.78), "No one aboard", font=V.font(V.SERIF_I, 64), fill=(170, 156, 130))
    return V.vignette(im, 0.5)


def sc_explosion():
    im = V.grad((60, 66, 78), (140, 136, 130))
    hz = int(H * 0.62)
    V.sea(im, hz, (60, 70, 84), (20, 24, 30), (150, 160, 170), seed=101, rough=1.5)
    schooner(im, W * 0.5, hz + 40, s=0.9, sails=False, color=(20, 18, 16), tilt=-6)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    random.seed(4)
    for i in range(60):
        r = random.randint(60, 220)
        x, y = W * 0.5 + random.gauss(0, 180), hz - 150 + random.gauss(0, 120)
        c = random.choice([(250, 200, 120, 160), (240, 150, 70, 150), (90, 86, 84, 170)])
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    lay = lay.filter(ImageFilter.GaussianBlur(30))
    im.paste(lay, (0, 0), lay)
    return V.vignette(im)


def sc_bottle():
    im = V.grad((180, 166, 140), (120, 104, 84))
    d = ImageDraw.Draw(im)
    # sand texture lines
    random.seed(9)
    for _ in range(600):
        x, y = random.randint(0, W), random.randint(0, H)
        d.point((x, y), fill=(150, 134, 110))
    # bottle
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle((W * 0.18, H * 0.42, W * 0.52, H * 0.62), radius=120, fill=(60, 110, 80, 200))
    ld.rectangle((W * 0.52, H * 0.49, W * 0.62, H * 0.55), fill=(60, 110, 80, 200))
    ld.rectangle((W * 0.62, H * 0.485, W * 0.65, H * 0.555), fill=(120, 90, 60, 255))
    lay = lay.rotate(-8, center=(W * 0.4, H * 0.52), resample=Image.BICUBIC)
    im.paste(lay, (0, 0), lay)
    note = V.paper(820, 520, 12, tone=(236, 228, 206))
    nd = ImageDraw.Draw(note)
    V.text_block(nd, (50, 50), "“...captured by oil-burning boat... crew handcuffed... hiding...”", V.font(V.SERIF_I, 52), INK, 720)
    nd.text((50, 420), "Note reported found near Buxton, April 1921 (paraphrased)", font=V.font(V.SERIF, 28), fill=GREY)
    nl = note.convert("RGBA").rotate(6, expand=True, resample=Image.BICUBIC)
    im.paste(nl, (int(W * 0.6), int(H * 0.12)), nl)
    return V.vignette(im, 0.4)


def sc_stamp_hoax():
    im = sc_bottle()
    V.stamp(im, "HOAX — WRITER CONFESSED", (W * 0.5, H * 0.5), angle=-10, size=110)
    return im


def sc_investigation():
    bg, _ = V.card(["Commerce · Treasury · Justice · Navy · State",
                    "Also lost off the coast at about the same time: the sulfur steamer Hewitt, with all hands.",
                    "Inquiry closed late 1922 — no official finding."],
                   title="The federal inquiry, 1921–1922", foot="Commerce Secretary: Herbert Hoover", w=2000, h=900, seed=111)
    return bg


def sc_mutiny():
    im = V.grad((18, 20, 25), (30, 33, 40))
    d = ImageDraw.Draw(im)
    rows = [("Barbados", "Mate heard threatening to “get the captain”"),
            ("Barbados", "Mate says the captain cannot see well enough to navigate"),
            ("Cape Lookout", "Red-haired stranger speaks for the ship; crew on the quarterdeck"),
            ("Diamond Shoals", "Ship left with log, instruments, belongings and lifeboats taken")]
    y = 230
    d.text((240, 110), "THE CASE FOR MUTINY", font=V.font(V.SANS_B, 72), fill=AMBER)
    for place, txt in rows:
        d.ellipse((240, y + 18, 270, y + 48), fill=AMBER)
        d.text((310, y), place.upper(), font=V.font(V.SANS_B, 44), fill=GREY)
        d.text((310, y + 60), txt, font=V.font(V.SERIF, 60), fill=PAPER)
        y += 230
    d.line((255, 260, 255, y - 170), fill=AMBER, width=4)
    d.text((240, H - 330), "Consistent with mutiny — but none of it is proof.", font=V.font(V.SERIF_I, 56), fill=GREY)
    return V.vignette(im, 0.4)


def sc_verdict2():
    im = V.grad((18, 20, 25), (30, 33, 40))
    d = ImageDraw.Draw(im)
    cols = [("DOCUMENTED", AMBER, ["Mate threatened the captain in Barbados", "Red-haired man hailed Cape Lookout lightship",
                                   "Grounded on Diamond Shoals, sails set", "Log, instruments, lifeboats gone",
                                   "Bottle note was a confessed hoax", "Inquiry closed with no finding"]),
            ("LEGEND", (150, 156, 166), ["The exact meal left on the stove", "A cat that survived aboard",
                                          "Something supernatural off Hatteras"])]
    for i, (head, c, items) in enumerate(cols):
        x = 200 + i * 1260
        d.text((x, 180), head, font=V.font(V.SANS_B, 90), fill=c)
        d.rectangle((x, 300, x + 1040, 306), fill=c)
        y = 360
        for it in items:
            d.text((x, y), ("✓  " if i == 0 else "✕  ") + it, font=V.font(V.SERIF, 54), fill=PAPER if i == 0 else (150, 156, 166))
            y += 120
    return V.vignette(im, 0.4)


def sc_outro():
    im, hz = V.night_base(131, horizon=0.68)
    d = ImageDraw.Draw(im)
    V.center_text(d, H * 0.16, "THE QUIET ARCHIVE", V.font(V.SERIF_B, 110), PAPER)
    V.center_text(d, H * 0.16 + 150, "True stories history left unfinished", V.font(V.SERIF_I, 56), PAPER)
    return V.vignette(im)


def render(visual, cap):
    m = {
        "ghost_aground": lambda: sc_ghost_aground(False), "ghost_dawn": lambda: sc_ghost_aground(True),
        "title2": sc_title2, "schooner_sail": sc_schooner_sail, "route_map": sc_route_map,
        "quote_card": sc_quote_card, "lightship": sc_lightship, "ship_night2": sc_ship_night2,
        "shoals_map": sc_shoals_map, "boarding_list": sc_boarding_list, "galley": sc_galley,
        "explosion": sc_explosion, "bottle": sc_bottle, "stamp_hoax": sc_stamp_hoax,
        "investigation": sc_investigation, "mutiny": sc_mutiny, "verdict2": sc_verdict2, "outro": sc_outro,
        "theories2": lambda: V.sc_tiles([("Hurricane", "Storm forced them off"), ("Pirates", "Ship seized at sea"),
                                         ("Radicals", "Papers urged seizing ships"), ("Rum runners", "Prohibition smugglers"),
                                         ("Mutiny", "“A plain case of mutiny”")], "FIVE THEORIES, NO PROOF", AMBER),
    }
    im = m[visual]() if visual in m else V.render(visual, "")
    return V.caption(im, cap)
