# article-image-template

version: 2026-10-18 · changes in `CHANGELOG.md`

Structure contract for article images: which images an article exports, the slots each image has, and the one renderer.
Looks (colours, fonts, texture) live in a style pack under `../article-image-styles/<pack>/`. Pixel sizes live in
`specs/image-sizes/sizes.json`. Nothing here holds article text.

## Files
| file | what |
|---|---|
| `slots.json` | machine contract: required image set per language, layouts and their fields, element kinds |
| `lib/components.py` | layout primitives (`page photo grid br nav tele prog ab target node line`) and layouts (`hero`, `frame`); colours come from the pack palette |
| `lib/render.py` | `render.py ARTICLE_DIR [--lang zh,en] [--only NAME] [--out DIR] [--check] [--safe-overlay]` |

## Per article (data layer)
```
<article>/
  article.yaml           style, langs, platforms, out dirs, pinned template/sizes versions, locked lines
  photos/                source photos, referenced by bare filename
  render/slots.<lang>.json   text + positions only; one file per language, same renderer
  render/html/<lang>/    generated HTML (inspect / debug)
  render/manifest.<lang>.json  what was rendered: slot, size, bytes, sha256, style + versions
  images/<lang dir>/     finished PNGs, names from sizes.json `filename`
  work/                  experiments, safe-zone overlays (work/safe/), retired files
```

## Rules
- Each figure names a size **slot ID** (`wechat.cover`, `x.article_header`, …). Never write pixels in slots; if a figure
  does declare `w`/`h` they must equal sizes.json, otherwise render.py exits 2. Retired IDs and wrong-language IDs also exit 2.
- Required set (from `slots.json`): zh → wechat.cover, wechat.square, wechat.body; en → x.article_header, x.body.
  `wechat.square` carries no title.
- A new language = a new `slots.<lang>.json` (and fonts in the pack). A new platform = entries in sizes.json and here. No new scripts.
- String args may use `@palette-name@` so slot HTML does not hard-code colours.
- After rendering: open `work/safe/` overlays (from `--safe-overlay`) and check key content is inside the safe box;
  for wechat.square also check it at 200 px and 120 px.
- Over-size bodies for WeChat (>1 MB) are flagged in the manifest: convert to JPG q85 before upload.

## Versioning
Bump `version` in `slots.json` + one line in CHANGELOG for any contract change. Packs are add-only (copy to `<pack>-v2` for big changes) so old articles re-render identically from their pinned `style` and versions.
