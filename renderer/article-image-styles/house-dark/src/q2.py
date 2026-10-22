import sys; sys.path.insert(0, 'src')
from lib2 import *
W, H = 900, 900
c = Canvas(W, H)
TEX = dict(fine=1.7, mid=0.9, scratch=0.8, mottle=1.4, broad=0.4, scale=0.9)
c.background(texture=TEX, hlines=(60, 600), vlines=(44,), crosses=((44, 60, 14), (44, 600, 14), (856, 60, 14)), sphere=(690, 750, 225))
title_block(c, 72, 92, 'HOUSE BOT', '自动化 QA', 112, '实践经验和复盘', 38, '3 个 HOUSE BOT · 完整复盘', 23, gap_sub=30)
c.bot(250, 735, 66, 'teal', ring=True, label='QA 运维 bot', lfs=26)
c.render('cover-1x1.png', 'q2')
