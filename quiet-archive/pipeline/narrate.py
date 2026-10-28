"""Narrate a script.md with Piper, one sentence at a time.

Outputs in <out_dir>:
  scenes.json  - per scene: id, visual, caption, audio file, duration, sentences with start/end
  sNN.wav      - narration for each scene (with pauses)
  narration.srt
"""
import json, re, subprocess, sys, wave, os

PIPER = "/home/claude/tts/piper/piper"
MODEL = "/home/claude/tts/en-us-ryan-high.onnx"
RATE = 22050
GAP_SENT, GAP_PARA, LEAD, TAIL = 0.35, 0.75, 0.4, 0.9


def parse(path):
    scenes, cur = [], None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("## "):
            parts = [p.strip() for p in line[3:].split("|")]
            cur = {"id": parts[0], "visual": parts[1], "caption": parts[2] if len(parts) > 2 else "", "paras": []}
            scenes.append(cur)
        elif cur is not None and line.strip() and not line.startswith(("#", "<!--")):
            cur["paras"].append(line.strip())
    return scenes


def sentences(p):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'])", p) if s.strip()]


def synth(text, path):
    subprocess.run([PIPER, "--model", MODEL, "--output_file", path, "--length_scale", "1.07", "--noise_scale", "0.6"],
                   input=text.replace("ò", "o").encode(), check=True, capture_output=True)
    with wave.open(path) as w:
        return w.readframes(w.getnframes())


def silence(sec):
    return b"\x00\x00" * int(RATE * sec)


def srt_time(t):
    h, m = int(t // 3600), int(t % 3600 // 60)
    s = t % 60
    return f"{h:02}:{m:02}:{int(s):02},{int(round((s % 1) * 1000)) % 1000:03}"


def main(script, out):
    os.makedirs(out, exist_ok=True)
    tmp = os.path.join(out, "_s.wav")
    scenes = parse(script)
    t_global, srt, idx = 0.0, [], 1
    for sc in scenes:
        pcm = silence(LEAD)
        t = LEAD
        sc["sentences"] = []
        for pi, para in enumerate(sc["paras"]):
            for sent in sentences(para):
                raw = synth(sent, tmp)
                d = len(raw) / 2 / RATE
                sc["sentences"].append({"text": sent, "start": round(t, 3), "end": round(t + d, 3)})
                srt.append(f"{idx}\n{srt_time(t_global + t)} --> {srt_time(t_global + t + d)}\n{sent}\n")
                idx += 1
                pcm += raw + silence(GAP_SENT)
                t += d + GAP_SENT
            pcm += silence(GAP_PARA - GAP_SENT)
            t += GAP_PARA - GAP_SENT
        pcm += silence(TAIL)
        t += TAIL
        sc["audio"] = f"{sc['id']}.wav"
        sc["duration"] = round(len(pcm) / 2 / RATE, 3)
        with wave.open(os.path.join(out, sc["audio"]), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(pcm)
        t_global += sc["duration"]
        del sc["paras"]
        print(sc["id"], sc["duration"], flush=True)
    os.remove(tmp)
    json.dump(scenes, open(os.path.join(out, "scenes.json"), "w"), indent=1)
    open(os.path.join(out, "narration.srt"), "w").write("\n".join(srt))
    print("TOTAL", round(t_global / 60, 2), "min")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
