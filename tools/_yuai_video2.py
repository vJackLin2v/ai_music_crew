
import os, json, subprocess
os.environ["PATH"] = r"H:\tools\ffmpeg\ffmpeg-master-latest-win64-gpl\bin;" + os.environ.get("PATH","")
FF = r"H:\tools\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
W = r"H:\ai_music_crew\work\yuai-video"
IMG = r"H:\小鲸鱼-产出\成品\专辑封面_1440.jpg"
AUD = r"H:\ai_music_crew\out\yuai-chorus\雨爱副歌_cover.wav"
SIDE = 1440

shots = [
    (0.50,0.50,1.00,"全脸"),
    (0.50,0.46,0.62,"眼睛"),
    (0.50,0.66,0.45,"嘴巴"),
    (0.50,0.90,0.55,"领结"),
    (0.24,0.45,0.55,"发丝"),
    (0.50,0.50,0.95,"全脸二"),
]
clips = []
for i,(cx,cy,size,name) in enumerate(shots):
    s = int(SIDE*size)
    x = max(0, min(SIDE-s, int(SIDE*cx - s/2)))
    yy = max(0, min(SIDE-s, int(SIDE*cy - s/2)))
    out = os.path.join(W, f"shot{i}.mp4")
    # 放大到 120% 再裁一个会缓慢平移的 1080x1920 窗口（crop 支持 t 表达式，很快）
    vf = (f"crop={s}:{s}:{x}:{yy},scale=1296:2304:flags=bicubic,"
          f"crop=1080:1920:x='(iw-1080)/2+70*sin(t*0.45+{i})':y='(ih-1920)/2-60*sin(t*0.30+{i})',"
          f"eq=saturation=1.06:gamma=1.02")
    r = subprocess.run([FF,"-y","-loop","1","-framerate","30","-t","5","-i",IMG,
                        "-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",out],
                       capture_output=True, text=True, encoding="utf-8", errors="ignore")
    print("shot", i, name, "ok" if r.returncode==0 else "FAIL " + (r.stderr or "")[-200:], flush=True)
    if r.returncode==0: clips.append(out)

lst = os.path.join(W,"list.txt")
open(lst,"w",encoding="utf-8").write("\n".join("file '%s'" % c.replace("\\","/") for c in clips))
silent = os.path.join(W,"silent.mp4")
subprocess.run([FF,"-y","-f","concat","-safe","0","-i",lst,"-c","copy",silent], check=True, capture_output=True)
final = os.path.join(W,"雨爱_竖屏_样片.mp4")
r = subprocess.run([FF,"-y","-i",silent,"-i",AUD,
    "-vf", "ass=" + os.path.join(W,"subs.ass"),
    "-map","0:v","-map","1:a","-shortest",
    "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
    "-c:a","aac","-b:a","192k", final], capture_output=True, text=True, encoding="utf-8", errors="ignore")
print("FINAL", r.returncode, final, os.path.getsize(final)//1024 if os.path.exists(final) else 0, "KB", flush=True)
