
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = r"H:\ai_music_crew\work\art\front_clean.png"
OUT = r"H:\ai_music_crew\work\puppet"
os.makedirs(OUT, exist_ok=True)
FPS = 30
N = 900
CH_H = 1560
POS_X, POS_Y = 300, 380
CANVAS = (1080, 1920)

im = Image.open(SRC).convert("RGBA")
scale = CH_H / im.height
cw, ch = int(im.width*scale), CH_H
im = im.resize((cw, ch), Image.LANCZOS)
print("character:", cw, ch)

# 平滑混合蒙版：上部=1（跟随旋转），下部=0
mask = np.zeros((ch, cw), dtype=np.float32)
y0, y1 = int(ch*0.42), int(ch*0.58)
for y in range(ch):
    if y < y0: v = 1.0
    elif y > y1: v = 0.0
    else:
        t = (y - y0) / max(1, (y1 - y0))
        v = float(0.5 - 0.5*math.cos(math.pi*(1-t)))   # smoothstep
    mask[y, :] = v
MaskImg = Image.fromarray((mask*255).astype(np.uint8))

pivot = (cw/2, ch*0.46)
for i in range(N):
    t = i / FPS
    # 头部摆动
    ang = math.radians(1.6*math.sin(2*math.pi*t/4.2) + 0.5*math.sin(2*math.pi*t/1.9))
    # 呼吸：竖向缩放
    br = 1.0 + 0.006*math.sin(2*math.pi*t/3.4)
    # 整体上下浮动
    bob = 7*math.sin(2*math.pi*t/3.8)

    rot = im.rotate(math.degrees(ang), resample=Image.BICUBIC, center=pivot)
    body_scaled = im.resize((cw, int(round(ch*br))), Image.LANCZOS)
    # 呼吸以底边为锚点
    layer = Image.new("RGBA", (cw, ch), (0,0,0,0))
    layer.alpha_composite(body_scaled, (0, ch - body_scaled.height))
    # 上部用旋转版、下部用呼吸版
    frame = Image.composite(rot, layer, MaskImg)

    canvas = Image.new("RGBA", CANVAS, (0,0,0,0))
    canvas.alpha_composite(frame, (POS_X, int(POS_Y + bob)))
    canvas.save(os.path.join(OUT, f"p{i:05d}.png"))
    if i % 150 == 0:
        print("frame", i, flush=True)
print("done", N)
