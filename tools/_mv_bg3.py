
import os, random
from PIL import Image, ImageDraw, ImageFilter
W,H = 1920,1080
random.seed(33)

# 1. 天空
img = Image.new("RGB",(W,H))
d = ImageDraw.Draw(img)
for y in range(H):
    t = y/H
    if t < 0.60:
        k = t/0.60
        col = (int(10+16*k), int(18+34*k), int(48+64*k))
    else:
        k = (t-0.60)/0.40
        col = (int(26+4*k), int(52+4*k), int(112-36*k))
    d.line([(0,y),(W,y)], fill=col)

# 2. 光晕（先加，再画楼）
glow = Image.new("RGB",(W,H),(0,0,0))
gd = ImageDraw.Draw(glow)
for r in range(760,0,-14):
    a = int(5 + (760-r)*0.11)
    gd.ellipse([W*0.5-r, H*0.68-r*0.42, W*0.5+r, H*0.68+r*0.42],
               fill=(min(255,int(a*1.2)), min(255,int(a*2.0)), min(255,int(a*3.0))))
glow = glow.filter(ImageFilter.GaussianBlur(80))
img = Image.blend(img, glow, 0.55)
d = ImageDraw.Draw(img)

# 3. 楼群（画在光晕之后）
def layer(base_y, color, wmin, wmax, hmin, hmax, lit, rim):
    x = -80
    while x < W+80:
        bw = random.randint(wmin,wmax); bh = random.randint(hmin,hmax)
        top = base_y - bh
        d.rectangle([x, top, x+bw, base_y], fill=color)
        d.line([(x,top),(x+bw,top)], fill=rim, width=2)
        for wy in range(int(top)+12, base_y-8, 18):
            for wx in range(int(x)+10, int(x+bw)-8, 16):
                if random.random() < lit:
                    c = random.choice([(255,225,160),(255,205,130),(190,225,255),(255,240,200)])
                    d.rectangle([wx, wy, wx+5, wy+8], fill=c)
        x += bw + random.randint(6, 18)

layer(int(H*0.82), (16,24,50), 70, 160, 100, 240, 0.14, (60,84,140))
layer(int(H*0.90), (9,14,32), 90, 210, 140, 330, 0.20, (46,64,110))

# 4. 雨 + 光斑
rain = Image.new("RGBA",(W,H),(0,0,0,0))
rd = ImageDraw.Draw(rain)
for _ in range(800):
    x = random.randint(-100, W+100); y = random.randint(-150, H)
    ln = random.randint(30, 130)
    rd.line([(x,y),(x-10,y+ln)], fill=(170,200,255,random.randint(8,30)), width=1)
img = Image.alpha_composite(img.convert("RGBA"), rain).convert("RGB")

bokeh = Image.new("RGBA",(W,H),(0,0,0,0))
bd = ImageDraw.Draw(bokeh)
for _ in range(70):
    x = random.randint(0,W); y = random.randint(int(H*0.08), int(H*0.92))
    r = random.randint(2,8)
    bd.ellipse([x-r,y-r,x+r,y+r], fill=(200,225,255,random.randint(30,120)))
img = Image.alpha_composite(img.convert("RGBA"), bokeh.filter(ImageFilter.GaussianBlur(3))).convert("RGB")
img.save(r"H:\ai_music_crew\work\mv-out\bg_city.png")
print("ok")
