"""Markdown → X Article Draft.js ContentState.

X Articles API (POST /2/articles/draft) takes a Draft.js-style content_state,
not Markdown. Schema (docs.x.com/x-api/articles/create-draft-article, 2026-10):
  - block keys are snake_case: text, type, key, data, entity_ranges, inline_style_ranges
  - block types: unstyled, header-one/two (## -> one, ### -> two; header-three makes X 503), unordered-list-item,
    ordered-list-item, blockquote, atomic
  - inline styles: bold, italic, strikethrough (lowercase)
  - atomic blocks (text " ") point via entity_ranges at entities of type
    image / markdown (code, GFM tables) / divider / post / link / latex / emoji
  - images: upload with POST /2/media/upload (tweet_image), then an image
    entity with data.media_items=[{media_category, media_id}]
  - cover: top-level cover_media {media_category, media_id}

This module also writes a cleaned Markdown sidecar so the user can paste into
https://x.com/compose/articles if needed. Markdown tables are flattened to
bulleted "**name**: value" lines (both in the sidecar and the API payload) so
readers never see raw pipes. Never publishes.
"""

from __future__ import annotations

import re
import secrets
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
H1_RE = re.compile(r"^# (?!#)(.+?)\s*$")
IMAGE_RE = re.compile(r"^!\[.*?\]\(.*\)\s*$")
IMAGE_PARTS_RE = re.compile(r"^!\[(?P<alt>.*?)\]\((?P<src>[^)\s]+)(?:\s+\"[^\"]*\")?\)\s*$")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
HR_RE = re.compile(r"^[-*_]{3,}\s*$")
UL_RE = re.compile(r"^[-*+] (.+)$")
OL_RE = re.compile(r"^\d+[.)] (.+)$")
H2_RE = re.compile(r"^## (.+)$")
H3_RE = re.compile(r"^### (.+)$")
BOLD_ITALIC_RE = re.compile(r"\*\*\*(.+?)\*\*\*")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
CODE_FENCE_RE = re.compile(r"^```")
TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$")
TABLE_SEP_RE = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
NUMERIC_RE = re.compile(r"^[\d.,%+~-]+$")

IMAGE_PLACEHOLDER_PREFIX = "pending-upload:"


def _block_key() -> str:
    return secrets.token_hex(3)[:5]


