
import os, math, random
from PIL import Image, ImageDraw, ImageFilter
W,H = 1080,1920
random.seed(3)
img = Image.new("RGB",(W,H),(12,22,42))
d = ImageDraw.Draw(img)
# 竖向渐变
for y in range(H):
    t = y/H
    r = int(14 + 26*t); g = int(26 + 40*t); b = int(52 + 70*t)
    d.line([(0,y),(W,y)], fill=(r,g,b))
# 径向光晕（人物背后）
glow = Image.new("RGB",(W,H),(0,0,0))
gd = ImageDraw.Draw(glow)
for i in range(28,-1,-1):
    rad = int(160 + i*22)
    a = int(3 + (28-i)*1.1)
    gd.ellipse([W//2-rad, int(H*0.52)-rad, W//2+rad, int(H*0.52)+rad], fill=(a+40, a+85, a+130))
glow = glow.filter(ImageFilter.GaussianBlur(60))
img = Image.blend(img, glow, 0.55)
# 雨丝
d = ImageDraw.Draw(img, "RGBA")
for _ in range(220):
    x = random.randint(-50, W+50); y = random.randint(-100, H)
    ln = random.randint(40, 160)
    d.line([(x,y),(x-12,y+ln)], fill=(150,200,255,random.randint(10,26)), width=1)
# 暗角
vig = Image.new("L",(W,H),0)
vd = ImageDraw.Draw(vig)
for i in range(60):
    m = int(i*6)
    vd.ellipse([-m, -m, W+m, H+m], outline=255-int(i*4))
vig = vig.filter(ImageFilter.GaussianBlur(120))
dark = Image.new("RGB",(W,H),(0,0,0))
img = Image.composite(img, dark, vig)
out = r"H:\ai_music_crew\live2d\out\bg.png"
img.save(out)
print("bg saved", os.path.getsize(out)//1024, "KB")
