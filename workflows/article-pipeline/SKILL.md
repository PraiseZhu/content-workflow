---
name: article-pipeline
description: Produce one article as a matched pair (long-form Chinese platform + English X Article) from topic to draft box — outline, unsent draft, final sent to the author, inline de-AI gates, images, cross-check, preview, draft push, history record. Use when writing, revising or publishing an article for an author's channels.
---

# article-pipeline

Method only. Who, when and which accounts live in the project config, never here:
- `<articles>/config/voice.md` — the author's preferences (avoid/follow lists, hard constraints)
- `<articles>/config/channels.yaml` — channels, image slots per channel, draft rules, **where secrets live**
- `<articles>/config/private-names.txt`, `glossary.json` — used by deai-lint
- `<articles>/<date-slug>/article.yaml` — title, locked lines, style pack, langs, platforms, status

## Rules that hold at every step
- **Two of everything.** Every step produces the zh and the en version; en is written from the same outline, not translated sentence by sentence.
- **The final is the first version the author sees.** No separate review round: the author comments on the final directly.
- **Locked lines.** The author's chosen title and conclusion lines go under `locked:` in article.yaml and are never reworded (deai-lint fails the gate if they change).
- **Author-pinned bans.** Patterns the author has banned outright (listed in deai-lint's pinned rules) are hard bans at outline, draft and final; no exceptions, no whitelisting for a single article.
- **Sources.** Follow voice.md's source constraints (e.g. regions not to cite). No invented facts, numbers or anecdotes; missing material is marked `[待作者补]` / `[author to supply]`.
- **Images by language.** Each platform gets images only in its language (sizes.json `lang`).
- **Draft box never overwritten; push only when both covers exist; never publish/post without the author's explicit go.**
- **Secrets** are read only from the location named in channels.yaml (outside the backup tree). Never copy them into the article dir, the formatter's folder, logs, or chat.

## Article folder
```
<date-slug>/ article.yaml · content/zh.md en.md (finals) · drafts/ (outline + unsent drafts)
             images/<lang>/ · render/slots.<lang>.json · work/ (anything; never referenced) · publish.log
```

## Steps
| # | step | input → output | gate / check |
|---|---|---|---|
| 1 | Topic | weekly list of 10 candidates: EN title, why it is worth writing, which tag, what first-hand material exists, total score → `outlines/<YYYY-Www>.md` | wait for the author to pick; no outline before that |
| 2 | Outline + thesis | picked topic → `drafts/outline.zh.md` / `.en.md`: elevated thesis, mechanism/organisation angle, section skeleton, material per section | **deai-lint `gate --stage outline`** (+ outline rubric dims) |
| 3 | Draft (not sent) | outline → `drafts/draft.<lang>.md` | **deai-lint `gate --stage draft`** + full rubric; most fixing happens here (≤2 targeted rounds) |
| 4 | Final (sent to author) | draft → `content/<lang>.md`; 3-line summary on top (gate result, what changed, material the author must supply) | **deai-lint `gate --stage final`**; locked lines intact |
| 5 | De-AI | — | runs inline at 2/3/4 (no separate pass); after the author's own edit run `gate --stage author_final` and feed recurring edits back as candidate rules |
| 6 | Images | finals + slots → `images/<lang>/` | follow the **article-image-render** skill; render.py size check must pass |
| 7 | Cross-check | zh vs en: same claims, numbers, figures, locked lines; image text matches article text; no private names | list mismatches; fix before preview |
| 8 | Layout preview | final → platform format (long-form formatter for zh; X Article format for en, no raw markdown: `lint --x`) | author looks at the preview |
| 9 | Push to draft box | preview + covers → platform draft | run the project's publish preflight first (images, final gate, secrets location); new draft each time; check both cover crops in the backend afterwards |
| 10 | Record | → `publish.log` (where, draft ID, time) + article.yaml `status`, and the formatter's history record | — |

Statuses in article.yaml: `outline → draft → final → editing (author) → ready → drafted → published`. Automation never overwrites a file whose status is `editing` or later; it edits the same file, it does not make `-v2` copies.

## Changing this skill
One line in the skill folder's CHANGELOG.md per change (date, what, why). Preferences go to voice.md, not here.
