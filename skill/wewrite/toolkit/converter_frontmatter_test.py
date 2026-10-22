#!/usr/bin/env python3
"""WeChat converter must strip YAML frontmatter before HTML/digest. No network."""
import unittest
from converter import WeChatConverter, strip_frontmatter

MD = """---
title: 测试标题
topic_id: 2026-10-16-x
status: draft
---

# 测试标题

正文第一段，摘要应从这里开始。

---

分隔线后的段落。
"""


class FrontmatterTest(unittest.TestCase):
    def test_strip(self):
        out = strip_frontmatter(MD)
        self.assertTrue(out.lstrip().startswith("# 测试标题"))
        self.assertIn("分隔线后的段落", out)

    def test_no_frontmatter_unchanged(self):
        self.assertEqual(strip_frontmatter("# A\n\nbody\n"), "# A\n\nbody\n")

    def test_convert_html_and_digest_clean(self):
        r = WeChatConverter().convert(MD)
        self.assertNotIn("topic_id", r.html)
        self.assertNotIn("topic_id", r.digest)
        self.assertTrue(r.digest.startswith("正文第一段"))
        self.assertEqual(r.title, "测试标题")


if __name__ == "__main__":
    unittest.main()
