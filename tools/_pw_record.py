
import json, os, time
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"
WAV = r"H:\ai_music_crew\voice\xiaojingyu\record-read.wav"
ARGS = ["--no-first-run", "--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream",
        f"--use-file-for-fake-audio-capture={WAV}",
        "--autoplay-policy=no-user-gesture-required"]

def snap(page, name):
    p = os.path.join(OUT, name)
    page.screenshot(path=p)
    return p

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-haimian", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="zh-CN", args=ARGS)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://www.haimian.com/create", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    try: page.get_by_text("我知道了", exact=True).first.click(timeout=2500)
    except Exception: pass
    try: page.get_by_text("选音色", exact=True).first.click(timeout=6000); print("选音色 ok")
    except Exception as e: print("选音色 fail", str(e)[:80])
    page.wait_for_timeout(1200)
    try: page.get_by_text("新增音色", exact=True).first.click(timeout=6000); print("新增音色 ok")
    except Exception as e: print("新增音色 fail", str(e)[:80])
    page.wait_for_timeout(2000)
    snap(page, "haimian-08-record-dialog.png")

    # 点「开始清唱」
    started = False
    for lbl in ["开始清唱", "开始录制", "开始", "录制"]:
        try:
            page.get_by_text(lbl, exact=True).first.click(timeout=4000)
            print("clicked", lbl); started = True; break
        except Exception: continue
    if not started:
        print("!! 找不到开始按钮"); snap(page, "haimian-08b.png")
    page.wait_for_timeout(3000)
    snap(page, "haimian-09-recording.png")
    print("REC TEXT>>>", page.evaluate("() => document.body.innerText.slice(-400)").replace("\n"," | "))

    # 录 24 秒
    page.wait_for_timeout(22000)
    snap(page, "haimian-10-recorded.png")
    info = page.evaluate("""() => {
      const modals=[...document.querySelectorAll('div')].filter(d=>/modal|dialog/i.test(String(d.className)));
      const last = modals.sort((a,b)=>b.innerText.length-a.innerText.length)[0];
      return {modalText: last?last.innerText.slice(-500):null,
              buttons:[...document.querySelectorAll('button')].map(b=>b.innerText.trim()).filter(Boolean)};
    }""")
    print("AFTER-REC>>>", json.dumps(info, ensure_ascii=False)[:1500])
    ctx.close()
