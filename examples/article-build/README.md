# render/

Current (2026-10-18): `slots.zh.json`, `slots.en.json` → rendered by
`python3 renderer/article-image-template/lib/render.py <this article dir>`.
Generated HTML goes to `html/<lang>/`; run record in `manifest.<lang>.json`.

Legacy, not used any more: `build.py`, `build_en.py` and the `*.html` files beside them (their output). The new renderer
reproduces their PNGs byte-for-byte (see ../work/migrate/acceptance-20261018.txt). Archive them into ../work/ once approved.
The 1500×600 header template was retired to ../work/retired-1500x600/.
