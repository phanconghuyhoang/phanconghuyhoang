"""Flannan Isles story, v2: several distinct images per visual + motion/effect maps for render2.py."""
import math, random
from PIL import Image, ImageDraw, ImageFilter
import visuals as V
from visuals import W, H, PAPER, AMBER, GREY, INK, RED, BG


def cliffs_close(seed=301, night=True):
    im = V.grad((12, 15, 24), (34, 40, 54)) if night else V.grad((70, 80, 96), (150, 154, 160))
    if night:
        V.stars(im, seed=seed, n=160, maxy=0.35)
    V.clouds(im, (40, 46, 60) if night else (170, 172, 178), seed=seed, alpha=130)
    hz = int(H * 0.7)
    V.sea(im, hz, (24, 30, 44) if night else (70, 84, 100), (8, 10, 14), (90, 104, 124), seed=seed, rough=3)
    d = ImageDraw.Draw(im)
    pts = [(W * 0.25, H), (W * 0.28, H * 0.5), (W * 0.34, H * 0.36), (W * 0.46, H * 0.3), (W * 0.62, H * 0.28),
           (W * 0.72, H * 0.4), (W * 0.8, H * 0.62), (W * 0.84, H)]
    d.polygon(pts, fill=(10, 11, 14))
    for k in range(5):  # surf at the foot of the cliff
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        r = random.Random(seed + k)
        for _ in range(30):
            x = r.uniform(W * 0.2, W * 0.9); y = H * 0.74 + r.uniform(-20, 80)
            ld.ellipse((x - 120, y - 18, x + 120, y + 18), fill=(220, 228, 236, 90))
        im.paste(lay.filter(ImageFilter.GaussianBlur(10)), (0, 0), lay.filter(ImageFilter.GaussianBlur(10)))
    V.lighthouse(im, W * 0.55, H * 0.29, h=170, lit=False)
    return V.vignette(im, 0.6)


def lantern_room_dark():
    im = V.grad((14, 16, 22), (30, 32, 40))
    d = ImageDraw.Draw(im)
    for i in range(7):  # window mullions
        x = W * 0.1 + i * W * 0.13
        d.rectangle((x, H * 0.1, x + 18, H * 0.7), fill=(40, 42, 48))
    d.rectangle((0, H * 0.1, W, H * 0.13), fill=(40, 42, 48)); d.rectangle((0, H * 0.68, W, H * 0.72), fill=(40, 42, 48))
    # big Fresnel lens, unlit
    cx, cy = W * 0.5, H * 0.45
    for k in range(9):
        r = 380 - k * 36
        d.ellipse((cx - r * 0.7, cy - r, cx + r * 0.7, cy + r), outline=(90, 100, 110), width=6)
    d.rectangle((cx - 60, H * 0.72, cx + 60, H), fill=(50, 48, 46))
    V.stars(im, seed=33, n=60, maxy=0.12)
    d.text((W * 0.06, H * 0.84), "The lamp was cleaned and filled. Nobody lit it.", font=V.font(V.SERIF_I, 60), fill=(180, 170, 150))
    return V.vignette(im, 0.55)


def harbour_wait():
    im = V.grad((40, 44, 52), (90, 92, 98))
    V.clouds(im, (110, 112, 120), seed=311, n=24, alpha=150, ymax=0.7)
    hz = int(H * 0.62)
    V.sea(im, hz, (50, 58, 70), (14, 16, 20), (140, 150, 160), seed=311, rough=2.5)
    d = ImageDraw.Draw(im)
    d.rectangle((0, hz - 10, W * 0.55, hz + 60), fill=(30, 28, 26))  # pier
    for i in range(10):
        d.rectangle((i * W * 0.055, hz + 40, i * W * 0.055 + 30, H), fill=(26, 24, 22))
    V.ship(im, W * 0.72, hz + 50, s=1.0, light=True)
    d.text((W * 0.06, H * 0.08), "Breasclete, Lewis · waiting for a gap in the weather", font=V.font(V.SERIF_I, 56), fill=PAPER)
    return V.vignette(im, 0.5)


