
import os, json
from playwright.sync_api import sync_playwright
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BASE = "https://music.douyin.com/support/content/"
URL = BASE + "207534?hideAvatar=1&hideUnify=1&pageId=474&spaceId=299"
OUT = r"H:\ai_music_crew\shots"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EDGE, headless=True)
    pg = b.new_context(viewport={"width":1400,"height":1200}, locale="zh-CN").new_page()
    pg.goto(URL, wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(5000)
    # 列出 iframe 文本
    texts = []
    for fr in pg.frames:
        try:
            t = fr.inner_text("body")
        except Exception:
            continue
        if t and len(t.strip()) > 50:
            texts.append({"url": fr.url[:100], "len": len(t), "text": t})
    print("frames with text:", len(texts))
    for x in texts:
        print("---", x["len"], x["url"])
    if texts:
        best = max(texts, key=lambda x: x["len"])
        open(os.path.join(OUT, "qishui-article.txt"), "w", encoding="utf-8").write(best["text"])
        print("saved article, len", best["len"])
    # 找上一篇链接
    links = pg.evaluate("""() => [...document.querySelectorAll('a')].map(a => ({href: a.href, text: (a.innerText||'').trim().slice(0,40)})).filter(x => x.text)""")
    want = [l for l in links if "批量" in l["text"] or "上传" in l["text"]]
    print("LINKS:", json.dumps(want[:10], ensure_ascii=False))
    b.close()
