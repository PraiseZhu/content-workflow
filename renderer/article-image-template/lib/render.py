#!/usr/bin/env python3
"""render.py — one renderer for every language and platform.

  render.py ARTICLE_DIR [--lang zh,en] [--only NAME[,NAME]] [--out DIR] [--check] [--safe-overlay]

Reads ARTICLE_DIR/article.yaml -> style pack (article.yaml `style:` or styles/ACTIVE) ->
specs/image-sizes/sizes.json -> ARTICLE_DIR/render/slots.<lang>.json -> HTML -> headless Chromium -> PNG.
Writes images to the per-language dir from article.yaml `out:` (default images/<lang>), HTML to render/html/<lang>/,
and render/manifest.<lang>.json. --check validates slots against sizes.json without rendering (exit 2 on error).
Env: SIZES_JSON, STYLES_DIR, CHROMIUM override the defaults."""
import json, os, re, subprocess, sys, hashlib, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from components import Kit, elements

SIZES = os.environ.get('SIZES_JSON', 'specs/image-sizes/sizes.json')
STYLES = os.environ.get('STYLES_DIR', 'renderer/article-image-styles')
CHROMIUM = os.environ.get('CHROMIUM', 'chromium')

class SpecError(Exception): pass

def mini_yaml(path):
    """Tiny YAML subset: `key: value`, `key: [a, b]`, one level of nested maps, and `- item` lists."""
    root, stack = {}, [(-1, None)]
    cur_key = None; cur = root; parent_for = {}
    def scalar(v):
        v = v.strip()
        if v.startswith('[') and v.endswith(']'): return [scalar(x) for x in v[1:-1].split(',') if x.strip()]
        if len(v) >= 2 and v[0] == v[-1] and v[0] in '"\'': return v[1:-1]
        if re.fullmatch(r'-?\d+', v): return int(v)
        return {'true': True, 'false': False, 'null': None, '': None}.get(v, v)
    top = None
    for raw in open(path, encoding='utf-8'):
        line = raw.split(' #')[0].rstrip() if not raw.lstrip().startswith('- "') else raw.rstrip()
        if not line.strip() or line.lstrip().startswith('#'): continue
        ind = len(line) - len(line.lstrip())
        s = line.strip()
        if s.startswith('- '):
            tgt = root[top] if ind > 0 and top and isinstance(root.get(top), list) else None
            if tgt is None: root[top] = tgt = []
            tgt.append(scalar(s[2:])); continue
        k, _, v = s.partition(':')
        if ind == 0:
            top = k.strip()
            root[top] = scalar(v) if v.strip() else None
        else:
            if root.get(top) is None: root[top] = {}
            root[top][k.strip()] = scalar(v)
    return root

def load_style(name):
    d = os.path.join(STYLES, name)
    st = json.load(open(os.path.join(d, 'style.json'), encoding='utf-8'))
    css = open(os.path.join(d, st.get('css', 'tokens.css')), encoding='utf-8').read()
    if css.startswith('/*'): css = css.split('*/', 1)[1].lstrip('\n')
    return st, '\n' + css

def check_figure(fig, lang, sizes, errs):
    sid = fig.get('slot'); spec = sizes['slots'].get(sid)
    name = fig.get('name', sid)
    if spec is None: errs.append(f'{name}: unknown slot id {sid!r} (not in sizes.json)'); return None
    if spec['status'] == 'retired':
        errs.append(f'{name}: slot {sid} is retired since {spec.get("retired")}; use {spec.get("replaced_by")}'); return None
    if spec['lang'] != lang: errs.append(f'{name}: slot {sid} is {spec["lang"]}-only, slots file is {lang}')
    if ('w' in fig or 'h' in fig) and (fig.get('w'), fig.get('h')) != (spec['w'], spec['h']):
        errs.append(f'{name}: declares {fig.get("w")}x{fig.get("h")} but {sid} is {spec["w"]}x{spec["h"]} in sizes.json {sizes["version"]}')
    if spec.get('title') is False and fig.get('title_html'):
        errs.append(f'{name}: slot {sid} must not carry a title')
    return spec

