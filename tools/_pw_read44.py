
import json, os
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"
WAV = r"H:\ai_music_crew\voice\xiaojingyu\record-read.wav"   # 只朗读指定段落（与界面文本一致）
ARGS = ["--no-first-run","--use-fake-ui-for-media-stream","--use-fake-device-for-media-stream",
        f"--use-file-for-fake-audio-capture={WAV}","--autoplay-policy=no-user-gesture-required"]
LOG = os.path.join(OUT,"pw-read44.txt"); open(LOG,"w",encoding="utf-8").close()
def log(*a):
    s=" ".join(str(x) for x in a); print(s,flush=True); open(LOG,"a",encoding="utf-8").write(s+"\n")
def modal(p):
    return p.evaluate("""()=>{const d=[...document.querySelectorAll('div')].filter(x=>/modal|dialog/i.test(String(x.className)));
      const l=d.sort((a,b)=>b.innerText.length-a.innerText.length)[0]; return l?l.innerText:'';}""")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-haimian", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="zh-CN", args=ARGS)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    errs=[]
    def on_resp(r):
        if "voice/info" in r.url:
            try:
                t=r.text()
                if '"status":3' in t or 'err_message' in t:
                    i=t.find("err_message")
                    if i>0: log("API-ERR>>>", t[max(0,i-120):i+80].replace("\n"," "))
            except Exception: pass
    page.on("response", on_resp)
    page.goto("https://www.haimian.com/create", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    try: page.get_by_text("我知道了", exact=True).first.click(timeout=2500)
    except Exception: pass
    for step in ["选音色","新增音色","开始清唱"]:
        try: page.get_by_text(step, exact=True).first.click(timeout=8000); log("ok",step)
        except Exception as e: log("fail",step,str(e)[:60])
        page.wait_for_timeout(1500)
    page.wait_for_timeout(24000)     # 录 24 秒（覆盖 20.7 秒朗读）
    try: page.locator("text=/^\\s*00:\\d\\d\\s*$/").last.click(timeout=5000); log("stopped")
    except Exception: log("stop fail")
    page.wait_for_timeout(2500)
    try: page.get_by_text("提交", exact=True).first.click(timeout=6000); log("submitted")
    except Exception: log("submit fail")
    for i in range(20):
        page.wait_for_timeout(10000)
        t = modal(page)
        log(f"t+{(i+1)*10}s:", t[-140:].replace("\n"," | "))
        if "制作中" not in t:
            log("END")
            break
    page.screenshot(path=os.path.join(OUT,"haimian-21-read-result.png"))
    log("FINAL:", modal(page)[-300:].replace("\n"," | "))
    ctx.close()
