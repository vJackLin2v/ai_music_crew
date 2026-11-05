
import json, os, time
from playwright.sync_api import sync_playwright

OUT = r"H:\ai_music_crew\shots"
STYLE = open(r"H:\ai_music_crew\work\songs\大梦归.style.txt", encoding="utf-8").read().strip()
LYRICS = open(r"H:\ai_music_crew\work\songs\大梦归.lyrics.txt", encoding="utf-8").read().strip()
LOG = os.path.join(OUT, "suno-half.txt"); open(LOG,"w",encoding="utf-8").close()
def log(*a):
    s=" ".join(str(x) for x in a); print(s, flush=True); open(LOG,"a",encoding="utf-8").write(s+"\n")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-suno", channel="msedge", headless=False,
        viewport={"width":1440,"height":900}, locale="en-US",
        args=["--no-first-run","--disable-blink-features=AutomationControlled"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(7000)
    try: page.get_by_text("Advanced", exact=True).first.click(timeout=4000)
    except Exception: pass

    ed = page.locator('[contenteditable="true"]').first
    ed.click(); page.keyboard.press("Control+A"); page.keyboard.press("Delete")
    lines = LYRICS.split("\n")
    for i, line in enumerate(lines):
        if line.strip(): page.keyboard.insert_text(line)
        if i != len(lines)-1: page.keyboard.press("Enter")
    try: page.get_by_text("Styles", exact=True).first.click(timeout=5000)
    except Exception: pass
    page.wait_for_timeout(900)
    st = page.locator("textarea").nth(1)
    if st.count(): st.fill(STYLE)
    log("form filled — 请在窗口里点掉 Cloudflare 的『Verify you are human』，再点 Create")
    page.screenshot(path=os.path.join(OUT,"suno-15-waiting.png"))

    # 先记录已有歌曲数
    def song_count():
        try:
            return page.evaluate("""() => document.querySelectorAll('a[href*="/song/"]').length""")
        except Exception:
            return -1
    before = song_count(); log("songs before:", before)

    appeared = False
    for i in range(120):     # 最多 12 分钟
        page.wait_for_timeout(6000)
        now = song_count()
        try:
            txt = page.evaluate("() => document.body.innerText")
        except Exception:
            continue
        if "Creating" in txt or "Generating" in txt or (now > before >= 0):
            appeared = True
            log(f"检测到新生成 ~{(i+1)*6}s, songs={now}"); break
        if i % 10 == 0: log(f"等待中 {i*6}s songs={now}")
    page.screenshot(path=os.path.join(OUT,"suno-16-after.png"))
    log("appeared:", appeared)
    if appeared:
        for j in range(30):
            page.wait_for_timeout(6000)
            t = page.evaluate("() => document.body.innerText")
            if "Creating" not in t and "Generating" not in t:
                log(f"生成结束 ~{(j+1)*6}s"); break
        page.screenshot(path=os.path.join(OUT,"suno-17-done.png"))
        links = page.evaluate("""() => [...document.querySelectorAll('a[href*="/song/"]')].slice(0,6).map(a=>({href:a.getAttribute('href'), text:(a.innerText||'').trim().slice(0,50)}))""")
        log("LINKS:", json.dumps(links, ensure_ascii=False)[:700])
    ctx.close()
