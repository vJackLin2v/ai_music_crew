
import json, os, subprocess, sys
ROOT = r"H:\ai_music_crew"
songs = json.load(open(os.path.join(ROOT, "work", "songs", "five_songs.json"), encoding="utf-8"))
target = [s for s in songs if s["name"] == "荒"][0]
env = os.environ.copy()
for k in ("HTTP_PROXY","HTTPS_PROXY","http_proxy","https_proxy","ALL_PROXY","all_proxy","NO_PROXY","no_proxy"):
    env.pop(k, None)
env["SONG_NAME"] = target["name"]; env["SONG_TOPIC"] = target["topic"]
r = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "run_crews.py")],
                   cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="ignore")
print("exit", r.returncode)
print((r.stdout or "")[-500:])
