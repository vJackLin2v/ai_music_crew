
import json, os
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-haimian", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="zh-CN", args=["--no-first-run"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://www.haimian.com/create", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    for lbl in ["我知道了"]:
        try: page.get_by_text(lbl, exact=True).first.click(timeout=2500)
        except Exception: pass
    try:
        page.get_by_text("选音色", exact=True).first.click(timeout=6000); print("opened 选音色")
    except Exception as e: print("fail1", str(e)[:80])
    page.wait_for_timeout(1500)
    try:
        page.get_by_text("新增音色", exact=True).first.click(timeout=6000); print("clicked 新增音色")
    except Exception as e: print("fail2", str(e)[:100])
    page.wait_for_timeout(2500)
    page.screenshot(path=os.path.join(OUT, "haimian-07-add-voice.png"))
    body = page.evaluate("() => document.body ? document.body.innerText : ''")
    print("TEXT>>>", body[:500].replace("\n"," | "))
    info = page.evaluate("""() => {
      const modals=[...document.querySelectorAll('div')].filter(d=>/modal|dialog|Modal/i.test(String(d.className)));
      const last = modals.sort((a,b)=>b.innerText.length-a.innerText.length)[0];
      return {
        modalCount: modals.length,
        modalText: last ? last.innerText.slice(0,600) : null,
        fileInputs: [...document.querySelectorAll('input[type=file]')].map(i=>({accept:i.accept, multiple:i.multiple})),
        buttons: [...document.querySelectorAll('button,div[role=button]')].map(b=>(b.innerText||'').trim()).filter(Boolean).slice(0,25),
        hasUploadWord: /上传|选择文件|导入/.test(document.body.innerText),
      };
    }""")
    print("INFO>>>", json.dumps(info, ensure_ascii=False))
    ctx.close()
