
import json, os
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"
os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-suno", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="en-US", args=["--no-first-run"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    for url in ["https://suno.com/me", "https://suno.com/search?q=%E9%9D%92%E8%8A%B1"]:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(6000)
            t = page.evaluate("() => document.body.innerText.slice(0,500)")
            print("URL:", page.url)
            print("TEXT:", t.replace("\n"," | ")[:400])
            page.screenshot(path=os.path.join(OUT, "suno-lib.png"))
        except Exception as e:
            print(url, "ERR", str(e)[:120])
    ctx.close()
