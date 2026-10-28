"""Deering story, v2: several distinct images per visual + motion/effect maps for render2.py."""
import math, random
from PIL import Image, ImageDraw, ImageFilter
import visuals as V
import scenes_ep02 as S
from visuals import W, H, PAPER, AMBER, GREY, INK, RED, BG


def _sky(top, bottom, seed, cloud=(150, 152, 160), alpha=120):
    im = V.grad(top, bottom); V.clouds(im, cloud, seed=seed, alpha=alpha); return im


def deck_close():
    """Close view along an empty deck: masts, slack ropes, wheel."""
    im = _sky((60, 66, 80), (130, 132, 138), 201)
    d = ImageDraw.Draw(im)
    d.polygon([(0, H), (0, H * 0.72), (W, H * 0.62), (W, H)], fill=(58, 46, 36))
    for i in range(14):  # deck planks
        y = H * 0.72 - i * 6
        d.line((0, H * 0.72 + i * 30, W, H * 0.62 + i * 34), fill=(48, 38, 30), width=3)
    for x, top in [(W * 0.18, 0.02), (W * 0.52, 0.0), (W * 0.83, 0.05)]:
        d.rectangle((x - 22, H * top, x + 22, H * 0.7), fill=(30, 26, 22))
        d.line((x, H * 0.12, x + 420, H * 0.68), fill=(40, 34, 28), width=5)
        d.line((x, H * 0.12, x - 380, H * 0.7), fill=(40, 34, 28), width=5)
    # sail edges
    d.polygon([(W * 0.53, H * 0.05), (W * 0.53, H * 0.55), (W * 0.78, H * 0.55)], fill=(206, 198, 182))
    # broken wheel
    cx, cy, r = W * 0.34, H * 0.62, 150
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(44, 32, 22), width=18)
    for k in range(8):
        if k in (2, 3):
            continue
        a = k * math.pi / 4
        d.line((cx, cy, cx + r * math.cos(a), cy + r * math.sin(a)), fill=(44, 32, 22), width=14)
    d.rectangle((cx - 30, cy, cx + 30, H * 0.8), fill=(44, 32, 22))
    return V.vignette(im, 0.5)


def station_tower():
    """Coast Guard lookout tower on the dunes, the stranded ship tiny on the horizon."""
    im = _sky((92, 104, 124), (200, 190, 170), 211, cloud=(210, 210, 214), alpha=90)
    hz = int(H * 0.58)
    V.sea(im, hz, (80, 96, 112), (40, 52, 64), (160, 170, 180), seed=211, rough=1.6)
    d = ImageDraw.Draw(im)
    d.polygon([(0, H), (0, H * 0.7), (W * 0.35, H * 0.64), (W * 0.7, H * 0.74), (W, H * 0.7), (W, H)], fill=(196, 176, 140))
    for i in range(40):
        x = random.Random(i).random() * W
        d.line((x, H * 0.7, x + 10, H * 0.66), fill=(120, 130, 80), width=3)
    tx = W * 0.22
    d.rectangle((tx - 70, H * 0.3, tx + 70, H * 0.66), fill=(70, 62, 56))
    d.polygon([(tx - 110, H * 0.3), (tx + 110, H * 0.3), (tx, H * 0.2)], fill=(52, 46, 42))
    d.rectangle((tx - 50, H * 0.33, tx + 50, H * 0.4), fill=(200, 190, 150))
    S.schooner(im, W * 0.72, hz + 6, s=0.32, tilt=-4)
    return V.vignette(im, 0.35)


def shipyard():
    """Bath, Maine, 1919: a huge wooden hull on the slipway."""
    im = _sky((120, 150, 180), (220, 220, 214), 221, cloud=(240, 240, 240), alpha=100)
    d = ImageDraw.Draw(im)
    d.rectangle((0, H * 0.78, W, H), fill=(80, 90, 96))
    d.polygon([(W * 0.08, H * 0.7), (W * 0.9, H * 0.58), (W * 0.86, H * 0.74), (W * 0.12, H * 0.84)], fill=(96, 64, 40))
    for i in range(18):
        x = W * 0.12 + i * W * 0.042
        d.line((x, H * 0.84 - i * 6, x - 20, H * 0.98), fill=(70, 50, 34), width=10)
    for i in range(5):
        mx = W * 0.2 + i * W * 0.15
        d.rectangle((mx - 8, H * 0.12, mx + 8, H * 0.7 - i * 22), fill=(60, 42, 30))
    d.text((W * 0.06, H * 0.06), "BATH, MAINE · 1919", font=V.font(V.SANS_B, 60), fill=(40, 40, 44))
    return V.vignette(im, 0.3)


