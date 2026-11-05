
import json, os
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True, args=["--no-first-run"])
    ctx = b.new_context(viewport={"width":1440,"height":900}, locale="zh-CN")
    page = ctx.new_page()
    page.goto("https://www.haimian.com/create", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3500)
    # 关弹窗
    try: page.get_by_text("我知道了", exact=True).first.click(timeout=3000)
    except Exception: pass
    page.wait_for_timeout(500)
    # 点「选音色」
    try:
        page.get_by_text("选音色", exact=True).first.click(timeout=6000); print("clicked 选音色")
    except Exception as e:
        print("click fail:", str(e)[:120])
    page.wait_for_timeout(2500)
    page.screenshot(path=os.path.join(OUT,"haimian-04-voice-panel.png"))
    txt = page.evaluate("() => document.body ? document.body.innerText : ''")
    print("TEXT>>>", txt[:700].replace("\n"," | "))
    # 面板里所有可点项
    panel = page.evaluate("""() => {
      const out=[];
      for(const e of document.querySelectorAll('div,span,button,li')){
        const t=(e.childElementCount===0?(e.textContent||''):'').trim();
        if(t && t.length<20 && /音色|克隆|录音|录制|上传|新增|我的|专属|删除|清空/.test(t)) out.push({cls:String(e.className).slice(0,45),text:t});
      }
      const uniq=[]; const seen=new Set();
      for(const o of out){ const k=o.text; if(!seen.has(k)){seen.add(k); uniq.push(o);} }
      return uniq.slice(0,30);
    }""")
    print("PANEL>>>", json.dumps(panel, ensure_ascii=False))
    b.close()
