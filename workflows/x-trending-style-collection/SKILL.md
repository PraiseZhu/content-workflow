---
name: x-trending-style-collection
description: >-
  Use this when collecting cover + inline image style sets from trending X
  Articles into a style library (daily batch).
---
# X trending style collection

One set = the cover image + one inline (body) image from the SAME trending X Article. Goal is a distinctive personal brand reference, not breadth.

## Inputs (from the routine)
- Library root (e.g. a `x-trending` folder) and target sets per run (e.g. 10).
- The user's own house style to compare against, if known (from memory).

## Steps
1. Find candidates with the public X tools (`x` namespace: search_posts_all / get_news). Query for X Articles (long-form) in the user's topic areas (AI agents, workflows, design, org/R&D). Prefer high bookmarks/impressions in the last ~14 days. Skip any post id already listed in the library `index.md` or any day folder.
2. For each candidate, fetch the post (get_posts_by_id) and pull the article cover URL and the first body image URL. Skip posts without both.
3. Download both images with curl into `<root>/<YYYY-MM-DD>/<NN>-<handle>/cover.<ext>` and `inline.<ext>`. Verify each file is a real image (`file` command) and non-trivial size.
4. Write `style.md` in that folder: post URL, title, author, publish time (convert UTC to the user's zone), engagement with fetch time, image source URLs, then a 风格 section (配色 / 构图 / 质感 / 个人标签强度 1-5) and a 参考 section (可借鉴 / 风险 / compared to the user's house style). Write in the user's language. Only facts from the API; never invent numbers.
5. Prefer variety: no more than 2 sets of the same style genre per day.
6. Update `<root>/index.md`: under the current ISO week, add the day count and each set grouped by style genre, one line: path, 标签强度, 《title (truncated)》, URL. Also append rows to `<root>/<date>/_rows.json` as [genre, NN, handle, strength, title, post_id].
7. Report: number of sets added and the folder. If fewer than target, say why in one line. If zero new sets, stay quiet unless something is broken.
