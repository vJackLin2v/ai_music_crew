
import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = r"H:\ai_music_crew"
JOBS = os.environ.get("JOBS_FILE", "ten_songs.json")
SONGS = json.load(open(os.path.join(ROOT, "work", "songs", JOBS), encoding="utf-8"))
OUT = os.path.join(ROOT, "work", "flow-out"); os.makedirs(OUT, exist_ok=True)
WORKERS = int(os.environ.get("WORKERS", "5"))

def run_one(s):
    final = os.path.join(OUT, f"{s['name']}.md")
    if os.path.exists(final) and os.path.getsize(final) > 800:
        return f"{s['name']} 跳过（已存在）"
    env = os.environ.copy()
    for k in ("HTTP_PROXY","HTTPS_PROXY","http_proxy","https_proxy","ALL_PROXY","all_proxy","NO_PROXY","no_proxy"):
        env.pop(k, None)
    env["SONG_NAME"] = s["name"]; env["SONG_TOPIC"] = s["topic"]
    t0 = time.time()
    r = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "run_crews.py")],
                       cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return f"{s['name']} exit={r.returncode} {time.time()-t0:.0f}s"

print(f"批量开始：{len(SONGS)} 首，并发 {WORKERS}", flush=True)
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = {ex.submit(run_one, s): s for s in SONGS}
    for f in as_completed(futs):
        print(f.result(), flush=True)
print("ALL DONE", flush=True)
