
import os, time
os.environ["HTTPS_PROXY"]="http://127.0.0.1:7890"; os.environ["HTTP_PROXY"]="http://127.0.0.1:7890"
from huggingface_hub import hf_hub_download
try:
    p = hf_hub_download(repo_id="Comfy-Org/Wan_2.1_ComfyUI_repackaged",
                        filename="split_files/clip_vision/clip_vision_h.safetensors",
                        local_dir=r"H:\Comfy-Desktop\ComfyUI-Shared\models\clip_vision")
    print("OK", round(os.path.getsize(p)/1024**3,2), "GB", p, flush=True)
except Exception as e:
    print("FAIL", str(e)[:300], flush=True)
