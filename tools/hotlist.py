
import json, urllib.parse, urllib.request, datetime, os

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/141.0 Safari/537.36"}
def get(url, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))

def qq_top(top_id, num=20):
    d = {"comm": {"ct": 24, "cv": 0},
         "topList": {"module": "musicToplist.ToplistInfoServer", "method": "GetDetail",
                     "param": {"topId": top_id, "offset": 0, "num": num}}}
    r = get("https://u.y.qq.com/cgi-bin/musicu.fcg?data=" + urllib.parse.quote(json.dumps(d, ensure_ascii=False)))
    data = r["topList"]["data"]
    out = []
    for s in data["songInfoList"]:
        out.append({
            "rank": len(out) + 1,
            "title": s.get("title", ""),
            "singer": "、".join(x.get("name", "") for x in s.get("singer", [])),
            "album": (s.get("album") or {}).get("name", ""),
            "duration": s.get("interval"),
        })
    return data.get("title", ""), out

def bili_covers(num=20):
    r = get("https://api.bilibili.com/x/web-interface/ranking/v2?rid=3&type=all",
            {"Referer": "https://www.bilibili.com/"})
    out = []
    for v in r["data"]["list"]:
        if v.get("tname") not in ("翻唱", "音乐", "原创音乐", "演奏"):
            continue
        out.append({
            "rank": len(out) + 1,
            "title": v.get("title", ""),
            "up": (v.get("owner") or {}).get("name", ""),
            "category": v.get("tname", ""),
            "views": (v.get("stat") or {}).get("view", 0),
            "bvid": v.get("bvid", ""),
        })
        if len(out) >= num:
            break
    return out

day = datetime.date.today().isoformat()
res = {}
name, songs = qq_top(26, 20)
res["qq_rehot"] = {"name": name, "items": songs}
name2, songs2 = qq_top(65, 10)
res["qq_guofeng"] = {"name": name2, "items": songs2}
res["bili_covers"] = bili_covers(20)

os.makedirs(r"H:\ai_music_crew\hotlist", exist_ok=True)
p = rf"H:\ai_music_crew\hotlist\{day}.json"
json.dump(res, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("saved", p)
print("\n=== QQ", res["qq_rehot"]["name"])
for s in songs[:10]:
    print(f"{s['rank']:2d}. {s['title']} — {s['singer']}")
print("\n=== 国风热歌榜")
for s in songs2[:8]:
    print(f"{s['rank']:2d}. {s['title']} — {s['singer']}")
print("\n=== B站音乐区 翻唱/音乐 热门")
for v in res["bili_covers"][:12]:
    print(f"{v['rank']:2d}. [{v['category']}] {v['title'][:40]} — {v['up']} ({v['views']//10000}万播放)")
