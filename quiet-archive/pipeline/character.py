"""Stick-figure character rig for The Quiet Archive.

Archie, the archive keeper, is the channel's host: a round-glasses stick figure with an amber scarf and a
three-hair tuft. The same rig draws the story characters (captains, sailors, keepers), using different props.

Drawing is done on an RGBA layer at 2x and downsampled, so lines stay smooth while the figure moves.

Pose = dict of joint angles in degrees. Angle 0 points straight down; positive turns towards screen right
(counter-clockwise on screen). Limb angles are absolute (not relative to the parent) for simple authoring.
"""
import math, random
from PIL import Image, ImageDraw

PAPER = (238, 232, 218)
INK = (22, 22, 26)
AMBER = (226, 160, 60)
RED = (196, 72, 56)

# head radius = 1 unit
L = dict(torso=1.8, neck=0.3, uarm=1.05, farm=1.0, thigh=1.15, shin=1.15)

POSES = {
    #            torso head  lua  lfa   rua  rfa  lth  lsh  rth  rsh
    "idle":      (0,    0,   -22, -12,  22,  12,  -10, -6,  10,  6),
    "talk1":     (2,    4,   -20, -60,  14,   8,  -10, -6,  10,  6),
    "talk2":     (-2,  -4,   -14, -8,   24,   70, -10, -6,  10,  6),
    "talk3":     (0,    2,   -35, -95,  35,   95, -10, -6,  10,  6),
    "point_r":   (4,    8,   -14, -8,   95,   100, -10, -6, 12,  8),
    "point_l":   (-4,  -8,   -95, -100, 14,   8,  -12, -8,  10,  6),
    "point_up":  (0,   10,   -14, -8,   150,  170, -10, -6, 10,  6),
    "shrug":     (0,  -10,   -60, -150, 60,   150, -10, -6, 10,  6),
    "facepalm":  (6,   18,   -14, -8,   150,  200, -10, -6, 10,  6),
    "scared":    (-6, -10,   -140,-170, 140,  170, -22, -10, 22, 10),
    "think":     (2,   12,   -14, -8,   70,   200, -10, -6, 10,  6),
    "lean_in":   (14,  14,   -30, -10,  40,   20,  -6,  -14, 16, 4),
    "arms_wide": (0,    0,   -100,-110, 100,  110, -14, -8, 14,  8),
    "jump":      (0,    0,   -150,-160, 150,  160, -40, 10, 40, -10),
    "hands_hips":(0,    0,   -45, 20,   45,  -20,  -14, -8, 14,  8),
    "wave":      (0,    6,   -14, -8,   120,  175, -10, -6, 10,  6),
    "sit":       (0,    0,   -30, 20,   30,  -20,  80,  0,  85,  0),
    "walk_a":    (4,    0,   20,  10,  -20,  -30,  25,  5, -25, -40),
    "walk_b":    (4,    0,  -20, -30,   20,   10, -25, -40, 25,  5),
    "lie":       (90,  90,   80,  80,   100, 100,  85, 85,  95, 95),
}
KEYS = ("torso", "head", "lua", "lfa", "rua", "rfa", "lth", "lsh", "rth", "rsh")

EXPR = ("neutral", "smug", "shocked", "scared", "deadpan", "laugh", "sad", "suspicious", "angry", "wink")


def pose(name):
    return dict(zip(KEYS, POSES[name]))


def lerp_pose(a, b, u):
    return {k: a[k] + (b[k] - a[k]) * u for k in KEYS}


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def vec(a, l):
    r = math.radians(a)
    return math.sin(r) * l, math.cos(r) * l


class Look:
    """Visual identity: props and colours."""
    def __init__(self, kind="archie", body=PAPER, accent=AMBER, seed=0):
        self.kind, self.body, self.accent, self.seed = kind, body, accent, seed


