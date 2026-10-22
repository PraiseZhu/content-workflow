#!/usr/bin/env python3
"""English HOW gate: fail the 2026-08-20 fingerprints, pass a cleaned draft."""

import os
import unittest
from pathlib import Path

from humanness_score import english_how_gate, _detect_lang, score_article


BAD = """
This piece is four things: what a handoff is, why it is thin, where, and how.

I recently watched a multi-model collaboration catch thinness in the act.

What holds up a thin brief was never the brief. It was the person receiving it.
It looks like noise. It is not. It is the ground the next model has to stand on.
The record sat there, lost in silence, lost into a wall of green.
If you've hit some historical mess — that change pulls the plan — off paper — into — reality — wait — more.
"""

_GOOD_REL = Path(os.path.expandvars("${CONTENT_ROOT}/output/x/handoff-thin-en.md"))
_GOOD_CANDIDATES = [
    os.environ.get("WEWRITE_EN_GOOD_SAMPLE", ""),
    str(Path(__file__).resolve().parent.parent / "output/x/handoff-thin-en.md"),
    str(Path(os.path.expandvars("${OBSIDIAN_ROOT}")) / _GOOD_REL),
    str(Path.home() / "Obsidian" / _GOOD_REL),
    str(Path("/Volumes/AKB2/Obsidian") / _GOOD_REL),
]
# 2026-10-12: was hard-coded to the ${BOX_HOME} path, which fails on the Mac.
GOOD = next((Path(p) for p in _GOOD_CANDIDATES if p and Path(p).is_file()), None)


class EnGateTests(unittest.TestCase):
    def test_bad_fails(self):
        ok, findings = english_how_gate(BAD)
        self.assertFalse(ok)
        joined = " ".join(findings)
        self.assertIn("syllabus_toc", joined)
        self.assertIn("spectator_voice", joined)
        self.assertIn("hr_brief", joined)
        self.assertIn("literary_double", joined)
        self.assertIn("historical mess", joined.lower())

    def test_current_en_draft_passes(self):
        if GOOD is None:
            self.skipTest("handoff-thin-en.md sample not found; set WEWRITE_EN_GOOD_SAMPLE")
        text = GOOD.read_text(encoding="utf-8")
        self.assertEqual(_detect_lang(text), "en")
        ok, findings = english_how_gate(text)
        self.assertTrue(ok, findings)
        result = score_article(text)
        self.assertEqual(result["lang"], "en")
        self.assertTrue(result["en_gate"]["ok"], result["en_gate"]["findings"])


if __name__ == "__main__":
    unittest.main()
