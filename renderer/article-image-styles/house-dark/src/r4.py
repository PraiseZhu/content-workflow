import sys; sys.path.insert(0, 'src')
from lib2 import *
W, H = 1500, 600
c = Canvas(W, H)
k = 1500/680
TEX = dict(fine=1.35, mid=0.45, scratch=0.22, mottle=0.65, broad=0.3, scale=0.62)
c.background(texture=TEX, hlines=(55*k, 225*k), vlines=(30*k, 300*k), crosses=((30*k, 55*k, 12), (30*k, 225*k, 12), (300*k, 55*k, 12), (300*k, 225*k, 12)), sphere=(587*k, 129*k, 89*k))
c.back = [b.replace('filter="url(#grain)" opacity=".17"', 'filter="url(#grain)" opacity=".085"') for b in c.back]
title_block(c, 96, 150, 'HOUSEBOT', 'AUTOMATED QA', 66, 'LESSONS &amp; RETROSPECTIVE', 23, '3 HOUSE BOTS · BUILD LOG', 15, gap_sub=26)
xs = [x*k + 22 for x in (330, 382, 433, 485, 537)]
row = [(xs[0], 'magenta', 'circle', 'WHITE BOX', ()), (xs[1], 'orange', 'hex', 'GRAY BOX', ()), (xs[2], 'blue', 'circle', 'BLACK BOX', ()),
       (xs[3], 'purple', 'circle', 'AI REVIEW', ()), (xs[4], 'red', 'circle', 'DAILY BOT', ())]
team(c, (sum(xs)/5, 92*k), row, 19*k, 15*k, 160*k, lfs=15.5, chief_label='QA OPS BOT', loop_dx=18*k)
c.render('x-header-5x2.png', 'r4')
