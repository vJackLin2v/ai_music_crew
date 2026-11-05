
import json, os, sys, time, multiprocessing as mp
import numpy as np, sounddevice as sd, soundfile as sf
from playwright.sync_api import sync_playwright

OUT = r"H:\ai_music_crew\shots"
WAV = r"H:\ai_music_crew\voice\xiaojingyu\record-full35.wav"
IN_DEV, OUT_DEV = 12, 16
LOG = os.path.join(OUT, "pw-cable.txt"); open(LOG,"w",encoding="utf-8").close()
def log(*a):
    s=" ".join(str(x) for x in a); print(s,flush=True); open(LOG,"a",encoding="utf-8").write(s+"\n")

def player(seconds=180):
    d, sr = sf.read(WAV, dtype="float32")
    end = time.time() + seconds
    while time.time() < end:
        sd.play(d, sr, device=OUT_DEV, blocking=True)

def modal(p):
    return p.evaluate("""()=>{const d=[...document.querySelectorAll('div')].filter(x=>/modal|dialog/i.test(String(x.className)));
      const l=d.sort((a,b)=>b.innerText.length-a.innerText.length)[0]; return l?l.innerText:'';}""")

GETMIC = """() => {
  const md = navigator.mediaDevices;
  if (!md.__patched) {
    const orig = md.getUserMedia.bind(md);
    md.getUserMedia = async (c) => {
      const devs = await md.enumerateDevices();
      const cable = devs.find(d => d.kind === 'audioinput' && /CABLE Output/i.test(d.label));
      if (cable) {
        c = c || {};
        c.audio = Object.assign({}, (typeof c.audio === 'object' ? c.audio : {}), { deviceId: { exact: cable.deviceId } });
      }
      return orig(c);
    };
    md.__patched = true;
  }
}"""

SAMPLER = """async () => {
  const s = await navigator.mediaDevices.getUserMedia({audio:true});
  const ctx = new AudioContext(); await ctx.resume();
  const src = ctx.createMediaStreamSource(s), an = ctx.createAnalyser();
  an.fftSize = 2048; src.connect(an);
  const buf = new Float32Array(an.fftSize);
  let peak = 0;
  for (let i=0;i<40;i++){ await new Promise(r=>setTimeout(r,50)); an.getFloatTimeDomainData(buf);
    for (const v of buf) peak = Math.max(peak, Math.abs(v)); }
  return {peak:+peak.toFixed(4), label: s.getAudioTracks()[0].label};
}"""

if __name__ == "__main__":
    pl = mp.Process(target=player); pl.start()
    time.sleep(1.0)
    ctx = sync_playwright().start()
    bctx = ctx.chromium.launch_persistent_context(r"H:\pw-haimian", channel="msedge", headless=True,
        viewport={"width":1440,"height":900}, locale="zh-CN",
        args=["--no-first-run","--use-fake-ui-for-media-stream"])
    bctx.add_init_script("(" + GETMIC + ")()")
    page = bctx.pages[0] if bctx.pages else bctx.new_page()
    page.goto("https://www.haimian.com/", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)
    log("MIC CHECK:", json.dumps(page.evaluate(SAMPLER), ensure_ascii=False))

    def on_resp(r):
        if "voice/info" in r.url or "voice/register" in r.url:
            try:
                t=r.text(); i=t.find("err_message")
                if i>0: log("API-ERR>>>", t[max(0,i-50):i+60].replace("\n"," "))
                elif '"status":1' in t or '"status":0' in t: pass
            except Exception: pass
    page.on("response", on_resp)

    page.goto("https://www.haimian.com/create", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    try: page.get_by_text("我知道了", exact=True).first.click(timeout=2500)
    except Exception: pass
    for step in ["选音色","新增音色","开始清唱"]:
        try: page.get_by_text(step, exact=True).first.click(timeout=8000); log("ok",step)
        except Exception as e: log("fail",step,str(e)[:60])
        page.wait_for_timeout(1500)
    page.wait_for_timeout(58000)
    try: page.locator("text=/^\\s*00:\\d\\d\\s*$/").last.click(timeout=5000); log("stopped")
    except Exception: log("stop fail")
    page.wait_for_timeout(2500)
    try: page.get_by_text("提交", exact=True).first.click(timeout=6000); log("submitted")
    except Exception: log("submit fail")
    for i in range(24):
        page.wait_for_timeout(10000)
        t = modal(page)
        log(f"t+{(i+1)*10}s:", t[-120:].replace("\n"," | "))
        if "制作中" not in t:
            log("END"); break
    page.screenshot(path=os.path.join(OUT,"haimian-23-cable-result.png"))
    log("FINAL:", modal(page)[-300:].replace("\n"," | "))
    bctx.close(); ctx.stop()
    try: pl.terminate()
    except Exception: pass
