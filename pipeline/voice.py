"""Narration: Kokoro "Michael" (am_michael), speed 1.0, clean (no filter). Channel rule: this is Doc Stick's voice.

synth(phrases, wav, voice, speed) -> (wav, [(start, end) per phrase], total seconds)
Model files (~350 MB) download once into ~/.cache/kokoro.
"""
import os, urllib.request
import numpy as np

CACHE = os.path.expanduser("~/.cache/kokoro")
URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
FILES = ("kokoro-v1.0.onnx", "voices-v1.0.bin")
SR = 24000
LEAD = 0.35          # silence before the first word


def _model():
    os.makedirs(CACHE, exist_ok=True)
    for f in FILES:
        p = os.path.join(CACHE, f)
        if not os.path.exists(p):
            print("downloading", f); urllib.request.urlretrieve(URL + f, p + ".part"); os.replace(p + ".part", p)
    from kokoro_onnx import Kokoro
    return Kokoro(*(os.path.join(CACHE, f) for f in FILES))


def synth(phrases, wav, voice="am_michael", speed=1.0):
    import soundfile as sf
    k = _model()
    out = [np.zeros(int(SR * LEAD), np.float32)]; t = LEAD; times = []
    for ph in phrases:
        a, _ = k.create(ph["say"], voice=voice, speed=speed, lang="en-us")
        a = a.astype(np.float32); idx = np.where(np.abs(a) > 0.01)[0]
        a = a[max(0, idx[0] - 150):idx[-1] + 900]
        times.append((round(t, 3), round(t + len(a) / SR, 3)))
        out.append(a); t += len(a) / SR
        g = ph.get("pause", 0.2); out.append(np.zeros(int(SR * g), np.float32)); t += g
    sf.write(wav, np.concatenate(out), SR)
    return wav, times, round(t, 3)
