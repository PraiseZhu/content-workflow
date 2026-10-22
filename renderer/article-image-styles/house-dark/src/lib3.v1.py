import math, os, subprocess
from lib2 import C, EYE
OR = '#FF6A2B'; GR = '#2ECC71'; GRAY = '#8C8C8C'; DIM = '#5f5f5f'
SANS = "'Inter','Noto Sans CJK SC',sans-serif"
MONO = "'JetBrains Mono','Noto Sans CJK SC',monospace"

class Fig:
    def __init__(s, W, H):
        s.W, s.H = W, H; s.svg = []; s.html = []
    # ---- primitives ----
    def ball(s, x, y, r, color, shape='circle'):
        col = C.get(color, color)
        if shape == 'hex':
            R = r*1.1
            pts = ' '.join(f'{x + R*math.cos(math.radians(a)):.1f},{y + R*math.sin(math.radians(a)):.1f}' for a in range(-90, 270, 60))
            s.svg.append(f'<polygon points="{pts}" fill="{col}" stroke="{col}" stroke-width="{r*0.22}" stroke-linejoin="round" transform="translate({x} {y}) scale(.93) translate({-x} {-y})"/>')
        else:
            s.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/>')
        L, w, sp = 0.60*r, 0.22*r, 0.46*r
        for dx in (-sp/2, sp/2):
            ex = x + dx
            s.svg.append(f'<rect x="{ex-w/2:.2f}" y="{y-L/2:.2f}" width="{w:.2f}" height="{L:.2f}" rx="{w/2:.2f}" fill="{EYE}" transform="rotate(22 {ex:.2f} {y})"/>')

    def arrow(s, pts, color=OR, dashed=False, width=4, head=True, radius=18):
        d = f'M{pts[0][0]} {pts[0][1]}'
        for i in range(1, len(pts)):
            if i < len(pts)-1:
                p0, p1, p2 = pts[i-1], pts[i], pts[i+1]
                v1 = (p1[0]-p0[0], p1[1]-p0[1]); l1 = math.hypot(*v1)
                v2 = (p2[0]-p1[0], p2[1]-p1[1]); l2 = math.hypot(*v2)
                rr = min(radius, l1/2, l2/2)
                a = (p1[0]-v1[0]/l1*rr, p1[1]-v1[1]/l1*rr); b = (p1[0]+v2[0]/l2*rr, p1[1]+v2[1]/l2*rr)
                d += f' L{a[0]:.1f} {a[1]:.1f} Q{p1[0]} {p1[1]} {b[0]:.1f} {b[1]:.1f}'
            else:
                d += f' L{pts[i][0]} {pts[i][1]}'
        mid = color.replace('#', '')
        dash = ' stroke-dasharray="12 10"' if dashed else ''
        mk = f' marker-end="url(#h{mid})"' if head else ''
        s.svg.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash}{mk} stroke-linecap="round" stroke-linejoin="round"/>')
        s._cols = getattr(s, '_cols', set()) | {color}

    def line(s, x1, y1, x2, y2, color=DIM, dashed=True, width=3):
        dash = ' stroke-dasharray="12 12"' if dashed else ''
        s.svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{dash}/>')

    def box(s, cx, cy, w, h, title=None, sub=None, kind='dark', tfs=44, sfs=34, radius=18, tcolor=None, align='center'):
        if kind == 'dark':
            bg, bd, tc = '#262626', '#262626', '#F2F2F2'
        elif kind == 'outline':
            bg, bd, tc = '#1b1b1b', '#3a3a3a', '#bdbdbd'
        elif kind == 'orange':
            bg, bd, tc = 'rgba(255,106,43,.10)', 'rgba(255,106,43,.85)', '#F2F2F2'
        elif kind == 'green':
            bg, bd, tc = 'rgba(46,204,113,.12)', 'rgba(46,204,113,.85)', GR
        tc = tcolor or tc
        inner = ''
        if title:
            inner += f'<div style="font-family:{SANS};font-weight:700;font-size:{tfs}px;color:{tc};line-height:1.25">{title}</div>'
        if sub:
            inner += f'<div style="font-family:{MONO};font-weight:400;font-size:{sfs}px;color:#9a9a9a;line-height:1.35;margin-top:{6 if title else 0}px">{sub}</div>'
        s.html.append(f'<div style="position:absolute;left:{cx-w/2}px;top:{cy-h/2}px;width:{w}px;height:{h}px;box-sizing:border-box;background:{bg};'
                      f'border:2px solid {bd};border-radius:{radius}px;display:flex;flex-direction:column;justify-content:center;align-items:{"center" if align=="center" else "flex-start"};'
                      f'text-align:{align};padding:0 26px">{inner}</div>')
        return (cx-w/2, cy-h/2, w, h)

    def card(s, x, y, w, h, kind, title, items, foot=None, tfs=46, ifs=38, ffs=32):
        if kind == 'green':
            bg, bd, tc, ic, fc = '#0F1F18', 'rgba(46,204,113,.45)', GR, '#BFE9CF', 'rgba(46,204,113,.75)'
        else:
            bg, bd, tc, ic, fc = '#1A0F08', 'rgba(255,106,43,.45)', OR, '#F3CDB6', 'rgba(255,106,43,.8)'
        its = ''.join(f'<div style="font-family:{MONO};font-size:{ifs}px;color:{ic};line-height:1.25;margin:10px 0">{t}</div>' for t in items)
        ft = f'<div style="font-family:{MONO};font-size:{ffs}px;color:{fc};margin-top:18px">{foot}</div>' if foot else ''
        s.html.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;box-sizing:border-box;background:{bg};border:2px solid {bd};border-radius:22px;'
                      f'display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:20px 24px">'
                      f'<div style="font-family:{SANS};font-weight:800;font-size:{tfs}px;color:{tc};margin-bottom:16px">{title}</div>{its}{ft}</div>')

    def text(s, x, y, t, fs=34, color=GRAY, anchor='middle', weight=400, font=None, ls=0.0, rot=0):
        font = font or MONO
        tx = {'middle': '-50%', 'start': '0', 'end': '-100%'}[anchor]
        rt = f' rotate({rot}deg)' if rot else ''
        s.html.append(f'<div style="position:absolute;left:{x}px;top:{y}px;transform:translate({tx},-50%){rt};font-family:{font};font-size:{fs}px;font-weight:{weight};'
                      f'color:{color};white-space:nowrap;letter-spacing:{ls}em;line-height:1.2">{t}</div>')

    def summary(s, y, key, rest, fs=38):
        s.html.append(f'<div style="position:absolute;left:0;width:{s.W}px;top:{y}px;transform:translateY(-50%);text-align:center;font-family:{MONO};font-size:{fs}px;letter-spacing:.06em;white-space:nowrap">'
                      f'<span style="color:{OR};font-weight:800">{key}</span><span style="color:{GRAY}">{rest}</span></div>')

    def render(s, out, name):
        cols = getattr(s, '_cols', set()) | {OR, GR, '#8C8C8C'}
        markers = ''.join(f'<marker id="h{c.replace("#","")}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.2" markerHeight="4.2" orient="auto"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>' for c in cols)
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{s.W}" height="{s.H}" style="position:absolute;left:0;top:0"><defs>{markers}</defs>{"".join(s.svg)}</svg>'
        html = f'''<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:#141414}}body{{width:{s.W}px;height:{s.H}px;position:relative;overflow:hidden;-webkit-font-smoothing:antialiased}}</style></head>
<body>{svg}{"".join(s.html)}</body></html>'''
        out = os.path.abspath(out)
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + '.html')
        open(src, 'w').write(html)
        subprocess.run(['chromium', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', f'--window-size={s.W},{s.H}',
                        '--force-device-scale-factor=1', '--virtual-time-budget=3000', f'--screenshot={out}', 'file://' + src], check=True, capture_output=True)
