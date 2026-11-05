
import os, random
from PIL import Image, ImageDraw, ImageFilter
W,H = 1080,1920
random.seed(5)
base = Image.new("RGB",(W,H))
d = ImageDraw.Draw(base)
for y in range(H):
    t = y/H
    d.line([(0,y),(W,y)], fill=(int(10+18*t), int(22+34*t), int(46+64*t)))
# 背后光晕：径向渐变（用 L 蒙版画实心圆叠加）
glow = Image.new("RGB",(W,H),(0,0,0))
g = ImageDraw.Draw(glow)
for r in range(420, 0, -12):
    a = int(6 + (420-r)*0.16)
    g.ellipse([540-r, int(H*0.48)-r, 540+r, int(H*0.48)+r], fill=(min(255,a), min(255,int(a*1.8)), min(255,int(a*2.6))))
glow = glow.filter(ImageFilter.GaussianBlur(70))
img = Image.blend(base, glow, 0.75)
# 雨丝
dr = ImageDraw.Draw(img, "RGBA")
for _ in range(260):
    x = random.randint(-60, W+60); y = random.randint(-120, H)
    ln = random.randint(50, 180)
    dr.line([(x,y),(x-14,y+ln)], fill=(160,205,255,random.randint(12,30)), width=1)
img.save(r"H:\ai_music_crew\live2d\out\bg2.png")
print("ok", os.path.getsize(r"H:\ai_music_crew\live2d\out\bg2.png")//1024, "KB")
