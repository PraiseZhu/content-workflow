import sys; sys.path.insert(0, 'src')
import lib3
from lib3 import *
EN = len(sys.argv) > 1 and sys.argv[1] == 'en'
lib3.SUB = SANS
T = dict(
 zh=dict(lab='整体架构 · 现在在跑的样子', me='我', me_s='定规则 · 拍板 · 收异常', grp='协作群', grp_s='两个 bot 对字段、对口径',
   t1='PR 合并事件', t1s='合并即触发', t2='每 2 小时对账', t2s='纯脚本 · 补漏测', ops='QA 运维 bot', ops_s='测试流水线', rep='报告 JSON', rep_s='每个 PR 一份',
   day='QA 日报 bot', day_s='每天 9 点', o1='团队群日报', o1s='P0、P1 和有建议的 P2<br>@ PR 作者', o2='私信作者', o2s='别人合并的 P0 / P1<br>每个问题只发一次',
   iss='派活工单', iss_s='私有仓 · 测试佐证的 P0/P1<br>以及 QA 系统故障', key='交接：', rest='两个 bot 只靠报告 JSON 交接，派活、@ 人、私信各有门槛'),
 en=dict(lab='ARCHITECTURE · AS IT RUNS TODAY', me='Me', me_s='rules · tie-breaks · alerts', grp='Shared chat', grp_s='bots agree on fields & wording',
   t1='PR merged', t1s='event fires on merge', t2='Every 2 hours', t2s='script fills gaps', ops='QA ops bot', ops_s='test pipeline', rep='JSON report', rep_s='one per PR',
   day='QA daily bot', day_s='9 a.m. daily', o1='Team digest', o1s='@ authors of P0, P1<br>and actionable P2', o2='DM the author', o2s='P0 / P1 on others\' PRs<br>once per finding',
   iss='Work tickets', iss_s='private repo · test-backed<br>P0/P1 + QA system failures', key='HANDOFF: ', rest='the bots share only the JSON report; tickets, @s and DMs each have a bar'),
)['en' if EN else 'zh']
W, H = 1600, 800
f = Fig(W, H)
TF, SF = 28, 25
f.text(60, 48, T['lab'], 22, '#6f6f6f', 'start', 500, MONO, ls=.12)
f.box(800, 104, 380, 100, T['me'], T['me_s'], kind='green', tfs=TF, sfs=SF-1)
f.arrow([(800, 156), (800, 192)], color=GR, width=3.5)
f.ball(800, 232, 34, 'purple')
f.text(850, 214, T['grp'], 26, '#F2F2F2', 'start', 600, SANS)
f.text(850, 246, T['grp_s'], 22, GRAY, 'start')
f.line(800, 266, 800, 282, '#8C8C8C', False, 2.5)
f.arrow([(800, 282), (480, 282), (480, 314)], color='#8C8C8C', dashed=True, width=2.5)
f.arrow([(800, 282), (1120, 282), (1120, 314)], color='#8C8C8C', dashed=True, width=2.5)
y = 390
f.box(160, y - 84, 260, 110, T['t1'], T['t1s'], tfs=TF-2, sfs=SF-2)
f.box(160, y + 84, 260, 110, T['t2'], T['t2s'], tfs=TF-2, sfs=SF-2)
f.arrow([(290, y - 84), (340, y - 84), (340, y), (404, y)])
f.arrow([(290, y + 84), (340, y + 84), (340, y)], head=False)
f.ball(480, y, 62, 'teal')
f.text(480, y + 96, T['ops'], TF, '#F2F2F2', 'middle', 600, SANS)
f.text(480, y + 134, T['ops_s'], SF, GRAY)
f.arrow([(552, y), (668, y)])
f.box(800, y, 256, 104, T['rep'], T['rep_s'], kind='orange', tfs=TF, sfs=SF-2)
f.arrow([(930, y), (1046, y)])
f.ball(1120, y, 62, 'blue')
f.text(1120, y + 96, T['day'], TF, '#F2F2F2', 'middle', 600, SANS)
f.text(1120, y + 134, T['day_s'], SF, GRAY)
f.arrow([(1192, y), (1230, y), (1230, y - 84), (1266, y - 84)])
f.arrow([(1230, y), (1230, y + 84), (1266, y + 84)])
f.box(1418, y - 84, 296, 124, T['o1'], T['o1s'], tfs=TF-2, sfs=SF-3)
f.box(1418, y + 84, 296, 124, T['o2'], T['o2s'], tfs=TF-2, sfs=SF-3)
f.arrow([(480, y + 160), (480, 596)])
f.box(480, 660, 360, 120, T['iss'], T['iss_s'], tfs=TF-2, sfs=SF-3)
f.summary(762, T['key'], T['rest'], 23)
f.render(f'inline{"-en" if EN else ""}/fig1-architecture{"-en" if EN else ""}.png', 'g1' + ('en' if EN else ''))
