---
name: deai-lint
description: >-
  Use this when checking a Chinese or English article draft for AI-flavoured
  writing at the outline, draft, or final step: deterministic hard-ban rules
  plus an evidence-backed rubric review, never a single score.
---
# deai-lint

The goal is that the draft reads like the author's own approved finals. It does not try to look human or dodge detectors. A total score is never the gate.

## Where things are
- Tool: `python3 <tool-dir>/deai_lint.py` (in the box backup tree; see the article pipeline config for the path).
- Rules (contract layer, versioned): `<rules-dir>/{zh,en,personal,rubric}.json`, `tests/`, `calibration/`, `CHANGELOG.md`.
- Project data (never copy it into this skill): private-names list, glossary, style profile, voice anchors, `article.yaml` with `locked:` lines. All of these live in the project's config folder.

## Gate
`gate.pass = hard_ban_hits == 0 AND every rubric dimension == pass AND locked lines intact`
- There are no weights and no averaging. A `warn` only goes in the report. `needs_author` doesn't fail the gate, but it is listed at the top of the version sent to the author.
- At most 2 rounds of targeted fixes per stage. If it still fails, carry on and mark `DONE_WITH_CONCERNS`.

## Per stage
- **outline**: `gate --stage outline` + rubric for the outline dims only (thesis, structure, substance). Only the leak and locked-line hard bans apply. Mark missing material `[待作者补]` / `[author to supply]`.
- **draft** (not sent): `gate --stage draft` + full rubric. Most fixing happens here.
- **final** (sent): `gate --stage final` + full rubric. Re-scan for contrast frames and aphorisms that came back in new words; put the 3-line summary at the top.
- **author's edit**: `gate --stage author_final` (hard bans only). No rubric; diff against the final and feed recurring edits back as candidate rules (warn first).
- **X / English**: write from the same outline in English, convert to X format, then `lint --x`. No raw markdown left after conversion.

## Rubric review
1. `deai_lint.py rubric-prompt draft.md --stage <stage>` builds the prompt. Run it in a **fresh context**, a different model if one is available. The reviewer only flags and never rewrites the draft.
2. Save its JSON, then pass it via `--rubric`. The script voids any `fail` that has no verbatim `evidence` or no `rewrite`.
3. Missing substance is `needs_author`. Never invent facts, numbers or anecdotes.

## Fixing
- Fix the structure first, then the sentences. Change only the flagged line or paragraph.
- Never touch locked lines. A hit inside a locked line is reported as a warn.
- Quotes, code, tables and proper nouns are not scanned. Fixed habits of the author go in the rule's `allow` list, not into ad-hoc exceptions.

## Output
- `work/deai/<stage>.json`: gate, hard_bans (line, rule, text, fix), rubric, warnings, locked_lines, rules_version, legacy.
- In chat, three lines only: gate result; what to fix (line plus one-line fix); what material the author must supply.
- `legacy`: the old composite humanness score, report only, kept for comparison during the transition.

## Changing rules
- Edit the JSON, bump `version` and add a line to `CHANGELOG.md`. Then run `deai_lint.py test` and `deai_lint.py calibrate`. Neither may get worse.
- New rules start as `warn`. Promote one to `ban` only after 0 false positives on 3 consecutive approved articles. A `ban` rule with a false-positive rate over 20% on the approved set gets demoted.
- While the approved set is empty, the pass line is provisional: it is only proven to catch AI drafts, not to spare the author's writing.
- Re-calibrate when the author approves a new article: `deai_lint.py calibrate --add-pass /abs/path.md`.

## Author-pinned hard bans
Some rules are pinned by the author and must never be demoted, whitelisted or narrowed, even if calibration lists them as "降为 warn 候选". Rules marked `"outline": true` also block at the outline stage. Current pinned rule: `zh.contrast.bu_shi_er_shi` (the 不是…而是 contrast pattern and its variants), a permanent hard ban at outline, draft and final.
