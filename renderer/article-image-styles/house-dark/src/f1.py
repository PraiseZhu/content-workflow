import sys; sys.path.insert(0, 'src')
from lib3 import *
W, H = 1600, 800
f = Fig(W, H)
y = 380
# human + collab
f.box(780, 62, 150, 76, '人', kind='green', tfs=40)
f.arrow([(780, 102), (780, 160)], color=GR, dashed=True)
f.text(752, 132, '对不上时拍板', 32, GR, 'end')
cx, cy = 780, 210
f.ball(cx, cy, 44, 'purple')
f.text(842, 192, '协作群 bot', 36, '#F2F2F2', 'start', 700, SANS)
f.text(842, 236, '对字段 · 对口径', 31, GRAY, 'start')
f.arrow([(cx, cy + 50), (cx, 280), (560, 280), (560, y - 72)], color='#8C8C8C', dashed=True, width=3)
f.arrow([(cx, 280), (1000, 280), (1000, y - 72)], color='#8C8C8C', dashed=True, width=3)
# main flow
f.box(165, y, 230, 104, 'PR 合并', kind='dark', tfs=44)
f.arrow([(284, y), (482, y)])
f.text(383, y - 34, '约 12 秒', 32, OR)
f.ball(560, y, 66, 'teal')
f.text(560, y + 104, 'QA 运维 bot', 38, '#F2F2F2', 'middle', 700, SANS)
f.text(560, y + 148, '14 项检查', 32, GRAY)
f.arrow([(636, y), (922, y)])
f.text(779, y - 34, '报告 JSON', 32, OR)
f.ball(1000, y, 66, 'blue')
f.text(1000, y + 104, 'QA 日报 bot', 38, '#F2F2F2', 'middle', 700, SANS)
f.text(1000, y + 148, '每天 9 点', 32, GRAY)
f.arrow([(1076, y), (1130, y), (1130, 300), (1196, 300)])
f.arrow([(1130, y), (1130, 460), (1196, 460)])
f.box(1385, 300, 360, 104, '团队群', '按级别 @ 作者', tfs=40, sfs=30)
f.box(1385, 460, 360, 104, 'P0 / P1', '私信 PR 作者', tfs=40, sfs=30)
# checker
f.ball(780, 610, 40, 'orange', 'hex')
f.text(780, 680, '检查 bot · 挑错', 32, GRAY)
f.arrow([(732, 610), (560, 610), (560, y + 176)], color='#8C8C8C', dashed=True, width=3)
f.arrow([(828, 610), (1000, 610), (1000, y + 176)], color='#8C8C8C', dashed=True, width=3)
f.summary(754, '架构：', '两个 bot 只靠一份报告 JSON 交接，人只在对不上时拍板', 36)
f.render('inline/fig1-architecture.png', 'f1')
