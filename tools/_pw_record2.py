
import json, os, time
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"
WAV = r"H:\ai_music_crew\voice\xiaojingyu\record-mix.wav"
ARGS = ["--no-first-run", "--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream",
        f"--use-file-for-fake-audio-capture={WAV}",
        "--autoplay-policy=no-user-gesture-required"]

def snap(page, name):
    page.screenshot(path=os.path.join(OUT, name))

def modal_text(page):
    return page.evaluate("""() => {
      const m=[...document.querySelectorAll('div')].filter(d=>/modal|dialog/i.test(String(d.className)));
      const l=m.sort((a,b)=>b.innerText.length-a.innerText.length)[0];
      return l?l.innerText.slice(-450):null;
    }""")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-haimian", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="zh-CN", args=ARGS)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://www.haimian.com/create", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    try: page.get_by_text("我知道了", exact=True).first.click(timeout=2500)
    except Exception: pass
    for step in ["选音色", "新增音色", "开始清唱"]:
        try:
            page.get_by_text(step, exact=True).first.click(timeout=6000); print("ok", step)
        except Exception as e: print("fail", step, str(e)[:70])
        page.wait_for_timeout(1500)
    page.wait_for_timeout(38000)   # 录 ~40 秒
    print("pre-stop modal:", modal_text(page))
    # 点计时器那个胶囊停止
    stopped = False
    for sel in ["text=/^\\s*00:\\d\\d\\s*$/", ".modal-wrapper-fRdvek >> text=/00:/", "text=/00:/"]:
        try:
            page.locator(sel).last.click(timeout=4000); print("stopped via", sel); stopped = True; break
        except Exception as e: print("stop fail", sel, str(e)[:60])
    if not stopped:
        page.mouse.click(720, 670)
        print("clicked pill by coords")
    page.wait_for_timeout(4000)
    snap(page, "haimian-11-after-stop.png")
    print("POST-STOP modal:", modal_text(page))
    print("POST-STOP buttons:", page.evaluate("()=>[...document.querySelectorAll('button')].map(b=>b.innerText.trim()).filter(Boolean).slice(-12)"))
    print("POST-STOP inputs:", page.evaluate("()=>[...document.querySelectorAll('input')].map(i=>({ph:i.placeholder,type:i.type}))"))
    ctx.close()
