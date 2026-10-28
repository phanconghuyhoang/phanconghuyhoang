"""Small synthesized sound effects (no samples, no licensing): whoosh, pop, boing, thud, ding, sting, tick, scratch.
All return float32 mono at 48 kHz, peak about 0.5."""
import numpy as np

SR = 48000


def _env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-4))
    return e


def whoosh(d=0.45):
    n = int(SR * d); rng = np.random.default_rng(1)
    x = rng.standard_normal(n)
    # sweep a simple resonant band-pass by moving-average differences
    out = np.zeros(n); lo = 0.0; bp = 0.0
    for i in range(n):
        f = 0.02 + 0.25 * np.sin(np.pi * i / n)
        lo += f * (x[i] - lo); bp += f * (lo - bp)
        out[i] = lo - bp
    e = np.sin(np.pi * np.arange(n) / n) ** 2
    return (out * e / (np.abs(out).max() + 1e-9) * 0.45).astype(np.float32)


def pop():
    n = int(SR * 0.09); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 30) + 300
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.001, 0.025) * 0.5).astype(np.float32)


def boing():
    n = int(SR * 0.6); t = np.arange(n) / SR
    f = 180 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4) + 140 * np.exp(-t * 6)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.25) * 0.5).astype(np.float32)


def thud():
    n = int(SR * 0.5); t = np.arange(n) / SR
    f = 60 + 90 * np.exp(-t * 25)
    rng = np.random.default_rng(2)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.001, 0.18) + rng.standard_normal(n) * _env(n, 0.001, 0.02) * 0.3
    return (x / np.abs(x).max() * 0.55).astype(np.float32)


def ding():
    n = int(SR * 1.2); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((1320, 1), (2640, 0.35), (3960, 0.15)))
    return (x * _env(n, 0.002, 0.35) / 1.5 * 0.4).astype(np.float32)


def sting():
    """Low dramatic hit: 'dun-dun'."""
    def hit(f0, d):
        n = int(SR * d); t = np.arange(n) / SR
        x = sum(np.sin(2 * np.pi * f0 * k * t) / k for k in (1, 2, 3, 4)) * _env(n, 0.004, 0.5)
        return x
    a = hit(73.4, 0.55); b = hit(69.3, 1.4)
    x = np.concatenate([a, np.zeros(int(SR * 0.05)), b])
    return (x / np.abs(x).max() * 0.55).astype(np.float32)


def tick():
    n = int(SR * 0.03)
    rng = np.random.default_rng(3)
    return (rng.standard_normal(n) * _env(n, 0.0005, 0.004) * 0.4).astype(np.float32)


def scratch():
    n = int(SR * 0.35); t = np.arange(n) / SR
    rng = np.random.default_rng(4)
    f = 400 + 1200 * np.sin(2 * np.pi * 3 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + rng.standard_normal(n) * 0.3
    return (x * _env(n, 0.002, 0.15) / np.abs(x).max() * 0.45).astype(np.float32)


def crickets():
    n = int(SR * 1.6); t = np.arange(n) / SR
    chirp = (np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 30 * t) > 0.3) * ((t % 0.5) < 0.18))
    return (chirp * 0.18).astype(np.float32)


BANK = dict(whoosh=whoosh, pop=pop, boing=boing, thud=thud, ding=ding, sting=sting, tick=tick, scratch=scratch, crickets=crickets)


def track(cues, total):
    """cues: [(time, name)] -> stereo float32 array (n, 2) at 48 kHz."""
    out = np.zeros(int(SR * (total + 2)), np.float32)
    cache = {}
    for t, name in cues:
        if name not in BANK:
            continue
        if name not in cache:
            cache[name] = BANK[name]()
        s = cache[name]; i = int(t * SR)
        out[i:i + len(s)] += s[: max(0, len(out) - i)]
    return np.stack([out, out], 1)
