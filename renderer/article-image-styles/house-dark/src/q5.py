import sys; sys.path.insert(0, 'src')
from lib2 import *
W, H = 1600, 900
c = Canvas(W, H)
c.background(hlines=(120, 820), vlines=(44, 700), crosses=((44, 120, 13), (44, 820, 13), (700, 120, 13), (700, 820, 13)), sphere=(1432, 470, 180))
title_block(c, 72, 230, 'HOUSEBOT', 'AUTOMATED QA', 60, 'LESSONS &amp; RETROSPECTIVE', 21, '3 HOUSE BOTS · BUILD LOG', 14, gap_sub=22)
# human chip
c.chip(0, 650, ['HUMAN DECIDES', 'what counts as evidence', 'whose word is final', 'the merge button'], fs=17, pad=16, x0=76)
cx, cy = 1060, 235
row_y = 480
xs = [840, 1060, 1280]
row = [(xs[0], 'blue', 'circle', 'DAILY REPORT BOT', ('every morning',)),
       (xs[1], 'purple', 'circle', 'COLLAB CHAT BOT', ('fields & wording',)),
       (xs[2], 'orange', 'hex', 'CHECKER BOT', ('relays · picks holes',))]
bus, by = team(c, (cx, cy), row, 44, 40, row_y, lfs=16, sfs=13.5, chief_label='QA OPS BOT', loop_dx=92)
R = 44*1.45
# drop labels
for x, t in zip(xs, ['report JSON', 'align', 'review']):
    c.elabel(x + 12, (bus + row_y - 40)/2 + 6, t, 13, anchor='start', pad=4)
# inputs
c.chip(900, 62, ['PR MERGED · ~12s'], fs=15, pad=10)
c.chip(1230, 62, ['CATCH-UP · EVERY 2H'], fs=15, pad=10)
c.edge([(900, 79), (900, 118), (cx, 118)], arrow=False)
c.edge([(1230, 79), (1230, 118), (cx, 118)], arrow=False)
c.dot(cx, 118, 4)
c.edge([(cx, 118), (cx, cy - R - 6)])
# sides
c.chip(0, cy, ['ISSUE · PRIVATE REPO', 'P0/P1 + failing test'], fs=15, pad=11, x0=682)
c.edge([(cx - R, cy), (890, cy)])
c.chip(0, cy, ['14 CHECKS', 'white / gray / black box', 'AI review · coverage gate'], fs=15, pad=11, x0=1162)
c.edge([(cx + R, cy), (1154, cy)])
# outputs from daily
c.front.append(c.text(1060, by + 30, 'ONE SHARED GROUP CHAT', 13, '#9b9b9f', 'middle', 500, ls=.1))
c.edge([(840, by), (840, 700)], arrow=False)
c.edge([(840, 700), (740, 700), (740, 735)])
c.edge([(840, 700), (960, 700), (960, 735)])
c.chip(740, 770, ['TEAM CHAT', '@ author by severity'], fs=15, pad=10)
c.chip(960, 770, ['DM PR AUTHOR', 'P0 / P1'], fs=15, pad=10)
c.render('x-flow-16x9.png', 'q5')
