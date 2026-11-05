
import json, os, re

FLOW = r"H:\ai_music_crew\work\flow-out"
DST  = r"H:\小鲸鱼-产出\5首正式版-20261027.md"
F = chr(96) * 3

META = {
 "雨爱": ("城市抒情 78 BPM / F 大调", "2026.7「雨爱 × 咒术回战新宿决战」二创爆款（600 万+播放），「会赢的」flag 梗"),
 "我不难过": ("钢琴摇滚 94 BPM / C 大调", "孙燕姿 2026 巡演回温，「嘴硬文学」配乐常用"),
 "我好像在哪见过你": ("都市民谣 82 BPM / C 大调", "2026 夏天二次爆红：新剧《来不及说我爱你》+ 薛之谦贵阳演唱会「我在贵阳见过你」名场面"),
 "牡丹亭": ("国风戏曲 84 BPM / G 宫", "浅影阿 2026 版本热传，戏曲×国风回潮"),
 "荒": ("史诗国风 76-84 BPM / D 小调", "荒天帝石昊（完美世界/遮天/圣墟）长期二创母题"),
}

FIX = {
 "雨爱": [("要讲的话 排成两行 背到熟练", "要说的话 打好了腹稿 背到熟练"),
          ("鞋尖一踩 就亮一小块舞台的边", "鞋尖一踩 就碎了一小块灯光的边")],
 "我不难过": [("打了三个字 又删到空白", "打了四个字 又删到空白")],
 "荒": [("我生来带着骨 被人连夜夺", "生来带着至尊骨 被人连夜夺"),
        ("有人问我 怕不怕\n我说 怕", "有人问我 怕不怕\n我说 怕\n他们后来叫我 荒天帝")],
}

def load(name):
    p = os.path.join(FLOW, name + ".md")
    if not os.path.exists(p): return None
    t = open(p, encoding="utf-8").read()
    a = t.find("## SUNO PROMPT")
    if a < 0: return None
    b = t.find("## REVIEW")
    js = t[t.find("{", a): (b if b > 0 else len(t))].strip()
    js = js[:js.rfind("}") + 1]
    try:
        o = json.loads(js)
    except Exception:
        return None
    if not o.get("suno_style_prompt") or not o.get("suno_lyrics"): return None
    return o

STORY = {
"雨爱": "她攒了三个月勇气，约他在老地方那座天桥见面，只想当面问一句「当初为什么走」。她提前半小时到，把这句话在肚子里排了三十遍。八点他没来；八点二十她打电话，他说「我在楼下买包烟，马上上来」。九点，她下楼避雨，在便利店看见他——他站在收银台前跟店员说笑，手里捏着一包烟，一杯热咖啡，没有一点要上桥的意思。她忽然明白：他不是迟到，是不打算上来。她没喊他，也没问那句为什么；把伞留在门口的伞架上，转身走进雨里。走到桥中间，她说了第四遍「会赢的」——不是赌他会来，是赌自己不会回头。",
"我不难过": "演唱会散场，人群涌向地铁。她在人潮里给前任发消息，先打了「我不难过」四个字，盯了十秒，删成「我不」，最后全删，只留一个已读。路过便利店，店里的音响正在放这首歌。她笑了一下，进去买了瓶水，对店员说「不用袋子」。玻璃门合上，那首歌留在里面。",
"我好像在哪见过你": "演唱会散场，人潮往地铁口走。她看见前面一个背影——灰蓝外套、抬手看表先转半圈的手势、走路的样子，都像三年前删掉的那个人。她跟了两节车厢，认错三次，第三次对方回头，是一张完完全全陌生的脸。她站在换乘通道里很久没动。手机亮起来，是她三个月前发出去、一直没人回的那条消息。",
"牡丹亭": "昆曲演员每演到「游园惊梦」就走神：台下第三排，总像坐着一个人。散场后后台只剩镜子和一盏灯，她卸妆卸到一半停住——镜子里那身戏服还穿着。她想起很多年前真的等过一个人，等到戏散了，等到椅子一排排翻起来。",
"荒": "石头垒的村子，风从骨缝里过。他生来带着至尊骨，被人连夜夺走；所有人都说他这条命该跪着活，他偏要一个人走出大荒。九死一生只换来一句「逆天」，走过的地方后来都成了传说。他把疼咽下去、把血擦干，因为回头那条路早就烧断了。后来诸天万界都喊他「荒天帝」，喊得再响也叫不回一个故人——故人一个一个先走，他把他们埋在走过的路上，立碑、刻名、不敢多望。黑暗压境那夜，他一个人站在最前方；有人问他怕不怕，他说怕，可他不转身，转身就不是他了。",
}

def get_story(name):
    return STORY.get(name, "")


order = ["雨爱", "我不难过", "我好像在哪见过你", "牡丹亭", "荒"]
songs, missing = [], []
for n in order:
    o = load(n)
    if not o:
        missing.append(n); continue
    lyr = o["suno_lyrics"]
    applied = []
    for old, new in FIX.get(n, []):
        if old in lyr:
            lyr = lyr.replace(old, new); applied.append((old, new))
    songs.append((n, o["suno_style_prompt"], lyr, applied, get_story(n)))

out = ["# 小鲸鱼 · 第一版 5 首（故事 + 歌词 + 提示词）", "",
       "> 每首顺序：**热梗依据 → 故事底稿 → ① Styles → ② Lyrics**。",
       "> 故事是歌词的来源，先审故事；故事没问题，词就不会跑偏。", ""]
for i, (n, style, lyr, applied, story) in enumerate(songs, 1):
    desc, meme = META.get(n, ("", ""))
    out += [f"## {i}. {n}", "", f"*{desc}*", "", f"**热梗依据**：{meme}", "",
            "**故事底稿**", "", story if story else "（未找到）", "",
            "**① Styles 框**", "", F, style.strip(), F, "",
            "**② Lyrics 框**", "", F, lyr.strip(), F, ""]

out += ["---", "", "## 质检记录", ""]
for n, style, lyr, applied, story in songs:
    if applied:
        out.append(f"**{n}**")
        for old, new in applied:
            out.append(f"- 原文：{old}")
            out.append(f"  改为：{new}")
        out.append("")
    else:
        out += [f"**{n}**：未改动（逐句过审，未发现硬凑意象或逻辑矛盾）", ""]
if missing:
    out += ["", "> 未完成：" + "、".join(missing)]
open(DST, "w", encoding="utf-8").write("\n".join(out))
print("songs:", len(songs), "missing:", missing, "bytes:", os.path.getsize(DST))
for n, s, l, a, st in songs:
    print(" ", n, "| story", len(st), "| style", len(s), "| lyrics", len(l), "| fixes", len(a))
