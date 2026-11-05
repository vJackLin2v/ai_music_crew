
import os, json, re
from playwright.sync_api import sync_playwright
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = r"H:\ai_music_crew\shots"
os.makedirs(OUT, exist_ok=True)
queries = ["雨爱 翻唱", "AI翻唱 竖屏"]
res = {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EDGE, headless=True)
    ctx = b.new_context(viewport={"width":1440,"height":1000}, locale="zh-CN",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
    pg = ctx.new_page()
    for q in queries:
        try:
            pg.goto("https://search.bilibili.com/all?keyword=" + q.replace(" ", "%20"), wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(5000)
            items = pg.evaluate("""() => [...document.querySelectorAll('.bili-video-card')].slice(0,14).map(c => ({
                title: (c.querySelector('.bili-video-card__info--tit')?.innerText || '').trim(),
                author: (c.querySelector('.bili-video-card__info--author')?.innerText || '').trim(),
                play: (c.querySelector('.bili-video-card__stats--item')?.innerText || '').trim(),
                dur: (c.querySelector('.bili-video-card__stats__duration')?.innerText || '').trim()
            }))""")
            res[q] = [i for i in items if i.get("title")]
            pg.screenshot(path=os.path.join(OUT, f"bili-{q[:6]}.png"))
        except Exception as e:
            res[q] = [{"error": str(e)[:100]}]
    b.close()
open(os.path.join(OUT, "bili-research.json"), "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
for q, items in res.items():
    print("=== ", q, len(items))
    for i in items[:10]:
        print(f"  {i.get('dur','?'):>6} | {i.get('play','?'):>8} | {i.get('author','?')[:10]:<10} | {i.get('title','')[:40]}")
