
import json, os, time
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"
LOG = os.path.join(OUT, "suno-login.txt")
os.makedirs(OUT, exist_ok=True)
open(LOG,"w",encoding="utf-8").close()
def log(*a):
    s=" ".join(str(x) for x in a); print(s,flush=True); open(LOG,"a",encoding="utf-8").write(s+"\n")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-suno", channel="msedge", headless=False,
        viewport={"width":1440,"height":900}, locale="en-US",
        args=["--no-first-run","--disable-blink-features=AutomationControlled"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(6000)
    page.screenshot(path=os.path.join(OUT,"suno-01.png"))
    txt = page.evaluate("() => document.body ? document.body.innerText.slice(0,600) : ''")
    log("URL:", page.url)
    log("TEXT:", txt.replace("\n"," | ")[:400])

    logged = False
    for i in range(150):     # 最多 12.5 分钟
        page.wait_for_timeout(5000)
        try:
            t = page.evaluate("() => document.body ? document.body.innerText : ''")
        except Exception:
            continue
        has_login = ("Sign in" in t) or ("Log in" in t) or ("Sign up" in t)
        has_create = ("Create" in t) and ("Song" in t or "Lyrics" in t)
        if has_create and not has_login:
            logged = True; log(f"LOGIN DETECTED ~{(i+1)*5}s"); break
        if i % 12 == 0: log(f"waiting login... {i*5}s")
    page.screenshot(path=os.path.join(OUT,"suno-02.png"))
    log("LOGGED:", logged)
    if logged:
        # 探一下创作页结构
        info = page.evaluate("""() => ({
           buttons: [...document.querySelectorAll('button')].map(b=>b.innerText.trim()).filter(Boolean).slice(0,25),
           textareas: [...document.querySelectorAll('textarea')].length,
           inputs: [...document.querySelectorAll('input')].map(i=>i.placeholder||i.type).slice(0,10),
        })""")
        log("UI:", json.dumps(info, ensure_ascii=False)[:600])
    ctx.close()