def draw_figure(layer, x, y, s, p, expr="neutral", mouth=0.0, blink=0.0, look=None, facing=1, alpha=255):
    """Draw onto RGBA `layer` (already supersampled). (x, y) = hip position in px, s = head radius in px."""
    look = look or Look()
    d = ImageDraw.Draw(layer)
    lw = max(2, int(s * 0.30))
    col = look.body + (alpha,)
    ink = INK + (alpha,)
    out = max(1, int(lw * 0.45))

    def seg(p0, p1, w=lw, c=col):
        d.line([p0, p1], fill=ink, width=w + out * 2)
        for q in (p0, p1):
            rr = (w + out * 2) / 2
            d.ellipse((q[0] - rr, q[1] - rr, q[0] + rr, q[1] + rr), fill=ink)
        d.line([p0, p1], fill=c, width=w)
        for q in (p0, p1):
            rr = w / 2
            d.ellipse((q[0] - rr, q[1] - rr, q[0] + rr, q[1] + rr), fill=c)

    def pt(base, ang, ln):
        dx, dy = vec(ang, ln * s)
        return (base[0] + dx * facing, base[1] + dy)

    hip = (x, y)
    neck = pt(hip, 180 + p["torso"], L["torso"])
    head_c = pt(neck, 180 + p["torso"] + p["head"] * 0.5, L["neck"] + 1.0)
    # legs
    for th, sh in (("lth", "lsh"), ("rth", "rsh")):
        knee = pt(hip, p[th], L["thigh"])
        foot = pt(knee, p[sh], L["shin"])
        seg(hip, knee); seg(knee, foot)
    if look.kind == "woman":
        sk = [pt(hip, 180 + p["torso"], 0.5), pt(hip, -28, 1.7), pt(hip, 28, 1.7)]
        d.polygon(sk, fill=(70, 90, 140, alpha), outline=ink)
    seg(hip, neck)
    shoulder = pt(hip, 180 + p["torso"], L["torso"] * 0.86)
    hands = []
    for ua, fa in (("lua", "lfa"), ("rua", "rfa")):
        el = pt(shoulder, p[ua], L["uarm"])
        hd = pt(el, p[fa], L["farm"])
        seg(shoulder, el); seg(el, hd)
        hands.append(hd)
    # props below head
    if look.kind == "archie":
        # amber scarf: one tail hanging behind the shoulder, then a chunky band round the neck
        sc = look.accent + (alpha,)
        k = pt(neck, 0, 0.14)
        t0 = (k[0] - s * 0.25 * facing, k[1] + s * 0.05)
        t1 = pt(t0, -18 + p["torso"] * 1.5 + math.sin(p["head"] * 0.2) * 8, 0.95)
        seg(t0, t1, int(lw * 1.25), look.accent)
        d.rounded_rectangle((k[0] - s * 0.55, k[1] - s * 0.24, k[0] + s * 0.55, k[1] + s * 0.24), radius=s * 0.24, fill=sc, outline=ink, width=out)
    # head
    cx, cy = head_c
    r = s
    d.ellipse((cx - r - out, cy - r - out, cx + r + out, cy + r + out), fill=ink)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=look.body + (alpha,))
    tilt = math.radians(p["head"]) * 0.6
    ct, st = math.cos(tilt), math.sin(tilt)

    def hp(u, v):  # head-local coords (u right, v down), in head radii
        u *= facing
        return (cx + (u * ct - v * st) * r, cy + (u * st + v * ct) * r)

    fw = max(2, int(s * 0.12))
    # hats / hair
    if look.kind == "archie":
        for k2, a in enumerate((-28, -4, 20)):
            b0 = hp(-0.22 + k2 * 0.2, -0.92)
            b1 = (b0[0] + math.sin(math.radians(a)) * r * 0.6 * facing, b0[1] - math.cos(math.radians(a)) * r * 0.6)
            ctl = ((b0[0] + b1[0]) / 2 + r * 0.12 * facing, (b0[1] + b1[1]) / 2)
            d.line([b0, ctl, b1], fill=ink, width=int(fw * 1.5), joint="curve")
    elif look.kind == "captain":
        brim = [hp(-1.15, -0.62), hp(1.15, -0.62)]
        d.line(brim, fill=ink, width=int(fw * 1.6))
        top = [hp(-0.85, -0.62), hp(-0.75, -1.25), hp(0.75, -1.25), hp(0.85, -0.62)]
        d.polygon(top, fill=(30, 34, 52, alpha), outline=ink)
        d.ellipse([*hp(-0.12, -1.02), *hp(0.12, -0.82)], fill=look.accent + (alpha,))
    elif look.kind == "sailor":
        d.chord([*hp(-0.95, -1.35), *hp(0.95, -0.35)], 180, 360, fill=(235, 235, 240, alpha), outline=ink, width=out)
    elif look.kind == "keeper":
        d.chord([*hp(-1.0, -1.25), *hp(1.0, -0.2)], 180, 360, fill=(40, 52, 70, alpha), outline=ink, width=out)
        d.line([hp(-1.15, -0.72), hp(0.4, -0.72)], fill=ink, width=int(fw * 1.4))
    elif look.kind == "redhair":
        d.chord([*hp(-1.05, -1.12), *hp(1.05, 0.2)], 180, 360, fill=RED + (alpha,), outline=ink, width=out)
        for k2 in range(5):
            u = -0.7 + k2 * 0.35
            d.polygon([hp(u - 0.2, -0.9), hp(u + 0.05, -1.3), hp(u + 0.2, -0.88)], fill=RED + (alpha,))
    elif look.kind == "official":
        d.rectangle([*hp(-0.7, -1.6), *hp(0.7, -0.75)], fill=(28, 28, 32, alpha))
        d.line([hp(-1.1, -0.75), hp(1.1, -0.75)], fill=(28, 28, 32, alpha), width=int(fw * 1.6))
    elif look.kind == "pilot":
        d.chord([*hp(-1.08, -1.12), *hp(1.08, 0.4)], 180, 360, fill=(110, 76, 46, alpha), outline=ink, width=out)
        for side in (-1, 1):
            c0 = hp(side * 0.36, -0.62)
            d.ellipse((c0[0] - 0.22 * r, c0[1] - 0.18 * r, c0[0] + 0.22 * r, c0[1] + 0.18 * r), fill=(150, 200, 220, alpha), outline=ink, width=out)
    elif look.kind == "woman":
        d.chord([*hp(-1.08, -1.15), *hp(1.08, 0.55)], 180, 360, fill=(110, 70, 45, alpha), outline=ink, width=out)
        d.ellipse([*hp(-0.35, -1.45), *hp(0.35, -0.85)], fill=(110, 70, 45, alpha), outline=ink, width=out)
    elif look.kind == "judge":
        for k2 in range(6):
            u = -1.0 + k2 * 0.4
            d.ellipse([*hp(u - 0.3, -1.2), *hp(u + 0.3, -0.5)], fill=(236, 236, 236, alpha), outline=ink, width=out)
        for side in (-1, 1):
            d.ellipse([*hp(side * 1.05 - 0.25, -0.3), *hp(side * 1.05 + 0.25, 0.6)], fill=(236, 236, 236, alpha), outline=ink, width=out)
    elif look.kind == "writer":
        d.ellipse([*hp(-0.75, -1.55), *hp(0.75, -0.75)], fill=(40, 34, 30, alpha))
        d.line([hp(-1.1, -0.78), hp(1.1, -0.78)], fill=(40, 34, 30, alpha), width=int(fw * 1.8))
    if look.kind == "writer":
        d.chord([*hp(-0.6, 0.15), *hp(0.6, 0.55)], 180, 360, fill=(60, 44, 34, alpha))
    if look.kind == "beard" or look.kind == "captain":
        d.chord([*hp(-0.85, -0.2), *hp(0.85, 1.25)], 0, 180, fill=(200, 200, 205, alpha) if look.kind == "captain" else (90, 70, 55, alpha))

    face(d, hp, r, expr, mouth, blink, fw, alpha, glasses=(look.kind == "archie"))
    return dict(head=head_c, hands=hands, neck=neck)


