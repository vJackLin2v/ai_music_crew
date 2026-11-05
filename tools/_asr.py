
import os, sys, json
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
os.environ["PATH"] = r"H:\tools\ffmpeg\ffmpeg-master-latest-win64-gpl\bin;" + os.environ.get("PATH","")

import torch, librosa
from transformers import pipeline

files = {
 "青花": r"H:\AI学习计划\AI音乐\青花.mp3",
 "若月亮没来": r"H:\AI学习计划\AI音乐\若月亮没来.mp3",
}
pipe = pipeline("automatic-speech-recognition", model="openai/whisper-small",
                device=0 if torch.cuda.is_available() else -1,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
out = {}
for name, path in files.items():
    audio, sr = librosa.load(path, sr=16000, mono=True)
    print(f"[{name}] dur={len(audio)/sr:.1f}s", flush=True)
    r = pipe(audio, return_timestamps=True, generate_kwargs={"language": "zh", "task": "transcribe"})
    out[name] = r
    print(f"[{name}] text: {r['text'][:600]}", flush=True)
json.dump(out, open(r"H:\ai_music_crew\work\asr.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("done")
