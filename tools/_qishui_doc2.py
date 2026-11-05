
import os, json
from playwright.sync_api import sync_playwright
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = "https://music.douyin.com/support/content/207534?hideAvatar=1&hideUnify=1&pageId=474&spaceId=299"
OUT = r"H:\ai_music_crew\shots"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EDGE, headless=True)
    pg = b.new_context(viewport={"width":1400,"height":1200}, locale="zh-CN").new_page()
    pg.goto(URL, wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(5000)
    # 先展开所有可点的折叠项
    try:
        items = pg.locator("text=/批量发布|上传歌曲/").all()
        for it in items[:6]:
            try: it.click(timeout=1500)
            except Exception: pass
    except Exception: pass
    pg.wait_for_timeout(2500)
    txt = pg.evaluate("() => document.body ? document.body.innerText : ''")
    open(os.path.join(OUT, "qishui-doc.txt"), "w", encoding="utf-8").write(txt)
    # 也抓 HTML 里可能藏着的正文
    html = pg.content()
    open(os.path.join(OUT, "qishui-doc.html"), "w", encoding="utf-8").write(html)
    pg.screenshot(path=os.path.join(OUT, "qishui-batch.png"), full_page=True)
    b.close()
print("saved")
