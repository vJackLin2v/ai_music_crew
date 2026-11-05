import re, os
SRC = r"H:\小鲸鱼-产出\10首选题-完整版-20261027.md"
text = open(SRC, encoding='utf-8').read()
F = chr(96)*3
new_style = """史诗国风，D 小调，战鼓与低音弦乐铺底，二胡独奏开场，唢呐在主歌末尾切入，副歌加混声合唱；
76-84 BPM；女声主唱，清亮但带沙砾感，主歌压低近乎低语，副歌不飙假声、用真声硬顶上去；
情绪是孤独、倔强、一个人守到最后的悲壮，不哭天抢地，只是不肯退。
Epic Chinese fantasy ballad, female vocal, war drums, erhu, suona, string orchestra, choir, heroic, desolate, cinematic"""
new_lyrics = """[Verse 1]
石头垒的村子 风从骨缝里过
我生来带着至尊骨 后来被人夺走
他们说我这条命 该跪着活
大荒那么大 我偏要一个人走

[Verse 2]
九死一生 只换来一句逆天
走过的地方 后来都成了传说
我把疼都咽下去 把血擦干
因为回头那条路 早就烧断了

[Chorus]
荒天帝 一剑断万古
我守的不是天 是我记得的人
荒天帝 一人镇诸天
黑暗来了 就让它先撞我

[Verse 3]
后来诸天万界 都喊我的名号
喊得再响 也叫不回一个人
故人啊 一个一个先走
我把他们 埋在走过的路上

[Chorus]
荒天帝 一剑断万古
我守的不是天 是我记得的人
荒天帝 一人镇诸天
黑暗来了 就让它先撞我

[Bridge]
（低语）
有人问我 怕不怕
怕
可我不回头
回头 就不是我了

[Outro]
大荒的风 还在吹
我还站在那儿
等一个 永远等不到的人"""
i = text.find('### 4）荒 · ')
j = text.find('\n---\n', i)
if i < 0 or j < 0: raise SystemExit('section not found')
head = text[i:text.find('\n', i)]
block = []
block.append(head)
block.append('')
block.append('**选题来源**：QQ音乐国风热歌榜第 3（原唱平生不晚）｜只借歌名，词曲全新')
block.append('')
block.append('**Style Prompt**')
block.append('')
block.append(F)
block.append(new_style)
block.append(F)
block.append('')
block.append('**歌词**')
block.append('')
block.append(F)
block.append(new_lyrics)
block.append(F)
new = '\n'.join(block)
text = text[:i] + new + text[j:]
open(SRC, 'w', encoding='utf-8').write(text)
print('updated section, chars:', len(new))