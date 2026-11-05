
import os
from PIL import Image
src = r"H:\ai_music_crew\live2d\out\frames_hd"
dst = r"H:\ai_music_crew\work\mv-out\char_l"
os.makedirs(dst, exist_ok=True)
files = sorted(os.listdir(src))[:900]
for i, f in enumerate(files):
    im = Image.open(os.path.join(src, f)).convert("RGBA")
    c = im.crop((120, 430, 960, 1500))
    s = 1150 / c.height
    c = c.resize((int(c.width*s), 1150), Image.LANCZOS)
    canvas = Image.new("RGBA", (1920,1080), (0,0,0,0))
    canvas.alpha_composite(c, (1920 - c.width - 60, (1080-c.height)//2 + 40))
    canvas.save(os.path.join(dst, f"c{i:05d}.png"))
print("char frames ok", len(files))
