
import os, json, re
from playwright.sync_api import sync_playwright
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = r"H:\ai_music_crew\shots"
queries = {"雨爱": "雨爱 杨丞琳 原唱", "我不难过": "我不难过 孙燕姿", "我好像在哪见过你": "我好像在哪见过你 薛之谦"}
res = {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EDGE, headless=True)
    ctx = b.new_context(viewport={"width":1440,"height":1000}, locale="zh-CN",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
    pg = ctx.new_page()
    for k, q in queries.items():
        try:
            pg.goto("https://search.bilibili.com/all?keyword=" + q.replace(" ", "%20"), wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(4500)
            items = pg.evaluate("""() => [...document.querySelectorAll('a[href*="/video/BV"]')].slice(0,20).map(a => ({
                href: a.href.split('?')[0],
                title: (a.getAttribute('title') || a.innerText || '').trim().slice(0,50)
            }))""")
            seen, uniq = set(), []
            for i in items:
                bv = i["href"].rsplit("/",1)[-1]
                if bv and bv not in seen:
                    seen.add(bv); uniq.append({"bv": bv, "title": i["title"]})
            res[k] = uniq[:8]
        except Exception as e:
            res[k] = [{"error": str(e)[:80]}]
    b.close()
open(os.path.join(OUT, "bili-bv.json"), "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
print("ok")
