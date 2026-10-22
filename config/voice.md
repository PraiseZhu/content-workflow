# voice.md — the author's writing preferences (personal data; never copy into a generic skill)

version: 2026-10-18 · source: author's decisions relayed 2026-10-18. Author to confirm (PLAN #1 step 2).
Machine-checkable parts are enforced by deai-lint (`deai-rules/`, personal.json); this file is the human list.

## Avoid
- AI disclaimers / meta talk about being an AI or about the writing process
- Translationese (English syntax in Chinese)
- One sentence carrying two ideas — split it
- A purely colloquial tone
- Unexplained jargon — explain every term the first time it appears (glossary.json)
- Overstated claims — no superlatives without evidence
- The 「不是…而是」 contrast frame (and its reworded variants)
- Company / project / colleague names leaking (private-names.txt)
- Loose layout (padding paragraphs, empty transitions, scattered one-liners)
- Raw markdown on X (convert to X format; `deai_lint.py lint --x`)

## Follow
- X hot-article structure with an elevated thesis: hook → thesis lifted above the case → mechanism → implications
- Angle: organisational or mechanism level (how a team / system runs), not tool tips
- Topic tags: 设计师、摄影师、AI 时代组织运转、研发机制、自动化工作流

## Hard constraints
- The author's chosen title and conclusion lines are kept **verbatim** → put them under `locked:` in article.yaml (deai-lint checks they are intact).
- Local-audience rule (configurable; current setting): the author writes for a Chinese audience, so do **not** cite American posts or American people as sources or examples. Change or remove this line for your own audience.
- WeChat images Chinese only; X images English only (sizes.json lang).
