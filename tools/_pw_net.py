
import json, os
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"
WAV = r"H:\ai_music_crew\voice\xiaojingyu\record-sing.wav"   # 纯清唱 32 秒
ARGS = ["--no-first-run","--use-fake-ui-for-media-stream","--use-fake-device-for-media-stream",
        f"--use-file-for-fake-audio-capture={WAV}","--autoplay-policy=no-user-gesture-required"]
LOG = os.path.join(OUT,"pw-net.txt"); open(LOG,"w",encoding="utf-8").close()
def log(*a):
    s=" ".join(str(x) for x in a); print(s,flush=True); open(LOG,"a",encoding="utf-8").write(s+"\n")
def modal(page):
    return page.evaluate("""()=>{const d=[...document.querySelectorAll('div')].filter(x=>/modal|dialog/i.test(String(x.className)));
      const l=d.sort((a,b)=>b.innerText.length-a.innerText.length)[0]; return l?l.innerText:'';}""")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-haimian", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="zh-CN", args=ARGS)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()

    def on_resp(r):
        u = r.url
        if any(k in u.lower() for k in ("voice","timbre","clone","train","audio","upload","record")):
            try:
                body = r.text()[:400]
            except Exception:
                body = "<binary>"
            log("NET", r.status, u[:140], "|", body.replace("\n"," ")[:300])
    page.on("response", on_resp)

    page.goto("https://www.haimian.com/create", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    try: page.get_by_text("我知道了", exact=True).first.click(timeout=2500)
    except Exception: pass
    for step in ["选音色","新增音色","开始清唱"]:
        try: page.get_by_text(step, exact=True).first.click(timeout=8000); log("ok",step)
        except Exception as e: log("fail",step,str(e)[:60])
        page.wait_for_timeout(1500)
    page.wait_for_timeout(35000)
    try: page.locator("text=/^\\s*00:\\d\\d\\s*$/").last.click(timeout=5000); log("stopped")
    except Exception as e: log("stop fail",str(e)[:60])
    page.wait_for_timeout(2500)
    try: page.get_by_text("提交", exact=True).first.click(timeout=6000); log("submitted")
    except Exception as e: log("submit fail",str(e)[:60])
    for i in range(24):
        page.wait_for_timeout(10000)
        t = modal(page)
        log(f"t+{(i+1)*10}s:", t[-160:].replace("\n"," | "))
        if "制作中" not in t:
            log("DONE")
            break
    page.screenshot(path=os.path.join(OUT,"haimian-20-final2.png"))
    log("FINAL MODAL:", modal(page)[-300:].replace("\n"," | "))
    ctx.close()
