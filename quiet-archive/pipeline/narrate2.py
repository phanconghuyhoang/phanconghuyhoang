"""Narrate script.md with Kokoro. Writes audio/voice_full.wav (24 kHz mono), audio/scenes.json, audio/narration.srt.

usage: narrate2.py <script.md> <out_dir> [voice] [speed]
Paragraph markers [[TEXT]] are stripped from the spoken text (they drive on-screen titles in render2.py).
"""
import json, os, re, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import kokoro_tts as K

GAP_SENT, GAP_PARA, LEAD, TAIL = 0.32, 0.70, 0.35, 0.8


def parse(path):
    scenes, cur = [], None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("## "):
            p = [x.strip() for x in line[3:].split("|")]
            cur = {"id": p[0], "visual": p[1], "caption": p[2] if len(p) > 2 else "", "paras": []}
            scenes.append(cur)
        elif cur is not None and line.strip() and not line.startswith(("#", "<!--")):
            cur["paras"].append(re.sub(r"^\[\[.+?\]\]\s*", "", line.strip()))
    return scenes


def sentences(p):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'])", p) if s.strip()]


def srt_time(t):
    h, m = int(t // 3600), int(t % 3600 // 60); s = t % 60
    return f"{h:02}:{m:02}:{int(s):02},{int(round((s % 1) * 1000)) % 1000:03}"


def main(script, out, voice="af_heart", speed=0.95):
    os.makedirs(out, exist_ok=True)
    scenes = parse(script)
    sil = lambda s: np.zeros(int(K.SR * s), dtype=np.float32)
    full, srt, idx, tg = [], [], 1, 0.0
    for sc in scenes:
        t = LEAD; buf = [sil(LEAD)]; sc["sentences"] = []
        for para in sc["paras"]:
            for s in sentences(para):
                a = K.synth(s, voice=voice, speed=speed)
                a = a[np.argmax(np.abs(a) > 0.01):] if np.any(np.abs(a) > 0.01) else a  # trim lead silence
                d = len(a) / K.SR
                sc["sentences"].append({"text": s, "start": round(t, 3), "end": round(t + d, 3)})
                srt.append(f"{idx}\n{srt_time(tg + t)} --> {srt_time(tg + t + d)}\n{s}\n"); idx += 1
                buf += [a, sil(GAP_SENT)]; t += d + GAP_SENT
            buf.append(sil(GAP_PARA - GAP_SENT)); t += GAP_PARA - GAP_SENT
        buf.append(sil(TAIL)); t += TAIL
        sc["duration"] = round(t, 3)
        full += buf; tg += t
        del sc["paras"]
        print(sc["id"], sc["duration"], flush=True)
    pcm = np.concatenate(full)
    pcm = pcm / max(1e-6, np.max(np.abs(pcm))) * 0.9
    with wave.open(os.path.join(out, "voice_full.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(K.SR); w.writeframes((pcm * 32767).astype(np.int16).tobytes())
    json.dump(scenes, open(os.path.join(out, "scenes.json"), "w"), indent=1)
    open(os.path.join(out, "narration.srt"), "w").write("\n".join(srt))
    print("TOTAL", round(tg / 60, 2), "min")


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3] if len(a) > 3 else "af_heart", float(a[4]) if len(a) > 4 else 0.95)
