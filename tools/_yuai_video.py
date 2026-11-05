
import os, json, subprocess, math
os.environ["PATH"] = r"H:\tools\ffmpeg\ffmpeg-master-latest-win64-gpl\bin;" + os.environ.get("PATH","")
import librosa, torch
from transformers import pipeline

FF = r"H:\tools\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
W = r"H:\ai_music_crew\work\yuai-video"
os.makedirs(W, exist_ok=True)
IMG = r"H:\小鲸鱼-产出\成品\专辑封面_1440.jpg"
AUD = r"H:\ai_music_crew\out\yuai-chorus\雨爱副歌_cover.wav"
CUT = r"H:\ai_music_crew\work\yuai-chorus\雨爱副歌.mp3"

# 1) 对切好的副歌做人声对齐（用原唱音轨，字更清楚）
y, sr = librosa.load(CUT, sr=16000, mono=True)
pipe = pipeline("automatic-speech-recognition", model="openai/whisper-small", device=0 if torch.cuda.is_available() else -1)
r = pipe(y, return_timestamps=True, generate_kwargs={"language":"zh","task":"transcribe"})
segs = [{"t0": float(c["timestamp"][0] or 0), "t1": float(c["timestamp"][1] or 0), "text": c["text"].strip()} for c in r.get("chunks", [])]
json.dump(segs, open(os.path.join(W,"segs.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
for s in segs: print(f"  [{s['t0']:.1f}-{s['t1']:.1f}] {s['text']}")

# 2) 生成 ASS（逐字卡拉OK）
def ts(t):
    h=int(t//3600); m=int((t%3600)//60); s=t%60
    return f"{h}:{m:02d}:{s:05.2f}"
head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Kara,Microsoft YaHei,74,&H00FFFFFF,&H0055CCFF,&H00101820,&H60000000,1,0,0,0,100,100,2,0,1,7,4,2,50,50,240,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
lines=[]
for s in segs:
    txt = s["text"].replace(" ","")
    if not txt or s["t1"]<=s["t0"]: continue
    dur = s["t1"]-s["t0"]
    per = max(1, int(dur*100/max(1,len(txt))))
    kara = "".join(f"{{\\k{per}}}{ch}" for ch in txt)
    lines.append(f"Dialogue: 0,{ts(s['t0'])},{ts(s['t1'])},Kara,,0,0,0,,{{\\fad(120,120)}}{kara}")
open(os.path.join(W,"subs.ass"),"w",encoding="utf-8-sig").write(head + "\n".join(lines) + "\n")

# 3) 六个镜头（同一张图的不同裁切）
shots = [
    (0.50,0.50,1.00,"全脸"),
    (0.50,0.46,0.62,"眼睛"),
    (0.50,0.66,0.45,"嘴巴"),
    (0.50,0.90,0.55,"领结"),
    (0.24,0.45,0.55,"发丝"),
    (0.50,0.50,0.95,"全脸二"),
]
SIDE = 1440
clips=[]
for i,(cx,cy,size,name) in enumerate(shots):
    s = int(SIDE*size)
    x = max(0, min(SIDE-s, int(SIDE*cx - s/2)))
    yy = max(0, min(SIDE-s, int(SIDE*cy - s/2)))
    dur = 5 if i < 5 else 5
    out = os.path.join(W, f"shot{i}.mp4")
    vf = (f"crop={s}:{s}:{x}:{yy},scale=1080:1920:force_original_aspect_ratio=increase,"
          f"crop=1080:1920,zoompan=z='min(zoom+0.0007,1.10)':d={dur*30}:s=1080x1920:fps=30,"
          f"eq=saturation=1.06:gamma=1.02")
    subprocess.run([FF,"-y","-loop","1","-framerate","30","-t",str(dur),"-i",IMG,
                    "-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",out],
                   check=True, capture_output=True)
    clips.append(out)
    print("shot", i, name, "ok")

# 4) 拼接 + 字幕 + 音频
lst = os.path.join(W,"list.txt")
open(lst,"w",encoding="utf-8").write("\n".join(f"file '{c.replace(chr(92),'/')}'" for c in clips))
silent = os.path.join(W,"silent.mp4")
subprocess.run([FF,"-y","-f","concat","-safe","0","-i",lst,"-c","copy",silent], check=True, capture_output=True)
final = os.path.join(W,"雨爱_竖屏_样片.mp4")
subprocess.run([FF,"-y","-i",silent,"-i",AUD,
                "-vf", f"ass={os.path.join(W,'subs.ass')}",
                "-map","0:v","-map","1:a","-shortest",
                "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
                "-c:a","aac","-b:a","192k", final], check=True, capture_output=True)
print("FINAL", final, os.path.getsize(final)//1024, "KB")
