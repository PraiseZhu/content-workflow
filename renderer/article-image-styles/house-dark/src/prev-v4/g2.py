import sys; sys.path.insert(0, 'src')
import lib3
from lib3 import *
EN = len(sys.argv) > 1 and sys.argv[1] == 'en'
lib3.SUB = SANS
T = dict(
 zh=dict(lab='触发与兜底 · 每次开跑都走同一条流水线',
   t1='PR 合并事件', t1s='GitHub 事件即时触发<br>实测合并后 12 秒开跑', t2='每 2 小时对账', t2s='纯脚本，不调模型<br>没缺的话几秒就退出',
   p=[('环境自检', '缺依赖先自动补装'), ('拿锁排队', '同一时间只跑一个<br>最多等 4 小时'), ('分诊', '29 个维度判适用<br>决定可选检查跑不跑'), ('白盒 · 灰盒 · 黑盒', '21 项检查，单测分片<br>没改动的步骤复用结果'),
      ('失败三次确认', '重跑 → 合并前版本<br>→ 最新主干'), ('AI 补测试', '只补没覆盖的维度<br>抓住植入错误才保留'), ('AI 代码审查', '同一输入复用结论<br>重审只做对比不覆盖'), ('报告 JSON', '每个 PR 一份<br>交给日报 bot')],
   gap='对账：昨天和今天的合并 vs 已有报告，缺哪个补哪个', key='兜底：', rest='事件负责快，每 2 小时对账负责不漏'),
 en=dict(lab='TRIGGERS & BACKSTOP · EVERY RUN, SAME PIPELINE',
   t1='PR merged', t1s='GitHub event<br>12 s to first test', t2='Every 2 hours', t2s='plain script<br>no model calls',
   p=[('Self-check', 'fixes missing deps'), ('Lock', 'one run at a time<br>waits up to 4 h'), ('Triage', '29 dimensions<br>picks extra checks'), ('Checks', '21 across 3 boxes<br>unchanged steps reused'),
      ('Confirm', 'rerun → pre-merge<br>→ latest main'), ('AI tests', 'for uncovered areas<br>kept if it catches<br>a planted bug'), ('AI review', 'cached per input<br>re-runs only compare'), ('JSON report', 'one per PR<br>to the daily bot')],
   key='BACKSTOP: ', rest='the event is fast; the 2-hour reconcile makes sure nothing slips'),
)['en' if EN else 'zh']
W, H = 1600, 755
f = Fig(W, H)
TF, SF = (26, 20) if EN else (27, 22)
f.text(60, 48, T['lab'], 22, '#6f6f6f', 'start', 500, MONO, ls=.12)
# triggers
f.box(165, 190, 270, 128, T['t1'], T['t1s'], tfs=TF, sfs=SF)
f.box(165, 400, 270, 128, T['t2'], T['t2s'], tfs=TF, sfs=SF)
f.arrow([(300, 190), (330, 190), (330, 295), (362, 295)])
f.arrow([(300, 400), (330, 400), (330, 295)], head=False)
xs = [560, 868, 1176, 1460]
xs = [497, 798, 1099, 1415]
ws = [250, 250, 250, 290]
for i in range(4):
    t, sub = T['p'][i]
    f.box(xs[i], 295, ws[i], 150, t, sub, tfs=TF, sfs=SF)
    if i < 3: f.arrow([(xs[i] + ws[i]/2, 295), (xs[i+1] - ws[i+1]/2 - 6, 295)])
f.ball(398, 168, 24, 'teal')
f.text(434, 168, 'QA 运维 bot' if not EN else 'QA ops bot', 22, '#cfcfcf', 'start', 600, SANS)
# wrap down to row 2
y2 = 560
f.arrow([(1415, 370), (1415, 428), (497, 428), (497, y2 - 81)])
for i in range(4):
    t, sub = T['p'][4 + i]
    f.box(xs[i], y2, ws[i], 150, t, sub, tfs=TF, sfs=SF, kind='orange' if i == 3 else 'dark')
    if i < 3: f.arrow([(xs[i] + ws[i]/2, y2), (xs[i+1] - ws[i+1]/2 - 6, y2)])
f.text(185, 500, T['gap'] if False else '', 20, GRAY)
f.summary(695, T['key'], T['rest'], 23)
f.render(f'inline{"-en" if EN else ""}/fig2-trigger{"-en" if EN else ""}.png', 'g2' + ('en' if EN else ''))
