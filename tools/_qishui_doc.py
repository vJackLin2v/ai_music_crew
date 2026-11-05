
import os, json
from playwright.sync_api import sync_playwright
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = "https://music.douyin.com/support/content/207534?hideAvatar=1&hideUnify=1&pageId=474&spaceId=299"
OUT = r"H:\ai_music_crew\shots"
os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EDGE, headless=True)
    pg = b.new_context(viewport={"width":1400,"height":1000}, locale="zh-CN").new_page()
    pg.goto(URL, wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(6000)
    txt = pg.evaluate("() => document.body ? document.body.innerText : ''")
    print("LEN:", len(txt))
    print(txt[:3000])
    pg.screenshot(path=os.path.join(OUT, "qishui-batch.png"), full_page=True)
    b.close()
