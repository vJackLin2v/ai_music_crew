
import os, sys, time
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
from huggingface_hub import hf_hub_download

REPO = "Comfy-Org/Wan_2.2_ComfyUI_Repackaged"
BASE = r"H:\Comfy-Desktop\ComfyUI-Shared\models"
jobs = [
    ("split_files/diffusion_models/wan2.2_animate_14B_int8_convrot.safetensors", "diffusion_models"),
    ("split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors", "text_encoders"),
    ("split_files/vae/wan_2.1_vae.safetensors", "vae"),
    ("split_files/loras/wan2.2_animate_14B_relight_lora_bf16.safetensors", "loras"),
]
for i, (fn, sub) in enumerate(jobs, 1):
    dest = os.path.join(BASE, sub)
    os.makedirs(dest, exist_ok=True)
    print(f"[{i}/{len(jobs)}] {fn}", flush=True)
    t0 = time.time()
    try:
        p = hf_hub_download(repo_id=REPO, filename=fn, local_dir=dest, local_dir_use_symlinks=False)
        sz = os.path.getsize(p) / 1024**3
        print(f"    OK {sz:.2f}GB in {time.time()-t0:.0f}s -> {p}", flush=True)
    except Exception as e:
        print("    FAIL", str(e)[:200], flush=True)
print("DONE", flush=True)
