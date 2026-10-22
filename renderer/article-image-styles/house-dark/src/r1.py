import sys; sys.path.insert(0, 'src')
from lib2 import *
import lib
from fonts import FACES
lib.EXTRA_CSS = FACES + (".t{font-family:'Archivo Black','MiSansW',sans-serif!important}"
    ".m,.tag{font-family:'JetBrains Mono','MiSansW',monospace!important}"
    "svg text{font-family:'JetBrains Mono','MiSansW',monospace!important}")
W, H = 2350, 1000
c = Canvas(W, H)
k = 1000/272
scx = 2350 - 93*k
off = lambda xr: scx + (xr - 587)*k
TEX = dict(fine=1.35, mid=0.45, scratch=0.22, mottle=0.65, broad=0.3, scale=1.0)
c.background(texture=TEX, hlines=(55*k, 225*k), vlines=(30*k, off(300)), crosses=((30*k, 55*k, 18), (30*k, 225*k, 18), (off(300), 55*k, 18), (off(300), 225*k, 18)),
             sphere=(scx, 129*k, 89*k))
c.back = [b.replace('filter="url(#grain)" opacity=".17"', 'filter="url(#grain)" opacity=".085"') for b in c.back]
x, y, fs = 160, 262, 142
fz = round(fs*0.87)
c.html.append(f'<div class="t" style="left:{x}px;top:{y}px;font-size:{fs}px;color:#F2F2F2">GROK BOT</div>')
y2 = y + fs*1.04 + (fs - fz)*0.55
c.html.append(f'<div class="t" style="left:{x}px;top:{y2:.0f}px;font-size:{fz}px;color:{TEAL_T};font-weight:700;letter-spacing:.01em">自动化 <span style="font-size:{fs}px">QA</span></div>')
ys = y + fs*1.04*2 + 40
c.html.append(f'<div class="m" style="left:{x+4}px;top:{ys:.0f}px;font-size:40px;font-weight:400;letter-spacing:.14em;color:#e6e6e6">实践经验和复盘</div>')
yt = ys + 40*1.95
c.html.append(f'<div class="tag" style="left:{x+4}px;top:{yt:.0f}px;font-size:27px;font-weight:500;padding:12px 26px;letter-spacing:.1em;border-color:rgba(255,255,255,.6)">3 个 GROK BOT · 完整复盘</div>')
xs = [off(x) for x in (330, 382, 433, 485, 537)]
row = [(xs[0], 'magenta', 'circle', '白盒', ()), (xs[1], 'orange', 'hex', '灰盒', ()), (xs[2], 'blue', 'circle', '黑盒', ()),
       (xs[3], 'purple', 'circle', 'AI 审查', ()), (xs[4], 'red', 'circle', '日报 bot', ())]
team(c, (xs[2], 92*k), row, 19*k, 15*k, 160*k, lfs=27, chief_label='QA 运维 bot', loop_dx=18*k, sw=2.6)
c.render('cover-2.35.png', 'r1')
