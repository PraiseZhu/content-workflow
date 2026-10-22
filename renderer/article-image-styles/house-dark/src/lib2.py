import math
from lib import Canvas as Base, MONO, DISP, BG, tw
import lib
C = dict(teal='#1DB9B5', magenta='#F82D87', orange='#F6761D', blue='#2D7CF5', purple='#834EF4', red='#EF4140')
lib.C.update(C)
lib.BG = '#141414'
TEAL_T = '#1AC5CC'
EYE = '#151618'

class Canvas(Base):
    def background(self, hlines=(), vlines=(), crosses=(), sphere=None, texture=None, **k):
        W, H = self.W, self.H
        b = self.back
        if texture:
            import os, sys
            sys.path.insert(0, os.path.dirname(__file__))
            from texture import make, save
            p = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'tex-{W}x{H}.png')
            save(make(W, H, **texture), p)
            b.append(f'<image href="file://{p}" x="0" y="0" width="{W}" height="{H}"/>')
            self.no_noise = True
        else:
            b.append(f'<rect width="{W}" height="{H}" fill="#141414"/>')
        b.append(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')
        for y in hlines:
            b.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#fff" stroke-opacity=".08"/>')
        for x in vlines:
            b.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#fff" stroke-opacity=".08"/>')
        for (x, y, s) in crosses:
            b.append(f'<g stroke="#fff" stroke-opacity=".30" stroke-width="1.2" fill="none"><circle cx="{x}" cy="{y}" r="{s*0.42}"/>'
                     f'<line x1="{x-s}" y1="{y}" x2="{x+s}" y2="{y}"/><line x1="{x}" y1="{y-s}" x2="{x}" y2="{y+s}"/></g>')
        if sphere:
            self.sphere(*sphere)

    def sphere(self, cx, cy, r):
        b = self.back
        for k, op, da in ((1.17, .16, '4 6'), (1.38, .10, '3 8')):
            b.append(f'<circle cx="{cx}" cy="{cy}" r="{r*k}" fill="none" stroke="#fff" stroke-opacity="{op}" stroke-width="1.3" stroke-dasharray="{da}"/>')
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#sph2)"/>')
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" filter="url(#grain)" opacity=".17"/>')
        for (dx, dy, L, w, ang) in ((0.04, -0.16, 0.75, 0.27, -39), (0.68, -0.40, 0.68, 0.26, -36)):
            ex, ey = cx + dx*r, cy + dy*r
            b.append(f'<rect x="{ex - w*r/2}" y="{ey - L*r/2}" width="{w*r}" height="{L*r}" rx="{w*r/2}" fill="#121212" transform="rotate({ang} {ex} {ey})"/>')

    def bot(self, x, y, r, color, shape='circle', ring=False, label=None, sub=(), lfs=None, sfs=None, gap=None, lpos='below'):
        col = C.get(color, color)
        f = self.front
        if shape == 'hex':
            R = r*1.1
            pts = ' '.join(f'{x + R*math.cos(math.radians(a)):.1f},{y + R*math.sin(math.radians(a)):.1f}' for a in range(-90, 270, 60))
            f.append(f'<polygon points="{pts}" fill="{col}" stroke="{col}" stroke-width="{r*0.22}" stroke-linejoin="round" transform="translate({x} {y}) scale(.93) translate({-x} {-y})"/>')
        else:
            f.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/>')
        L, w, s = 0.60*r, 0.22*r, 0.46*r
        for dx in (-s/2, s/2):
            ex = x + dx
            f.append(f'<rect x="{ex-w/2:.2f}" y="{y-L/2:.2f}" width="{w:.2f}" height="{L:.2f}" rx="{w/2:.2f}" fill="{EYE}" transform="rotate(22 {ex:.2f} {y})"/>')
        lab_top = y + r
        if ring:
            R = r*1.45
            lw = tw(label or '', lfs or max(14, r*0.42)) / 2 + 10
            ga = 18
            a0, a1 = 90+ga, 90-ga  # gap around bottom
            p0 = (x + R*math.cos(math.radians(a0)), y + R*math.sin(math.radians(a0)))
            p1 = (x + R*math.cos(math.radians(a1)), y + R*math.sin(math.radians(a1)))
            f.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f} A{R} {R} 0 1 1 {p1[0]:.1f} {p1[1]:.1f}" fill="none" stroke="#d8d8d8" stroke-opacity=".75" stroke-width="{max(1.5, r*0.035):.2f}"/>')
            for a in (180, 270, 0):
                px, py = x + R*math.cos(math.radians(a)), y + R*math.sin(math.radians(a))
                f.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{max(2.5, r*0.06):.1f}" fill="#d8d8d8"/>')
            q0 = (x + R*math.cos(math.radians(155)), y + R*math.sin(math.radians(155)))
            q1 = (x + R*math.cos(math.radians(25)), y + R*math.sin(math.radians(25)))
            self._ring = (q0, q1, R)
            lab_top = y + R - (lfs or r*0.4)*0.05
        if label:
            lfs = lfs or max(14, r*0.42)
            sfs = sfs or lfs*0.8
            gap = gap if gap is not None else r*0.32
            lines = [(label, lfs, '#f2f2f2', 600)] + [(t, sfs, '#9b9b9f', 400) for t in sub]
            if lpos == 'below':
                ty = lab_top + gap + lfs*0.85
                for (t, fs, c_, wt) in lines:
                    f.append(self.text(x, ty, t, fs, c_, 'middle', wt)); ty += fs*1.35
                self.lb = ty - lines[-1][1]*1.35 + lines[-1][1]*0.35
            else:
                total = sum(l[1]*1.35 for l in lines)
                ty = y - total/2 + lines[0][1]*0.95
                ax = x + r + gap if lpos == 'right' else x - r - gap
                anc = 'start' if lpos == 'right' else 'end'
                for (t, fs, c_, wt) in lines:
                    f.append(self.text(ax, ty, t, fs, c_, anc, wt)); ty += fs*1.35
        return self

    def odot(self, x, y, r=5):
        self.mid.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#141414" stroke="#fff" stroke-opacity=".9" stroke-width="1.6"/>')

    def chip(self, cx, cy, lines, fs=18, pad=12, anchor='middle', op=.55, x0=None, first_color='#f2f2f2'):
        w = max(tw(t, fs if i == 0 else fs*0.85) for i, t in enumerate(lines)) + 2*pad
        h = fs*1.1 + sum(fs*0.85*1.45 for _ in lines[1:]) + 2*pad - fs*0.1
        x = cx - w/2 if x0 is None else x0
        y = cy - h/2
        self.front.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#141414" stroke="#fff" stroke-opacity="{op}" stroke-width="1.4"/>')
        ty = y + pad + fs*0.85
        for i, t in enumerate(lines):
            fsz = fs if i == 0 else fs*0.85
            self.front.append(self.text(x + w/2, ty, t, fsz, first_color if i == 0 else '#a8a8ad', 'middle', 600 if i == 0 else 400))
            ty += fsz*1.45
        return (x, y, w, h)

    def svg(self):
        s = super().svg()
        extra = ('<radialGradient id="sph2" cx="32%" cy="28%" r="80%"><stop offset="0" stop-color="#4b4b4b"/><stop offset=".45" stop-color="#3a3a3a"/>'
                 '<stop offset=".85" stop-color="#2d2d2d"/><stop offset="1" stop-color="#282828"/></radialGradient>'
                 '<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="4" seed="3"/><feColorMatrix type="saturate" values="0"/>'
                 '<feComposite in2="SourceGraphic" operator="in"/></filter>'
                 '<pattern id="grid" width="36" height="36" patternUnits="userSpaceOnUse"><path d="M36 0H0V36" fill="none" stroke="#fff" stroke-opacity=".04"/></pattern>')
        s = s.replace('<pattern id="grid" width="40"', '<pattern id="gridold" width="40"', 1)
        return s.replace('</defs>', extra + '</defs>', 1)

HEAD_CSS = ''
def title_block(c, x, y, l1, l2, fs, sub, sfs, tag, tfs, gap_sub=None, lh=1.04, l1font=None):
    c.html.append(f'<div class="t" style="left:{x}px;top:{y}px;font-size:{fs}px;color:#F2F2F2">{l1}</div>')
    c.html.append(f'<div class="t" style="left:{x}px;top:{y+fs*lh:.0f}px;font-size:{fs}px;color:{TEAL_T}">{l2}</div>')
    ys = y + fs*lh*2 + (gap_sub if gap_sub is not None else fs*0.32)
    c.html.append(f'<div class="m" style="left:{x+4}px;top:{ys:.0f}px;font-size:{sfs}px;font-weight:400;letter-spacing:.12em;color:#e6e6e6">{sub}</div>')
    yt = ys + sfs*1.9
    c.html.append(f'<div class="tag" style="left:{x+4}px;top:{yt:.0f}px;font-size:{tfs}px;padding:{tfs*0.45:.0f}px {tfs*0.9:.0f}px;letter-spacing:.1em;border-color:rgba(255,255,255,.6)">{tag}</div>')
    return yt + tfs*2.4


def team(c, chief, row, rc, r, row_y, lfs, sfs=None, bus_gap=None, loop=True, loop_dx=None, chief_label='', chief_sub=(), arrow_labels=None, bottom=True, sw=2.0):
    """reference structure: chief with ring on top, fork bus to a row of bots, bottom bus with open dots + loop arrows.
    row: list of (x, color, shape, label, sub)"""
    cx, cy = chief
    c.bot(cx, cy, rc, 'teal', ring=True, label=chief_label, sub=chief_sub, lfs=lfs*1.05, sfs=sfs, gap=0)
    p0, p1, R = c._ring
    lh = tw(chief_label, lfs*1.05)/2 + 18
    bus = cy + R + lfs*2.3 if bus_gap is None else cy + R + bus_gap
    xs = [t[0] for t in row]
    ntop = row_y - r - 10
    # left/right fork from ring ends
    c.edge([p0, (min(p0[0] - (p0[1]-cy)*0.15, cx - lh), bus), (xs[0], bus), (xs[0], ntop)], radius=r*0.6, width=sw)
    c.edge([p1, (max(p1[0] + (p1[1]-cy)*0.15, cx + lh), bus), (xs[-1], bus), (xs[-1], ntop)], radius=r*0.6, width=sw)
    for x in xs[1:-1]:
        c.edge([(x, bus), (x, ntop)], width=sw)
    c.edge([(cx, cy + R + lfs*1.45), (cx, bus)], arrow=False, width=sw)
    lbs = []
    for (x, col, shape, lab, sub) in row:
        c.bot(x, row_y, r, col, shape=shape, label=lab, sub=sub, lfs=lfs, sfs=sfs, gap=r*0.38)
        lbs.append(c.lb)
    if bottom:
        lb = max(lbs) + r*0.35
        by = lb + r*0.85
        for x in xs:
            c.edge([(x, lb), (x, by)], arrow=False, width=sw)
        ldx = max(loop_dx or r*2.3, tw(row[0][3], lfs)/2 + 20, tw(row[-1][3], lfs)/2 + 20)
        if loop:
            c.edge([(xs[0], by), (xs[0] - ldx, by), (xs[0] - ldx, row_y), (xs[0] - r - 10, row_y)], radius=r*0.9, width=sw)
            c.edge([(xs[-1], by), (xs[-1] + ldx, by), (xs[-1] + ldx, row_y), (xs[-1] + r + 10, row_y)], radius=r*0.9, width=sw)
        c.edge([(xs[0], by), (xs[-1], by)], arrow=False, width=sw)
        for x in xs:
            c.odot(x, by, max(4, r*0.13))
        return bus, by
    return bus, None
