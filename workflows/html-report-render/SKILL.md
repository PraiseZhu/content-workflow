---
name: html-report-render
description: >-
  Use this when a report, digest, or one-pager should be designed as a polished
  HTML page and delivered as a long image (PNG) and PDF, with charts and Chinese
  text.
---
# HTML report render

Design the report as one self-contained HTML file, render it with headless Chrome, check it visually, then deliver.

## Tools on the box
- Renderer: `node renderer/html-render/render.mjs page.html [width=1200] [--scale=2]` writes `page.png` (full-page long image, 2x) and `page.pdf` (A4, backgrounds kept), and prints JSON with any page errors or failed requests.
- Charts: either inline SVG / CSS bars in the HTML, or a vendored chart lib copied next to the file (no CDN; render is offline-safe), or matplotlib PNGs from `${VENV}/bin/python`.
- Fonts: MiSans (`~/.local/share/fonts/misans/`) and Noto Sans CJK SC are installed; use `font-family: MiSans, 'Noto Sans CJK SC', sans-serif`. Mono: `ui-monospace, 'Noto Sans Mono CJK SC'`.

## Build the page
1. Single file, all CSS inline in `<style>`, images by relative path. Fixed width (default 1200px), `margin:0`.
2. Use the user's visual style from memory if known (e.g. near-black grid background with corner crosshairs and grain, white bold title with an accent-color second line, mono tag boxes, thin connector lines). Otherwise: dark neutral background, one accent color, generous spacing.
3. Layout: hero (title, period, 3-4 big KPI numbers), then sections as cards (产出 / 会话 / 质量与风险 / 下周), charts full-width inside cards, a footer with data sources and generated time (user's zone).
4. Typographic rules: 1 font family, at most 3 sizes for body, numbers tabular (`font-variant-numeric: tabular-nums`), line-height 1.6 for Chinese, no orphaned headings, no raw markdown symbols.
5. Print CSS: `@page { size: A4; margin: 0 }`, `-webkit-print-color-adjust: exact`, `break-inside: avoid` on cards.

## Render and verify
1. Run the renderer. If `errors` is non-empty, fix missing assets and re-render.
2. Open the PNG with Read and check: no tofu boxes for Chinese, nothing overflowing or clipped, charts readable, numbers match the data. Fix and re-render until clean (max 3 passes).
3. Open the PDF first page (`pdftoppm -png -r 60 -f 1 -l 1`) and check page breaks don't cut a card.

## Deliver
Keep `page.html`, `page.png`, `page.pdf` together in the report folder. Send the PNG inline and the PDF as an attachment. Never invent numbers to fill a layout; drop the block instead.
