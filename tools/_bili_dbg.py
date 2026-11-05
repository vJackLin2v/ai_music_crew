
import os, json, re
from playwright.sync_api import sync_playwright
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = r"H:\ai_music_crew\shots"
q = "雨爱 杨丞琳"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EDGE, headless=True)
    ctx = b.new_context(viewport={"width":1440,"height":1000}, locale="zh-CN",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
    pg = ctx.new_page()
    pg.goto("https://search.bilibili.com/all?keyword=" + q, wait_until="domcontentloaded", timeout=45000)
    pg.wait_for_timeout(6000)
    hrefs = pg.evaluate("() => [...document.querySelectorAll('a')].map(a => a.href).filter(h => h.includes('BV')).slice(0,30)")
    print("BV links:", len(hrefs))
    for h in hrefs[:10]: print(" ", h)
    txt = pg.evaluate("() => document.body.innerText.slice(0,300)")
    open(os.path.join(OUT,"bili-search-debug.txt"),"w",encoding="utf-8").write(txt)
    pg.screenshot(path=os.path.join(OUT,"bili-search.png"))
    b.close()
