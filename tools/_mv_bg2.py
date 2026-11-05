
import os, random
from PIL import Image, ImageDraw, ImageFilter
W,H = 1920,1080
random.seed(33)
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

glow = Image.new("RGB",(W,H),(0,0,0))
gd = ImageDraw.Draw(glow)
for r in range(760,0,-14):
    a = int(5 + (760-r)*0.11)
    gd.ellipse([W*0.5-r, H*0.66-r*0.42, W*0.5+r, H*0.66+r*0.42],
               fill=(min(255,int(a*1.2)), min(255,int(a*2.0)), min(255,int(a*3.0))))
glow = glow.filter(ImageFilter.GaussianBlur(80))
img = Image.blend(img, glow, 0.9)

def layer(base_y, color, count, wmin, wmax, hmin, hmax, lit, rim):
    x = -80
    while x < W+80:
        bw = random.randint(wmin,wmax); bh = random.randint(hmin,hmax)
        top = base_y - bh
        d.rectangle([x, top, x+bw, base_y], fill=color)
        d.line([(x,top),(x+bw,top)], fill=rim, width=2)
        for wy in range(top+12, base_y-8, 18):
            for wx in range(int(x)+10, int(x+bw)-8, 16):
                if random.random() < lit:
                    c = random.choice([(255,225,160),(255,205,130),(190,225,255),(255,240,200)])
                    d.rectangle([wx, wy, wx+5, wy+8], fill=c)
        x += bw + random.randint(6, 18)

layer(int(H*0.80), (22,32,64), 40, 70, 160, 100, 250, 0.10, (70,95,150))
layer(int(H*0.88), (12,18,40), 30, 90, 210, 140, 330, 0.16, (52,72,120))

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
    x = random.randint(0,W); y = random.randint(int(H*0.08), int(H*0.9))
    r = random.randint(2,8)
    bd.ellipse([x-r,y-r,x+r,y+r], fill=(200,225,255,random.randint(30,120)))
bokeh = bokeh.filter(ImageFilter.GaussianBlur(3))
img = Image.alpha_composite(img.convert("RGBA"), bokeh).convert("RGB")
img.save(r"H:\ai_music_crew\work\mv-out\bg_city.png")

# 头像
im = Image.open(r"H:\ai_music_crew\live2d\out\frames_hd\f00010.png").convert("RGBA")
box = (270, 700, 810, 1240)
face = im.crop(box).resize((512,512), Image.LANCZOS)
mask = Image.new("L",(512,512),0)
ImageDraw.Draw(mask).ellipse([0,0,511,511], fill=255)
av = Image.new("RGBA",(512,512),(0,0,0,0))
av.paste(face,(0,0),mask)
ring = Image.new("RGBA",(512,512),(0,0,0,0))
rd2 = ImageDraw.Draw(ring)
rd2.ellipse([3,3,508,508], outline=(255,255,255,215), width=5)
av = Image.alpha_composite(av, ring)
av.save(r"H:\ai_music_crew\work\mv-out\avatar.png")
print("ok")
