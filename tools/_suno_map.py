
import json, os
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-suno", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="en-US", args=["--no-first-run"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(5000)
    try: page.get_by_text("Advanced", exact=True).first.click(timeout=4000)
    except Exception: pass
    page.wait_for_timeout(2500)
    fields = page.evaluate("""() => {
      const out = [];
      for (const el of document.querySelectorAll('textarea, [contenteditable=true], input[type=text]')) {
        const r = el.getBoundingClientRect();
        if (r.width < 40 || r.height < 10) continue;
        out.push({
          tag: el.tagName, type: el.type || '', ph: el.placeholder || '',
          aria: el.getAttribute('aria-label') || '', id: el.id || '',
          rect: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
          parentText: (el.closest('div')?.innerText || '').slice(0, 80).replace(/\n/g, ' | '),
        });
      }
      return out;
    }""")
    print(json.dumps(fields, ensure_ascii=False, indent=1)[:2200])
    btns = page.evaluate("""() => [...document.querySelectorAll('button')]
        .filter(b => { const r = b.getBoundingClientRect(); return r.width>0 && r.height>0; })
        .map(b => ({t: (b.innerText||'').trim().slice(0,24), r: [Math.round(b.getBoundingClientRect().x), Math.round(b.getBoundingClientRect().y)]}))
        .filter(x => x.t)""")
    print("BTNS:", json.dumps([b for b in btns if b['r'][1] > 200], ensure_ascii=False)[:1200])
    page.screenshot(path=os.path.join(OUT,"suno-05-adv-full.png"), full_page=False)
    ctx.close()
