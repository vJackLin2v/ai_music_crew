
import os, sys, subprocess
for k in ("HTTP_PROXY","HTTPS_PROXY","http_proxy","https_proxy","ALL_PROXY","all_proxy","NO_PROXY","no_proxy"):
    os.environ.pop(k, None)
key = subprocess.run(["powershell","-NoProfile","-Command",
     "[Environment]::GetEnvironmentVariable('COMMANDCODE_API_KEY','User')"],
     capture_output=True, text=True).stdout.strip()
os.environ["DEEPSEEK_API_KEY"] = key
os.environ["DEEPSEEK_API_BASE"] = "https://api.commandcode.ai/provider/v1"
os.environ["DEEPSEEK_MODEL"] = "openai/deepseek/deepseek-v4.1-flash"

ROOT = r"H:\ai_music_crew"
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "src")); os.chdir(ROOT)
from ai_music_crew.main import SongFlow

TOPIC = os.environ.get("SONG_TOPIC") or (
  "写一首歌名叫《荒》的国风流行：苍凉、大编制弦乐与二胡，女声清亮偏气声，"
  "主题是荒原上的等待与不肯回头。要有金句、有画面感、不要堆砌辞藻，时长两分半到三分钟。")
print("TOPIC:", TOPIC, flush=True)
SongFlow().kickoff(inputs={"trigger": {"topic": TOPIC}})
print("FLOW DONE", flush=True)
