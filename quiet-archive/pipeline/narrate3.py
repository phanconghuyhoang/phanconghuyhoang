"""Narrate a v3 script (host-driven, tagged) with Kokoro.

Script format:
    ## s01 | <background> | <layout>
    {a:lean_in/suspicious} First sentence. Second sentence. {p:0.6}{a:shrug/deadpan}{s:boing} Punchline.

Tags in {...} attach to the next sentence:  a: host pose/expr   c: cast command   t: big kinetic text
    s: sound effect   p: pause (seconds of silence before the sentence)   z: comedic zoom on the host
    bg: switch background   cam: camera framing for the background
Outputs <out>/voice_full.wav, scenes.json (sentences with start/end/tags, scene durations), narration.srt
usage: narrate3.py script.md outdir [voice] [speed]
"""
import json, os, re, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import kokoro_tts as K

GAP_SENT, GAP_PARA, LEAD, TAIL = 0.22, 0.5, 0.3, 0.6
TAG = re.compile(r"\{([a-z]+):?([^}]*)\}")


def sentences(p):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", p) if s.strip()]


def parse(path):
    scenes, cur = [], None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("## "):
            p = [x.strip() for x in line[3:].split("|")]
            cur = {"id": p[0], "bg": p[1] if len(p) > 1 else "room", "layout": p[2] if len(p) > 2 else "host", "paras": []}
            scenes.append(cur)
        elif cur is not None and line.strip() and not line.startswith(("#", "<!--")):
            items, pending = [], []
            pos = 0
            for m in TAG.finditer(line):
                txt = line[pos:m.start()].strip()
                if txt:
                    for s in sentences(txt):
                        items.append((s, pending)); pending = []
                pending.append([m.group(1), m.group(2).strip()])
                pos = m.end()
            txt = line[pos:].strip()
            if txt:
                for s in sentences(txt):
                    items.append((s, pending)); pending = []
            elif pending and items:
                items[-1][1].extend(pending)
            elif pending:
                items.append(("", pending))
            cur["paras"].append(items)
    return scenes


def srt_time(t):
    h, m = int(t // 3600), int(t % 3600 // 60); s = t % 60
    return f"{h:02}:{m:02}:{int(s):02},{int(round((s % 1) * 1000)) % 1000:03}"


def main(script, out, voice="am_michael", speed=1.0):
    os.makedirs(out, exist_ok=True)
    scenes = parse(script)
    sil = lambda s: np.zeros(int(K.SR * s), dtype=np.float32)
    full, srt, idx, tg = [], [], 1, 0.0
    for sc in scenes:
        t = LEAD; buf = [sil(LEAD)]; sc["sentences"] = []
        for para in sc["paras"]:
            for text, tags in para:
                for k, v in tags:
                    if k == "p":
                        d = float(v or 0.5); buf.append(sil(d)); t += d
                if not text:
                    sc["sentences"].append({"text": "", "start": round(t, 3), "end": round(t + 0.6, 3), "tags": tags})
                    buf.append(sil(0.6)); t += 0.6
                    continue
                a = K.synth(text, voice=voice, speed=speed)
                nz = np.where(np.abs(a) > 0.01)[0]
                if len(nz):
                    a = a[nz[0]: nz[-1] + int(K.SR * 0.05)]
                d = len(a) / K.SR
                sc["sentences"].append({"text": text, "start": round(t, 3), "end": round(t + d, 3), "tags": tags})
                srt.append(f"{idx}\n{srt_time(tg + t)} --> {srt_time(tg + t + d)}\n{text}\n"); idx += 1
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
    main(a[1], a[2], a[3] if len(a) > 3 else "am_michael", float(a[4]) if len(a) > 4 else 1.0)
