# 11 · 定时任务 Routines

| 任务 | 时间（Asia/Shanghai） | cron | Prompt |
|---|---|---|---|
| 每周 10 个选题 + 一周数据复盘 | 周五 08:04 | `4 8 * * 5` | [routines/weekly-topics.md](../routines/weekly-topics.md) |
| X 热门长文配图风格收集（10 组/天，≥50/周，周五 Top 5） | 周一至周五 10:04 | `4 10 * * 1-5` | [routines/daily-style-collection.md](../routines/daily-style-collection.md) |

其余工作（写文、出图、推草稿）按作者请求随时做，没有固定时间。

任意 agent 平台都可以跑：把 prompt 放进平台的定时任务；或者用 cron 调起一个能读 X 公开数据的 agent CLI。时区务必设成 Asia/Shanghai（或你自己的时区并相应改时间）。

完成标准与异常处理见 [knowledge/知识沉淀.md](../knowledge/知识沉淀.md)。
