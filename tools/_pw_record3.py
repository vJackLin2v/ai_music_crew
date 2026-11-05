
import json, os, time
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"
WAV = r"H:\ai_music_crew\voice\xiaojingyu\record-mix.wav"
ARGS = ["--no-first-run","--use-fake-ui-for-media-stream","--use-fake-device-for-media-stream",
        f"--use-file-for-fake-audio-capture={WAV}","--autoplay-policy=no-user-gesture-required"]
LOG = os.path.join(OUT, "pw-record-log.txt")
open(LOG,"w",encoding="utf-8").close()
def log(*a):
    s=" ".join(str(x) for x in a); print(s, flush=True)
    open(LOG,"a",encoding="utf-8").write(s+"\n")
def snap(page,name): page.screenshot(path=os.path.join(OUT,name))

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-haimian", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="zh-CN", args=ARGS)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://www.haimian.com/create", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    try: page.get_by_text("我知道了", exact=True).first.click(timeout=2500)
    except Exception: pass
    for step in ["选音色","新增音色","开始清唱"]:
        try: page.get_by_text(step, exact=True).first.click(timeout=8000); log("ok",step)
        except Exception as e: log("fail",step,str(e)[:70])
        page.wait_for_timeout(1500)
    page.wait_for_timeout(42000)
    try:
        page.locator("text=/^\\s*00:\\d\\d\\s*$/").last.click(timeout=5000); log("stopped")
    except Exception as e: log("stop fail", str(e)[:80])
    page.wait_for_timeout(3000)
    snap(page,"haimian-12-ready.png")
    # 提交
    clicked=False
    for lbl in ["提交"]:
        try: page.get_by_text(lbl, exact=True).first.click(timeout=6000); log("clicked",lbl); clicked=True; break
        except Exception as e: log("submit fail", str(e)[:80])
    page.wait_for_timeout(5000)
    snap(page,"haimian-13-after-submit.png")
    body = page.evaluate("()=>document.body.innerText")
    log("AFTER-SUBMIT tail:", body[-350:].replace("\n"," | "))
    log("inputs:", page.evaluate("()=>[...document.querySelectorAll('input')].map(i=>({ph:i.placeholder,type:i.type,v:i.value}))"))
    # 若有命名输入框，填「小鲸鱼」
    try:
        inp = page.locator("input[placeholder*='音色'], input[placeholder*='名称'], input[placeholder*='名字']").first
        if inp.count()>0:
            inp.fill("小鲸鱼"); log("filled name")
            for lbl in ["确定","完成","确认","保存"]:
                try: page.get_by_text(lbl, exact=True).first.click(timeout=3000); log("clicked",lbl); break
                except Exception: pass
    except Exception as e: log("name step: ", str(e)[:80])
    page.wait_for_timeout(8000)
    snap(page,"haimian-14-final.png")
    log("FINAL tail:", page.evaluate("()=>document.body.innerText")[-400:].replace("\n"," | "))
    ctx.close()
