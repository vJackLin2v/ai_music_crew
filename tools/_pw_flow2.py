
import json, os, time
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"
WAV = r"H:\ai_music_crew\voice\xiaojingyu\record-mix.wav"
ARGS = ["--no-first-run","--use-fake-ui-for-media-stream","--use-fake-device-for-media-stream",
        f"--use-file-for-fake-audio-capture={WAV}","--autoplay-policy=no-user-gesture-required"]
LOG = os.path.join(OUT,"pw-flow2.txt"); open(LOG,"w",encoding="utf-8").close()
def log(*a):
    s=" ".join(str(x) for x in a); print(s,flush=True); open(LOG,"a",encoding="utf-8").write(s+"\n")
def modal(page):
    return page.evaluate("""()=>{const d=[...document.querySelectorAll('div')].filter(x=>/modal|dialog/i.test(String(x.className)));
      const l=d.sort((a,b)=>b.innerText.length-a.innerText.length)[0]; return l?l.innerText:'';}""")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-haimian", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="zh-CN", args=ARGS)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    # 1) 资产页勘察
    page.goto("https://www.haimian.com/assets", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    page.screenshot(path=os.path.join(OUT,"haimian-18-assets.png"))
    log("ASSETS URL:", page.url)
    log("ASSETS TEXT:", page.evaluate("()=>document.body.innerText")[:400].replace("\n"," | "))
    log("ASSETS 音色 hits:", page.evaluate("""()=>{const o=[];for(const e of document.querySelectorAll('*')){const t=(e.childElementCount===0?(e.textContent||''):'').trim();if(t&&t.length<24&&/音色|我的/.test(t))o.push(t);}return [...new Set(o)].slice(0,15)}"""))

    # 2) 重新录制并等训练完成
    page.goto("https://www.haimian.com/create", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    try: page.get_by_text("我知道了", exact=True).first.click(timeout=2500)
    except Exception: pass
    for step in ["选音色","新增音色","开始清唱"]:
        try: page.get_by_text(step, exact=True).first.click(timeout=8000); log("ok",step)
        except Exception as e: log("fail",step,str(e)[:60])
        page.wait_for_timeout(1500)
    page.wait_for_timeout(42000)
    try: page.locator("text=/^\\s*00:\\d\\d\\s*$/").last.click(timeout=5000); log("stopped")
    except Exception as e: log("stop fail",str(e)[:60])
    page.wait_for_timeout(2500)
    try: page.get_by_text("提交", exact=True).first.click(timeout=6000); log("submitted")
    except Exception as e: log("submit fail",str(e)[:60])
    # 3) 等训练
    for i in range(36):
        page.wait_for_timeout(10000)
        t = modal(page)
        tail = t[-200:].replace("\n"," | ")
        log(f"t+{(i+1)*10}s:", tail)
        if "制作中" not in t:
            log("TRAINING DONE/ENDED")
            break
    page.screenshot(path=os.path.join(OUT,"haimian-19-training-end.png"))
    log("MODAL END:", modal(page)[-400:].replace("\n"," | "))
    log("IMGS:", page.evaluate("""()=>[...document.querySelectorAll('img')].map(i=>i.alt||'').filter(Boolean).slice(0,10)"""))
    ctx.close()
