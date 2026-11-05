
import json, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/141.0 Safari/537.36"}

def get(url, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))

# ---- QQ音乐：先看有哪些榜
q = get("https://u.y.qq.com/cgi-bin/musicu.fcg?data=" + urllib.parse.quote(json.dumps({
    "comm": {"ct": 24, "cv": 0},
    "topList": {"module": "musicToplist.ToplistInfoServer", "method": "GetAll", "param": {}}
}, ensure_ascii=False)))
groups = q["topList"]["data"]["group"]
print("QQ音乐榜单分组：")
for g in groups:
    names = [(t["topId"], t["title"]) for t in g["toplist"]]
    print(" ", g["groupName"], "->", names[:8])
