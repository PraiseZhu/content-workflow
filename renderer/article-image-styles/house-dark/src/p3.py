import sys; sys.path.insert(0, 'src')
from lib import *
W, H = 1080, 2160
c = Canvas(W, H)
c.background(hlines=(440, 1890), vlines=(60, 1020), crosses=((60,440,16),(1020,440,16),(60,1890,16),(1020,1890,16)),
             sphere=(1050, 2110, 240))
c.html.append('<div class="tag" style="left:80px;top:78px;font-size:20px;padding:7px 14px;letter-spacing:.06em">ARCHITECTURE · 3 HOUSE BOTS</div>')
c.html.append('<div class="t" style="left:78px;top:140px;font-size:92px;color:#fff">自动化 QA</div>')
c.html.append('<div class="t" style="left:78px;top:240px;font-size:92px;color:#2EC4B6">完整流程</div>')
c.html.append('<div class="m" style="left:82px;top:362px;font-size:24px;letter-spacing:.03em;color:#bdbdc2">合并后 12 秒开测 · 14 项检查 · 每天日报</div>')
L, S = 26, 19
# Row A
yA = 590
c.node(380, yA, 56, 'magenta', 'icon', 'merge', label='PR 合并', sub=['GitHub 事件 · 约 12 秒'], lpos='above', lfs=L, sfs=S, gap=16)
c.node(700, yA, 56, 'purple', 'icon', 'clock', label='补测脚本', sub=['每 2 小时 · 不调模型'], lpos='above', lfs=L, sfs=S, gap=16)
c.edge([(380, yA+68), (380, 730), (540, 730), (540, 756)])
c.edge([(700, yA+68), (700, 730), (540, 730)], arrow=False)
c.dot(540, 730)
# Row B: ops
yB = 860
c.node(540, yB, 90, 'teal')
lx = 612; ly = 990
for i, (t, fs, col, w) in enumerate([('QA 运维 bot', 28, '#fff', 600), ('14 项检查', 20, '#e0e0e4', 500),
                                      ('白盒 · 灰盒 · 黑盒', 19, '#9a9a9f', 400), ('+ AI 代码审查', 19, '#9a9a9f', 400), ('+ 覆盖率门槛', 19, '#9a9a9f', 400)]):
    c.front.append(c.text(lx, ly, t, fs, col, 'start', w)); ly += fs*1.45 + (6 if i == 0 else 0)
# issue
c.edge([(540-90-12, yB), (180, yB), (180, 1150-56-14)])
c.elabel(312, yB-22, 'P0 / P1 · 有失败测试佐证', 18)
c.node(180, 1150, 56, 'red', 'icon', 'issue', label='私有仓工单', sub=['派活'], lfs=L-2, sfs=S, gap=16)
# JSON
yC = 1150
c.node(540, yC, 56, 'orange', 'icon', 'json', label='报告 JSON', sub=['每个 PR 一份'], lpos='left', lfs=L-2, sfs=S, gap=22)
c.edge([(540, yB+90+12), (540, yC-56-14)])
# collab bot
c.node(880, yC, 64, 'purple', label='协作群 bot', sub=['对齐字段和口径'], lfs=L-2, sfs=S, gap=16)
c.edge([(540+90+14, yB), (880, yB), (880, yC-64-14)], dashed=True, both=True)
# daily
yD = 1450
c.node(540, yD, 84, 'blue', label='QA 日报 bot', sub=['每天早上发'], lpos='left', lfs=L+2, sfs=S, gap=24)
c.edge([(540, yC+56+12), (540, yD-84-14)])
c.edge([(540+84+14, yD), (760, yD), (760, yC), (880-64-14, yC)], dashed=True, both=True)
# checker
c.node(880, yD+20, 60, 'orange', shape='hex', label='检查 bot', sub=['转达方案 · 挑错'], lfs=L-2, sfs=S, gap=16)
c.edge([(880, yD+20-60-12), (880, 1300)], dashed=True, arrow=False)
c.dot(880, 1300)
# outputs
yE = 1735
c.edge([(540, yD+84+12), (540, 1620)], arrow=False)
c.dot(540, 1620)
c.edge([(540, 1620), (330, 1620), (330, yE-60-14)])
c.edge([(540, 1620), (750, 1620), (750, yE-60-14)])
c.node(330, yE, 60, 'magenta', 'icon', 'chat', label='团队群', sub=['按级别 @ 作者'], lfs=L-2, sfs=S, gap=16)
c.node(750, yE, 60, 'red', 'icon', 'mail', label='私信 PR 作者', sub=['P0 / P1'], lfs=L-2, sfs=S, gap=16)
# footer: human
c.box(80, 1935, 700, 150, fill='#0b0b0c', op=0.55)
c.front.append(f'<circle cx="150" cy="2010" r="40" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="2"/>')
c.front.append(c.icon('human', 150, 2010, 70))
c.front.append(c.text(220, 1990, '人只留三件事', 30, '#2EC4B6', 'start', 700))
c.front.append(c.text(220, 2040, '定什么算数 · 定谁说了算 · 按合并键', 22, '#e9e9ec', 'start', 500))
c.render('qa-architecture-styled.png', 'p3')
