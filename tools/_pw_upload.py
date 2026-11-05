
import json, os
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"
WAV = r"H:\ai_music_crew\voice\xiaojingyu\record-read.wav"
ARGS = ["--no-first-run","--use-fake-ui-for-media-stream","--use-fake-device-for-media-stream",
        f"--use-file-for-fake-audio-capture={WAV}","--autoplay-policy=no-user-gesture-required"]
LOG = os.path.join(OUT,"pw-upload.txt"); open(LOG,"w",encoding="utf-8").close()
def log(*a):
    s=" ".join(str(x) for x in a); print(s,flush=True); open(LOG,"a",encoding="utf-8").write(s+"\n")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-haimian", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="zh-CN", args=ARGS)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    def on_req(r):
        try:
            if r.method == "POST":
                b = r.post_data_buffer
                size = len(b) if b else 0
                if size > 0 or any(k in r.url for k in ("voice","upload","record","audio")):
                    log("REQ", r.method, r.url[:110], "bytes=", size)
        except Exception: pass
    page.on("request", on_req)
    page.goto("https://www.haimian.com/create", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    try: page.get_by_text("我知道了", exact=True).first.click(timeout=2500)
    except Exception: pass
    for step in ["选音色","新增音色","开始清唱"]:
        try: page.get_by_text(step, exact=True).first.click(timeout=8000)
        except Exception: pass
        page.wait_for_timeout(1200)
    page.wait_for_timeout(26000)
    try: page.locator("text=/^\\s*00:\\d\\d\\s*$/").last.click(timeout=5000)
    except Exception: pass
    page.wait_for_timeout(2000)
    try: page.get_by_text("提交", exact=True).first.click(timeout=6000)
    except Exception: pass
    page.wait_for_timeout(15000)
    ctx.close()
