
import random
from PIL import Image, ImageDraw, ImageFilter
W,H = 1920,1080
random.seed(9)
img = Image.new("RGB",(W,H),(10,10,18))
d = ImageDraw.Draw(img)
for y in range(H):
    t=y/H
    d.line([(0,y),(W,y)], fill=(int(8+10*t), int(9+8*t), int(16+14*t)))
# 大光斑
bok = Image.new("RGBA",(W,H),(0,0,0,0))
bd = ImageDraw.Draw(bok)
palette = [(220,40,60),(60,110,220),(80,180,150),(230,190,90),(200,80,180),(70,70,120)]
for _ in range(26):
    cx = random.randint(-150, W+150); cy = random.randint(-100, H+100)
    r = random.randint(70, 230)
    c = random.choice(palette)
    a = random.randint(60, 150)
    bd.ellipse([cx-r,cy-r,cx+r,cy+r], fill=(c[0],c[1],c[2],a))
bok = bok.filter(ImageFilter.GaussianBlur(38))
img = Image.alpha_composite(img.convert("RGBA"), bok).convert("RGB")
# 暗角
vig = Image.new("L",(W,H),0)
ImageDraw.Draw(vig).ellipse([-260,-180,W+260,H+180], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(180))
img = Image.composite(img, Image.new("RGB",(W,H),(4,4,8)), vig)
img.save(r"H:\ai_music_crew\work\mv-out\bg_bokeh.png")
print("bg ok")

# 角色：从 Live2D 帧裁半身，铺到右侧
fr = Image.open(r"H:\ai_music_crew\live2d\out\frames_hd\f00010.png").convert("RGBA")
crop = fr.crop((120, 430, 960, 1500))          # 头部到胸口
scale = 1150 / crop.height
crop = crop.resize((int(crop.width*scale), 1150), Image.LANCZOS)
canvas = Image.open(r"H:\ai_music_crew\work\mv-out\bg_bokeh.png").convert("RGBA")
x = 1920 - crop.width - 60
y = (1080 - crop.height) // 2 + 40
canvas.alpha_composite(crop, (max(0,x), max(0,y)))
canvas.convert("RGB").save(r"H:\ai_music_crew\work\mv-out\test_frame.png")
print("frame ok", crop.size)
