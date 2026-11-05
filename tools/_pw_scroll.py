
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
    page.wait_for_timeout(2000)

    # 找滚动容器并滚到顶
    page.evaluate("""() => {
      const d=[...document.querySelectorAll('div')].filter(x=>/modal|dialog/i.test(String(x.className)));
      const m=d.sort((a,b)=>b.innerText.length-a.innerText.length)[0];
      if(!m) return;
      for(const e of m.querySelectorAll('*')){
        if(e.scrollHeight > e.clientHeight + 10 && e.clientHeight > 100){ e.scrollTop = 0; }
      }
    }""")
    page.wait_for_timeout(800)
    page.screenshot(path=os.path.join(OUT,"haimian-16-list-top.png"))
    rows_top = page.evaluate("""() => [...document.querySelectorAll('img')].map(i=>({alt:i.alt, src:(i.src||'').slice(0,60)})).slice(0,20)""")
    print("IMGS top:", json.dumps(rows_top, ensure_ascii=False)[:800])

    page.evaluate("""() => {
      const d=[...document.querySelectorAll('div')].filter(x=>/modal|dialog/i.test(String(x.className)));
      const m=d.sort((a,b)=>b.innerText.length-a.innerText.length)[0];
      if(!m) return;
      for(const e of m.querySelectorAll('*')){
        if(e.scrollHeight > e.clientHeight + 10 && e.clientHeight > 100){ e.scrollTop = e.scrollHeight; }
      }
    }""")
    page.wait_for_timeout(800)
    page.screenshot(path=os.path.join(OUT,"haimian-17-list-bottom.png"))
    m = page.evaluate("""() => {
      const d=[...document.querySelectorAll('div')].filter(x=>/modal|dialog/i.test(String(x.className)));
      const l=d.sort((a,b)=>b.innerText.length-a.innerText.length)[0];
      return l? l.innerText : null;
    }""")
    print("PANEL ALL>>>", (m or "").replace("\n"," | ")[:800])
    ctx.close()
