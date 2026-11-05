
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = r"H:\小鲸鱼-产出\立绘-三视图.png"
OUTDIR = r"H:\ai_music_crew\work\art"
os.makedirs(OUTDIR, exist_ok=True)
if not os.path.exists(SRC):
    print("MISSING:", SRC); sys.exit(2)

im = Image.open(SRC).convert("RGB")
W, H = im.size
print("原图:", W, "x", H)

# 1) 竖切三栏（三视图一般等分）
third = W // 3
front = im.crop((0, 0, third, H))
front.save(os.path.join(OUTDIR, "front_raw.png"))

# 2) 白底转透明（从四角泛洪）
def white_to_alpha(img, thr=238):
    arr = np.array(img.convert("RGB")).astype(np.int16)
    # 近白像素
    mask = (arr[:,:,0] >= thr) & (arr[:,:,1] >= thr) & (arr[:,:,2] >= thr)
    from scipy import ndimage
    # 只去掉与边缘连通的白色，避免吃掉衣服里的白
    seed = np.zeros_like(mask)
    seed[0,:] = mask[0,:]; seed[-1,:] = mask[-1,:]
    seed[:,0] = mask[:,0]; seed[:,-1] = mask[:,-1]
    lbl, n = ndimage.label(mask)
    keep = np.zeros_like(mask)
    for i in set(lbl[seed].tolist()):
        if i == 0: continue
        keep |= (lbl == i)
    alpha = np.where(keep, 0, 255).astype(np.uint8)
    rgb = np.array(img.convert("RGB"))
    out = np.dstack([rgb, alpha])
    return Image.fromarray(out, "RGBA")

fg = white_to_alpha(front)
bbox = fg.split()[-1].getbbox()
if bbox:
    fg = fg.crop(bbox)
fg.save(os.path.join(OUTDIR, "front_alpha.png"))
print("抠图完成:", fg.size)

# 3) 放大到 1536 高
scale = 1536 / fg.height
fg2 = fg.resize((max(1,int(fg.width*scale)), 1536), Image.LANCZOS)
fg2.save(os.path.join(OUTDIR, "front_final.png"))
print("输出:", os.path.join(OUTDIR, "front_final.png"), fg2.size)
