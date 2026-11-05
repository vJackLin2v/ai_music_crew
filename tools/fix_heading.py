import io
SRC = r"H:\小鲸鱼-产出\10首选题-完整版-20261027.md"
t = open(SRC, encoding='utf-8').read()
old = '### 4）荒 · 苍凉古风 70-78 BPM / D 小调'
new = '### 4）荒 · 史诗国风（荒天帝石昊） 76-84 BPM / D 小调'
if old in t:
    t = t.replace(old, new); open(SRC,'w',encoding='utf-8').write(t); print('heading updated')
else:
    import re
    m = re.search(r'### 4）荒 · [^\n]*', t)
    print('not found, current:', m.group(0) if m else 'none')