
import sys, traceback
from playwright.sync_api import sync_playwright
try:
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(r"H:\pw-suno", channel="msedge", headless=True,
            viewport={"width":1440,"height":900}, locale="en-US", args=["--no-first-run"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://suno.com/me", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)
        print("URL:", page.url)
        print("TEXT:", page.evaluate("() => document.body.innerText.slice(0,300)").replace("\n"," | "))
        ctx.close()
except Exception as e:
    print("FULL ERROR:")
    traceback.print_exc()
