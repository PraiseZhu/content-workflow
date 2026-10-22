import sys; sys.path.insert(0, 'src')
from lib import *
W, H = 1500, 600
c = Canvas(W, H)
c.background(hlines=(84, 530), vlines=(56, 860), crosses=((56,84,15),(860,84,15),(56,530,15),(860,530,15),(1400,84,15)),
             sphere=(1490, 540, 215))
c.html.append('<div class="t" style="left:90px;top:150px;font-size:76px;color:#fff;letter-spacing:-0.005em">AUTOMATED QA</div>')
c.html.append('<div class="t" style="left:90px;top:234px;font-size:76px;color:#2EC4B6;letter-spacing:-0.005em">RAN IN 55 MIN</div>')
c.html.append('<div class="m" style="left:94px;top:346px;font-size:25px;letter-spacing:.06em">TRUSTING IT TOOK THE WEEKEND</div>')
c.html.append('<div class="tag" style="left:94px;top:400px;font-size:19px;padding:9px 16px;letter-spacing:.08em">3 HOUSE BOTS · BUILD LOG</div>')
y1, y2 = 205, 445
X = dict(pr=950, ops=1135, day=1320, chk=1040)
F = 19
c.node(X['pr'], y1, 42, 'magenta', 'icon', 'merge', label='PR MERGED', lfs=F)
c.node(X['ops'], y1, 60, 'teal', label='QA OPS BOT', sub=['14 CHECKS'], lfs=F, sfs=15)
c.node(X['day'], y1, 54, 'blue', label='DAILY REPORT', lfs=F)
c.node(X['chk'], y2, 44, 'orange', shape='hex', label='CHECKER BOT', lfs=F)
c.node(X['day'], y2, 44, 'purple', 'icon', 'chat', label='TEAM CHAT', lfs=F)
c.edge([(X['pr']+42+10, y1), (X['ops']-60-12, y1)])
c.elabel((X['pr']+X['ops'])/2+4, y1-16, '12s', 15)
c.edge([(X['ops']+60+10, y1), (X['day']-54-12, y1)])
c.elabel((X['ops']+X['day'])/2+3, y1-16, 'JSON', 15)
c.edge([(X['day'], 300), (X['day'], y2-44-12)], dot_start=True)
c.edge([(X['chk'], y2-44-10), (X['chk'], 372), (X['ops'], 372), (X['ops'], 352)], dashed=True, arrow=False)
c.dot(X['ops'], 348)
c.render('x-header-5x2.png', 'p4')
