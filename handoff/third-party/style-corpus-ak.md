# 输出风格语料 · @AnatoliKopadze 的 X Article(真长文,非推文)

> 用户 2026-07-26 指定为公众号输出风格参考,并纠正过一次:**要的是这种带标题分章节的长文,不是引流长推文**。
> 抓取口径:`twitter user-posts -n 200` 拿到 191 条自有推文 → Article 不出现在时间线,靠 120 条自引用反查出 8 个 Article id → 逐个 `twitter article <id> -m` 取全文 Markdown。
> **缺口如实标注:只挖到 8 篇,不是 20 篇。** 原因:user-posts 硬上限 200 条(仅回溯到 2026-05-08),`twitter search` 端点当前 404,无法往更早窗口挖。补齐路径见 output-style.md 末节。

| # | 标题 | 发布 | 赞 | 书签 | 字节 | 文件 |
|---|---|---|---|---|---|---|
| 1 | Graph Engineering explained: what it is, when to use it an | Jul 24 14:57 | 499 | 1.7K | 16373 | `style-corpus/2080668775796314331.md` |
| 2 | Loops explained: Claude, GPT, Mira and what actually works | Jun 20 13:40 | 8.1K | 32.9K | 14781 | `style-corpus/2068328135611822149.md` |
| 3 | 21 Things most claude users have Never Set Up and It's Cos | May 01 14:46 | 1.7K | 8.5K | 14387 | `style-corpus/2050225292585607440.md` |
| 4 | 20 prompting rules that finally make Claude work the way y | May 05 14:08 | 256 | 685 | 10568 | `style-corpus/2051665228044124548.md` |
| 5 | Claude Can Do All of This. Most People Have No Idea. | May 22 13:18 | 4.3K | 19.6K | 10150 | `style-corpus/2057813254617858078.md` |
| 6 | How to Actually Use Claude. 18 steps that unlock 100% of i | May 13 14:26 | 7.7K | 29.8K | 10077 | `style-corpus/2054568935274549597.md` |
| 7 | AI Agents. What they are and how to Build Your Own Step by | Jun 08 14:04 | 1.3K | 4.8K | 9365 | `style-corpus/2063985608381362576.md` |
| 8 | 20 Claude Prompts that turn a $20 Subscription into a pers | Apr 29 14:14 | 1.5K | 8.4K | 8323 | `style-corpus/2049492553133629950.md` |
