
import os, json, base64, time
import numpy as np, librosa
from playwright.sync_api import sync_playwright

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = r"H:\ai_music_crew\live2d\out"
FRAMES = os.path.join(OUT, "frames_hd")
os.makedirs(FRAMES, exist_ok=True)
AUD = r"H:\ai_music_crew\out\yuai-chorus\雨爱副歌_cover.wav"
FPS = 30
SCALE, POSY = 0.85, 0.62

y, sr = librosa.load(AUD, sr=22050, mono=True)
dur = len(y)/sr
hop = int(sr/FPS)
env = np.array([np.sqrt(np.mean(y[i:i+hop]**2)) if i+hop <= len(y) else 0.0 for i in range(0, len(y), hop)])
env = env/(np.percentile(env, 95)+1e-6)
env = np.clip(env,0,1)**0.65
env = np.convolve(env, np.ones(4)/4, mode="same")
N = int(dur*FPS)
env = np.pad(env, (0, max(0, N-len(env))))[:N]

rng = np.random.default_rng(11)
blinks=[]; t=1.2
while t < dur:
    blinks.append(t); t += rng.uniform(2.4, 4.6)
def blink(tt):
    for b in blinks:
        d = tt-b
        if 0 <= d < 0.18:
            return max(0.0, 1-(d/0.09)) if d<0.09 else (d-0.09)/0.09
    return 1.0

EXPR = [(0.0,"开心兴奋"), (10.0,"调皮"), (20.0,"脸红")]
t0=time.time()
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EDGE, headless=True,
        args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width":1080,"height":1920})
    pg.goto("http://127.0.0.1:8765/index.html", wait_until="load", timeout=60000)
    for _ in range(60):
        if pg.evaluate("() => window.__ready"): break
        time.sleep(0.3)
    pg.evaluate("""(a) => { const m=window.model; const h=m.internalModel.height||m.height;
        m.scale.set((1920*a.s)/h); m.position.set(540, 1920*a.p); }""", {"s":SCALE,"p":POSY})
    pg.evaluate("() => { try{ window.motion('idle'); }catch(e){} }")
    cur=None
    for i in range(N):
        tt=i/FPS
        for at,name in EXPR:
            if tt>=at and cur!=name:
                cur=name; pg.evaluate("(n)=>{ try{ window.expr(n); }catch(e){} }", name)
        pg.evaluate("""(a)=>{ window.setMouth(a.m); window.setEye(a.e); window.step(1/30); }""",
                    {"m": float(env[i]), "e": blink(tt)})
        data = pg.evaluate("() => window.snap()")
        open(os.path.join(FRAMES, f"f{i:05d}.png"),"wb").write(base64.b64decode(data.split(",",1)[1]))
        if i%150==0: print(f"{i}/{N} {time.time()-t0:.0f}s", flush=True)
    b.close()
print("done", N, round(time.time()-t0), "s", flush=True)
