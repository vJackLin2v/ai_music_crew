
import json, os
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-haimian", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="zh-CN", args=["--no-first-run"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://www.haimian.com/create", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3500)
    try: page.get_by_text("我知道了", exact=True).first.click(timeout=2500)
    except Exception: pass
    try: page.get_by_text("选音色", exact=True).first.click(timeout=6000)
    except Exception as e: print("open fail", str(e)[:80])
    page.wait_for_timeout(2500)
    page.screenshot(path=os.path.join(OUT,"haimian-15-voice-list.png"))
    m = page.evaluate("""() => {
      const d=[...document.querySelectorAll('div')].filter(x=>/modal|dialog/i.test(String(x.className)));
      const l=d.sort((a,b)=>b.innerText.length-a.innerText.length)[0];
      return l? l.innerText : null;
    }""")
    print("VOICE PANEL>>>", (m or "")[:600].replace("\n"," | "))
    ctx.close()
