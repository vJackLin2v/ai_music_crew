
import json, os, sys
from playwright.sync_api import sync_playwright

OUT = r"H:\ai_music_crew\shots"
os.makedirs(OUT, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True, args=["--disable-blink-features=AutomationControlled", "--no-first-run"])
    ctx = b.new_context(viewport={"width":1440,"height":900}, locale="zh-CN",
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0")
    page = ctx.new_page()
    page.goto("https://www.haimian.com/", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    print("URL:", page.url)
    print("TITLE:", page.title())
    txt = page.evaluate("() => document.body ? document.body.innerText : ''")
    print("TEXT>>>", txt[:1500].replace("\n"," | "))
    page.screenshot(path=os.path.join(OUT,"haimian-01-home.png"), full_page=False)
    els = page.evaluate("""() => {
      const out=[];
      document.querySelectorAll('a,button,[role=button],[class*=btn],[class*=Btn]').forEach(e=>{
        const t=(e.innerText||e.getAttribute('aria-label')||'').trim().replace(/\\s+/g,' ');
        if(t && t.length<=24) out.push(t);
      });
      return [...new Set(out)];
    }""")
    print("CLICKABLE>>>", json.dumps(els, ensure_ascii=False)[:1500])
    b.close()
