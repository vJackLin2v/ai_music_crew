
import os, json
from playwright.sync_api import sync_playwright
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = r"H:\ai_music_crew\shots"
q = "雨爱 杨丞琳 MV 官方"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EDGE, headless=True)
    ctx = b.new_context(viewport={"width":1500,"height":1200}, locale="zh-CN",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
    pg = ctx.new_page()
    pg.goto("https://search.bilibili.com/all?keyword=" + q.replace(" ", "%20"), wait_until="domcontentloaded", timeout=45000)
    pg.wait_for_timeout(5000)
    items = pg.evaluate("""() => [...document.querySelectorAll('a')]
        .filter(a => a.href.includes('bilibili.com/video/BV'))
        .map(a => { const c = a.closest('.bili-video-card') || a.parentElement;
          return {href: a.href.split('?')[0],
                  title: (c?.querySelector('.bili-video-card__info--tit')?.innerText||'').trim(),
                  dur: (c?.querySelector('.bili-video-card__stats__duration')?.innerText||'').trim(),
                  play: (c?.querySelector('.bili-video-card__stats--item')?.innerText||'').trim()}; })
        .filter(x => x.title)""")
    seen, uniq = set(), []
    for i in items:
        if i["href"] in seen: continue
        seen.add(i["href"]); uniq.append(i)
    json.dump(uniq[:12], open(os.path.join(OUT,"yuai_mv.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print("found", len(uniq))
    b.close()
