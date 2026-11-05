
import json, os
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True, args=["--no-first-run"])
    ctx = b.new_context(viewport={"width":1440,"height":900}, locale="zh-CN")
    page = ctx.new_page()
    page.goto("https://www.haimian.com/", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)
    # 关掉公告弹窗
    for label in ["我知道了", "关闭", "×"]:
        try:
            page.get_by_text(label, exact=True).first.click(timeout=3000)
            print("closed modal via", label); break
        except Exception: pass
    page.wait_for_timeout(800)
    # 点左侧导航「创作」
    for sel in ["span.nav-item-text-zap81L", "text=创作"]:
        try:
            page.locator(sel).filter(has_text="创作").first.click(timeout=5000); print("clicked 创作"); break
        except Exception as e: print("nav fail", sel, str(e)[:80])
    page.wait_for_timeout(3500)
    print("URL:", page.url)
    txt = page.evaluate("() => document.body ? document.body.innerText : ''")
    print("TEXT>>>", txt[:800].replace("\n"," | "))
    page.screenshot(path=os.path.join(OUT,"haimian-03-after-create.png"))
    # 找「选音色」「自定义」
    hits = page.evaluate("""() => {
      const out=[]; for(const e of document.querySelectorAll('*')){
        const t=(e.childElementCount===0?(e.textContent||''):'').trim();
        if(t && t.length<24 && /音色|克隆|声音|自定义|录音|专属/.test(t)) out.push({cls:String(e.className).slice(0,40),text:t});
      } return out.slice(0,30);
    }""")
    print("HITS>>>", json.dumps(hits, ensure_ascii=False))
    b.close()
