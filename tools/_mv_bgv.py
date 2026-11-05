
import random
from PIL import Image, ImageDraw, ImageFilter
W,H = 1080,1920
random.seed(14)
img = Image.new("RGB",(W,H),(8,8,14))
d = ImageDraw.Draw(img)
for y in range(H):
    t=y/H
    d.line([(0,y),(W,y)], fill=(int(7+9*t), int(8+8*t), int(14+12*t)))
bok = Image.new("RGBA",(W,H),(0,0,0,0))
bd = ImageDraw.Draw(bok)
palette = [(220,50,70),(50,110,220),(70,180,150),(230,190,90),(200,80,180),(60,60,110)]
for _ in range(30):
    cx = random.randint(-120, W+120); cy = random.randint(-120, H+120)
    r = random.randint(80, 260); c = random.choice(palette); a = random.randint(55, 140)
    bd.ellipse([cx-r,cy-r,cx+r,cy+r], fill=(c[0],c[1],c[2],a))
bok = bok.filter(ImageFilter.GaussianBlur(42))
img = Image.alpha_composite(img.convert("RGBA"), bok).convert("RGB")
vig = Image.new("L",(W,H),0)
ImageDraw.Draw(vig).ellipse([-140,-120,W+140,H+120], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(150))
img = Image.composite(img, Image.new("RGB",(W,H),(4,4,8)), vig)
img.save(r"H:\ai_music_crew\work\mv-out\bg_bokeh_v.png")
print("vertical bg ok")
