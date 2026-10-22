# 09 · 记录与复盘 History & review

- 每篇文章推草稿后在 `${CONTENT_ROOT}/history.yaml` 追加一条，示例见 [examples/history.example.yaml](../examples/history.example.yaml)（字段：日期、slug、标题、主题、平台、草稿 ID、状态、发布时间、数据）。
- 草稿 ID（微信 media_id、X article_id）只存在本地 history.yaml，不入库。
- 核对：微信用 `draft/get` 读回；X 无读取接口，记录返回的 ID。
- **一周复盘**：发布满 7 天的文章，`scripts/fetch_stats.py` 拉数据（阅读、点赞、在看、转发、收藏；X 曝光/书签），与上篇对比，结论写进下周五的选题报告。
- 效果复盘方法：[skill/wewrite/references/effect-review.md](../skill/wewrite/references/effect-review.md)；改稿学习：[learn-edits.md](../skill/wewrite/references/learn-edits.md)。
