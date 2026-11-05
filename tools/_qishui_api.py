
import os, json
from playwright.sync_api import sync_playwright
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = "https://music.douyin.com/support/content/207534?hideAvatar=1&hideUnify=1&pageId=474&spaceId=299"
OUT = r"H:\ai_music_crew\shots"
hits = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EDGE, headless=True)
    pg = b.new_context(viewport={"width":1400,"height":1000}, locale="zh-CN").new_page()
    def on_resp(r):
        u = r.url
        if any(k in u for k in ("content", "article", "space", "doc")) and ("api" in u or "json" in (r.headers.get("content-type") or "")):
            try:
                body = r.text()
                hits.append({"url": u, "status": r.status, "len": len(body), "head": body[:300]})
            except Exception:
                pass
    pg.on("response", on_resp)
    pg.goto(URL, wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(4000)
    b.close()
json.dump(hits, open(os.path.join(OUT, "qishui-api.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("captured:", len(hits))
for h in hits[:10]:
    print(h["status"], h["url"][:120], h["len"])
