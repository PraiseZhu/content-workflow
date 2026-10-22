import sys; sys.path.insert(0, 'src')
from lib2 import *
W, H = 1080, 2160
c = Canvas(W, H)
c.background(hlines=(530, 2020), vlines=(44, 1036), crosses=((44, 530, 15), (1036, 530, 15), (44, 2020, 15), (1036, 2020, 15)), sphere=(880, 300, 205))
title_block(c, 70, 96, 'HOUSE BOT', '自动化 QA', 100, '实践经验和复盘', 38, '3 个 HOUSE BOT · 完整复盘', 22, gap_sub=30)
cx, cy = 540, 860
rc = 70; R = rc*1.45
row_y = 1230
xs = [220, 540, 860]
row = [(xs[0], 'blue', 'circle', 'QA 日报 bot', ('每天早上发',)),
       (xs[1], 'purple', 'circle', '协作群 bot', ('对字段和口径',)),
       (xs[2], 'orange', 'hex', '检查 bot', ('转达方案 · 挑错',))]
bus, by = team(c, (cx, cy), row, rc, 62, row_y, lfs=27, sfs=21, chief_label='QA 运维 bot', loop_dx=150, sw=2.4)
for x, t in zip(xs, ['报告 JSON', '对齐', '复核']):
    c.elabel(x + 14, (bus + row_y - 62)/2 + 8, t, 19, anchor='start', pad=5)
# inputs
c.chip(300, 600, ['PR 合并 · 约 12 秒开测'], fs=22, pad=13)
c.chip(780, 600, ['补测脚本 · 每 2 小时'], fs=22, pad=13)
c.edge([(300, 625), (300, 680), (cx, 680)], arrow=False)
c.edge([(780, 625), (780, 680), (cx, 680)], arrow=False)
c.dot(cx, 680, 5)
c.edge([(cx, 680), (cx, cy - R - 8)])
# side chips
x, y, w, h = c.chip(0, cy, ['14 项检查', '白盒·灰盒·黑盒', 'AI 审查·覆盖率门槛'], fs=21, pad=13, x0=60)
c.edge([(cx - R, cy), (x + w + 8, cy)], arrow=False)
c.dot(x + w, cy, 4)
c.chip(0, cy, ['私有仓工单', 'P0/P1 + 失败测试'], fs=21, pad=13, x0=760)
c.edge([(cx + R, cy), (752, cy)])
# group caption + outputs
c.front.append(c.text(cx, by + 44, '一个群 · 三个 HOUSE BOT 对口径', 19, '#9b9b9f', 'middle', 500, ls=.06))
oy = by + 130
c.edge([(220, by), (220, oy + 50)])
c.dot(220, oy, 4)
c.edge([(220, oy), (560, oy), (560, oy + 50)])
c.chip(220, oy + 100, ['团队群', '按级别 @ 作者'], fs=22, pad=14)
c.chip(560, oy + 100, ['私信 PR 作者', 'P0 / P1'], fs=22, pad=14)
# human
hy = oy + 300
c.chip(540, hy, ['人负责的三件事', '定什么算数 · 定谁说了算 · 按合并键'], fs=26, pad=24, first_color=TEAL_T)
c.front.append(c.text(70, 2080, 'HOUSE BOT · QA PIPELINE', 16, '#6f6f74', 'start', 500, ls=.14))
c.render('qa-architecture-styled.png', 'q3')
print(by, oy, hy)
