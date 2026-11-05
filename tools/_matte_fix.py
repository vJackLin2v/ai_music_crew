
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
im = Image.open(r"H:\ai_music_crew\work\art\front_final.png").convert("RGBA")
a = np.array(im)
alpha = a[:,:,3]
# 腐蚀 1px 去白边
er = ndimage.binary_erosion(alpha > 128, iterations=2)
alpha2 = np.where(er, alpha, 0).astype(np.uint8)
# 轻微羽化
am = Image.fromarray(alpha2).filter(ImageFilter.GaussianBlur(1.2))
a[:,:,3] = np.array(am)
Image.fromarray(a, "RGBA").save(r"H:\ai_music_crew\work\art\front_clean.png")
print("ok")
