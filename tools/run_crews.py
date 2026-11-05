
import os, sys, json, subprocess, time, re

for k in ("HTTP_PROXY","HTTPS_PROXY","http_proxy","https_proxy","ALL_PROXY","all_proxy","NO_PROXY","no_proxy"):
    os.environ.pop(k, None)
KEY_ENV = os.environ.get("LLM_KEY_ENV", "COMMANDCODE_API_KEY")
BASE = os.environ.get("LLM_BASE", "https://api.commandcode.ai/provider/v1")
MODEL = os.environ.get("LLM_MODEL", "openai/deepseek/deepseek-v4.1-flash")
key = subprocess.run(["powershell","-NoProfile","-Command",
     "[Environment]::GetEnvironmentVariable('%s','User')" % KEY_ENV],
     capture_output=True, text=True).stdout.strip()
print("[llm] %s %s (%d chars key)" % (BASE, MODEL, len(key)), flush=True)
os.environ["DEEPSEEK_API_KEY"] = key
os.environ["DEEPSEEK_API_BASE"] = BASE
os.environ["DEEPSEEK_MODEL"] = MODEL

ROOT = r"H:\ai_music_crew"
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "src")); os.chdir(ROOT)
from ai_music_crew.crews.production_crew.production_crew import ProductionCrew
from ai_music_crew.crews.output_crew.output_crew import OutputCrew

# 把 reasoning_effort=high 注到项目自己构造的 LLM 上（项目代码不改）
def _wrap_llm(cls):
    orig = cls._llm
    def patched(self):
        llm = orig(self)
        try:
            ap = dict(getattr(llm, "additional_params", None) or {})
            if ("commandcode" in BASE) or ("deepseek" in MODEL.lower()):
                ap.setdefault("reasoning_effort", "high")
            llm.additional_params = ap
        except Exception as e:
            print("[patch] llm patch failed:", e, flush=True)
        return llm
    cls._llm = patched
    return cls
_wrap_llm(ProductionCrew)
_wrap_llm(OutputCrew)
print("[patch] reasoning_effort=high applied", flush=True)

def parse_json(raw):
    if not raw: return None
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m: return None
    try: return json.loads(m.group(0))
    except Exception: return None

NAME = os.environ["SONG_NAME"]
TOPIC = os.environ["SONG_TOPIC"]
OUT = os.path.join(ROOT, "work", "flow-out"); os.makedirs(OUT, exist_ok=True)
final = os.path.join(OUT, f"{NAME}.md")

def dump_tasks(tag, result):
    rows = []
    for i, t in enumerate(getattr(result, "tasks_output", []) or []):
        rows.append(t.raw)
        with open(os.path.join(OUT, f"{NAME}.{tag}{i}.json"), "w", encoding="utf-8") as f:
            f.write(t.raw)
    return rows

t0 = time.time()
print(f"[{NAME}] production...", flush=True)
prod = ProductionCrew().crew().kickoff(inputs={
    "topic": TOPIC, "feedback": "", "instrumental_hint": "", "skill_prompt": ""})
tasks = dump_tasks("prod", prod)

brief = lyrics = arr = None
for raw in tasks:
    d = parse_json(raw)
    if not d: continue
    if "title_suggestion" in d: brief = d
    elif "verse_1" in d: lyrics = d
    elif "instruments" in d: arr = d
print(f"[{NAME}] production done {time.time()-t0:.0f}s", flush=True)

ctx = json.dumps({"brief": brief, "lyrics": lyrics, "arrangement": arr}, ensure_ascii=False)
suno = review = None
for rnd in range(2):
    print(f"[{NAME}] output/review round {rnd+1}...", flush=True)
    out = OutputCrew().crew().kickoff(inputs={
        "topic": TOPIC, "feedback": ctx, "instrumental_hint": "", "suno_override_hint": ""})
    rows = dump_tasks(f"out{rnd+1}", out)
    for raw in rows:
        d = parse_json(raw)
        if not d: continue
        if "suno_style_prompt" in d: suno = d
        elif "verdict" in d: review = d
    if review and "通过" in str(review.get("verdict", "")):
        print(f"[{NAME}] review PASSED", flush=True); break
    if review:
        ctx = json.dumps(review, ensure_ascii=False)

with open(final, "w", encoding="utf-8") as f:
    f.write(f"# {NAME}\n\n## TOPIC\n{TOPIC}\n\n")
    f.write("## BRIEF\n" + json.dumps(brief, ensure_ascii=False, indent=2) + "\n\n")
    f.write("## LYRICS\n" + json.dumps(lyrics, ensure_ascii=False, indent=2) + "\n\n")
    f.write("## ARRANGEMENT\n" + json.dumps(arr, ensure_ascii=False, indent=2) + "\n\n")
    f.write("## SUNO PROMPT\n" + json.dumps(suno, ensure_ascii=False, indent=2) + "\n\n")
    f.write("## REVIEW\n" + json.dumps(review, ensure_ascii=False, indent=2) + "\n")
print(f"[{NAME}] SAVED {final} total={time.time()-t0:.0f}s", flush=True)
