
import sys, json
from playwright.sync_api import sync_playwright
WAV = sys.argv[1]
ARGS = ["--no-first-run","--use-fake-ui-for-media-stream","--use-fake-device-for-media-stream",
        f"--use-file-for-fake-audio-capture={WAV}"]
JS = """async () => {
  const stream = await navigator.mediaDevices.getUserMedia({audio:true});
  const ctx = new AudioContext();
  const src = ctx.createMediaStreamSource(stream);
  const an = ctx.createAnalyser(); an.fftSize = 2048; src.connect(an);
  const buf = new Float32Array(an.fftSize);
  let peak = 0, rmsSum = 0, n = 0;
  for (let i=0;i<40;i++){
    await new Promise(r=>setTimeout(r,50));
    an.getFloatTimeDomainData(buf);
    for (const v of buf){ peak = Math.max(peak, Math.abs(v)); rmsSum += v*v; n++; }
  }
  return {peak: +peak.toFixed(4), rms: +Math.sqrt(rmsSum/n).toFixed(5),
          devices: (await navigator.mediaDevices.enumerateDevices()).filter(d=>d.kind==='audioinput').map(d=>d.label)};
}"""
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True, args=ARGS)
    pg = b.new_context().new_page()
    pg.goto("https://www.haimian.com/", wait_until="domcontentloaded", timeout=45000)
    pg.wait_for_timeout(1500)
    print(WAV.split("\\")[-1], "->", json.dumps(pg.evaluate(JS), ensure_ascii=False))
    b.close()
