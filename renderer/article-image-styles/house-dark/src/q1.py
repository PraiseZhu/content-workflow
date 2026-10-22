import sys; sys.path.insert(0, 'src')
from lib2 import *
W, H = 2350, 1000
c = Canvas(W, H)
k = 1000/272
scx = 2350 - 93*k
off = lambda xr: scx + (xr - 587)*k
TEX = dict(fine=2.0, mid=1.0, scratch=0.9, mottle=1.6, broad=0.4, scale=1.0)
c.background(texture=TEX, hlines=(55*k, 225*k), vlines=(30*k, off(300)), crosses=((30*k, 55*k, 18), (30*k, 225*k, 18), (off(300), 55*k, 18), (off(300), 225*k, 18)),
             sphere=(scx, 129*k, 89*k))
title_block(c, 160, 262, 'GROK BOT', '自动化 QA', 142, '实践经验和复盘', 46, '3 个 GROK BOT · 完整复盘', 30, gap_sub=40)
xs = [off(x) for x in (330, 382, 433, 485, 537)]
row = [(xs[0], 'magenta', 'circle', '白盒', ()), (xs[1], 'orange', 'hex', '灰盒', ()), (xs[2], 'blue', 'circle', '黑盒', ()),
       (xs[3], 'purple', 'circle', 'AI 审查', ()), (xs[4], 'red', 'circle', '日报 bot', ())]
team(c, (xs[2], 92*k), row, 19*k, 15*k, 160*k, lfs=31, chief_label='QA 运维 bot', loop_dx=18*k, sw=2.6)
c.render('cover-2.35.png', 'q1')
