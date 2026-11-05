import os, re, json
SRC = r"H:\小鲸鱼-产出\10首选题-完整版-20261027.md"
DST = r"H:\小鲸鱼-产出\suno-ready"
os.makedirs(DST, exist_ok=True)
text = open(SRC, encoding='utf-8').read()
start = text.find('## 一、汽水线')
end = text.find('## 二、B 站线')
body = text[start:end]
F = chr(96) * 3
sections = re.split(r"\n### ", body)[1:]
rows = []
for sec in sections:
    head = sec.split('\n', 1)[0].strip()
    m = re.match(r"\d+）\s*(.+?)\s*·\s*(.+)", head)
    if not m: continue
    name = m.group(1).strip()
    blocks = re.findall(re.escape(F) + r"[^\n]*\n([\s\S]*?)" + re.escape(F), sec)
    if len(blocks) < 2:
        print('skip', name); continue
    style, lyrics = blocks[0].strip(), blocks[1].strip()
    safe = re.sub(r'[\\/:*?"<>|]', "_", name)
    open(os.path.join(DST, f"{safe}.style.txt"), "w", encoding="utf-8").write(style)
    open(os.path.join(DST, f"{safe}.lyrics.txt"), "w", encoding="utf-8").write(lyrics)
    rows.append({"name": name, "style": len(style), "lyrics": len(lyrics)})
json.dump(rows, open(os.path.join(DST, "_index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for r in rows: print(r['name'], r['style'], r['lyrics'])
print('total', len(rows))