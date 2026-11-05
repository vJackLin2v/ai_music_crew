
import json, os, time
from playwright.sync_api import sync_playwright

OUT = r"H:\ai_music_crew\shots"
STYLE = open(r"H:\ai_music_crew\work\songs\大梦归.style.txt", encoding="utf-8").read().strip()
LYRICS = open(r"H:\ai_music_crew\work\songs\大梦归.lyrics.txt", encoding="utf-8").read().strip()
LOG = os.path.join(OUT, "suno-head.txt"); open(LOG,"w",encoding="utf-8").close()
def log(*a):
    s=" ".join(str(x) for x in a); print(s, flush=True); open(LOG,"a",encoding="utf-8").write(s+"\n")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-suno", channel="msedge", headless=False,
        viewport={"width":1440,"height":900}, locale="en-US",
        args=["--no-first-run","--disable-blink-features=AutomationControlled"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(7000)
    try: page.get_by_text("Advanced", exact=True).first.click(timeout=4000)
    except Exception: pass

    ed = page.locator('[contenteditable="true"]').first
    ed.click(); page.keyboard.press("Control+A"); page.keyboard.press("Delete")
    lines = LYRICS.split("\n")
    for i, line in enumerate(lines):
        if line.strip(): page.keyboard.insert_text(line)
        if i != len(lines)-1: page.keyboard.press("Enter")
    page.wait_for_timeout(500)
    try: page.get_by_text("Styles", exact=True).first.click(timeout=5000)
    except Exception: pass
    page.wait_for_timeout(1000)
    st = page.locator("textarea").nth(1)
    if st.count(): st.fill(STYLE)
    log("filled lyrics+style")
    page.screenshot(path=os.path.join(OUT,"suno-14-ready.png"))
    ctx.close()

    # 用同一个 profile 重新以有头方式打开，交给用户点 Cloudflare + Create
    log("DONE-FILL")
