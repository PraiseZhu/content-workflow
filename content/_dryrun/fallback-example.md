# 降级路径示例（image-gen 出图失败时的文中占位格式）

> 依据 `automation/image-style.md` 的降级约定：「image-gen 出图失败 → 文中留『配图位 + 本 prompt』占位，不阻塞推送」。
> 本文件是该约定的一次格式 dry-run（2026-07-25，worker 实测 image-gen 通道返回 IMAGE_API_KEY_MISSING 后生成）。

## 文中嵌入示例（markdown 正文片段）

……前文段落。

> **【配图位 · 待补】**
> 位置：头图（16:9）
> 子风格：S1 · 奶油底极简插画
> prompt：`A minimal desk with a coral notebook. Warm cream/off-white background, minimal flat illustration, soft coral & muted earth accents, generous negative space, hand-drawn feel, editorial, no text`
> 失败原因：IMAGE_API_KEY_MISSING（image-gen key 未配置，2026-07-25 dry-run）

后文段落继续，排版与推送流程不被配图缺失阻塞……

## 节点图占位（同一文章内第二个配图位）

> **【配图位 · 待补】**
> 位置：H2「第二节点」配图（4:3）
> 子风格：S1 · 奶油底极简插画（单篇内锁定同一子风格）
> prompt：`An open notebook with a pen, top-down view. Warm cream/off-white background, minimal flat illustration, soft coral & muted earth accents, generous negative space, hand-drawn feel, editorial, no text`

## 格式要点

1. 占位块用 blockquote，人眼与排版引擎都可识别、可后处理（grep `【配图位` 即可定位全部待补位）。
2. 必带四字段：位置（含比例）、子风格编号、完整 prompt（可直接复投）、失败原因。
3. prompt 原样保留，补图时无需重新组织语言，人工或脚本拿着它重投 image-gen 即可。
4. 不含文字约束（no text）等固定约束已写进 prompt，补图时不需要额外回忆规则。