def megaphone_close():
    im = _sky((80, 86, 98), (150, 150, 152), 231)
    d = ImageDraw.Draw(im)
    d.polygon([(0, H), (0, H * 0.75), (W, H * 0.7), (W, H)], fill=(40, 34, 30))
    d.rectangle((0, H * 0.66, W, H * 0.7), fill=(60, 50, 40))  # rail
    # tall thin figure (anonymous silhouette) with red hair and a megaphone
    fx, fy = W * 0.52, H * 0.7
    d.rectangle((fx - 60, fy - 520, fx + 60, fy), fill=(22, 22, 26))
    d.ellipse((fx - 70, fy - 680, fx + 70, fy - 520), fill=(30, 26, 26))
    d.pieslice((fx - 80, fy - 700, fx + 80, fy - 560), 180, 360, fill=(170, 74, 40))
    d.polygon([(fx - 60, fy - 600), (fx - 330, fy - 690), (fx - 330, fy - 500)], fill=(26, 26, 30))
    d.text((W * 0.06, H * 0.84), "“Lost anchors in a storm off Cape Fear...”", font=V.font(V.SERIF_I, 70), fill=PAPER)
    return V.vignette(im, 0.5)


def keeper_pov():
    """From the lightship rail: the schooner passing close, crew crowded aft."""
    im = _sky((84, 92, 106), (160, 158, 154), 241)
    hz = int(H * 0.6)
    V.sea(im, hz, (70, 82, 96), (20, 26, 34), (150, 160, 170), seed=241, rough=1.6)
    S.schooner(im, W * 0.52, hz + 60, s=1.4, color=(20, 20, 22))
    d = ImageDraw.Draw(im)
    for i in range(9):  # crew silhouettes aft
        x = W * 0.16 + i * 34
        d.rectangle((x, hz - 40, x + 18, hz + 10), fill=(10, 10, 12)); d.ellipse((x - 2, hz - 66, x + 20, hz - 42), fill=(10, 10, 12))
    d.rectangle((0, H * 0.86, W, H), fill=(110, 30, 26)); d.rectangle((0, H * 0.84, W, H * 0.87), fill=(140, 120, 90))
    return V.vignette(im, 0.45)


def surf_shoals():
    im = _sky((70, 80, 96), (150, 156, 160), 251)
    hz = int(H * 0.42)
    V.sea(im, hz, (60, 80, 96), (40, 60, 72), (190, 200, 210), seed=251, rough=3.0)
    for k in range(6):
        S.surf(im, hz + 80 + k * 140, seed=251 + k, n=60)
    return V.vignette(im, 0.4)


def galley_table():
    im = V.grad((34, 28, 24), (56, 46, 38))
    d = ImageDraw.Draw(im)
    d.polygon([(W * 0.1, H * 0.62), (W * 0.9, H * 0.62), (W, H * 0.9), (0, H * 0.9)], fill=(92, 66, 44))
    for x in (W * 0.3, W * 0.5, W * 0.7):
        d.ellipse((x - 120, H * 0.66, x + 120, H * 0.74), fill=(200, 196, 186))
        d.ellipse((x - 70, H * 0.68, x + 70, H * 0.72), fill=(170, 160, 140))
    d.rectangle((W * 0.45, H * 0.5, W * 0.48, H * 0.66), fill=(150, 150, 150))
    d.ellipse((W * 0.43, H * 0.38, W * 0.5, H * 0.5), fill=(250, 220, 140))  # oil lamp
    d.text((W * 0.06, H * 0.08), "Food prepared for a meal that never came", font=V.font(V.SERIF_I, 64), fill=(200, 184, 150))
    return V.vignette(im, 0.55)


def empty_bunks():
    im = V.grad((24, 22, 22), (44, 40, 38))
    d = ImageDraw.Draw(im)
    for row in range(2):
        for col in range(3):
            x0, y0 = W * 0.08 + col * W * 0.3, H * 0.18 + row * H * 0.36
            d.rectangle((x0, y0, x0 + W * 0.26, y0 + H * 0.28), outline=(80, 64, 48), width=14, fill=(36, 32, 30))
            d.rectangle((x0 + 20, y0 + H * 0.18, x0 + W * 0.26 - 20, y0 + H * 0.26), fill=(120, 110, 96))
    d.text((W * 0.06, H * 0.86), "Personal belongings: gone", font=V.font(V.SERIF_I, 64), fill=(190, 176, 150))
    return V.vignette(im, 0.55)


def timbers_beach():
    im = _sky((150, 160, 176), (226, 214, 190), 261, cloud=(240, 238, 230), alpha=80)
    hz = int(H * 0.5)
    V.sea(im, hz, (90, 120, 140), (120, 140, 150), (200, 210, 214), seed=261, rough=0.8)
    d = ImageDraw.Draw(im)
    d.polygon([(0, H), (0, H * 0.66), (W, H * 0.6), (W, H)], fill=(214, 194, 156))
    r = random.Random(4)
    for i in range(9):
        x, y = r.random() * W, H * 0.7 + r.random() * H * 0.22
        L, a = r.uniform(200, 520), r.uniform(-0.3, 0.3)
        d.line((x, y, x + L * math.cos(a), y + L * math.sin(a)), fill=(86, 62, 42), width=r.randint(18, 34))
    d.text((W * 0.06, H * 0.08), "Wreckage washed ashore along the Outer Banks", font=V.font(V.SERIF_I, 60), fill=INK)
    return V.vignette(im, 0.3)