def face(d, hp, r, expr, mouth, blink, fw, alpha, glasses=False):
    ink = INK + (alpha,)
    ey, ex = -0.12, 0.36
    eye_r = 0.12
    if expr in ("shocked", "scared"):
        eye_r = 0.2
    # brows
    brow = {
        "neutral": (0, 0), "smug": (-8, 10), "shocked": (-14, 14), "scared": (18, -18), "deadpan": (0, 0),
        "laugh": (-6, 6), "sad": (22, -22), "suspicious": (-16, 4), "angry": (24, -24), "wink": (-6, 6),
    }[expr]
    by = ey - (0.42 if expr in ("shocked", "scared") else 0.32)
    for side, ang in ((-1, brow[0]), (1, brow[1])):
        c = hp(side * ex, by)
        a = math.radians(ang) * side
        dx, dy = math.cos(a) * 0.2 * r, math.sin(a) * 0.2 * r
        d.line([(c[0] - dx, c[1] + dy), (c[0] + dx, c[1] - dy)], fill=ink, width=fw)
    # eyes
    for side in (-1, 1):
        c = hp(side * ex, ey)
        closed = blink > 0.5 or (expr == "laugh") or (expr == "wink" and side == 1)
        if expr == "deadpan" and not closed:
            d.line([(c[0] - 0.14 * r, c[1]), (c[0] + 0.14 * r, c[1])], fill=ink, width=fw)
            d.chord((c[0] - 0.14 * r, c[1] - 0.02 * r, c[0] + 0.14 * r, c[1] + 0.16 * r), 0, 180, fill=ink)
        elif expr == "suspicious" and not closed:
            d.chord((c[0] - 0.15 * r, c[1] - 0.12 * r, c[0] + 0.15 * r, c[1] + 0.12 * r), 0, 180, fill=ink)
            d.line([(c[0] - 0.16 * r, c[1]), (c[0] + 0.16 * r, c[1])], fill=ink, width=fw)
        elif closed:
            d.arc((c[0] - 0.15 * r, c[1] - 0.12 * r, c[0] + 0.15 * r, c[1] + 0.12 * r), 180, 360, fill=ink, width=fw)
        else:
            rr = eye_r * r
            if expr in ("shocked", "scared"):
                d.ellipse((c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr), outline=ink, width=fw)
                pr = rr * 0.45
                d.ellipse((c[0] - pr, c[1] - pr, c[0] + pr, c[1] + pr), fill=ink)
            else:
                d.ellipse((c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr), fill=ink)
        if glasses:
            gr = 0.26 * r
            d.ellipse((c[0] - gr, c[1] - gr, c[0] + gr, c[1] + gr), outline=ink, width=max(1, fw - 1))
    if glasses:
        a, b = hp(-ex + 0.26, ey), hp(ex - 0.26, ey)
        d.line([a, b], fill=ink, width=max(1, fw - 1))
    # mouth
    m = hp(0, 0.45)
    w = 0.32 * r
    o = min(max(mouth, 0.0), 1.0)
    if expr in ("shocked", "scared") or (o > 0.15 and expr not in ("smug",)):
        h = (0.08 + 0.32 * o) * r if expr not in ("shocked", "scared") else (0.22 + 0.2 * o) * r
        ww = w * (0.7 if expr in ("shocked", "scared") else 0.9)
        d.ellipse((m[0] - ww, m[1] - h, m[0] + ww, m[1] + h), fill=(90, 30, 30, alpha), outline=ink, width=fw)
    elif expr == "smug":
        d.arc((m[0] - w, m[1] - 0.25 * r, m[0] + w * 0.6, m[1] + 0.12 * r), 10, 120, fill=ink, width=fw)
        if o > 0.15:
            d.ellipse((m[0] - w * 0.4, m[1] - 0.05 * r, m[0] + w * 0.3, m[1] + (0.05 + 0.2 * o) * r), fill=(90, 30, 30, alpha), outline=ink, width=fw)
    elif expr == "laugh":
        d.chord((m[0] - w, m[1] - 0.2 * r, m[0] + w, m[1] + 0.3 * r), 0, 180, fill=(90, 30, 30, alpha), outline=ink, width=fw)
    elif expr in ("sad", "angry"):
        d.arc((m[0] - w * 0.8, m[1] + 0.02 * r, m[0] + w * 0.8, m[1] + 0.35 * r), 200, 340, fill=ink, width=fw)
    elif expr in ("deadpan", "suspicious"):
        d.line([(m[0] - w * 0.6, m[1] + 0.05 * r), (m[0] + w * 0.6, m[1] + 0.05 * r)], fill=ink, width=fw)
    else:
        d.arc((m[0] - w * 0.8, m[1] - 0.2 * r, m[0] + w * 0.8, m[1] + 0.12 * r), 20, 160, fill=ink, width=fw)
    if expr == "scared":
        # sweat drop
        sx, sy = hp(1.05, -0.5)
        d.polygon([(sx, sy - 0.25 * r), (sx - 0.1 * r, sy), (sx + 0.1 * r, sy)], fill=(140, 190, 230, alpha))
        d.ellipse((sx - 0.1 * r, sy - 0.06 * r, sx + 0.1 * r, sy + 0.14 * r), fill=(140, 190, 230, alpha))


