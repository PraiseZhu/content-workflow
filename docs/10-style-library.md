# 10 · 风格库 Style library

目的：从 X 热门长文的封面和配图里找能沉淀成**个人品牌**的视觉风格，而不是求多。

## 结构
```
${STYLE_LIBRARY_DIR}/
  index.md                      # 按 ISO 周 → 按风格流派分组（模板：style-library/index.template.md）
  weekly-YYYY-Www.md            # 周五 Top 5
  YYYY-MM-DD/
    NN-<creator_handle>/
      cover.jpg  inline.jpg     # 原图（不入本仓库）
      style.md                  # 示例：style-library/example/style.md
```

## style.md 字段
链接、标题、作者、发布时间（本地时区）、互动数据（含抓取时间）、图片源；**风格**：配色 / 构图版式 / 质感 / 个人标签强度 1–5；**参考**：可借鉴 / 风险 / 与自家风格的冲突。

## 从风格库到风格包
周五 Top 5 → 作者挑 → 把配色、字体、网格、纹理固化成 `renderer/article-image-styles/<pack>/`（style.json + tokens.css + STYLE.md）→ 改 `ACTIVE`。

定时任务：[routines/daily-style-collection.md](../routines/daily-style-collection.md)。
