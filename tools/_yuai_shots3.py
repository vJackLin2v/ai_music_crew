
import os, subprocess
FF = r"H:\tools\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
W = r"H:\ai_music_crew\work\yuai-video"
IMG = r"H:\小鲸鱼-产出\成品\专辑封面_1440.jpg"
SIDE = 1440
shots = [
    (0.50,0.48,1.00,"全脸"),
    (0.50,0.42,0.76,"上半脸"),
    (0.50,0.55,0.92,"脸与手"),
    (0.50,0.44,0.58,"眼睛"),
    (0.50,0.86,0.52,"领结"),
    (0.50,0.50,1.00,"全脸收"),
]
clips=[]
for i,(cx,cy,size,name) in enumerate(shots):
    s = int(SIDE*size); x = max(0, min(SIDE-s, int(SIDE*cx - s/2))); yy = max(0, min(SIDE-s, int(SIDE*cy - s/2)))
    out = os.path.join(W, f"shot{i}.mp4")
    vf = (f"crop={s}:{s}:{x}:{yy},scale=1296:2304:flags=bicubic,"
          f"crop=1080:1920:x='(iw-1080)/2+55*sin(t*0.40+{i})':y='(ih-1920)/2-45*sin(t*0.28+{i})',"
          f"eq=saturation=1.02:gamma=1.0")
    r = subprocess.run([FF,"-y","-loop","1","-framerate","30","-t","5","-i",IMG,"-vf",vf,
        "-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",out],
        capture_output=True, text=True, encoding="utf-8", errors="ignore")
    print("shot", i, name, "ok" if r.returncode==0 else "FAIL", flush=True)
    if r.returncode==0: clips.append(out)
open(os.path.join(W,"list.txt"),"w",encoding="utf-8").write("\n".join("file '%s'" % c.replace(chr(92),"/") for c in clips))
subprocess.run([FF,"-y","-f","concat","-safe","0","-i",os.path.join(W,"list.txt"),"-c","copy",os.path.join(W,"silent.mp4")],
               check=True, capture_output=True)
print("concat ok", flush=True)
