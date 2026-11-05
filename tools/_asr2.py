
import os, sys, json, subprocess, glob
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PATH"] = r"H:\tools\ffmpeg\ffmpeg-master-latest-win64-gpl\bin;" + os.environ.get("PATH","")

PY = r"H:\ai_music_crew\.svc\Scripts\python.exe"
OUT = r"H:\ai_music_crew\work\asr2"
os.makedirs(OUT, exist_ok=True)

files = {
 "青花": r"H:\AI学习计划\AI音乐\青花.mp3",
 "若月亮没来": r"H:\AI学习计划\AI音乐\若月亮没来.mp3",
}

# 1) 分离人声
for name, path in files.items():
    d = os.path.join(OUT, name)
    if not os.path.exists(os.path.join(d, "vocals.wav")):
        print(f"[{name}] separating ...", flush=True)
        r = subprocess.run([PY, "-m", "demucs", "--two-stems", "vocals", "-n", "htdemucs_ft",
                            "-o", os.path.join(d, "sep"), path],
                           capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if r.returncode != 0:
            print("demucs failed:", (r.stderr or "")[-300:], flush=True)
            continue
        v = glob.glob(os.path.join(d, "sep", "htdemucs_ft", "*", "vocals.wav"))
        if v:
            import shutil; shutil.copy2(v[0], os.path.join(d, "vocals.wav"))
            print(f"[{name}] vocals ready {os.path.getsize(os.path.join(d,'vocals.wav'))//1024}KB", flush=True)

# 2) 分析 + ASR
import torch, librosa
import numpy as np
from transformers import pipeline

pipe = pipeline("automatic-speech-recognition", model="openai/whisper-small",
                device=0 if torch.cuda.is_available() else -1)

res = {}
for name in files:
    vp = os.path.join(OUT, name, "vocals.wav")
    if not os.path.exists(vp):
        print(f"[{name}] no vocals", flush=True); continue
    y, sr = librosa.load(vp, sr=16000, mono=True)
    # BPM / 调性
    y44, sr44 = librosa.load(vp, sr=44100, mono=True)
    tempo, _ = librosa.beat.beat_track(y=y44, sr=sr44)
    chroma = librosa.feature.chroma_cqt(y=y44, sr=sr44).mean(axis=1)
    keys = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
    key = keys[int(np.argmax(chroma))]
    print(f"[{name}] bpm={float(tempo):.1f} key={key} dur={len(y)/sr:.1f}s", flush=True)
    r = pipe(y, return_timestamps=True, generate_kwargs={"language":"zh","task":"transcribe"})
    res[name] = {"bpm": float(tempo), "key": key, "dur": len(y)/sr, "text": r["text"], "chunks": r["chunks"]}
    print(f"[{name}] text head: {r['text'][:300]}", flush=True)

json.dump(res, open(os.path.join(OUT, "result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE")
