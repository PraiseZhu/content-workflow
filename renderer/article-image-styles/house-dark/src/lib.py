import math, subprocess, os, unicodedata

C = dict(teal='#2EC4B6', magenta='#E8318A', orange='#F2711C', blue='#3B7BF6',
         purple='#8B5CF6', red='#EF4444')
MONO = "'JetBrains Mono','Noto Sans CJK SC',monospace"
DISP = "'Archivo Black','Noto Sans CJK SC',sans-serif"
BG = '#0b0b0c'
EXTRA_CSS = ''

def tw(s, fs, mono=True):
    """rough text width estimate"""
    w = 0
    for ch in s:
        if unicodedata.east_asian_width(ch) in 'WF':
            w += fs * 1.0
        elif ch == ' ':
            w += fs * 0.6
        else:
            w += fs * (0.6 if mono else 0.62)
    return w

class Canvas:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.back = []   # bg decorations
        self.mid = []    # edges
        self.front = []  # nodes / labels
        self.html = []   # html overlay

    # ---------- background ----------
    def background(self, hlines=(), vlines=(), crosses=(), grid=40, sphere=None, rings=True):
        W, H = self.W, self.H
        b = self.back
        b.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
        b.append(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')
        b.append(f'<rect width="{W}" height="{H}" fill="url(#grid5)"/>')
        for y in hlines:
            b.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#fff" stroke-opacity=".09" stroke-width="1"/>')
        for x in vlines:
            b.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#fff" stroke-opacity=".09" stroke-width="1"/>')
        for (x, y, s) in crosses:
            b.append(f'<g stroke="#fff" stroke-opacity=".28" stroke-width="1.2" fill="none">'
                     f'<circle cx="{x}" cy="{y}" r="{s*0.45}"/>'
                     f'<line x1="{x-s}" y1="{y}" x2="{x+s}" y2="{y}"/><line x1="{x}" y1="{y-s}" x2="{x}" y2="{y+s}"/></g>')
        if sphere:
            cx, cy, r = sphere
            if rings:
                b.append(f'<circle cx="{cx}" cy="{cy}" r="{r*1.18}" fill="none" stroke="#fff" stroke-opacity=".10" stroke-width="1.2" stroke-dasharray="3 7"/>')
                b.append(f'<circle cx="{cx}" cy="{cy}" r="{r*1.42}" fill="none" stroke="#fff" stroke-opacity=".06" stroke-width="1"/>')
            b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#sph)"/>')
            ew, eh = r*0.15, r*0.42
            for dx in (-0.36, -0.02):
                ex, ey = cx + dx*r, cy - 0.12*r
                b.append(f'<rect x="{ex-ew/2}" y="{ey-eh/2}" width="{ew}" height="{eh}" rx="{ew/2}" fill="#121213" transform="rotate(18 {ex} {ey})"/>')

    # ---------- nodes ----------
    def node(self, x, y, r, color, kind='bot', icon=None, shape='circle',
             label=None, sub=(), lpos='below', lfs=None, sfs=None, lcolor='#fff', gap=None):
        col = C.get(color, color)
        f = self.front
        f.append(f'<g filter="url(#glow)">')
        if shape == 'hex':
            pts = ' '.join(f'{x + r*0.93*math.cos(math.radians(a))},{y + r*0.93*math.sin(math.radians(a))}' for a in range(-90, 270, 60))
            f.append(f'<polygon points="{pts}" fill="{col}" stroke="{col}" stroke-width="{r*0.16}" stroke-linejoin="round"/>')
            pts2 = ' '.join(f'{x + r*0.80*math.cos(math.radians(a))},{y + r*0.80*math.sin(math.radians(a))}' for a in range(-90, 270, 60))
            f.append(f'<polygon points="{pts2}" fill="none" stroke="#000" stroke-opacity=".28" stroke-width="{r*0.05}" stroke-linejoin="round"/>')
        else:
            f.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/>')
            f.append(f'<circle cx="{x}" cy="{y}" r="{r*0.84}" fill="none" stroke="#000" stroke-opacity=".28" stroke-width="{r*0.05}"/>')
        f.append(f'<circle cx="{x}" cy="{y}" r="{r*0.8}" fill="url(#hl)"/>')
        f.append('</g>')
        if kind == 'bot':
            ew, eh = r*0.17, r*0.52
            for dx in (-0.17, 0.17):
                ex = x + dx*r
                f.append(f'<rect x="{ex-ew/2}" y="{y-eh/2}" width="{ew}" height="{eh}" rx="{ew/2}" fill="#fff" transform="rotate(20 {ex} {y})"/>')
        else:
            f.append(self.icon(icon, x, y, r))
        # labels
        if label:
            lfs = lfs or max(16, r*0.36)
            sfs = sfs or lfs*0.78
            gap = gap if gap is not None else r*0.32
            lines = [(label, lfs, lcolor, 600)] + [(s, sfs, '#9a9a9f', 400) for s in sub]
            if lpos == 'below':
                ty = y + r + gap + lfs*0.85
                for (t, fs, c, w) in lines:
                    f.append(self.text(x, ty, t, fs, c, 'middle', w))
                    ty += fs*1.35
                self._lb = ty - lines[-1][1]*1.35 + lines[-1][1]*0.4
            elif lpos == 'above':
                total = sum(l[1]*1.35 for l in lines)
                ty = y - r - gap - total + lines[0][1]*0.95
                for (t, fs, c, w) in lines:
                    f.append(self.text(x, ty, t, fs, c, 'middle', w))
                    ty += fs*1.35
            else:
                total = sum(l[1]*1.35 for l in lines)
                ty = y - total/2 + lines[0][1]*0.95
                ax = x + r + gap if lpos == 'right' else x - r - gap
                anc = 'start' if lpos == 'right' else 'end'
                for (t, fs, c, w) in lines:
                    f.append(self.text(ax, ty, t, fs, c, anc, w))
                    ty += fs*1.35
        return (x, y, r)

    def icon(self, name, x, y, r):
        s = r
        sw = r*0.09
        g = f'<g fill="none" stroke="#fff" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
        if name == 'merge':
            a, b, c = (x-0.22*s, y-0.32*s), (x-0.22*s, y+0.32*s), (x+0.26*s, y+0.05*s)
            cr = 0.1*s
            g += (f'<line x1="{a[0]}" y1="{a[1]+cr}" x2="{b[0]}" y2="{b[1]-cr}"/>'
                  f'<path d="M{a[0]} {a[1]+cr} C {a[0]} {y+0.05*s}, {c[0]-0.2*s} {c[1]}, {c[0]-cr} {c[1]}"/>')
            for p in (a, b, c):
                g += f'<circle cx="{p[0]}" cy="{p[1]}" r="{cr}"/>'
        elif name == 'clock':
            g += (f'<circle cx="{x}" cy="{y}" r="{0.36*s}"/>'
                  f'<path d="M{x} {y-0.22*s} V{y} L{x+0.15*s} {y+0.1*s}"/>')
        elif name == 'json':
            g += '</g>' + self.text(x, y+0.17*s, '{ }', 0.5*s, '#fff', 'middle', 800) + '<g>'
        elif name == 'chat':
            g += (f'<path d="M{x-0.36*s} {y-0.26*s} h{0.72*s} v{0.44*s} h{-0.44*s} l{-0.16*s} {0.16*s} v{-0.16*s} h{-0.12*s} z"/>')
            for dx in (-0.16, 0, 0.16):
                g += f'<circle cx="{x+dx*s}" cy="{y-0.04*s}" r="{0.03*s}" fill="#fff"/>'
        elif name == 'mail':
            g += (f'<rect x="{x-0.34*s}" y="{y-0.23*s}" width="{0.68*s}" height="{0.46*s}" rx="{0.05*s}"/>'
                  f'<path d="M{x-0.34*s} {y-0.2*s} L{x} {y+0.06*s} L{x+0.34*s} {y-0.2*s}"/>')
        elif name == 'issue':
            g += (f'<circle cx="{x}" cy="{y}" r="{0.34*s}"/>'
                  f'<circle cx="{x}" cy="{y}" r="{0.07*s}" fill="#fff"/>')
        elif name == 'human':
            g += (f'<circle cx="{x}" cy="{y-0.14*s}" r="{0.14*s}"/>'
                  f'<path d="M{x-0.3*s} {y+0.32*s} C{x-0.3*s} {y+0.05*s}, {x+0.3*s} {y+0.05*s}, {x+0.3*s} {y+0.32*s}"/>')
        g += '</g>'
        return g

    def text(self, x, y, t, fs, color='#fff', anchor='start', weight=500, font=MONO, ls=0.02, opacity=1):
        t = t.replace('&', '&amp;').replace('<', '&lt;')
        return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{fs}" font-weight="{weight}" fill="{color}" '
                f'fill-opacity="{opacity}" text-anchor="{anchor}" letter-spacing="{ls}em">{t}</text>')

    # ---------- edges ----------
    def edge(self, pts, dashed=False, arrow=True, both=False, dot_start=False, color='#fff', width=2.2, radius=16, op=0.85):
        d = f'M{pts[0][0]} {pts[0][1]}'
        for i in range(1, len(pts)):
            if i < len(pts)-1:
                p0, p1, p2 = pts[i-1], pts[i], pts[i+1]
                v1 = (p1[0]-p0[0], p1[1]-p0[1]); l1 = math.hypot(*v1)
                v2 = (p2[0]-p1[0], p2[1]-p1[1]); l2 = math.hypot(*v2)
                rr = min(radius, l1/2, l2/2)
                a = (p1[0]-v1[0]/l1*rr, p1[1]-v1[1]/l1*rr)
                b = (p1[0]+v2[0]/l2*rr, p1[1]+v2[1]/l2*rr)
                d += f' L{a[0]} {a[1]} Q{p1[0]} {p1[1]} {b[0]} {b[1]}'
            else:
                d += f' L{pts[i][0]} {pts[i][1]}'
        dash = ' stroke-dasharray="7 7"' if dashed else ''
        me = ' marker-end="url(#arr)"' if arrow else ''
        ms = ' marker-start="url(#arrs)"' if both else ''
        self.mid.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="{width}"{dash}{me}{ms} stroke-linejoin="round"/>')
        if dot_start:
            self.dot(*pts[0])

    def dot(self, x, y, r=5):
        self.mid.append(f'<circle cx="{x}" cy="{y}" r="{r+2.5}" fill="{BG}"/><circle cx="{x}" cy="{y}" r="{r}" fill="#fff" fill-opacity=".9"/>')

    def elabel(self, x, y, t, fs=18, anchor='middle', color='#cfcfd4', pad=8):
        w = tw(t, fs)
        x0 = x - w/2 if anchor == 'middle' else (x if anchor == 'start' else x - w)
        self.front.append(f'<rect x="{x0-pad}" y="{y-fs*0.95}" width="{w+2*pad}" height="{fs*1.4}" fill="{BG}" fill-opacity=".92"/>')
        self.front.append(self.text(x, y, t, fs, color, anchor, 500))

    def box(self, x, y, w, h, dashed=False, op=0.45, fill=None, sw=1.5):
        dash = ' stroke-dasharray="6 6"' if dashed else ''
        fl = fill or 'none'
        self.front.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fl}" stroke="#fff" stroke-opacity="{op}" stroke-width="{sw}"{dash}/>')

    # ---------- render ----------
    def svg(self):
        W, H = self.W, self.H
        defs = f'''<defs>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#fff" stroke-opacity=".035" stroke-width="1"/></pattern>
<pattern id="grid5" width="200" height="200" patternUnits="userSpaceOnUse"><path d="M200 0H0V200" fill="none" stroke="#fff" stroke-opacity=".045" stroke-width="1"/></pattern>
<radialGradient id="sph" cx="38%" cy="32%" r="75%"><stop offset="0" stop-color="#a3a3a6"/><stop offset=".35" stop-color="#6b6b6e"/><stop offset=".72" stop-color="#2c2c2e"/><stop offset="1" stop-color="#141415"/></radialGradient>
<radialGradient id="hl" cx="35%" cy="28%" r="70%"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/></radialGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur in="SourceGraphic" stdDeviation="14" result="b"/><feColorMatrix in="b" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 .35 0"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="noise"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter>
<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="#fff"/></marker>
<marker id="arrs" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M10 0L0 5L10 10z" fill="#fff"/></marker>
</defs>'''
        noise = '' if getattr(self, 'no_noise', False) else f'<rect width="{W}" height="{H}" filter="url(#noise)" opacity=".05"/>'
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0">'
                + defs + ''.join(self.back) + noise + ''.join(self.mid) + ''.join(self.front) + '</svg>')

    def render(self, out, name):
        html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;padding:0;background:{BG};}}
body{{width:{self.W}px;height:{self.H}px;position:relative;overflow:hidden;font-synthesis:none;-webkit-font-smoothing:antialiased}}
.t{{position:absolute;font-family:{DISP};font-weight:900;line-height:1.02;letter-spacing:-0.01em;white-space:nowrap}}
.m{{position:absolute;font-family:{MONO};font-weight:500;white-space:nowrap;color:#e9e9ec}}
.tag{{position:absolute;font-family:{MONO};font-weight:500;white-space:nowrap;color:#e9e9ec;border:1.5px solid rgba(255,255,255,.55);}}
{EXTRA_CSS}</style></head><body>{self.svg()}{''.join(self.html)}</body></html>'''
        out = os.path.abspath(out); src = os.path.join(os.path.dirname(out), 'src', name + '.html')
        open(src, 'w').write(html)
        subprocess.run(['chromium', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                        f'--window-size={self.W},{self.H}', '--force-device-scale-factor=1',
                        '--virtual-time-budget=3000', f'--screenshot={out}', 'file://' + src],
                       check=True, capture_output=True)
        return out
