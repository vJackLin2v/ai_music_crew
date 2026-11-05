
import json, os, time
from playwright.sync_api import sync_playwright

OUT = r"H:\ai_music_crew\shots"
STYLE = open(r"H:\ai_music_crew\work\songs\大梦归.style.txt", encoding="utf-8").read().strip()
LYRICS = open(r"H:\ai_music_crew\work\songs\大梦归.lyrics.txt", encoding="utf-8").read().strip()
LOG = os.path.join(OUT, "suno-gen.txt"); open(LOG,"w",encoding="utf-8").close()
def log(*a):
    s=" ".join(str(x) for x in a); print(s, flush=True); open(LOG,"a",encoding="utf-8").write(s+"\n")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-suno", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="en-US", args=["--no-first-run"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(6000)
    try: page.get_by_text("Advanced", exact=True).first.click(timeout=4000)
    except Exception: pass

    ed = page.locator('[contenteditable="true"]').first
    ed.click()
    page.keyboard.press("Control+A"); page.keyboard.press("Delete")
    lines = LYRICS.split("\n")
    for i, line in enumerate(lines):
        if line.strip(): page.keyboard.insert_text(line)
        if i != len(lines)-1: page.keyboard.press("Enter")
    page.wait_for_timeout(600)
    log("lyrics len:", len(ed.inner_text()))

    try: page.get_by_text("Styles", exact=True).first.click(timeout=5000)
    except Exception: pass
    page.wait_for_timeout(1200)
    st = page.locator("textarea").nth(1)
    if st.count():
        st.fill(STYLE); log("style filled:", len(STYLE))
    page.wait_for_timeout(800)
    page.screenshot(path=os.path.join(OUT,"suno-11-ready.png"))

    try:
        page.get_by_role("button", name="Create").last.click(timeout=8000); log("CREATE clicked")
    except Exception as e:
        log("create fail", str(e)[:100])
    page.wait_for_timeout(6000)
    page.screenshot(path=os.path.join(OUT,"suno-12-submitted.png"))
    log("submitted at", time.strftime("%H:%M:%S"))

    found = False
    for i in range(40):
        page.wait_for_timeout(6000)
        try:
            t = page.evaluate("() => document.body.innerText")
        except Exception:
            continue
        if "大梦归" in t:
            found = True; log(f"SONG APPEARED ~{(i+1)*6}s"); break
    page.screenshot(path=os.path.join(OUT,"suno-13-result.png"))
    log("found:", found)
    if found:
        # 抓最近生成的条目链接
        links = page.evaluate("""() => [...document.querySelectorAll('a[href*="/song/"]')].slice(0,8).map(a=>({href:a.getAttribute('href'), text:(a.innerText||'').trim().slice(0,40)}))""")
        log("LINKS:", json.dumps(links, ensure_ascii=False)[:500])
    ctx.close()
