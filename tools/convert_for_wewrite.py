#!/usr/bin/env python3
"""把 Obsidian 笔记转换为 wewrite 友好格式（临时副本）。"""
import re
import sys
from pathlib import Path

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
attach_dir = (src.parent / "Attachments").resolve()

text = src.read_text(encoding="utf-8")

# 1. 剥离 frontmatter
m = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
if m:
    text = text[m.end():]

# 2. 截断 `## 📋 SEO + 元数据` 之后所有内容（含其前的 `---`）
m = re.search(r"\n---\n+## 📋 SEO", text)
if m:
    text = text[:m.start()]

# 3. 移除 mp4 行（封面走 cover 字段，正文视频走腾讯视频后台）
text = re.sub(r"^!\[\[[^\]]+\.mp4\]\]\s*$\n?", "", text, flags=re.MULTILINE)

# 4. wikilink 图片 -> 标准 markdown
def rewrite_img(m):
    fname = m.group(1).strip()
    p = attach_dir / fname
    return f"![]({p.as_posix()})"

text = re.sub(r"!\[\[([^\]]+\.(png|jpg|jpeg|webp|gif))\]\]", rewrite_img, text, flags=re.IGNORECASE)

# 5. 移除 `%% ... %%` Obsidian 私有注释
text = re.sub(r"%%.*?%%", "", text, flags=re.DOTALL)

dst.write_text(text, encoding="utf-8")
print(f"Wrote: {dst} ({len(text)} chars)")
