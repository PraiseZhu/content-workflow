#!/usr/bin/env python3
"""Tests for the 2026-10-12 de-AI upgrade of humanness_score.py."""

import tempfile
import unittest
from pathlib import Path

import humanness_score as hs

CLEAN_ZH = ("评审会上，设计稿刚改完第三版，前端已经开始接组件。我们把验收标准改成能跑的页面，"
            "评审时间从四十分钟压到十五分钟。代价是设计师要多学一点前端，这个代价我认。\n\n"
            "第二个变化在工具上。原来标注要单独做一轮，现在组件库直接导出参数，"
            "标注这一步可以取消。省下来的时间用在走查上。\n\n"
            "最后一公里还是人在看：上线前我会亲自走一遍主流程。") * 3


class DeAiUpgradeTests(unittest.TestCase):
    def test_clean_article_banned_words_full_score(self):
        r = hs.score_banned_words(CLEAN_ZH)
        self.assertEqual(r["score"], 1.0, r["detail"])  # 最后一公里 is not sentence-start "最后，"

    def test_sentence_start_only(self):
        f = hs.banned_word_findings("最后，我们上线了。另外两个服务没动。\n\n另外，还有一件事。")
        self.assertEqual(f["sentence_start"].count("最后"), 1)
        self.assertEqual(f["sentence_start"].count("另外"), 1)

    def test_tiers(self):
        f = hs.banned_word_findings("赋能团队。说白了就是这样。说白了也没别的。\n\n打通闭环，对齐目标。")
        self.assertIn("赋能", f["hard"])
        self.assertTrue(any(x.startswith("说白了") for x in f["once_exceeded"]))
        self.assertTrue(f["para_cluster"])

    def test_report_only_not_scored(self):
        res = hs.score_article(CLEAN_ZH)
        for name in hs.REPORT_ONLY_CHECKS:
            tier = res["tier1"] if name in res["tier1"] else res["tier2"]
            self.assertTrue(tier[name]["report_only"])
        self.assertNotIn("emotional_arc", res["param_scores"])
        self.assertNotIn("self_correction_rate", res["param_scores"])
        self.assertNotIn("broken_sentence_rate", res["param_scores"])

    def test_tics_not_in_bonus_list(self):
        for w in ["说白了", "讲真", "说实话", "坦白讲", "老实说", "其实吧"]:
            self.assertNotIn(w, hs.WARM_WORDS)

    def test_lint_zh_patterns(self):
        txt = "# 一、开头\n\n这不是工具问题，而是机制问题。我们用 Claude Code 搭了 3 个流程。下面先讲背景。\n\n本文为AI辅助创作。"
        lint = hs.de_ai_lint(hs._clean_article_text(txt), txt)
        for k in ["not_x_but_y", "cjk_latin_space", "signpost", "ai_disclaimer", "heading_numeral"]:
            self.assertIn(k, lint["violations"], lint["violations"])
        res = hs.score_article(txt * 3)
        self.assertFalse(res["de_ai_gate"]["ok"])

    def test_no_space_text_passes_spacing(self):
        lint = hs.de_ai_lint("我们用Claude Code搭了3个流程，PR合并后自动跑。", None)
        self.assertNotIn("cjk_latin_space", lint["violations"])

    def test_en_gate_new_hard_checks(self):
        ok, findings, warns = hs.english_how_gate(
            "Here's the thing. The future belongs to builders. It serves as a gate.",
            return_warnings=True)
        self.assertFalse(ok)
        self.assertTrue(any("hook_phrase" in f for f in findings))
        self.assertTrue(any("generic_close" in f for f in findings))
        # legacy 2-tuple signature still works
        self.assertEqual(len(hs.english_how_gate("A plain sentence.")), 2)

    def test_baseline_not_configured(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = Path(d) / "b.yaml"
            cfg.write_text("samples: []\n", encoding="utf-8")
            self.assertEqual(hs.style_baseline_report(CLEAN_ZH, cfg)["status"], "not_configured")

    def test_baseline_with_samples(self):
        with tempfile.TemporaryDirectory() as d:
            for i in range(3):
                (Path(d) / f"s{i}.md").write_text(CLEAN_ZH + "补一句。" * i, encoding="utf-8")
            cfg = Path(d) / "b.yaml"
            cfg.write_text("samples:\n  - s0.md\n  - s1.md\n  - s2.md\nz_threshold: 1.5\n", encoding="utf-8")
            rep = hs.style_baseline_report("- **甲**：一。\n- **乙**：二。\n- **丙**：三。\n" * 5, cfg)
            self.assertEqual(rep["status"], "ok")
            self.assertEqual(rep["samples"], 3)
            self.assertIn("list_line_ratio", rep["off_baseline"])

    def test_legacy_compute_composite_signature(self):
        t = {"_summary": {"mean_score": 0.8}}
        c, w = hs.compute_composite(t, t)
        self.assertEqual(w, {"tier1": 0.625, "tier2": 0.375})


if __name__ == "__main__":
    unittest.main()
