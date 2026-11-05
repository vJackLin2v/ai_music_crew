
import os
import numpy as np
from PIL import Image
from scipy import ndimage
SRC = r"H:\小鲸鱼-产出\立绘-三视图.png"
OUT = r"H:\ai_music_crew\work\art"
os.makedirs(OUT, exist_ok=True)
im = Image.open(SRC).convert("RGB")
W,H = im.size
print("尺寸:", W, H)
third = W // 3
front = im.crop((0,0,third,H))
front.save(os.path.join(OUT,"front_raw.png"))

arr = np.array(front).astype(np.int16)
mask = (arr[:,:,0]>=236)&(arr[:,:,1]>=236)&(arr[:,:,2]>=236)
seed = np.zeros_like(mask)
seed[0,:]=mask[0,:]; seed[-1,:]=mask[-1,:]; seed[:,0]=mask[:,0]; seed[:,-1]=mask[:,-1]
lbl,n = ndimage.label(mask)
keep = np.zeros_like(mask)
for i in set(lbl[seed].tolist()):
    if i: keep |= (lbl==i)
alpha = np.where(keep,0,255).astype(np.uint8)
fg = Image.fromarray(np.dstack([np.array(front), alpha]), "RGBA")
bb = fg.split()[-1].getbbox()
if bb: fg = fg.crop(bb)
print("抠图后:", fg.size)
fg.save(os.path.join(OUT,"front_alpha.png"))
sc = 1536/fg.height
fg2 = fg.resize((int(fg.width*sc),1536), Image.LANCZOS)
fg2.save(os.path.join(OUT,"front_final.png"))
print("输出:", fg2.size)