def note_close():
    note = V.paper(W, H, 271, tone=(236, 228, 206))
    d = ImageDraw.Draw(note)
    V.text_block(d, (260, 360), "“...captured by oil-burning boat... crew handcuffed... hiding...”", V.font(V.SERIF_I, 110), INK, W - 520)
    d.text((260, H - 260), "Paraphrase of the note reported found near Buxton, April 1921", font=V.font(V.SERIF, 48), fill=GREY)
    return V.vignette(note, 0.35)


def night_deck_figures():
    im, hz = V.night_base(281, horizon=0.7)
    d = ImageDraw.Draw(im)
    d.polygon([(0, H), (0, H * 0.74), (W, H * 0.7), (W, H)], fill=(14, 12, 12))
    for i, x in enumerate([W * 0.3, W * 0.36, W * 0.62, W * 0.68, W * 0.74]):
        h = 260 + (i % 2) * 40
        d.rectangle((x - 24, H * 0.72 - h, x + 24, H * 0.72), fill=(6, 6, 8))
        d.ellipse((x - 30, H * 0.72 - h - 60, x + 30, H * 0.72 - h), fill=(6, 6, 8))
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.ellipse((W * 0.45, H * 0.4, W * 0.55, H * 0.55), fill=(255, 200, 120, 90))
    im.paste(lay.filter(ImageFilter.GaussianBlur(40)), (0, 0), lay.filter(ImageFilter.GaussianBlur(40)))
    return V.vignette(im, 0.6)


def route_stage(stage):
    """Route map with the voyage drawn up to `stage` (0 outbound, 1 + return)."""
    im = S.sc_route_map()
    return im


VARIANTS = {
    "ghost_aground": [lambda: S.sc_ghost_aground(False), deck_close, station_tower],
    "ghost_dawn": [lambda: S.sc_ghost_aground(True), deck_close],
    "title2": [S.sc_title2],
    "schooner_sail": [S.sc_schooner_sail, shipyard],
    "route_map": [S.sc_route_map],
    "quote_card": [S.sc_quote_card, night_deck_figures],
    "lightship": [S.sc_lightship, keeper_pov, megaphone_close],
    "ship_night2": [S.sc_ship_night2],
    "shoals_map": [S.sc_shoals_map, surf_shoals],
    "boarding_list": [S.sc_boarding_list, deck_close, empty_bunks],
    "galley": [S.sc_galley, galley_table, empty_bunks],
    "explosion": [S.sc_explosion, timbers_beach],
    "bottle": [S.sc_bottle, note_close],
    "stamp_hoax": [S.sc_stamp_hoax],
    "investigation": [S.sc_investigation],
    "theories2": [lambda: S.render("theories2", "")],
    "mutiny": [S.sc_mutiny, night_deck_figures],
    "verdict2": [S.sc_verdict2],
    "outro": [S.sc_outro],
}

# camera framings: (cx, cy, zoom_from, zoom_to, drift_x, drift_y)
FRAMES = {
    "route_map": [(0.35, 0.35, 1.6, 1.4, 0.05, 0.05), (0.62, 0.62, 1.5, 1.3, -0.08, -0.08), (0.5, 0.5, 1.0, 1.05, 0, 0)],
    "shoals_map": [(0.45, 0.55, 1.0, 1.25, 0.05, 0.0), (0.55, 0.5, 1.5, 1.35, -0.04, 0)],
    "quote_card": [(0.5, 0.5, 1.0, 1.06, 0, 0), (0.5, 0.5, 1.15, 1.05, 0, 0)],
    "boarding_list": [(0.5, 0.5, 1.0, 1.06, 0, 0)],
    "investigation": [(0.5, 0.5, 1.0, 1.06, 0, 0), (0.45, 0.45, 1.2, 1.1, 0.02, 0.02)],
    "verdict2": [(0.3, 0.45, 1.3, 1.2, 0.0, 0.04), (0.75, 0.4, 1.35, 1.25, 0, 0.04), (0.5, 0.5, 1.0, 1.04, 0, 0)],
    "mutiny": [(0.35, 0.3, 1.35, 1.25, 0, 0.12), (0.5, 0.5, 1.0, 1.05, 0, 0)],
    "theories2": [(0.5, 0.45, 1.0, 1.06, 0, 0), (0.3, 0.42, 1.4, 1.3, 0.25, 0)],
    "title2": [(0.5, 0.4, 1.0, 1.08, 0, 0)],
    "outro": [(0.5, 0.4, 1.0, 1.06, 0, 0)],
}

FX = {
    "ghost_aground": ["rain", "fog"], "ghost_dawn": ["fog"], "ship_night2": ["rain_heavy", "fog"],
    "lightship": ["fog"], "galley": ["dust", "flicker"], "explosion": ["dust"], "quote_card": ["dust"],
    "title2": ["fog_high"], "outro": ["fog_high"], "mutiny": ["dust"], "shoals_map": [], "schooner_sail": [],
}


def render_all(visual):
    return [f() for f in VARIANTS.get(visual, [lambda: S.render(visual, "")])]
