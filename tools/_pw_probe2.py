
import json, os
from playwright.sync_api import sync_playwright

OUT = r"H:\ai_music_crew\shots"

def dump(page, tag):
    txt = page.evaluate("() => document.body ? document.body.innerText : ''")
    print(f"--- {tag} URL:", page.url)
    print(f"--- {tag} TEXT>>>", txt[:900].replace("\n", " | "))

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True,
                          args=["--disable-blink-features=AutomationControlled", "--no-first-run"])
    ctx = b.new_context(viewport={"width":1440,"height":900}, locale="zh-CN")
    page = ctx.new_page()
    page.goto("https://www.haimian.com/", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)

    # 先看全站有哪些含「音色」的元素
    hits = page.evaluate("""() => {
      const out=[];
      const walk = document.querySelectorAll('*');
      for (const e of walk) {
        const t=(e.childElementCount === 0 ? (e.textContent||'') : '').trim();
        if (t.includes('音色') && t.length < 30) out.push({tag:e.tagName, cls:String(e.className).slice(0,60), text:t});
      }
      return out.slice(0,20);
    }""")
    print("HOME 音色 hits:", json.dumps(hits, ensure_ascii=False))

    # 点「创作」
    try:
        page.get_by_text("创作", exact=True).first.click(timeout=8000)
    except Exception as e:
        print("click 创作 failed:", e)
    page.wait_for_timeout(4000)
    dump(page, "create")
    page.screenshot(path=os.path.join(OUT, "haimian-02-create.png"))

    hits2 = page.evaluate("""() => {
      const out=[];
      const walk = document.querySelectorAll('*');
      for (const e of walk) {
        const t=(e.childElementCount === 0 ? (e.textContent||'') : '').trim();
        if (t && t.length < 30 && /音色|克隆|声音|声线|歌手|唱/.test(t)) out.push({tag:e.tagName, cls:String(e.className).slice(0,50), text:t});
      }
      return out.slice(0,40);
    }""")
    print("CREATE hits:", json.dumps(hits2, ensure_ascii=False))
    b.close()
