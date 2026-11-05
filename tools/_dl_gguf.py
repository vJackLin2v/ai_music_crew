
import os, time
os.environ["HTTPS_PROXY"]="http://127.0.0.1:7890"; os.environ["HTTP_PROXY"]="http://127.0.0.1:7890"
from huggingface_hub import hf_hub_download
t0=time.time()
try:
    p = hf_hub_download(repo_id="QuantStack/Wan2.2-Animate-14B-GGUF",
                        filename="Wan2.2-Animate-14B-Q4_K_S.gguf",
                        local_dir=r"H:\Comfy-Desktop\ComfyUI-Shared\models\diffusion_models")
    print("OK", round(os.path.getsize(p)/1024**3,2), "GB", round(time.time()-t0), "s", flush=True)
    print("PATH", p, flush=True)
except Exception as e:
    print("FAIL", str(e)[:200], flush=True)
