
import os, json
os.environ["PATH"] = r"H:\tools\ffmpeg\ffmpeg-master-latest-win64-gpl\bin;" + os.environ.get("PATH","")
import librosa, torch
from transformers import pipeline

p = r"H:\ai_music_crew\work\orig-in\雨爱.mp3"
y, sr = librosa.load(p, sr=16000, mono=True, duration=110)
pipe = pipeline("automatic-speech-recognition", model="openai/whisper-small", device=0 if torch.cuda.is_available() else -1)
r = pipe(y, return_timestamps=True, generate_kwargs={"language":"zh","task":"transcribe"})
out = []
for c in r.get("chunks", []):
    out.append({"t0": c["timestamp"][0], "t1": c["timestamp"][1], "text": c["text"].strip()})
open(r"H:\ai_music_crew\work\_yuai_align.json","w",encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print("segments:", len(out))
for c in out:
    t0 = c["timestamp"][0] or 0
    print(f"  [{t0:6.1f}s] {c['text']}")
