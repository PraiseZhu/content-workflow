---
name: article-image-render
description: Render an article's image set (covers, headers, body figures, per language and platform) from a structure template + swappable style pack + platform size spec with one command, then self-check sizes, safe zones and language. Use for step "images" of an article pipeline, for re-rendering old articles, or when adding a style pack, language or platform.
---

# article-image-render

HTML → headless Chromium → PNG. The generic "HTML to PNG and screenshot check" method is in **html-report-render**; this skill covers only what is specific to article images.

## Three inputs, never mixed
| layer | where | holds |
|---|---|---|
| size spec | `specs/image-sizes/sizes.json` (+ SPEC.md) | slot IDs → pixels, language, safe zone, byte limits, status (active/reference/retired) |
| template | `renderer/article-image-template/` | `slots.json` contract (required set, layouts, elements), `lib/components.py`, `lib/render.py` |
| style pack | `renderer/article-image-styles/<pack>/` (+ `ACTIVE`) | `style.json` palette/fonts/frame grid, `tokens.css`, `refs/` |
| article data | `<article>/article.yaml`, `photos/`, `render/slots.<lang>.json` | text and positions only |

Never copy pixel sizes into slots, scripts or skills: refer to slot IDs (`wechat.cover`, `x.article_header`, …).

## Run
```
python3 renderer/article-image-template/lib/render.py <article> --check          # validate only
python3 renderer/article-image-template/lib/render.py <article> --safe-overlay   # all langs
python3 .../render.py <article> --lang en --only header-x-2000x800                               # one image
python3 .../render.py <article> --out /tmp/rerender                                               # re-render without touching images/
```
Exit 2 = spec error (unknown or retired slot, declared size ≠ spec, wrong language, missing required slot). Fix the slots; never edit pixels to match by hand, and never pad/crop a PNG afterwards.

## New article
1. Copy a previous article's `render/slots.<lang>.json` as a starting point; replace text with the final's wording (titles verbatim).
2. Set `style:` and pin `template_version` / `sizes_version` in article.yaml.
3. `--check`, then render with `--safe-overlay`.

## Self-check (every render)
- Sizes: render.py verifies every PNG against sizes.json; read `render/manifest.<lang>.json` notes (e.g. "convert to JPG q85 before upload" for over-limit body images).
- Safe zones: look at `work/safe/<lang>/*.png`; key text inside the cyan box. Square cover: no title; check readability at 200 px and 120 px.
- Language: each platform's images are in its language only; image text matches the final.
- Look at every image at 100 % and at phone width before handing over.

## Re-render acceptance (migrations, pack edits)
Render to `--out /tmp/x`, compare to the existing PNGs pixel-by-pixel (e.g. PIL/numpy: count differing pixels). Expect 0; any difference must be explained (font update, Chromium version) before replacing images.

## Extending
- New style: new pack folder (`style.json` + `tokens.css` + `refs/`); packs are add-only (`<pack>-v2` for big changes).
- New language: `slots.<lang>.json` + fonts in the pack. New platform / image type: add the slot to sizes.json (version + CHANGELOG), then to the template's `slots.json`.
- Candidate styles from style-collection skills become packs here once chosen.
