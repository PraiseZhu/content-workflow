import sys; sys.path.insert(0, 'src')
import lib3
from lib3 import *
EN = len(sys.argv) > 1 and sys.argv[1] == 'en'
lib3.SUB = SANS
T = dict(
 zh=dict(lab='什么算数 · 发现 → 佐证 → 级别 → 动作', h=('发现从哪来', '测试佐证', '级别', '机器接着做什么'), rule='门槛由我定',
   yes='有', no='无',
   rows=[('检查失败', '重跑、合并前、最新主干都确认过', True, 'P0 / P1', '群里 @ 作者 · 私信作者（别人的 PR）<br>开派活工单（只在我自己的 PR 上）'),
         ('AI 代码审查', '看代码发现的', False, 'P1', '群里 @ 作者 · 私信注明「测试未复现」<br>不开派活工单'),
         ('AI 补的测试失败', '在当前代码上就失败', False, 'P2', '日报里写「可疑行为，还没人确认」<br>不 @、不私信'),
         ('不稳定测试', '首跑失败、重跑通过', False, 'P2', '和合并前版本对比后写进日报<br>不 @、不私信')],
   key='算数：', rest='只有测试打红才派活；审查能提醒，AI 补测和不稳定测试只算线索'),
 en=dict(lab='WHAT COUNTS · FINDING → EVIDENCE → SEVERITY → ACTION', h=('Where it came from', 'Test-backed', 'Level', 'What the bots do next'), rule='I set this bar',
   yes='yes', no='no',
   rows=[('Check failed', 'confirmed on rerun, pre-merge, main', True, 'P0 / P1', '@ author in team chat · DM (others\' PRs)<br>work ticket (my own PRs only)'),
         ('AI code review', 'found by reading the diff', False, 'P1', '@ author · DM marked "no failing test"<br>no work ticket'),
         ('AI-written test fails', 'fails on the merged code', False, 'P2', 'digest says "suspicious, unconfirmed"<br>no @, no DM'),
         ('Flaky test', 'failed, then passed on rerun', False, 'P2', 'compared with pre-merge, noted in digest<br>no @, no DM')],
   key='WHAT COUNTS: ', rest='only a red test opens a ticket; review can warn, AI tests and flakes are leads'),
)['en' if EN else 'zh']
W, H = 1600, 760
f = Fig(W, H)
TF, SF = (26, 21) if EN else (27, 23)
f.text(60, 48, T['lab'], 22, '#6f6f6f', 'start', 500, MONO, ls=.12)
cx = (250, 610, 770, 1215); wsrc, wact = 400, 650
hy = 128
for x, h in zip(cx, T['h']):
    f.text(x, hy, h, 22, '#7a7a7a', 'middle', 500)
f.text(cx[1], 94, T['rule'], 21, GR, 'middle', 600)
f.line(1220, 86, 1540, 86, GR, True, 2) if False else None
ys = [230, 370, 510, 650 - 0]
ys = [222, 352, 482, 612]
for (src, ssub, tb, lvl, act), y in zip(T['rows'], ys):
    f.box(cx[0], y, wsrc, 108, src, ssub, tfs=TF, sfs=SF - 1)
    f.arrow([(cx[0] + wsrc/2, y), (cx[1] - 62, y)], color='#8C8C8C', width=3)
    kind = 'green' if tb else 'outline'
    f.box(cx[1], y, 112, 56, T['yes'] if tb else T['no'], None, kind=kind, tfs=23, radius=28, tcolor=GR if tb else '#9a9a9a')
    f.text(cx[2], y, lvl, TF, OR if tb else '#e6e6e6', 'middle', 700, SANS)
    f.arrow([(cx[2] + 66, y), (cx[3] - wact/2 - 8, y)])
    f.box(cx[3], y, wact, 108, None, f'<span style="color:#e6e6e6">{act}</span>', kind='orange' if tb else 'dark', sfs=SF, align='center')
f.summary(718, T['key'], T['rest'], 23 if not EN else 22)
f.render(f'inline{"-en" if EN else ""}/fig3-evidence{"-en" if EN else ""}.png', 'g3' + ('en' if EN else ''))
