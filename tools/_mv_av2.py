
from PIL import Image, ImageDraw
im = Image.open(r"H:\ai_music_crew\live2d\out\frames_hd\f00010.png").convert("RGBA")
box = (250, 620, 830, 1200)
face = im.crop(box).resize((512,512), Image.LANCZOS)
mask = Image.new("L",(512,512),0)
ImageDraw.Draw(mask).ellipse([0,0,511,511], fill=255)
av = Image.new("RGBA",(512,512),(0,0,0,0))
av.paste(face,(0,0),mask)
ring = Image.new("RGBA",(512,512),(0,0,0,0))
ImageDraw.Draw(ring).ellipse([3,3,508,508], outline=(255,255,255,215), width=5)
Image.alpha_composite(av, ring).save(r"H:\ai_music_crew\work\mv-out\avatar.png")
print("avatar ok")