def steps_up():
    im = V.grad((60, 66, 78), (120, 124, 130))
    V.clouds(im, (150, 152, 158), seed=321, alpha=110)
    d = ImageDraw.Draw(im)
    d.polygon([(0, H), (0, H * 0.2), (W * 0.6, H * 0.05), (W, H * 0.1), (W, H)], fill=(36, 34, 32))
    for i in range(26):  # steep stair cut into the cliff, perspective
        y = H - i * 46
        w = 900 - i * 26
        d.rectangle((W * 0.5 - w / 2, y - 22, W * 0.5 + w / 2, y), fill=(98, 92, 84))
        d.rectangle((W * 0.5 - w / 2, y, W * 0.5 + w / 2, y + 24), fill=(64, 60, 56))
    d.line((W * 0.5 - 470, H, W * 0.5 - 120, H * 0.0), fill=(30, 30, 32), width=10)
    d.line((W * 0.5 + 470, H, W * 0.5 + 120, H * 0.0), fill=(30, 30, 32), width=10)
    V.lighthouse(im, W * 0.5, H * 0.06, h=120, lit=False)
    return V.vignette(im, 0.5)


def kitchen_clean():
    im = V.grad((36, 32, 28), (60, 52, 44))
    d = ImageDraw.Draw(im)
    d.polygon([(W * 0.12, H * 0.6), (W * 0.88, H * 0.6), (W, H * 0.92), (0, H * 0.92)], fill=(110, 82, 56))
    d.rectangle((W * 0.08, H * 0.18, W * 0.3, H * 0.6), fill=(28, 26, 26))  # range
    d.rectangle((W * 0.12, H * 0.42, W * 0.26, H * 0.56), fill=(16, 16, 16))
    for i, x in enumerate((W * 0.42, W * 0.58, W * 0.74)):
        d.ellipse((x - 90, H * 0.66, x + 90, H * 0.72), fill=(214, 210, 200))
    cx, cy, r = W * 0.82, H * 0.24, 110  # clock stopped
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(220, 208, 182), outline=(90, 70, 50), width=10)
    d.line((cx, cy, cx + 50, cy - 40), fill=INK, width=8); d.line((cx, cy, cx - 10, cy - 80), fill=INK, width=5)
    d.text((W * 0.06, H * 0.84), "The kitchen was clean. The clock had stopped.", font=V.font(V.SERIF_I, 60), fill=(200, 184, 150))
    return V.vignette(im, 0.55)


def railings_bent():
    im = V.grad((70, 76, 86), (130, 132, 136))
    V.clouds(im, (160, 162, 168), seed=331, alpha=100)
    hz = int(H * 0.68)
    V.sea(im, hz, (60, 74, 88), (20, 26, 34), (170, 180, 190), seed=331, rough=3)
    d = ImageDraw.Draw(im)
    d.polygon([(0, H), (0, H * 0.55), (W * 0.7, H * 0.45), (W, H * 0.5), (W, H)], fill=(40, 38, 36))
    for i in range(9):  # railing posts, several bent over
        x = W * 0.08 + i * W * 0.1
        bend = (0.0 if i % 3 else 0.6) + (0.3 if i in (4, 5) else 0)
        x2 = x + 220 * bend; y2 = H * 0.3 + 160 * bend
        d.line((x, H * 0.55 - i * 9, x2, y2 - i * 9), fill=(90, 70, 50), width=16)
    d.line((W * 0.08, H * 0.32, W * 0.36, H * 0.29), fill=(90, 70, 50), width=12)
    d.ellipse((W * 0.58, H * 0.5, W * 0.76, H * 0.66), fill=(70, 66, 62))  # the moved boulder
    d.text((W * 0.06, H * 0.86), "Iron railings bent. A boulder of more than a ton moved.", font=V.font(V.SERIF_I, 58), fill=PAPER)
    return V.vignette(im, 0.45)


