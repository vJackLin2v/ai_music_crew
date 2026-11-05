
import json, os
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-suno", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="en-US", args=["--no-first-run"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(6000)
    page.screenshot(path=os.path.join(OUT,"suno-03-create.png"))
    info = page.evaluate("""() => {
      const q = (s) => [...document.querySelectorAll(s)];
      return {
        url: location.href,
        textareas: q('textarea').map(t => ({ph: t.placeholder, id: t.id, cls: String(t.className).slice(0,40)})),
        editables: q('[contenteditable=true]').map(e => ({cls: String(e.className).slice(0,50), ph: e.getAttribute('data-placeholder') || ''})),
        buttons: q('button').map(b => (b.innerText||'').trim()).filter(Boolean).slice(0,40),
        inputs: q('input').map(i => ({ph: i.placeholder, type: i.type})).slice(0,12),
        tabs: q('[role=tab]').map(t => (t.innerText||'').trim()).slice(0,10),
        bodyHead: document.body.innerText.slice(0, 400),
      };
    }""")
    print(json.dumps(info, ensure_ascii=False, indent=1)[:2500])
    # 试试切到 Advanced
    for lbl in ("Advanced", "自定义", "Custom"):
        try:
            page.get_by_text(lbl, exact=True).first.click(timeout=3000); print("clicked", lbl); break
        except Exception: pass
    page.wait_for_timeout(2500)
    page.screenshot(path=os.path.join(OUT,"suno-04-advanced.png"))
    info2 = page.evaluate("""() => ({
        textareas: [...document.querySelectorAll('textarea')].map(t => t.placeholder),
        editables: [...document.querySelectorAll('[contenteditable=true]')].length,
        buttons: [...document.querySelectorAll('button')].map(b=>(b.innerText||'').trim()).filter(Boolean).slice(0,30),
    })""")
    print("ADV:", json.dumps(info2, ensure_ascii=False)[:1200])
    ctx.close()
