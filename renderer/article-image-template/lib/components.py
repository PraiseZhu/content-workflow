"""article-image-template components. Layout primitives only: no article text, no colours.
Colours come from the style pack's style.json `palette`; CSS from its tokens.css.
Every function returns an HTML string. Coordinates are export pixels."""
import math

class Kit:
    def __init__(self, style, css, W, H):
        self.p = style["palette"]; self.fr = style.get("frame", {}); self.css = css; self.W = W; self.H = H

    # ---- page / background ----
    def page(self, body, s=1.0):
        d = dict(W=self.W, H=self.H, nav=int(15*s), tag=int(30*s), chip=int(17*s), chipw=int(13*s),
                 colh=int(30*s), list=int(12*s), barh=int(12*s))
        return ('<!doctype html><html><head><meta charset="utf-8"><style>' + self.css % d +
                '</style></head><body>' + body + '<div class="grain"></div></body></html>')

    def photo(self, src, left, top, w, dim=1.0):
        return f'<img class="photo" src="{src}" style="left:{left}px;top:{top}px;width:{w}px;opacity:{dim}"><div class="tint"></div>'

    def grid(self, cols, rows):
        return (''.join(f'<div class="vl" style="left:{x}px"></div>' for x in cols) +
                ''.join(f'<div class="hl" style="top:{y}px"></div>' for y in rows))

    # ---- marks ----
    def br(self, x, y, w, h, plus=True):
        return (f'<div class="br" style="left:{x-w/2}px;top:{y-h/2}px;width:{w}px;height:{h}px"><i></i><i></i><i></i><i></i>' +
                ('<b>+</b>' if plus else '') + '</div>')

    def nav(self, items, xs, y, s=''):
        return ''.join(f'<div class="ab nav" style="left:{x}px;top:{y}px;{s}">{t}</div>' for t, x in zip(items, xs))

    def tele(self, x, y, lines, fs=12):
        return (f'<div class="ab mono" style="left:{x}px;top:{y}px;font-size:{fs}px;line-height:1.8;color:{self.p["ink_tele"]}">' +
                '<br>'.join(lines) + '</div>')

    def prog(self, x, y, w, p=88, fs=11):
        return (f'<div class="ab" style="left:{x}px;top:{y}px;width:{w}px"><div class="mono" style="font-size:{fs}px;margin-bottom:6px">'
                f'PROCESSING {p}%</div><div class="bar"><span style="width:{p}%"></span></div></div>')

    def ab(self, x, y, html, style=''):
        return f'<div class="ab" style="left:{x}px;top:{y}px;{style}">{html}</div>'

    def target(self, x, y, w, h, chip, sub, side='left'):
        cx = x-w/2-10 if side == 'left' else x+w/2+10
        tr = 'translateX(-100%)' if side == 'left' else ''
        return self.br(x, y, w, h) + self.ab(cx, y-h/2-8,
            f'<div class="chipw">{sub}</div><br><div class="chip" style="display:inline-block;margin-top:6px">{chip}</div>',
            f'transform:{tr} translateY(-100%);text-align:{"right" if side == "left" else "left"}')

    def node(self, x, y, label, sub, w=200, orange=False, center=True):
        p = self.p; c = p["accent"] if orange else p["ink"]
        l = x-w/2 if center else x
        return (f'<div class="ab" style="left:{l}px;top:{y-38}px;width:{w}px;height:76px;background:{p["panel"]}">'
            + ''.join(f'<div class="ab" style="{q};width:12px;height:12px;border-color:{c};border-style:solid;border-width:{bw}"></div>' for q, bw in
                [('left:0;top:0', '2px 0 0 2px'), ('right:0;top:0', '2px 2px 0 0'), ('left:0;bottom:0', '0 0 2px 2px'), ('right:0;bottom:0', '0 2px 2px 0')])
            + f'<div class="zh" style="text-align:center;font-size:22px;margin-top:12px;white-space:nowrap">{label}</div>'
            + f'<div class="mono" style="text-align:center;font-size:11px;margin-top:4px;color:{p["accent_soft"] if orange else p["ink_dim"]};white-space:nowrap">{sub}</div></div>')

    def line(self, x1, y1, x2, y2, orange=False, dash=False, label=''):
        L = math.hypot(x2-x1, y2-y1); a = math.degrees(math.atan2(y2-y1, x2-x1))
        c = self.p["accent"] if orange else self.p["ink_line"]
        st = f'border-top:1px {"dashed" if dash else "solid"} {c}'
        h = f'<div class="ab" style="left:{x1}px;top:{y1}px;width:{L}px;{st};transform-origin:0 0;transform:rotate({a}deg)"></div>'
        h += f'<div class="ab" style="left:{x2-4}px;top:{y2-4}px;width:8px;height:8px;background:{c}"></div>'
        if label:
            h += self.ab((x1+x2)/2, (y1+y2)/2-22, f'<div class="mono" style="font-size:11px;color:{self.p["ink_line"]};white-space:nowrap;transform:translateX(-50%)">{label}</div>')
        return h

    def raw(self, html):
        return html

    # ---- layouts ----
    def hero(self, s, g, t):
        """Cover / header layout. g = geometry (per slot size), t = text slots."""
        p = self.p
        b = self.photo(t['photo'], g['px'], g['py'], g['pw'])
        b += f'<div class="ab" style="left:{g["px"]+g["pw"]-500*s}px;top:0;width:{600*s}px;bottom:0;background:linear-gradient(90deg,{p["fade"]},{p["bg"]})"></div>'
        b += self.grid(g['cols'], g['rows'])
        b += f'<div class="hl or" style="top:{g["orule"]}px;height:2px;background:{p["accent"]}"></div>'
        b += f'<div class="vl or" style="left:{g["ovl"]}px;width:1px;opacity:.85"></div>'
        b += self.nav(t['nav'], g['navx'], g['navy'])
        b += self.ab(g['tagx'], g['tagy'], t['tag'], 'font:400 %dpx JetBrains Mono' % (34*s))
        b += self.tele(g['tagx'], g['tagy']+70*s, t['tele'], int(12*s))
        b += self.prog(g['tagx'], g['tagy']+150*s, 200*s, fs=int(11*s))
        b += self.target(*g['tgt'], t['target_chip'], t['target_sub'], side=g.get('side', 'left'))
        b += self.ab(g['tx'], g['ty'], '<div class="zh title" style="font-size:%dpx">%s</div>' % (g['tfs'], t['title_html']))
        b += self.ab(g['dx'], g['dy'], f'<div style="display:flex;gap:{18*s}px;align-items:flex-start"><div style="font:300 {64*s}px/0.9 Inter">{t["deck_mark"]}</div><div><div class="zh" style="font-size:{40*s}px;line-height:1.2">{t["deck_html"]}</div><div style="font:400 {20*s}px Inter;margin-top:{10*s}px;opacity:.9">{t["deck_sub"]}</div></div></div>')
        for (h, l), x in zip(t['columns'], g['colx']):
            b += self.ab(x, g['chy'], f'<div class="colh zh" style="font-weight:400">{h}</div>')
            b += self.ab(x, g['ly'], '<div class="list">' + '<br>'.join(l) + '</div>')
        b += self.ab(g['gx'], g['gy'], f'<div class="giant" style="font-size:{g["gfs"]}px">{t["giant"]}</div>')
        return self.page(b, s)

    def frame(self, bg, tag, head, body, dim=.7, px=0, py=0, pw=None, nav=None, tele=None, tele_y=790):
        """Body-figure layout: photo + grid + nav + [tag] + headline, then `body` elements."""
        fr = self.fr; pw = self.W if pw is None else pw
        b = self.photo(bg, px, py, pw, dim) + f'<div class="ab" style="inset:0;background:rgba({self.p["shade_rgb"]},{1-dim})"></div>'
        b += self.grid(fr['grid_cols'], fr['grid_rows'])
        b += self.nav(nav, fr['nav_x'], fr['nav_y'], 'font-size:13px')
        b += self.ab(60, 100, f'<div style="font:400 26px JetBrains Mono">[ {tag} ]</div>')
        b += self.ab(60, 140, f'<div class="zh" style="font-size:68px;line-height:1.1;letter-spacing:-.01em;white-space:nowrap">{head}</div>')
        b += body
        b += self.tele(60, tele_y, tele, 11)
        b += self.prog(1340, 800, 200, fs=11)
        return self.page(b, fr.get('scale', .8))

ELEMENTS = ('ab', 'node', 'line', 'br', 'target', 'raw', 'photo', 'grid', 'tele', 'prog', 'nav')

def elements(kit, items, tokens):
    """items: [{"c": <element>, "a": [args], "k": {kwargs}}]. String args may use @token@ for palette values."""
    out = []
    for it in items:
        c = it['c']
        if c not in ELEMENTS: raise ValueError(f'unknown element {c!r}; allowed: {ELEMENTS}')
        a = [sub(v, tokens) for v in it.get('a', [])]; k = {kk: sub(v, tokens) for kk, v in it.get('k', {}).items()}
        out.append(getattr(kit, c)(*a, **k))
    return ''.join(out)

def sub(v, tokens):
    if isinstance(v, str) and '@' in v:
        for k, val in tokens.items(): v = v.replace(f'@{k}@', val)
    elif isinstance(v, list): return [sub(x, tokens) for x in v]
    return v
