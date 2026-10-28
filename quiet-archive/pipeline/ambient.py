"""Original ambient music bed, synthesised from scratch (no samples, no third-party music).

ambient.py <seconds> <out.wav> [seed] [mood]
mood: "sea" (default, A minor drift) or "dread" (lower, D minor, slower)
Soft detuned pads through a slow chord loop, a quiet low drone, gentle filtered noise "air", and a
simple multi-tap reverb. Output 48 kHz stereo, peak about -14 dBFS before final mix.
"""
import sys, wave
import numpy as np

SR = 48000


def note(n):  # MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def pad(freqs, dur, rng, detune=0.004):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for f in freqs:
        for d in (-detune, 0, detune):
            ph = rng.uniform(0, 2 * np.pi)
            out += np.sin(2 * np.pi * f * (1 + d) * t + ph)
            out += 0.25 * np.sin(2 * np.pi * 2 * f * (1 + d) * t + ph)  # soft 2nd harmonic
    env = np.minimum(1, t / 3.0) * np.minimum(1, (dur - t) / 3.0)  # 3 s swells
    return out * env / (len(freqs) * 3)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x); acc = 0.0
    for i in range(0, len(x), 4096):  # vectorised-ish one-pole in blocks
        seg = x[i:i + 4096]
        out = np.empty_like(seg)
        for j, v in enumerate(seg):
            acc = (1 - a) * v + a * acc
            out[j] = acc
        y[i:i + 4096] = out
    return y


def reverb(x, rng):
    y = x.copy()
    for ms, g in [(53, .5), (79, .45), (113, .4), (167, .33), (241, .27), (331, .2), (467, .14), (619, .1)]:
        k = int(SR * ms / 1000)
        y[k:] += g * x[:-k]
    return y / 2.2


def build(seconds, seed=1, mood="sea"):
    rng = np.random.default_rng(seed)
    if mood == "dread":
        prog = [[50, 53, 57], [46, 50, 53], [48, 52, 55], [45, 49, 52]]  # Dm Bb C A
        drone, chord_len = 38, 16.0
    else:
        prog = [[45, 48, 52], [41, 45, 48], [48, 52, 55], [43, 47, 50]]  # Am F C G
        drone, chord_len = 33, 12.0
    n = int(seconds * SR)
    left = np.zeros(n + int(SR * (chord_len + 4))); right = np.zeros_like(left)
    t0, k = 0.0, 0
    while t0 < seconds:
        ch = [note(m) for m in prog[k % len(prog)]]
        seg = pad(ch, chord_len + 3, rng)
        a, b = int(t0 * SR), int(t0 * SR) + len(seg)
        left[a:b] += seg * (0.9 + 0.1 * rng.random())
        right[a:b] += np.roll(seg, 240) * (0.9 + 0.1 * rng.random())
        t0 += chord_len; k += 1
    t = np.arange(len(left)) / SR
    dr = 0.5 * np.sin(2 * np.pi * note(drone) * t) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 23))
    left += dr; right += dr
    air = rng.standard_normal(len(left)) * 0.02
    air = np.convolve(air, np.ones(64) / 64, mode="same") * (0.5 + 0.5 * np.sin(2 * np.pi * t / 17))
    left += air; right += np.roll(air, 900)
    left, right = reverb(left, rng)[:n], reverb(right, rng)[:n]
    fade = np.minimum(1, np.arange(n) / (4 * SR)) * np.minimum(1, (n - np.arange(n)) / (6 * SR))
    st = np.stack([left * fade, right * fade], 1)
    st /= np.max(np.abs(st)) + 1e-9
    return st * 0.2


if __name__ == "__main__":
    sec = float(sys.argv[1]); out = sys.argv[2]
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    mood = sys.argv[4] if len(sys.argv) > 4 else "sea"
    st = build(sec, seed, mood)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    print(out, sec)
