import os, re, shutil
SRC = r"H:\小鲸鱼-产出\10首选题-完整版-20261027.md"
DST = r"H:\小鲸鱼-产出\Suno提示词-10首.md"
text = open(SRC, encoding='utf-8').read()
start = text.find('## 一、汽水线')
end = text.find('## 二、B 站线')
body = text[start:end]
F = chr(96) * 3
sections = re.split(r"\n### ", body)[1:]
out = ['# 小鲸鱼 · 10 首 Suno 直接可用', '', '> 每首歌两个代码块：**第一个粘 Styles 框，第二个粘 Lyrics 框**。', '> Advanced 模式下操作，点 Create 即可。', '']
n = 0
for sec in sections:
    head = sec.split('\n', 1)[0].strip()
    m = re.match(r"\d+）\s*(.+?)\s*·\s*(.+)", head)
    if not m: continue
    name = m.group(1).strip(); desc = m.group(2).strip()
    blocks = re.findall(re.escape(F) + r"[^\n]*\n([\s\S]*?)" + re.escape(F), sec)
    if len(blocks) < 2: continue
    n += 1
    out.append(f'## {n}. {name}')
    out.append('')
    out.append(f'*{desc}*')
    out.append('')
    out.append('**① Styles 框**')
    out.append('')
    out.append(F)
    out.append(blocks[0].strip())
    out.append(F)
    out.append('')
    out.append('**② Lyrics 框**')
    out.append('')
    out.append(F)
    out.append(blocks[1].strip())
    out.append(F)
    out.append('')
open(DST, 'w', encoding='utf-8').write('\n'.join(out))
print('songs:', n)
print('bytes:', os.path.getsize(DST))
if os.path.isdir(r"H:\小鲸鱼-产出\suno-ready"):
    shutil.rmtree(r"H:\小鲸鱼-产出\suno-ready"); print('removed suno-ready/')