def main(a):
    art = os.path.abspath(a[0]); opt = lambda n, d=None: a[a.index(n)+1] if n in a else d
    meta = mini_yaml(os.path.join(art, 'article.yaml'))
    langs = (opt('--lang') or ','.join(meta.get('langs') or ['zh', 'en'])).split(',')
    only = set((opt('--only') or '').split(',')) - {''}
    sizes = json.load(open(SIZES, encoding='utf-8'))
    style_name = meta.get('style') or open(os.path.join(STYLES, 'ACTIVE')).read().strip()
    style, css = load_style(style_name)
    tokens = dict(style['palette'])
    if meta.get('sizes_version') and meta['sizes_version'] != sizes['version']:
        print(f'note: article pinned sizes {meta["sizes_version"]}, current {sizes["version"]}', file=sys.stderr)
    rc = 0
    for lang in langs:
        sl = json.load(open(os.path.join(art, 'render', f'slots.{lang}.json'), encoding='utf-8'))
        errs = []; plan = []
        for fig in sl['figures']:
            spec = check_figure(fig, lang, sizes, errs)
            if spec is None: continue
            name = spec['filename'].format(w=spec['w'], h=spec['h'], name=fig.get('name', '')).removesuffix('.png')
            if not only or name in only: plan.append((fig, spec, name))
        req = json.load(open(os.path.join(TEMPLATE_DIR, 'slots.json')))['required_set'].get(lang, [])
        missing = [r for r in req if r not in {f.get('slot') for f in sl['figures']}]
        if missing: errs.append(f'required slots missing for {lang}: {missing}')
        if errs:
            print(f'[{lang}] SPEC ERRORS:\n  ' + '\n  '.join(errs), file=sys.stderr); rc = 2; continue
        print(f'[{lang}] {len(plan)} figures OK against sizes.json {sizes["version"]}')
        if '--check' in a: continue
        out = os.path.join(art, opt('--out') and os.path.join(opt('--out'), lang) or (meta.get('out') or {}).get(lang) or f'images/{lang}')
        hdir = os.path.join(art, 'render', 'html', lang)
        os.makedirs(out, exist_ok=True); os.makedirs(hdir, exist_ok=True)
        photos = os.path.join(art, meta.get('photos') or 'photos')
        for f in os.listdir(photos):  # photos are referenced by bare filename next to the HTML
            l = os.path.join(hdir, f)
            if not os.path.lexists(l): os.symlink(os.path.relpath(os.path.join(photos, f), hdir), l)
        manifest = {'style': style_name, 'style_version': style.get('version'), 'sizes_version': sizes['version'],
                    'template_version': json.load(open(os.path.join(TEMPLATE_DIR, 'slots.json')))['version'],
                    'rendered_at': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'images': {}}
        for fig, spec, name in plan:
            W, H = spec['w'], spec['h']; kit = Kit(style, css, W, H)
            lay = fig['layout']
            if lay == 'hero':
                html = kit.hero(fig['scale'], fig['geom'], {k: v for k, v in fig['text'].items()} | {'photo': fig['photo']})
            elif lay == 'frame':
                body = elements(kit, fig['elements'], tokens)
                html = kit.frame(fig['photo'], fig['tag'], fig['head'], body, dim=fig.get('dim', .7),
                                 nav=fig.get('nav') or sl.get('nav'), tele=fig.get('tele') or sl.get('tele'), tele_y=fig.get('tele_y', 790))
            elif lay == 'canvas':
                html = kit.page(elements(kit, fig['elements'], tokens), fig.get('scale', 1.0))
            else: raise SpecError(f'{name}: unknown layout {lay}')
            hp = os.path.join(hdir, name + '.html'); open(hp, 'w').write(html)
            png = os.path.join(out, name + '.png')
            subprocess.run([CHROMIUM, '--headless=new', '--no-sandbox', '--hide-scrollbars', '--force-device-scale-factor=1',
                            f'--window-size={W},{H}', f'--screenshot={png}', '--virtual-time-budget=3000', 'file://' + hp],
                           check=True, capture_output=True)
            from PIL import Image
            got = Image.open(png).size; size = os.path.getsize(png); notes = []
            if got != (W, H): print(f'  FAIL {name}: rendered {got}, spec {W}x{H}', file=sys.stderr); rc = 1
            lim = spec.get('max_bytes')
            if lim and size > lim: notes.append(f'over max_bytes {lim}')
            if spec.get('upload_max_bytes') and size > spec['upload_max_bytes']: notes.append(spec.get('over_limit', 'over upload limit'))
            manifest['images'][name + '.png'] = {'slot': fig['slot'], 'w': W, 'h': H, 'bytes': size,
                                                 'sha256': hashlib.sha256(open(png, 'rb').read()).hexdigest(), 'notes': notes}
            print(f'  {name}.png {W}x{H} {size//1024}KB {"; ".join(notes)}')
            if '--safe-overlay' in a: overlay(png, spec, os.path.join(art, 'work', 'safe', lang))
        json.dump(manifest, open(os.path.join(art, 'render', f'manifest.{lang}.json'), 'w'), indent=1, ensure_ascii=False)
    return rc

def overlay(png, spec, d):
    from PIL import Image, ImageDraw
    os.makedirs(d, exist_ok=True); im = Image.open(png).convert('RGB'); dr = ImageDraw.Draw(im)
    if spec.get('safe'): dr.rectangle(spec['safe'], outline=(0, 255, 255), width=4)
    if spec.get('title_band_y'): y0, y1 = spec['title_band_y']; dr.rectangle([0, y0, spec['w'] - 1, y1], outline=(255, 0, 255), width=2)
    im.save(os.path.join(d, os.path.basename(png)))

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'): print(__doc__); sys.exit(0)
    sys.exit(main(sys.argv[1:]))
