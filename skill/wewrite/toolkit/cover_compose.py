"""Compose WeChat 2.35:1 + 1:1 covers into one thumb image.

WeChat draft/add (article_type=news) takes ONE thumb_media_id; the 2.35:1
(头条) and 1:1 (主页/分享卡片/次条) covers are crops of that image via
pic_crop_235_1 / pic_crop_1_1 ("X1_Y1_X2_Y2", normalized 0..1, ≤6 decimals).
There is no separate square-thumb field. So we stack the wide cover (top)
and the square cover (bottom-left) on one canvas and point each crop at its
own region. Without a square, omit crops (WeChat center-crops by default).
"""
from pathlib import Path
from PIL import Image, ImageOps

WIDE_W, WIDE_H = 2350, 1000
SQ = 1000


def _fmt(v: float) -> str:
    return f"{v:.6f}".rstrip("0").rstrip(".") or "0"


def compose_cover(wide_path: str, square_path: str, out_path: str):
    """Return (out_path, pic_crop_235_1, pic_crop_1_1)."""
    wide = ImageOps.fit(Image.open(wide_path).convert("RGB"), (WIDE_W, WIDE_H), Image.LANCZOS)
    sq = ImageOps.fit(Image.open(square_path).convert("RGB"), (SQ, SQ), Image.LANCZOS)
    H = WIDE_H + SQ
    canvas = Image.new("RGB", (WIDE_W, H), (0, 0, 0))
    canvas.paste(wide, (0, 0))
    canvas.paste(sq, (0, WIDE_H))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, "JPEG", quality=90, optimize=True)  # permanent image limit 10MB
    crop_wide = "_".join(_fmt(v) for v in (0, 0, 1, WIDE_H / H))
    crop_sq = "_".join(_fmt(v) for v in (0, WIDE_H / H, SQ / WIDE_W, 1))
    return out_path, crop_wide, crop_sq
