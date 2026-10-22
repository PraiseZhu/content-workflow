import sys; sys.path.insert(0, 'src')
from lib import *
W, H = 900, 900
c = Canvas(W, H)
c.background(hlines=(70, 830), vlines=(60, 840), crosses=((60,70,16),(840,70,16),(60,830,16)), sphere=(870, 875, 250))
c.html.append('<div class="t" style="left:80px;top:118px;font-size:118px;color:#fff">自动化 QA</div>')
c.html.append('<div class="t" style="left:80px;top:248px;font-size:118px;color:#2EC4B6">只留三件事</div>')
c.html.append('<div class="m" style="left:84px;top:402px;font-size:30px;letter-spacing:.03em">3 个 HOUSE BOT · 18 小时</div>')
c.html.append('<div class="tag" style="left:84px;top:458px;font-size:23px;padding:9px 16px;letter-spacing:.03em">什么算数 · 谁说了算 · 合并键</div>')
# main bot
x, y, r = 320, 680, 100
c.node(x, y, r, 'teal', label='QA 运维 BOT', lfs=26, gap=22)
c.edge([(x+r+12, y), (520, y), (520, 610)], arrow=False)
c.dot(520, 610)
c.front.append(c.text(540, 618, '14 项检查', 24, '#e9e9ec', 'start', 500))
c.edge([(x-r-12, y), (150, y), (150, 600)], arrow=False)
c.dot(150, 600)
c.render('cover-1x1.png', 'p2')
