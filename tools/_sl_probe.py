
import json, os, subprocess
from playwright.sync_api import sync_playwright

# 用 PowerShell + DPAPI 取密码（不打印）
ps = ("Add-Type -AssemblyName System.Security | Out-Null; "
      "$j = Get-Content 'H:\\小鲸鱼启停\\snowluma-login.json' -Raw | ConvertFrom-Json; "
      "[Text.Encoding]::UTF8.GetString([Security.Cryptography.ProtectedData]::Unprotect("
      "[Convert]::FromBase64String($j.passwordEnc), $null, "
      "[Security.Cryptography.DataProtectionScope]::CurrentUser))")
pwd = subprocess.run(["powershell","-NoProfile","-Command",ps], capture_output=True, text=True).stdout.strip()
print("pwd len:", len(pwd))

OUT = r"H:\小鲸鱼启停\_sl"
os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(r"H:\pw-snowluma", channel="msedge", headless=True,
        viewport={"width":1400,"height":900}, locale="zh-CN", args=["--no-first-run"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("http://127.0.0.1:5099", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2500)
    page.screenshot(path=os.path.join(OUT, "01-login.png"))
    txt = page.evaluate("() => document.body.innerText.slice(0,400)")
    print("LOGIN PAGE TEXT:", txt.replace("\n", " | ")[:300])

    # 尝试填密码
    for sel in ['input[type=password]', 'input[name=password]', 'input']:
        loc = page.locator(sel)
        if loc.count():
            loc.first.fill(pwd); print("filled via", sel); break
    for lbl in ["登录", "Log in", "Sign in", "进入"]:
        try:
            page.get_by_role("button", name=lbl).first.click(timeout=2000); print("clicked", lbl); break
        except Exception: pass
    page.wait_for_timeout(3500)
    page.screenshot(path=os.path.join(OUT, "02-after-login.png"))
    print("URL:", page.url)
    print("AFTER TEXT:", page.evaluate("() => document.body.innerText.slice(0,600)").replace("\n"," | ")[:500])
    ctx.close()