class Actor:
    """A character with a pose/expression timeline and automatic idle motion, blinking and lip-sync."""

    def __init__(self, look, seed=0, talk_gestures=True):
        self.look = look
        self.track = []          # (t, pose_name, expr)
        self.rng = random.Random(seed)
        self.blinks = []
        t = 0.5
        while t < 3600:
            self.blinks.append(t); t += self.rng.uniform(2.2, 5.0)
        self.talk = talk_gestures

    def key(self, t, pose_name, expr=None):
        self.track.append((t, pose_name, expr))
        self.track.sort(key=lambda k: k[0])

    def state(self, t, speaking=0.0):
        tr = self.track or [(0, "idle", "neutral")]
        prev = tr[0]; nxt = None
        for k in tr:
            if k[0] <= t:
                prev = k
            elif nxt is None:
                nxt = k
        expr = "neutral"
        for k in tr:
            if k[0] <= t and k[2]:
                expr = k[2]
        p_name = prev[1]
        # talking gesture cycling when the key is a plain idle/talk key
        if self.talk and p_name in ("idle", "talk") and speaking > 0.05:
            phase = int((t - prev[0]) / 1.6)
            p_name = ("talk1", "talk2", "idle", "talk3")[(phase + int(prev[0] * 7)) % 4]
            p0 = pose(("talk1", "talk2", "idle", "talk3")[(phase - 1 + int(prev[0] * 7)) % 4]) if phase > 0 else pose(prev[1] if prev[1] in POSES else "idle")
            u = ease(((t - prev[0]) - phase * 1.6) / 0.45)
            p = lerp_pose(p0, pose(p_name), u)
        else:
            if p_name == "talk":
                p_name = "idle"
            # transition from previous key's pose
            idx = tr.index(prev)
            before = tr[idx - 1][1] if idx > 0 else p_name
            before = "idle" if before == "talk" else before
            u = ease((t - prev[0]) / 0.35)
            p = lerp_pose(pose(before), pose(p_name), u)
            if p_name in ("walk_a", "walk_b"):
                ph = (math.sin(t * 6.0) + 1) / 2
                p = lerp_pose(pose("walk_a"), pose("walk_b"), ph)
        # idle life
        p["torso"] += math.sin(t * 1.3) * 1.5
        p["head"] += math.sin(t * 0.9 + 1) * 3
        blink = 1.0 if any(0 <= t - b < 0.12 for b in self.blinks) else 0.0
        return p, expr, blink

    def draw(self, layer, x, y, s, t, mouth=0.0, facing=1, alpha=255, bounce=True):
        p, expr, blink = self.state(t, mouth)
        yy = y - (abs(math.sin(t * 2.2)) * s * 0.05 if bounce else 0)
        if self.track and any(k[1] == "jump" and 0 <= t - k[0] < 0.6 for k in self.track):
            k = max(k[0] for k in self.track if k[1] == "jump" and k[0] <= t)
            yy -= math.sin(min((t - k) / 0.6, 1) * math.pi) * s * 1.6
        return draw_figure(layer, x, yy, s, p, expr, mouth, blink, self.look, facing, alpha)


def mouth_track(wav_float, sr, fps):
    """Per-frame mouth opening 0..1 from a mono float waveform."""
    import numpy as np
    hop = sr / fps
    n = int(len(wav_float) / hop) + 1
    env = np.zeros(n)
    for i in range(n):
        seg = wav_float[int(i * hop): int((i + 1) * hop)]
        env[i] = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
    pk = np.percentile(env[env > 0], 95) if (env > 0).any() else 1.0
    env = np.clip(env / (pk + 1e-9), 0, 1) ** 0.7
    # quantise to a few mouth shapes so it reads as cartoon lip-flap rather than jitter
    env = np.round(env * 3) / 3
    return env
