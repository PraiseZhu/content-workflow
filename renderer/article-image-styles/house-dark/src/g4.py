import sys; sys.path.insert(0, 'src')
import lib3
from lib3 import *
EN = len(sys.argv) > 1 and sys.argv[1] == 'en'
lib3.SUB = SANS
T = dict(
 zh=dict(lab='机器和人的边界', lt='机器做的', rt='留给我的三件事', stop='bot 停在这里',
   L=['合并事件触发 · 每 2 小时对账补测', '环境自检，缺依赖自动补装', '分诊 29 个维度 · 21 项检查', '失败三步确认 · AI 补测 · AI 审查', '写报告 JSON · 开派活工单（指纹去重）', '群日报 @ 作者 · 私信 P0 / P1'],
   R=[('定标准', '测试佐证门槛 · P0–P3 怎么分 · 额度'), ('定权限', '日报发哪个群由我确认<br>开工单的开关改配置开不了'), ('按合并键', '合入后才测，不拦合并 · 封版由人定')],
   foot='bot 只在异常时找我：发送失败、系统故障、新开工单', key='边界：', rest='动作全交给 bot，规则、权限和合并键留在人手里'),
 en=dict(lab='WHERE THE MACHINE STOPS', lt='The bots do', rt='Three things I kept', stop='bots stop here',
   L=['Trigger on merge · reconcile every 2 h', 'Self-check, install missing deps', 'Triage 29 dimensions · run 21 checks', 'Confirm failures · AI tests · AI review', 'Write the report · open deduped tickets', 'Team digest with @s · DM on P0 / P1'],
   R=[('Set the standards', 'the test-backed bar · P0–P3 · daily quota'), ('Set permissions', 'which chat gets the digest is my call<br>config alone can\'t turn on tickets'), ('Press merge', 'QA runs after merge · release cut is human')],
   foot='Bots only ping me when something breaks: failed sends, system faults, new tickets', key='BOUNDARY: ', rest='the bots take every action; rules, permissions and the merge button stay with me'),
)['en' if EN else 'zh']
W, H = 1600, 740
f = Fig(W, H)
f.text(60, 48, T['lab'], 22, '#6f6f6f', 'start', 500, MONO, ls=.12)
# left card
x0, y0, w, h = 60, 96, 640, 520
items = ''.join(f'<div style="display:flex;align-items:center;margin:26px 0"><span style="width:10px;height:10px;border-radius:5px;background:{OR};margin-right:18px;flex:none"></span>'
                f'<span style="font-family:{SANS};font-size:{24 if EN else 26}px;color:#ECD5C8">{t}</span></div>' for t in T['L'])
f.html.append(f'<div style="position:absolute;left:{x0}px;top:{y0}px;width:{w}px;height:{h}px;box-sizing:border-box;background:#1A110C;border:2px solid rgba(255,106,43,.5);border-radius:22px;padding:34px 40px">'
              f'<div style="font-family:{SANS};font-weight:600;font-size:28px;color:{OR};margin-bottom:14px">{T["lt"]}</div>{items}</div>')
# divider + bot
f.line(800, 96, 800, 300, '#5f5f5f', True, 3)
f.line(800, 428, 800, 616, '#5f5f5f', True, 3)
f.ball(800, 350, 40, 'teal')
f.text(800, 412, T['stop'], 22, GRAY, 'middle', 500)
f.arrow([(706, 350), (752, 350)], color=OR, width=3.5)
f.arrow([(848, 350), (894, 350)], color=GR, width=3.5, dashed=True)
# right card
x1 = 900
ritems = ''.join(f'<div style="margin:0 0 32px 0"><div style="display:flex;align-items:baseline"><span style="font-family:{MONO};font-weight:700;font-size:22px;color:{GR};margin-right:16px">0{i+1}</span>'
                 f'<span style="font-family:{SANS};font-weight:600;font-size:{27 if EN else 28}px;color:#F2F2F2">{t}</span></div>'
                 f'<div style="font-family:{SANS};font-size:{22 if EN else 24}px;color:#A9C9B6;margin:8px 0 0 50px;line-height:1.4">{s}</div></div>' for i, (t, s) in enumerate(T['R']))
f.html.append(f'<div style="position:absolute;left:{x1}px;top:{y0}px;width:{w}px;height:{h}px;box-sizing:border-box;background:#0F1D16;border:2px solid rgba(46,204,113,.5);border-radius:22px;padding:34px 40px">'
              f'<div style="font-family:{SANS};font-weight:600;font-size:28px;color:{GR};margin-bottom:26px">{T["rt"]}</div>{ritems}'
              f'<div style="position:absolute;left:40px;right:40px;bottom:28px;font-family:{SANS};font-size:{20 if EN else 22}px;color:#7d8f84;border-top:1px dashed rgba(46,204,113,.35);padding-top:16px">{T["foot"]}</div></div>')
f.summary(682, T['key'], T['rest'], 23 if not EN else 22)
f.render(f'inline{"-en" if EN else ""}/fig4-boundary{"-en" if EN else ""}.png', 'g4' + ('en' if EN else ''))