def wave_sea():
    im = V.grad((40, 46, 58), (100, 106, 116))
    V.clouds(im, (90, 96, 108), seed=341, n=26, alpha=170, ymax=0.6)
    hz = int(H * 0.72)
    V.sea(im, hz, (40, 54, 70), (10, 14, 20), (160, 170, 180), seed=341, rough=4)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    pts = [(0, H)] + [(x, hz - 520 * math.exp(-((x - W * 0.6) / (W * 0.25)) ** 2) - 30 * math.sin(x / 90)) for x in range(0, W + 40, 40)] + [(W, H)]
    d.polygon(pts, fill=(60, 84, 104, 255))
    for x in range(int(W * 0.35), int(W * 0.85), 30):
        y = hz - 520 * math.exp(-((x - W * 0.6) / (W * 0.25)) ** 2)
        d.ellipse((x - 40, y - 30, x + 40, y + 20), fill=(230, 236, 240, 160))
    im.paste(lay.filter(ImageFilter.GaussianBlur(3)), (0, 0), lay)
    d2 = ImageDraw.Draw(im)
    d2.polygon([(W * 0.84, H), (W * 0.86, H * 0.5), (W, H * 0.42), (W, H)], fill=(14, 14, 16))
    return V.vignette(im, 0.5)


def empty_rocks():
    im = V.grad((96, 110, 128), (190, 190, 184))
    V.clouds(im, (210, 210, 214), seed=351, alpha=80)
    hz = int(H * 0.58)
    V.sea(im, hz, (80, 96, 112), (30, 40, 52), (170, 180, 190), seed=351, rough=1.0)
    d = ImageDraw.Draw(im)
    r = random.Random(5)
    for i in range(7):
        x = r.uniform(0, W); y = r.uniform(H * 0.66, H * 0.9); w = r.uniform(200, 520)
        d.polygon([(x, y), (x + w * 0.3, y - w * 0.4), (x + w, y - w * 0.15), (x + w * 1.1, y + 40), (x - 40, y + 40)], fill=(30, 30, 34))
    return V.vignette(im, 0.35)


def table_myth():
    im = V.grad((30, 26, 24), (50, 44, 40))
    d = ImageDraw.Draw(im)
    d.polygon([(W * 0.15, H * 0.55), (W * 0.85, H * 0.55), (W * 0.95, H * 0.85), (W * 0.05, H * 0.85)], fill=(110, 82, 56))
    for x in (W * 0.35, W * 0.5, W * 0.65):
        d.ellipse((x - 100, H * 0.6, x + 100, H * 0.68), fill=(214, 210, 200)); d.ellipse((x - 50, H * 0.62, x + 50, H * 0.66), fill=(150, 110, 70))
    d.polygon([(W * 0.8, H * 0.62), (W * 0.9, H * 0.5), (W * 0.93, H * 0.52), (W * 0.84, H * 0.66)], fill=(70, 50, 34))  # chair on its side
    V.stamp(im, "NOT IN THE REPORT", (W * 0.5, H * 0.3), angle=-6, size=110)
    return V.vignette(im, 0.5)


def dawn_automatic():
    im = V.grad((96, 120, 150), (230, 200, 160))
    V.clouds(im, (240, 220, 200), seed=361, alpha=80)
    hz = int(H * 0.64)
    V.sea(im, hz, (110, 130, 150), (50, 64, 80), (200, 200, 200), seed=361, rough=0.7)
    V.island(im, hz + 8, W * 0.3, W * 0.85, 240, color=(30, 30, 34), seed=361)
    V.lighthouse(im, W * 0.6, hz + 8 - 232, h=300, lit=True, color=(34, 34, 38))
    d = ImageDraw.Draw(im)
    d.text((W * 0.06, H * 0.08), "Automated in 1971. No keepers since.", font=V.font(V.SERIF_I, 60), fill=(40, 40, 46))
    return V.vignette(im, 0.3)


