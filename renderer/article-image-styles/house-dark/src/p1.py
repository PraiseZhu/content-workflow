import sys; sys.path.insert(0, 'src')
from lib import *
W, H = 2350, 1000
c = Canvas(W, H)
c.background(hlines=(140, 880), vlines=(96, 1300), crosses=((96,140,22),(1300,140,22),(96,880,22),(1300,880,22),(2200,140,22)),
             sphere=(2335, 790, 300))
# title block
c.html.append('<div class="t" style="left:150px;top:205px;font-size:150px;color:#fff">自动化 QA</div>')
c.html.append('<div class="t" style="left:150px;top:370px;font-size:150px;color:#2EC4B6">只留三件事给人</div>')
c.html.append('<div class="m" style="left:156px;top:585px;font-size:44px;letter-spacing:.04em">3 个 GROK BOT · 18 小时搭完</div>')
c.html.append('<div class="tag" style="left:156px;top:676px;font-size:32px;padding:14px 24px;letter-spacing:.04em">55 分钟跑通 · 合并后 12 秒开测</div>')
# flow
y1, y2 = 330, 710
X = dict(pr=1360, ops=1660, day=1935, chk=1510)
c.node(X['pr'], y1, 62, 'magenta', 'icon', 'merge', label='PR 合并', lfs=30)
c.node(X['ops'], y1, 90, 'teal', label='运维 bot', sub=['14 项检查'], lfs=32, sfs=25)
c.node(X['day'], y1, 80, 'blue', label='日报 bot', sub=['每天早上'], lfs=32, sfs=25)
c.node(X['chk'], y2, 64, 'orange', shape='hex', label='检查 bot', sub=['挑错'], lfs=30, sfs=25)
c.node(X['day'], y2, 64, 'purple', 'icon', 'chat', label='团队群', sub=['@ 作者'], lfs=30, sfs=25)
c.edge([(X['pr']+62+12, y1), (X['ops']-90-14, y1)])
c.elabel((X['pr']+X['ops'])/2 + 14, y1-24, '12 秒', 22)
c.edge([(X['ops']+90+12, y1), (X['day']-80-14, y1)])
c.elabel((X['ops']+X['day'])/2 + 5, y1-24, 'JSON', 22)
c.edge([(X['day'], 555), (X['day'], y2-64-14)], dot_start=True)
c.edge([(X['chk'], y2-64-12), (X['chk'], 610), (X['ops'], 610), (X['ops'], 562)], dashed=True, arrow=False)
c.dot(X['ops'], 555)
c.render('cover-2.35.png', 'p1')
