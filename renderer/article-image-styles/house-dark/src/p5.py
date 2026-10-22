import sys; sys.path.insert(0, 'src')
from lib import *
W, H = 1600, 900
c = Canvas(W, H)
c.background(hlines=(250, 860), vlines=(50, 1150), crosses=((50,250,15),(1150,250,15),(50,860,15),(1150,860,15)),
             sphere=(1550, 890, 195))
c.html.append('<div class="tag" style="left:70px;top:52px;font-size:16px;padding:6px 12px;letter-spacing:.08em">QA PIPELINE · 3 HOUSE BOTS</div>')
c.html.append('<div class="t" style="left:68px;top:98px;font-size:56px;color:#fff">AUTOMATED QA</div>')
c.html.append('<div class="t" style="left:68px;top:158px;font-size:56px;color:#2EC4B6">THE FULL LOOP</div>')
F, S = 18, 14.5
# inputs
c.node(140, 420, 50, 'magenta', 'icon', 'merge', label='PR MERGED', sub=['GitHub event · ~12s'], lfs=F, sfs=S, gap=14)
c.node(140, 700, 50, 'purple', 'icon', 'clock', label='CATCH-UP SCRIPT', sub=['every 2h · no model calls'], lfs=F, sfs=S, gap=14)
c.edge([(140+50+12, 420), (290, 420), (290, 560), (440-88-14, 560)])
c.edge([(140+50+12, 700), (290, 700), (290, 560)], arrow=False)
c.dot(290, 560)
# ops
c.node(440, 560, 88, 'teal')
ly = 650
for i, (t, fs, col, w) in enumerate([('QA OPS BOT', 20, '#fff', 600), ('14 checks', 15.5, '#e0e0e4', 500),
        ('white / gray / black box', 14.5, '#9a9a9f', 400), ('+ AI review + coverage gate', 14.5, '#9a9a9f', 400)]):
    c.front.append(c.text(505, ly, t, fs, col, 'start', w)); ly += fs*1.5 + (4 if i == 0 else 0)
# issue
c.edge([(440, 560+88+12), (440, 800-44-14)])
c.node(440, 800, 44, 'red', 'icon', 'issue', label='ISSUE · PRIVATE REPO', sub=['P0/P1 + failing test'], lpos='right', lfs=16, sfs=S, gap=18)
# JSON
c.node(780, 560, 50, 'orange', 'icon', 'json', label='REPORT JSON', sub=['one per PR'], lpos='above', lfs=16, sfs=S, gap=12)
c.edge([(440+88+12, 560), (780-50-14, 560)])
# daily
c.node(1090, 560, 80, 'blue', label='DAILY REPORT BOT', sub=['every morning'], lfs=F, sfs=S, gap=16)
c.edge([(780+50+12, 560), (1090-80-14, 560)])
# collab + checker
c.node(780, 300, 54, 'purple', label='COLLAB CHAT BOT', sub=['agree on fields & wording'], lfs=16, sfs=S, gap=12)
c.edge([(440, 560-88-14), (440, 300), (780-54-14, 300)], dashed=True, both=True)
c.edge([(1090, 560-80-14), (1090, 300), (780+54+14, 300)], dashed=True, both=True)
c.node(780, 120, 46, 'orange', shape='hex', label='CHECKER BOT', sub=['relays plans · picks holes'], lpos='right', lfs=16, sfs=S, gap=18)
c.edge([(780, 120+46+10), (780, 300-54-12)], dashed=True, arrow=False)
# outputs
c.edge([(1090+80+12, 560), (1440-50-14, 560)])
c.edge([(1260, 560), (1260, 370), (1440-50-14, 370)])
c.dot(1260, 560)
c.node(1440, 370, 50, 'magenta', 'icon', 'chat', label='TEAM CHAT', sub=['@ author by severity'], lfs=F, sfs=S, gap=14)
c.node(1440, 560, 50, 'red', 'icon', 'mail', label='DM PR AUTHOR', sub=['P0 / P1'], lfs=F, sfs=S, gap=14)
# human box
c.box(1180, 52, 360, 150, fill='#0b0b0c', op=0.55)
c.front.append('<circle cx="1230" cy="127" r="28" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="1.8"/>')
c.front.append(c.icon('human', 1230, 127, 50))
c.front.append(c.text(1280, 92, 'HUMAN KEEPS 3 THINGS', 17, '#2EC4B6', 'start', 700))
for i, t in enumerate(['what counts as evidence', 'whose word is final', 'the merge button']):
    c.front.append(c.text(1280, 125 + i*24, '· ' + t, 15, '#e9e9ec', 'start', 500))
c.render('x-flow-16x9.png', 'p5')
