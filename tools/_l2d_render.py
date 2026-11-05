
import os, json, base64, time, math
import numpy as np
import librosa
from playwright.sync_api import sync_playwright

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = r"H:\ai_music_crew\live2d\out"
FRAMES = os.path.join(OUT, "frames")
os.makedirs(FRAMES, exist_ok=True)
AUD = r"H:\ai_music_crew\out\yuai-chorus\雨爱副歌_cover.wav"
FPS = 30

y, sr = librosa.load(AUD, sr=22050, mono=True)
dur = len(y) / sr
hop = int(sr / FPS)
env = np.array([np.sqrt(np.mean(y[i:i+hop]**2)) if i+hop <= len(y) else 0.0 for i in range(0, len(y), hop)])
env = env / (np.percentile(env, 95) + 1e-6)
env = np.clip(env, 0, 1) ** 0.65
# 平滑
k = np.ones(4) / 4
env = np.convolve(env, k, mode="same")
N = int(dur * FPS)
env = env[:N]
if len(env) < N: env = np.pad(env, (0, N - len(env)))
print("frames:", N, "dur:", round(dur,2), "env max:", round(float(env.max()),2), flush=True)

# 眨眼时间点
rng = np.random.default_rng(7)
blinks = []
t = 1.5
while t < dur:
    blinks.append(t); t += rng.uniform(2.6, 5.2)

def blink_val(tt):
    for b in blinks:
        d = tt - b
        if 0 <= d < 0.18:
            return max(0.0, 1 - (d / 0.09)) if d < 0.09 else (d - 0.09) / 0.09
    return 1.0

t0 = time.time()
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EDGE, headless=True,
        args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width":1080,"height":1920})
    pg.goto("http://127.0.0.1:8765/index.html", wait_until="load", timeout=60000)
    for _ in range(60):
        if pg.evaluate("() => window.__ready"): break
        time.sleep(0.3)
    pg.evaluate("() => { try { window.motion('idle'); } catch(e){} try { window.expr('开心兴奋'); } catch(e){} }")
    for i in range(N):
        tt = i / FPS
        m = float(env[i])
        e = blink_val(tt)
        pg.evaluate("""(a) => { window.setMouth(a.m); window.setEye(a.e); window.step(1/30); }""",
                    {"m": m, "e": e})
        data = pg.evaluate("() => window.snap()")
        raw = base64.b64decode(data.split(",",1)[1])
        open(os.path.join(FRAMES, f"f{i:05d}.png"), "wb").write(raw)
        if i % 100 == 0:
            print(f"frame {i}/{N}  {time.time()-t0:.0f}s", flush=True)
    b.close()
print("done", N, "frames in", round(time.time()-t0), "s", flush=True)