def strip_frontmatter(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    return text[m.end() :] if m else text


def extract_title(text: str, fallback: str = "") -> str:
    for line in text.splitlines():
        m = H1_RE.match(line.strip())
        if m:
            return m.group(1).strip()
    return fallback


def extract_frontmatter_field(raw: str, field: str) -> Optional[str]:
    m = re.match(r"^---\n(.*?)\n---", raw, re.DOTALL)
    if not m:
        return None
    fm = m.group(1)
    hit = re.search(
        rf"^{re.escape(field)}:\s*[\"']?([^\"'\n]+)[\"']?",
        fm,
        re.MULTILINE,
    )
    return hit.group(1).strip() if hit else None


# -- tables ------------------------------------------------------------------


def _split_row(line: str) -> List[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def table_to_bullets(rows: List[str]) -> List[str]:
    """Flatten a GFM pipe table into bullet lines, never leaving a '|'.

    - 2 columns:            "- **Type check**: Types line up at compile time"
    - 3+ cols, numeric 2nd: "- **Level** (4): unit, integration, API, end-to-end"
    - otherwise:            "- **A**: Header2: b; Header3: c"
    The header row is dropped (it only labels the columns); body cell text is kept verbatim.
    """
    if len(rows) < 2 or not TABLE_SEP_RE.match(rows[1].strip()):
        return rows
    header = _split_row(rows[0])
    body = [_split_row(r) for r in rows[2:]]
    out: List[str] = []
    numeric_second = len(header) >= 3 and all(
        len(r) > 1 and NUMERIC_RE.match(r[1] or "x") for r in body
    )
    for cells in body:
        cells = [c.replace("\\|", "/") for c in cells]
        name = cells[0] if cells else ""
        rest = cells[1:]
        name_md = f"**{name}**" if name and "**" not in name else name
        if len(header) == 2 or len(rest) == 1:
            out.append(f"- {name_md}: {rest[0] if rest else ''}".rstrip(": ").rstrip())
        elif numeric_second:
            tail = "; ".join(c for c in rest[1:] if c)
            out.append(f"- {name_md} ({rest[0]}): {tail}")
        else:
            pairs = [
                f"{header[i + 1]}: {c}" if i + 1 < len(header) and header[i + 1] else c
                for i, c in enumerate(rest)
                if c
            ]
            out.append(f"- {name_md}: " + "; ".join(pairs))
    return out


def flatten_tables(lines: List[str]) -> List[str]:
    out: List[str] = []
    i = 0
    in_fence = False
    while i < len(lines):
        line = lines[i]
        if CODE_FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue
        if (
            not in_fence
            and TABLE_ROW_RE.match(line.strip())
            and i + 1 < len(lines)
            and TABLE_SEP_RE.match(lines[i + 1].strip())
        ):
            j = i
            rows: List[str] = []
            while j < len(lines) and TABLE_ROW_RE.match(lines[j].strip()):
                rows.append(lines[j])
                j += 1
            out.append("")
            out.extend(table_to_bullets(rows))
            out.append("")
            i = j
            continue
        out.append(line)
        i += 1
    return out


# -- cleaning ----------------------------------------------------------------


def clean_markdown_for_x(text: str, keep_images: bool = False) -> Tuple[str, str]:
    """Return (title, cleaned_body_markdown).

    Body has no frontmatter, no H1, no HTML comments, tables flattened to bullets.
    Images are dropped unless keep_images=True (API path uploads them).
    Links keep visible text only (URL posts cost extra on X API).
    """
    body = strip_frontmatter(text)
    body = HTML_COMMENT_RE.sub("", body)
    title = extract_title(body)
    lines: List[str] = []
    in_fence = False
    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if CODE_FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            lines.append(line)
            continue
        if in_fence:
            lines.append(line)
            continue
        if H1_RE.match(line):
            continue
        if IMAGE_RE.match(line.strip()):
            if keep_images:
                lines.append("")
                lines.append(line.strip())
                lines.append("")
            continue
        if HR_RE.match(line.strip()):
            continue
        line = LINK_RE.sub(r"\1", line)
        lines.append(line)
    lines = flatten_tables(lines)
    cleaned = apply_x_spacing("\n".join(lines))
    return title, cleaned


def _is_list_item(s: str) -> bool:
    return bool(UL_RE.match(s) or OL_RE.match(s))


def apply_x_spacing(text: str) -> str:
    """X paste spacing: 1 blank line between paragraphs, 2 above headings.

    X's editor already adds ~1 line (28px) between adjacent blocks. An extra
    empty paragraph on top of that becomes a 2-3 line hole, which is why
    Close-style gaps look huge. Markdown mapping:

    - one blank line (`\\n\\n`) -> adjacent blocks (visual ~1 line)
    - two blank lines before `##` (`\\n\\n\\n##`) -> one empty block above
      the heading when pasted (visual ~2 lines)

    Do not collapse `\\n{3,}` down to `\\n\\n` -- that wipes heading space.
    Consecutive list items stay tight (no extra blank between `-` rows).
    """
    raw_lines = [ln.rstrip() for ln in text.splitlines()]
    lines: List[str] = []
    in_fence = False
    for line in raw_lines:
        if CODE_FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            lines.append(line)
            continue
        if in_fence:
            lines.append(line)
            continue
        lines.append(line)

    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    out: List[str] = []
    last_content = ""
    emitted_content = False
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if CODE_FENCE_RE.match(stripped):
            in_fence = not in_fence
            if emitted_content:
                out.append("")
            out.append(line)
            last_content = stripped
            emitted_content = True
            continue
        if in_fence:
            out.append(line)
            continue
        if not stripped:
            continue
        if emitted_content:
            is_heading = bool(H2_RE.match(stripped) or H3_RE.match(stripped))
            if is_heading:
                out.append("")
                out.append("")
            elif _is_list_item(stripped) and _is_list_item(last_content):
                pass
            else:
                out.append("")
        out.append(line)
        last_content = stripped
        emitted_content = True
    return ("\n".join(out) + "\n") if out else "\n"


def _inline_styles(text: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Strip md emphasis markers; return (plain, inline_style_ranges).

    Offsets/lengths follow JS string indices (UTF-16 code units), as DraftJS
    does; for BMP text that equals Python len(). Non-BMP chars (emoji) are
    counted as 2 to stay aligned with the composer.
    """
    ranges: List[Dict[str, Any]] = []
    out: List[str] = []

    def jslen(s: str) -> int:
        return sum(2 if ord(ch) > 0xFFFF else 1 for ch in s)

    i = 0
    while i < len(text):
        for marker, styles in (("***", ("bold", "italic")), ("**", ("bold",)), ("*", ("italic",))):
            if text.startswith(marker, i) and not (marker == "*" and text.startswith("**", i)):
                end = text.find(marker, i + len(marker))
                if end != -1 and end > i + len(marker):
                    inner = text[i + len(marker) : end]
                    start = jslen("".join(out))
                    out.append(inner)
                    for st in styles:
                        ranges.append({"offset": start, "length": jslen(inner), "style": st})
                    i = end + len(marker)
                    break
        else:
            out.append(text[i])
            i += 1
    return "".join(out), ranges


def _make_block(text: str, block_type: str) -> Dict[str, Any]:
    plain, styles = _inline_styles(text)
    block: Dict[str, Any] = {"text": plain, "type": block_type}
    if styles:
        block["inline_style_ranges"] = styles
    return block


@dataclass
class PendingImage:
    entity_key: int
    src: str
    alt: str


def markdown_to_content_state(
    body: str, base_dir: Optional[Path] = None
) -> Tuple[Dict[str, Any], List[PendingImage]]:
    """Build content_state. Image lines become atomic blocks + image entities
    whose media_id is a placeholder; fill them via fill_media_ids()."""
    blocks: List[Dict[str, Any]] = []
    entities: List[Dict[str, Any]] = []
    images: List[PendingImage] = []
    para: List[str] = []
    in_fence = False
    fence_buf: List[str] = []
    fence_lang = ""

    def add_atomic(value: Dict[str, Any]) -> int:
        k = len(entities)
        entities.append({"key": str(k), "value": value})
        blocks.append(
            {"text": " ", "type": "atomic", "entity_ranges": [{"key": k, "offset": 0, "length": 1}]}
        )
        return k

    def flush_para() -> None:
        nonlocal para
        if not para:
            return
        text = " ".join(s.strip() for s in para if s.strip())
        para = []
        if text:
            blocks.append(_make_block(text, "unstyled"))

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if CODE_FENCE_RE.match(stripped):
            if in_fence:
                flush_para()
                code = "\n".join(fence_buf)
                add_atomic(
                    {
                        "type": "markdown",
                        "mutability": "mutable",
                        "data": {"markdown": f"```{fence_lang}\n{code}\n```"},
                    }
                )
                fence_buf = []
                in_fence = False
            else:
                flush_para()
                fence_lang = stripped[3:].strip()
                in_fence = True
            continue
        if in_fence:
            fence_buf.append(line)
            continue

        if not stripped:
            flush_para()
            continue

        img = IMAGE_PARTS_RE.match(stripped)
        if img:
            flush_para()
            src = img.group("src")
            p = Path(src)
            if not p.is_absolute() and base_dir is not None:
                p = (base_dir / p).resolve()
            k = add_atomic(
                {
                    "type": "image",
                    "mutability": "immutable",
                    "data": {
                        "media_items": [
                            {"media_category": "tweet_image", "media_id": IMAGE_PLACEHOLDER_PREFIX + str(p)}
                        ]
                    },
                }
            )
            images.append(PendingImage(entity_key=k, src=str(p), alt=img.group("alt")))
            continue

        h2 = H2_RE.match(stripped)
        if h2:
            flush_para()
            blocks.append(_make_block(h2.group(1).strip(), "header-one"))
            continue
        h3 = H3_RE.match(stripped)
        if h3:
            flush_para()
            blocks.append(_make_block(h3.group(1).strip(), "header-two"))
            continue
        ul = UL_RE.match(stripped)
        if ul:
            flush_para()
            blocks.append(_make_block(ul.group(1).strip(), "unordered-list-item"))
            continue
        ol = OL_RE.match(stripped)
        if ol:
            flush_para()
            blocks.append(_make_block(ol.group(1).strip(), "ordered-list-item"))
            continue

        para.append(stripped)

    flush_para()
    if in_fence and fence_buf:
        add_atomic(
            {
                "type": "markdown",
                "mutability": "mutable",
                "data": {"markdown": f"```{fence_lang}\n" + "\n".join(fence_buf) + "\n```"},
            }
        )

    return {"blocks": blocks, "entities": entities}, images


def fill_media_ids(content_state: Dict[str, Any], mapping: Dict[int, str]) -> None:
    """Replace placeholder media ids (entity index -> real media_id)."""
    for k, media_id in mapping.items():
        items = content_state["entities"][k]["value"]["data"]["media_items"]
        for it in items:
            it["media_id"] = str(media_id)


def drop_pending_images(content_state: Dict[str, Any]) -> None:
    """Remove image atomic blocks whose media was never uploaded (local-only path)."""
    keep_blocks = []
    for b in content_state["blocks"]:
        if b.get("type") == "atomic" and b.get("entity_ranges"):
            k = b["entity_ranges"][0]["key"]
            v = content_state["entities"][k]["value"]
            if v["type"] == "image" and any(
                str(it["media_id"]).startswith(IMAGE_PLACEHOLDER_PREFIX) for it in v["data"]["media_items"]
            ):
                continue
        keep_blocks.append(b)
    content_state["blocks"] = keep_blocks


@dataclass
class XArticleDraft:
    title: str
    markdown: str
    content_state: Dict[str, Any]
    slug: str = ""
    warnings: List[str] = field(default_factory=list)
    images: List[PendingImage] = field(default_factory=list)
    cover: Optional[str] = None

    @property
    def block_count(self) -> int:
        return len(self.content_state.get("blocks") or [])


def convert_file(path: str, title_override: Optional[str] = None) -> XArticleDraft:
    src = Path(path)
    raw = src.read_text(encoding="utf-8")
    slug = extract_frontmatter_field(raw, "slug") or src.stem
    fm_title = extract_frontmatter_field(raw, "title")
    title, cleaned = clean_markdown_for_x(raw)
    _t, api_body = clean_markdown_for_x(raw, keep_images=True)
    title = title_override or title or fm_title or src.stem
    warnings: List[str] = []
    state, images = markdown_to_content_state(api_body, base_dir=src.parent)
    if not state["blocks"]:
        raise ValueError("X 排版后没有正文 blocks")
    for im in images:
        if not Path(im.src).exists():
            warnings.append(f"图片不存在: {im.src}")
    cover = extract_frontmatter_field(raw, "cover") or extract_frontmatter_field(raw, "cover_image")
    if cover and not Path(cover).is_absolute():
        cover = str((src.parent / cover).resolve())
    sidecar = f"# {title}\n\n{cleaned.lstrip()}"
    if not sidecar.endswith("\n"):
        sidecar += "\n"
    return XArticleDraft(
        title=title,
        markdown=sidecar,
        content_state=state,
        slug=slug,
        warnings=warnings,
        images=images,
        cover=cover,
    )


def write_sidecar(draft: XArticleDraft, dest: str) -> Path:
    out = Path(dest)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(draft.markdown, encoding="utf-8")
    return out
