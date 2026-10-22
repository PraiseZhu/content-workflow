import sys; sys.path.insert(0, 'src')
from lib3 import *
W, H = 1600, 790
f = Fig(W, H)
f.text(800, 46, '机器管到哪，人管到哪', 30, '#7a7a7a', ls=.08)
f.card(50, 92, 690, 440, 'orange', '机器 → 自己跑完',
       ['触发 · 测试 · 补测', '修环境 · 写报告', '@ 人 · 发私信'], foot='告诉我它测了什么', tfs=46, ifs=38, ffs=30)
f.card(860, 92, 690, 440, 'green', '人 → 留下三件事',
       ['定什么算数', '定谁说了算', '按合并键'], foot='规则只认我亲口说过的话', tfs=46, ifs=38, ffs=30)
f.line(800, 92, 800, 552, OR, dashed=True, width=3)
f.ball(800, 606, 42, 'teal')
f.text(800, 672, 'bot 停在这里', 30, OR)
f.arrow([(560, 606), (742, 606)])
f.arrow([(1040, 606), (858, 606)], color=GR)
f.text(548, 606, '7 件事自动跑', 30, OR, 'end')
f.text(1052, 606, '3 件事归人', 30, GR, 'start')
f.summary(748, '边界：', '这算不算问题、该谁去修，得人来定', 38)
f.render('inline/fig4-boundary.png', 'f4')