VARIANTS = {
    "lighthouse_night": [lambda: V.sc_lighthouse(lit=False), cliffs_close, lantern_room_dark],
    "title": [lambda: V.sc_title("THE FLANNAN ISLES", "December 1900")],
    "map": [V.sc_map, lambda: cliffs_close(302, night=False)],
    "construction": [V.sc_construction, steps_up],
    "keepers": [V.sc_keepers, lantern_room_dark],
    "ship_night": [V.sc_ship_night, lambda: cliffs_close(303)],
    "storm": [V.sc_storm, harbour_wait],
    "landing_east": [lambda: V.sc_landing(True), steps_up],
    "doorway": [V.sc_doorway, kitchen_clean, lantern_room_dark],
    "telegram": [V.sc_telegram, harbour_wait],
    "investigator": [V.sc_investigator, steps_up],
    "landing_west": [lambda: V.sc_cliff_diagram(False), railings_bent],
    "wave": [lambda: V.sc_cliff_diagram(True), wave_sea, railings_bent],
    "sea_calm": [V.sc_sea_calm, empty_rocks],
    "legend": [lambda: V.sc_fog_text("Where the legend begins")],
    "logbook": [V.sc_logbook],
    "poem": [V.sc_poem, table_myth],
    "theories": [lambda: V.render("theories", "")],
    "theories_real": [lambda: V.render("theories_real", ""), wave_sea],
    "verdict": [V.sc_verdict],
    "lighthouse_dawn": [lambda: V.sc_lighthouse(lit=True, dawn=True, seed=2), dawn_automatic, empty_rocks],
}

FRAMES = {
    "map": [(0.3, 0.35, 1.5, 1.3, 0.1, 0.03), (0.5, 0.5, 1.0, 1.06, 0, 0)],
    "keepers": [(0.25, 0.45, 1.6, 1.5, 0.0, 0.0), (0.53, 0.47, 1.6, 1.5, 0, 0), (0.8, 0.45, 1.6, 1.5, 0, 0), (0.5, 0.5, 1.0, 1.05, 0, 0)],
    "telegram": [(0.5, 0.5, 1.0, 1.06, 0, 0)], "investigator": [(0.5, 0.5, 1.0, 1.06, 0, 0)],
    "logbook": [(0.5, 0.45, 1.0, 1.08, 0, 0), (0.62, 0.62, 1.4, 1.3, 0, 0)],
    "landing_west": [(0.5, 0.5, 1.0, 1.06, 0, 0), (0.45, 0.35, 1.5, 1.4, 0, 0.05)],
    "wave": [(0.5, 0.5, 1.0, 1.06, 0, 0), (0.3, 0.5, 1.3, 1.2, 0.05, 0)],
    "verdict": [(0.3, 0.45, 1.3, 1.2, 0.0, 0.04), (0.75, 0.4, 1.35, 1.25, 0, 0.04), (0.5, 0.5, 1.0, 1.04, 0, 0)],
    "theories": [(0.5, 0.45, 1.0, 1.06, 0, 0), (0.3, 0.42, 1.4, 1.3, 0.25, 0)],
    "theories_real": [(0.5, 0.45, 1.0, 1.06, 0, 0)], "poem": [(0.5, 0.5, 1.0, 1.06, 0, 0)],
    "title": [(0.5, 0.4, 1.0, 1.08, 0, 0)], "legend": [(0.5, 0.45, 1.0, 1.1, 0, 0)],
}

FX = {
    "lighthouse_night": ["fog"], "ship_night": ["rain", "fog"], "storm": ["rain_heavy"], "landing_east": ["fog"],
    "doorway": ["dust", "flicker"], "wave": [], "sea_calm": ["fog"], "legend": ["fog", "fog_high"], "title": ["fog_high"],
    "telegram": ["dust"], "logbook": ["dust"], "poem": ["dust"], "lighthouse_dawn": ["fog"], "construction": [],
}


def render_all(visual):
    return [f() for f in VARIANTS.get(visual, [lambda: V.render(visual, "")])]
