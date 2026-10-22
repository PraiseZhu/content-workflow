# 05 · 去 AI 味与评分 De-AI & scoring

两套工具，互为补充：

## 1. deai-lint（闸门，规则引擎）
- 代码：`deai-lint/deai_lint.py`；规则数据：`deai-rules/{zh,en,personal,rubric}.json`；每条规则有测试 `deai-rules/tests/`，有校准集 `deai-rules/calibration/`。
- 阶段：`gate --stage outline|draft|final|author_final`；`ban` 级命中直接不过；`lint --x` 检查 X 格式（无原始 markdown 表格等）。
- 个人规则：`p.leak.names`（私名泄露）、`p.jargon_first_use`（术语首用解释）、`p.locked_lines`（锁定行逐字）。
- 作者改稿后跑 `author_final`，反复出现的改动沉淀成候选规则（见 `deai-rules/CHANGELOG.md`）。
- 方法：[workflows/deai-lint/SKILL.md](../workflows/deai-lint/SKILL.md)

## 2. humanness_score.py（评分）
- `skill/wewrite/scripts/humanness_score.py <article.md>`，目标 **< 30**（越低越像人写）。
- 统计层（句长方差、段落节奏、词汇温度）+ 规则层（否定排比、「不是…而是」、模板承接词等）+ 风格基线（与作者旧文的距离，样本配置在 `references/style-baseline.yaml`）。
- 参数：`writing-config.yaml`。

## 五步机械清单（逐条过，逐条标 ✅）
1. 删空背景开头 2. 过满判断加边界 3. 压承接词 4. 补具体对象/动作/场景 5. 结尾改收口（谁适合 + 下一步）

## 换家族润色
润色模型与主笔模型必须不同家族（同家族改不掉同家族的语言习惯）。不可用时如实标注「未去 AI 味」。
