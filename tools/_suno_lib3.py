
import json, os, sys
from playwright.sync_api import sync_playwright

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE):
    EDGE = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
print("edge:", EDGE, os.path.exists(EDGE))

OUT = r"H:\ai_music_crew\shots"
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-suno", executable_path=EDGE, headless=True,
        viewport={"width":1440,"height":900}, locale="en-US", args=["--no-first-run"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://suno.com/me", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(6000)
    print("URL:", page.url)
    print("TEXT:", page.evaluate("() => document.body.innerText.slice(0,600)").replace("\n"," | ")[:500])
    page.screenshot(path=os.path.join(OUT,"suno-me.png"))
    ctx.close()
