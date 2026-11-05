
import os, json, base64, time
from playwright.sync_api import sync_playwright
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUT = r"H:\ai_music_crew\live2d\out"
tests = [(0.62, 0.50), (0.85, 0.62), (1.00, 0.70)]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EDGE, headless=True,
        args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width":1080,"height":1920})
    pg.goto("http://127.0.0.1:8765/index.html", wait_until="load", timeout=60000)
    for _ in range(60):
        if pg.evaluate("() => window.__ready"): break
        time.sleep(0.3)
    for i,(s, py_ratio) in enumerate(tests):
        pg.evaluate("""(a) => {
            const m = window.model;
            const h = m.internalModel.height || m.height;
            m.scale.set((1920 * a.s) / h);
            m.position.set(540, 1920 * a.p);
            window.setMouth(0.7); window.setEye(1);
            window.step(1/30);
        }""", {"s": s, "p": py_ratio})
        data = pg.evaluate("() => window.snap()")
        raw = base64.b64decode(data.split(",",1)[1])
        open(os.path.join(OUT, f"fit{i}.png"),"wb").write(raw)
        print("saved fit", i, s, py_ratio, len(raw))
    b.close()
