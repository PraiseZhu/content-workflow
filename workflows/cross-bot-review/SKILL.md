---
name: cross-bot-review
description: Host the daily cross-bot review for a group of bots that share one pipeline (e.g. test → report → fix → merge). Use every day at the scheduled time, or when asked "where is today's review".
version: 2026-10-18
---
# Daily cross-bot review

Everything project-specific (who participates, repos, report paths, schedules, rules, who may decide) lives in the project's config directory (`<data-dir>/config/`: participants, sources, rules). This method never names bots, repos or people.

## Files
- `<data-dir>/inbox/<date>/<participant-id>.md` — each participant's short report for the data day.
- `<data-dir>/daily/<date>.md` (+ `.json`) — the review. One file per day. The file existing is the proof the review happened.
- `<data-dir>/config/rules.json` — every rule with source date and who decided. New requirements are added here (with a changelog line), not repeated in chat.

## Fixed sections (every section appears; empty = "无", never omitted)
1. **Output alignment** — do the pipeline's results and what was published agree (counts, levels, recipients)? Anything untested, late, or produced by a fallback path instead of the normal trigger, with the delay.
2. **Accuracy** — were the right checks applied to each item (wrong or missing assignment), are levels consistent with the rules (summary vs details, same metric graded differently, findings from unverified sources driving a level), environment problems blamed on items.
3. **Fix follow-up** — each problem → owner conclusion → fix change → merged. Days stuck per item.
4. **Unanswered owners** — who was notified, how many reminders, days silent; flag those past the escalation threshold.
5. **Decisions needed** — at most 3, each with a one-line reply the decider can send. Use the delegate named in config before the human owner.
6. **Pipeline health** — does the automation itself need fixing: tool failures, degraded runs, missing schedules, stale locks, recovery checks after a reset.
7. **Project-specific sections** declared in config (e.g. an upstream service inspection) — same format.
Then: **participant reports** (submitted / "未交" — never write a conclusion for a missing participant) and **what could not be checked** (no access, data not available).

## Steps
1. First line: if yesterday's `daily/<date>.md` is missing, say so.
2. Run the project's collector (if any) for the data day; it gathers facts read-only. Treat its output as leads, not verdicts.
3. Read every participant's inbox file. Cross-check claims against the source data; where they disagree, say which is right and why.
4. Calibrate: for each lead, confirm or dismiss with evidence (file, field, log line, command). Record changed conclusions as "from X to Y, because …".
5. Write `daily/<date>.md`. Keep each line one fact + evidence pointer.
6. Route: corrections to the bot that publishes; fixes to the bot that fixes; pipeline changes follow the config's change path (who writes, who accepts, who deploys). Notify the human owner only per the config's escalation list.
7. Posting the review to a shared channel only if config allows it.

## Rules
- Same format every day. Times always with timezone.
- Do not fix things inside the review; open an item and route it.
- Do not repeat what another participant already reported to the owner; reference it.
- A rule decided by a delegate is marked as such in rules.json.
- New participant / new source / new rule = a config edit + changelog line. No method change.
