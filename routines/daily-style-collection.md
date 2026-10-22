# Routine · 工作日 X 热门长文配图风格收集（Daily style collection）

- **时间**：周一至周五 10:04（Asia/Shanghai），cron `4 10 * * 1-5`
- **目标**：每天 10 组，每周 ≥50 组；每组 = 同一篇 X 热门长文（X Article）的 1 张封面 + 1 张正文配图
- **方法 skill**：[workflows/x-trending-style-collection](../workflows/x-trending-style-collection/SKILL.md)；周五加跑 [x-trending-style-weekly-pick](../workflows/x-trending-style-weekly-pick/SKILL.md)

## Prompt

```
收集今天的 X 热门长文配图风格，目标 10 组。

库目录：${STYLE_LIBRARY_DIR}
1. 用公开 X 读取工具找近 14 天（热度不够放宽到 7 天内高互动）主题相关（AI agent、工作流、设计、组织/研发机制）的 X Article。
   跳过 index.md 和任何日期目录里已收录的 post id；同一流派每天最多 2 组。
2. 每篇取封面 + 第一张正文图，下载到 <库>/<YYYY-MM-DD>/<NN>-<handle>/cover.<ext> 与 inline.<ext>；
   用 file 命令确认是真图片，每张 >5KB。缺任一张就跳过该篇。
3. 每组写 style.md：
   - 帖子链接、标题、作者、发布时间（换算到 Asia/Shanghai）、互动数据（点赞/转发/回复/收藏/曝光 + 抓取时间）、图片源链接
   - 风格：配色、构图/版式、质感、个人标签强度（1–5）
   - 参考：可借鉴什么、风险、与自家风格（默认暗色网格）是否冲突
   只写 API 返回的事实，不编数字。
4. 更新 <库>/index.md：本 ISO 周段落下记录当天组数，按风格流派分组，每组一行：路径、标签强度、《标题》、链接。
5. 如果今天是周五：读本周所有 style.md，按 标签强度 → 与自家风格的可借鉴度 → 互动 排序选 Top 5（同流派最多 2 个），
   每个一句理由 + 标题 + 链接 + 封面/配图路径，并写本周组数 vs 目标 50，存 weekly-YYYY-Www.md。
6. 报告：新增组数和目录；不足 10 组用一句话说明原因。
```

## 完成标准
- 当天目录下各组都有 cover、inline、style.md，图片 >5KB；index.md 当周段落已更新；周五有 weekly-YYYY-Www.md。
