
import json, os, time, sys
from playwright.sync_api import sync_playwright

OUT = r"H:\ai_music_crew\shots"
LOG = os.path.join(OUT, "pw-log.txt")
os.makedirs(OUT, exist_ok=True)

def log(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

open(LOG, "w", encoding="utf-8").close()

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        r"H:\pw-haimian", channel="msedge", headless=False,
        viewport={"width":1440,"height":900}, locale="zh-CN", args=["--no-first-run"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://www.haimian.com/create", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3500)
    try:
        page.get_by_text("我知道了", exact=True).first.click(timeout=3000)
    except Exception: pass
    try:
        page.get_by_text("选音色", exact=True).first.click(timeout=6000)
        log("clicked 选音色")
    except Exception as e:
        log("click 选音色 fail", str(e)[:100])
    page.wait_for_timeout(2500)
    page.screenshot(path=os.path.join(OUT, "haimian-05-login.png"))
    body = page.evaluate("() => document.body ? document.body.innerText : ''")
    log("LOGIN-PROMPT:", "登录" in body, "|needVoice:", "登录后即可选择" in body)

    # 等用户登录，最多 15 分钟
    logged = False
    for i in range(180):
        page.wait_for_timeout(5000)
        try:
            b = page.evaluate("() => document.body ? document.body.innerText : ''")
        except Exception:
            continue
        if "登录后即可选择" not in b and "立即登录" not in b:
            logged = True
            log(f"LOGIN DETECTED after ~{(i+1)*5}s")
            break
        if i % 12 == 0:
            log(f"waiting login... {i*5}s")
    if not logged:
        log("TIMEOUT: 未检测到登录")
        page.screenshot(path=os.path.join(OUT, "haimian-06-timeout.png"))
        ctx.close(); sys.exit(0)

    page.wait_for_timeout(2000)
    try:
        page.get_by_text("选音色", exact=True).first.click(timeout=6000)
        log("clicked 选音色 (logged in)")
    except Exception as e:
        log("2nd click fail", str(e)[:100])
    page.wait_for_timeout(2500)
    page.screenshot(path=os.path.join(OUT, "haimian-06-voice-panel.png"))
    b = page.evaluate("() => document.body ? document.body.innerText : ''")
    log("PANEL-TEXT:", b[:600].replace("\n"," | "))
    items = page.evaluate("""() => {
      const out=[]; const seen=new Set();
      for(const e of document.querySelectorAll('*')){
        const t=(e.childElementCount===0?(e.textContent||''):'').trim();
        if(t && t.length<20 && /音色|克隆|录音|录制|上传|新增|我的|专属|删除|时长|秒/.test(t) && !seen.has(t)){seen.add(t);out.push({cls:String(e.className).slice(0,45),text:t});}
      } return out.slice(0,30);
    }""")
    log("PANEL-ITEMS:", json.dumps(items, ensure_ascii=False))
    log("DONE-PHASE1")
    ctx.close()
