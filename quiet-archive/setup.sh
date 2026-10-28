#!/bin/sh
# Rebuild the TTS environment in a fresh session (paths used by pipeline/kokoro_tts.py).
set -e
R=$(cd "$(dirname "$0")" && pwd)
mkdir -p /home/claude/kokoro /home/claude/tts /home/claude/thewh1teagle/kokoro-onnx/src/kokoro_onnx
cat "$R"/assets/kokoro-v1.0.onnx.part* > /home/claude/kokoro/kokoro-v1.0.onnx
cp "$R"/assets/voices-v1.0.bin /home/claude/kokoro/
cp "$R"/assets/kokoro-config.json /home/claude/thewh1teagle/kokoro-onnx/src/kokoro_onnx/config.json
tar -xzf "$R"/assets/piper.tar.gz -C /home/claude/tts
chmod +x /home/claude/tts/piper/espeak-ng /home/claude/tts/piper/piper 2>/dev/null || true
python3 -c "import onnxruntime, numpy, PIL; print('deps ok')"
echo "setup done"
