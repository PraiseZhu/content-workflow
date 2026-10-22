#!/usr/bin/env python3
"""Local tests for Markdown → X Article conversion. No network."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from x_converter import (
    apply_x_spacing,
    clean_markdown_for_x,
    convert_file,
    markdown_to_content_state,
    fill_media_ids,
    strip_frontmatter,
)


SAMPLE = """---
title: 贵的模型出脑子,便宜的模型干活,有可能一开始你就错了
slug: handoff-thin
status: ready
---

# 贵的模型出脑子,便宜的模型干活,有可能一开始你就错了

贵的模型出方案,便宜的模型做执行,这好像是目前最通俗易懂的使用 agent 的方式。

![封面：交接](assets/handoff-thin/cover.png)

## 交接是什么

**计划可以描述理解,但承载不了理解。**

区别在于,**地图携带的是结论,现场携带的是理解**。

- 一种交的是地图
- 一种交的是现场

见 [文档](https://example.com/secret)。

<!-- 内部注释 -->

本文为 AI 辅助创作,观点与事实由作者本人确认。
"""


class ConvertTests(unittest.TestCase):
    def test_strips_frontmatter(self):
        body = strip_frontmatter(SAMPLE)
        self.assertFalse(body.startswith("---"))
        self.assertIn("贵的模型出方案", body)

    def test_clean_drops_images_comments_urls(self):
        title, cleaned = clean_markdown_for_x(SAMPLE)
        self.assertIn("贵的模型出脑子", title)
        self.assertNotIn("assets/handoff-thin/cover.png", cleaned)
        self.assertNotIn("https://example.com/secret", cleaned)
        self.assertIn("文档", cleaned)
        self.assertNotIn("内部注释", cleaned)
        self.assertNotIn("# 贵的模型", cleaned)
        self.assertIn("## 交接是什么", cleaned)

    def test_content_state_blocks(self):
        _, cleaned = clean_markdown_for_x(SAMPLE)
        state, _images = markdown_to_content_state(cleaned)
        types = [b["type"] for b in state["blocks"]]
        self.assertIn("header-one", types)  # ## -> header-one
        self.assertNotIn("header-three", types)  # backend 503s on header-three
        self.assertIn("unordered-list-item", types)
        self.assertIn("unstyled", types)
        self.assertFalse(any("**" in b["text"] for b in state["blocks"]))
        for b in state["blocks"]:
            self.assertTrue(set(b.keys()) <= {"text", "type", "inline_style_ranges"})
        self.assertEqual(set(state.keys()), {"blocks", "entities"})

    def test_x_spacing_rules(self):
        src = "\n".join(
            [
                "第一段。",
                "",
                "",
                "",
                "第二段。",
                "## 大标题",
                "标题下第一段。",
                "",
                "- 列表一",
                "",
                "- 列表二",
                "### 小标题",
                "结尾。",
            ]
        )
        out = apply_x_spacing(src)
        # 段与段之间恰好空 1 行
        self.assertIn("第一段。\n\n第二段。", out)
        # ## / ### 上方恰好空 2 行
        self.assertIn("第二段。\n\n\n## 大标题", out)
        self.assertIn("- 列表二\n\n\n### 小标题", out)
        # 标题与其下正文之间只空 1 行
        self.assertIn("## 大标题\n\n标题下第一段。", out)
        # 连续列表项之间不空行
        self.assertIn("- 列表一\n- 列表二", out)
        # 不留首尾空行,且 3 行以上空白不会被压成 1 行标题间距
        self.assertFalse(out.startswith("\n"))
        self.assertEqual(out.count("\n\n\n\n"), 0)

    def test_convert_file_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "2026-08-19-handoff-thin.md"
            src.write_text(SAMPLE, encoding="utf-8")
            draft = convert_file(str(src))
            self.assertEqual(draft.slug, "handoff-thin")
            self.assertTrue(draft.warnings)
            self.assertGreater(draft.block_count, 3)
            self.assertTrue(draft.markdown.startswith("# "))

    def test_tables_flatten_to_bullets(self):
        md = "\n".join([
            "Intro:", "", "| Check | What it does |", "|---|---|",
            "| Type check | Types line up at compile time |", "| Lint | Code follows the agreed style |", "",
            "| Group | Count | Dimensions |", "|---|---|---|", "| Level | 4 | unit, integration |",
        ])
        _, cleaned = clean_markdown_for_x(md)
        self.assertNotIn("|", cleaned)
        self.assertIn("- **Type check**: Types line up at compile time", cleaned)
        self.assertIn("- **Level** (4): unit, integration", cleaned)
        state, _ = markdown_to_content_state(cleaned)
        li = [b for b in state["blocks"] if b["type"] == "unordered-list-item"]
        self.assertEqual(li[0]["text"], "Type check: Types line up at compile time")
        self.assertEqual(li[0]["inline_style_ranges"], [{"offset": 0, "length": 10, "style": "bold"}])

    def test_images_become_atomic_entities(self):
        md = "Para.\n\n![Arch](fig1.png)\n\nAfter."
        _, body = clean_markdown_for_x(md, keep_images=True)
        state, images = markdown_to_content_state(body, base_dir=Path("/x"))
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0].src, "/x/fig1.png")
        atomic = [b for b in state["blocks"] if b["type"] == "atomic"]
        self.assertEqual(atomic[0]["entity_ranges"], [{"key": 0, "offset": 0, "length": 1}])
        self.assertEqual(state["entities"][0]["value"]["type"], "image")
        fill_media_ids(state, {0: "123"})
        self.assertEqual(state["entities"][0]["value"]["data"]["media_items"][0]["media_id"], "123")
        _, sidecar = clean_markdown_for_x(md)
        self.assertNotIn("![", sidecar)


if __name__ == "__main__":
    unittest.main()
