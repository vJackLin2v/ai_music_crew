
import json, os, sys, time, multiprocessing as mp
import numpy as np, sounddevice as sd, soundfile as sf
from playwright.sync_api import sync_playwright
OUT = r"H:\ai_music_crew\shots"
WAV = sys.argv[1]; REC_SEC = int(sys.argv[2]); TAG = sys.argv[3]
IN_DEV, OUT_DEV = 12, 16
LOG = os.path.join(OUT, f"pw-{TAG}.txt"); open(LOG,"w",encoding="utf-8").close()
def log(*a):
    s=" ".join(str(x) for x in a); print(s,flush=True); open(LOG,"a",encoding="utf-8").write(s+"\n")
def player(seconds=200):
    d, sr = sf.read(WAV, dtype="float32"); end = time.time()+seconds
    while time.time() < end: sd.play(d, sr, device=OUT_DEV, blocking=True)
def modal(p):
    return p.evaluate("""()=>{const d=[...document.querySelectorAll('div')].filter(x=>/modal|dialog/i.test(String(x.className)));
      const l=d.sort((a,b)=>b.innerText.length-a.innerText.length)[0]; return l?l.innerText:'';}""")
GETMIC = """() => { const md = navigator.mediaDevices; if (!md.__patched) {
  const orig = md.getUserMedia.bind(md);
  md.getUserMedia = async (c) => { const devs = await md.enumerateDevices();
    const cable = devs.find(d => d.kind==='audioinput' && /CABLE Output/i.test(d.label));
    if (cable) { c = c||{}; c.audio = Object.assign({}, (typeof c.audio==='object'?c.audio:{}), {deviceId:{exact:cable.deviceId}}); }
    return orig(c); }; md.__patched = true; } }"""
if __name__ == "__main__":
    pl = mp.Process(target=player); pl.start(); time.sleep(0.8)
    pw = sync_playwright().start()
    bctx = pw.chromium.launch_persistent_context(r"H:\pw-haimian", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="zh-CN", args=["--no-first-run","--use-fake-ui-for-media-stream"])
    bctx.add_init_script("(" + GETMIC + ")()")
    page = bctx.pages[0] if bctx.pages else bctx.new_page()
    page.on("response", lambda r: (lambda t: log("API-ERR>>>", t[t.find("err_message")-40:t.find("err_message")+60].replace("\n"," ")) if "voice/info" in r.url and "err_message" in t else None)(r.text() if r.request else ""))
    page.goto("https://www.haimian.com/create", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    try: page.get_by_text("我知道了", exact=True).first.click(timeout=2500)
    except Exception: pass
    for step in ["选音色","新增音色","开始清唱"]:
        try: page.get_by_text(step, exact=True).first.click(timeout=8000)
        except Exception: log("fail", step)
        page.wait_for_timeout(1400)
    page.wait_for_timeout(REC_SEC*1000)
    try: page.locator("text=/^\\s*00:\\d\\d\\s*$/").last.click(timeout=5000); log("stopped")
    except Exception: log("stop fail")
    page.wait_for_timeout(2200)
    try: page.get_by_text("提交", exact=True).first.click(timeout=6000); log("submitted")
    except Exception: log("submit fail")
    for i in range(18):
        page.wait_for_timeout(10000)
        t = modal(page); log(f"t+{(i+1)*10}s:", t[-110:].replace("\n"," | "))
        if "制作中" not in t: log("END"); break
    bctx.close(); pw.stop()
    try: pl.terminate()
    except Exception: pass
