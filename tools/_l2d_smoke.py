
import os, json, base64, time
from playwright.sync_api import sync_playwright
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = r"H:\ai_music_crew\live2d\out"
os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EDGE, headless=True, args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width":1080,"height":1920})
    pg.goto("http://127.0.0.1:8765/index.html", wait_until="load", timeout=60000)
    for i in range(40):
        ready = pg.evaluate("() => window.__ready")
        err = pg.evaluate("() => window.__err")
        if err: print("ERR:", err[:500]); break
        if ready: break
        time.sleep(0.5)
    print("ready:", pg.evaluate("() => window.__ready"), "err:", pg.evaluate("() => window.__err"))
    if pg.evaluate("() => window.__ready"):
        print("info:", pg.evaluate("() => window.info()"))
        for f in range(3):
            pg.evaluate("(dt) => window.step(dt)", 1/30)
        pg.evaluate("() => { window.setMouth(0.65); window.setEye(1); }")
        pg.evaluate("(dt) => window.step(dt)", 1/30)
        data = pg.evaluate("() => window.snap()")
        raw = base64.b64decode(data.split(",",1)[1])
        open(os.path.join(OUT,"smoke.png"),"wb").write(raw)
        print("saved smoke.png", len(raw), "bytes")
    b.close()
