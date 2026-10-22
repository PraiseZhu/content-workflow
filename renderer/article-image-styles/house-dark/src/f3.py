import sys; sys.path.insert(0, 'src')
from lib3 import *
W, H = 1600, 760
f = Fig(W, H)
f.text(800, 46, '每条发现都标明：有没有失败的测试佐证', 30, '#7a7a7a', ls=.06)
f.card(50, 92, 690, 450, 'green', '测试打红 → 开派活工单',
       ['有失败的测试佐证', 'P0 / P1 才开单', '派活进私有仓'], foot='派活要硬证据', tfs=44, ifs=36, ffs=30)
f.card(860, 92, 690, 450, 'orange', 'AI 判断 → 只提醒',
       ['审查判出 P1 → 私信作者', '<span style="color:#9a9a9a;font-size:32px">注明：审查结论，测试未复现</span>',
        'AI 补写的测试失败 → 记 P2', '<span style="color:#9a9a9a;font-size:32px">只算线索，不通知作者</span>'], foot='提醒可以松，但要讲明证据', tfs=44, ifs=34, ffs=30)
f.line(800, 92, 800, 560, OR, dashed=True, width=3)
f.ball(800, 618, 42, 'teal')
f.arrow([(600, 618), (742, 618)], color=GR)
f.arrow([(1000, 618), (858, 618)])
f.text(590, 618, '硬证据', 30, GR, 'end')
f.text(1010, 618, '软证据', 30, OR, 'start')
f.summary(712, '什么算数：', '同样是 P1，有没有测试打红，处理完全不同', 36)
f.render('inline/fig3-evidence.png', 'f3')
