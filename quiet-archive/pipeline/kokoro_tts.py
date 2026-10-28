"""Kokoro-82M (ONNX) text-to-speech with espeak-ng phonemes from the Piper bundle.

synth(text, voice='af_heart', speed=0.95) -> float32 numpy array at 24 kHz
"""
import json, os, re, subprocess
import numpy as np
import onnxruntime as rt

ROOT = "/home/claude/kokoro"
PIPER = "/home/claude/tts/piper"
SR = 24000
VOCAB = json.load(open("/home/claude/thewh1teagle/kokoro-onnx/src/kokoro_onnx/config.json"))["vocab"]

_sess = None
_voices = None


def _session():
    global _sess, _voices
    if _sess is None:
        so = rt.SessionOptions()
        so.intra_op_num_threads = os.cpu_count() or 2
        _sess = rt.InferenceSession(os.path.join(ROOT, "kokoro-v1.0.onnx"), so, providers=["CPUExecutionProvider"])
        _voices = np.load(os.path.join(ROOT, "voices-v1.0.bin"))
    return _sess, _voices


def _espeak(text, lang="en-us"):
    out = subprocess.run([os.path.join(PIPER, "espeak-ng"), "--path=" + PIPER, "-q", "--ipa", "-v", lang, text],
                         capture_output=True, text=True, env={**os.environ, "LD_LIBRARY_PATH": PIPER}).stdout
    return " ".join(l.strip() for l in out.splitlines() if l.strip())


def normalize(text):
    t = text.replace("—", ", ").replace("–", "-").replace("’", "'").replace("“", "").replace("”", "")
    t = t.replace("ò", "o").replace("Mòr", "Mor")
    return re.sub(r"\s+", " ", t).strip()


def phonemize(text, lang="en-us"):
    text = normalize(text)
    parts = re.split(r"([,.;:!?])", text)
    ph = ""
    for i in range(0, len(parts), 2):
        chunk = parts[i].strip()
        punct = parts[i + 1] if i + 1 < len(parts) else ""
        if chunk:
            ph += _espeak(chunk, lang)
        if punct:
            ph += punct
        ph += " "
    ph = "".join(c for c in ph if c in VOCAB)
    return re.sub(r"\s+", " ", ph).strip()


def synth(text, voice="af_heart", speed=0.95, lang="en-us"):
    sess, voices = _session()
    ph = phonemize(text, lang)
    toks = [VOCAB[c] for c in ph][:508]
    style = voices[voice][len(toks)]
    inputs = {i.name: None for i in sess.get_inputs()}
    tok_name = "input_ids" if "input_ids" in inputs else "tokens"
    feed = {tok_name: np.array([[0, *toks, 0]], dtype=np.int64),
            "style": np.asarray(style, dtype=np.float32),
            "speed": np.array([speed], dtype=np.float32)}
    audio = sess.run(None, feed)[0]
    return np.asarray(audio, dtype=np.float32).ravel()


if __name__ == "__main__":
    import sys, wave
    a = synth(sys.argv[1], voice=sys.argv[2] if len(sys.argv) > 2 else "af_heart")
    pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16)
    with wave.open(sys.argv[3] if len(sys.argv) > 3 else "/tmp/k.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print(len(a) / SR)
