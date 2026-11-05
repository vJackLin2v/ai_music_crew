
import os, random, math
from PIL import Image, ImageDraw, ImageFilter
W,H = 1920,1080
random.seed(21)

img = Image.new("RGB",(W,H))
d = ImageDraw.Draw(img)
# 天空渐变
for y in range(H):
    t = y/H
    if t < 0.55:
        k = t/0.55
        col = (int(8+14*k), int(14+30*k), int(40+60*k))
    else:
        k = (t-0.55)/0.45
        col = (int(22+6*k), int(44+8*k), int(100-30*k))
    d.line([(0,y),(W,y)], fill=col)

# 地平线光晕
glow = Image.new("RGB",(W,H),(0,0,0))
gd = ImageDraw.Draw(glow)
for r in range(700,0,-14):
    a = int(4 + (700-r)*0.09)
    gd.ellipse([W*0.5-r, H*0.62-r*0.45, W*0.5+r, H*0.62+r*0.45],
               fill=(min(255,int(a*1.1)), min(255,int(a*1.9)), min(255,int(a*2.8))))
glow = glow.filter(ImageFilter.GaussianBlur(90))
img = Image.blend(img, glow, 0.85)

# 楼群（两层，远浅近深）
def buildings(layer_top, color, count, wmin, wmax, hmin, hmax, lit_prob):
    x = -60
    while x < W+60:
        bw = random.randint(wmin,wmax)
        bh = random.randint(hmin,hmax)
        top = layer_top - bh
        d.rectangle([x, top, x+bw, layer_top], fill=color)
        # 窗户
        if lit_prob > 0:
            for wy in range(top+10, layer_top-6, 16):
                for wx in range(int(x)+8, int(x+bw)-6, 14):
                    if random.random() < lit_prob:
                        c = random.choice([(255,220,150),(255,200,120),(180,220,255)])
                        d.rectangle([wx, wy, wx+4, wy+7], fill=c)
        x += bw + random.randint(4, 16)

buildings(int(H*0.78), (18,28,58), 40, 60, 150, 90, 260, 0.05)
buildings(int(H*0.86), (10,16,36), 34, 80, 200, 120, 320, 0.10)

# 雨丝
rain = Image.new("RGBA",(W,H),(0,0,0,0))
rd = ImageDraw.Draw(rain)
for _ in range(900):
    x = random.randint(-100, W+100); y = random.randint(-150, H)
    ln = random.randint(30, 120)
    rd.line([(x,y),(x-10,y+ln)], fill=(170,200,255,random.randint(10,34)), width=1)
img = Image.alpha_composite(img.convert("RGBA"), rain).convert("RGB")

# 光斑粒子
bokeh = Image.new("RGBA",(W,H),(0,0,0,0))
bd = ImageDraw.Draw(bokeh)
for _ in range(60):
    x = random.randint(0,W); y = random.randint(int(H*0.05), int(H*0.85))
    r = random.randint(2,7)
    bd.ellipse([x-r,y-r,x+r,y+r], fill=(200,225,255,random.randint(30,110)))
bokeh = bokeh.filter(ImageFilter.GaussianBlur(3))
img = Image.alpha_composite(img.convert("RGBA"), bokeh).convert("RGB")
img.save(r"H:\ai_music_crew\work\mv-out\bg_city.png")
print("bg ok")

# 头像：从 Live2D 帧裁脸做圆形
fr = r"H:\ai_music_crew\live2d\out\frames_hd\f00010.png"
im = Image.open(fr).convert("RGBA")
# 脸部大致区域（1080x1920 中）
box = (150, 380, 930, 1160)
face = im.crop(box).resize((512,512), Image.LANCZOS)
mask = Image.new("L",(512,512),0)
md = ImageDraw.Draw(mask)
md.ellipse([0,0,511,511], fill=255)
av = Image.new("RGBA",(512,512),(0,0,0,0))
av.paste(face, (0,0), mask)
# 外圈白边
ring = Image.new("RGBA",(512,512),(0,0,0,0))
rd2 = ImageDraw.Draw(ring)
for i in range(3):
    rd2.ellipse([i*2, i*2, 511-i*2, 511-i*2], outline=(255,255,255,200), width=4)
av = Image.alpha_composite(av, ring)
os.makedirs(r"H:\ai_music_crew\work\mv-out", exist_ok=True)
av.save(r"H:\ai_music_crew\work\mv-out\avatar.png")
print("avatar ok")
