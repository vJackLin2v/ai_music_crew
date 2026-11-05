
import os, json, re
from playwright.sync_api import sync_playwright
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = r"H:\ai_music_crew\shots"
queries = ["翻唱 竖屏", "AI翻唱 歌词", "歌曲 竖屏 动态歌词"]
res = {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EDGE, headless=True)
    ctx = b.new_context(viewport={"width":1500,"height":1200}, locale="zh-CN",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
    pg = ctx.new_page()
    for q in queries:
        try:
            pg.goto("https://search.bilibili.com/all?keyword=" + q.replace(" ", "%20"), wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(5000)
            items = pg.evaluate("""() => [...document.querySelectorAll('a')]
                .filter(a => a.href.includes('bilibili.com/video/BV'))
                .map(a => {
                    const card = a.closest('.bili-video-card') || a.parentElement;
                    return {
                        href: a.href.split('?')[0],
                        title: (card?.querySelector('.bili-video-card__info--tit')?.innerText || '').trim(),
                        author: (card?.querySelector('.bili-video-card__info--author')?.innerText || '').trim(),
                        play: (card?.querySelector('.bili-video-card__stats--item')?.innerText || '').trim(),
                        dur: (card?.querySelector('.bili-video-card__stats__duration')?.innerText || '').trim()
                    };
                })
                .filter(x => x.title)""")
            seen, uniq = set(), []
            for i in items:
                if i["href"] in seen: continue
                seen.add(i["href"]); uniq.append(i)
            res[q] = uniq[:16]
        except Exception as e:
            res[q] = []
    b.close()
open(os.path.join(OUT, "bili-short.json"), "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
print("ok")
