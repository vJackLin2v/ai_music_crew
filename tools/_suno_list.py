
import json, os, re
from playwright.sync_api import sync_playwright
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = r"H:\ai_music_crew\shots"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-suno", executable_path=EDGE, headless=True,
        viewport={"width":1440,"height":900}, locale="en-US", args=["--no-first-run"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://suno.com/me", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(6000)
    songs = {}
    for i in range(12):
        found = page.evaluate("""() => [...document.querySelectorAll('a[href*="/song/"]')].map(a => ({href: a.getAttribute('href'), text: (a.innerText||'').trim().slice(0,60)}))""")
        for f in found:
            if f["text"]:
                songs[f["href"]] = f["text"]
        page.mouse.wheel(0, 2500)
        page.wait_for_timeout(1200)
    print("collected songs:", len(songs))
    hits = {k:v for k,v in songs.items() if ("青花" in v) or ("月亮" in v) or ("月亮" in v)}
    print("HITS:", json.dumps(hits, ensure_ascii=False)[:800])
    print("SAMPLE TITLES:", json.dumps(list(songs.items())[:12], ensure_ascii=False)[:900])
    ctx.close()
