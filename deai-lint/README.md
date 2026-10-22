# deai-lint（工具）

规则不在代码里，都在 `deai-rules/`（`$DEAI_RULES` 或 `--rules` 可以改）。
数据层在 `config/`：private-names.txt、glossary.json、style-profile.json、voice-anchors.md。

```
python3 deai_lint.py lint  draft.md [--x] [--article article.yaml]
python3 deai_lint.py gate  draft.md --stage outline|draft|final|author_final --rubric rubric.json --article article.yaml --out work/deai/draft.json
python3 deai_lint.py rubric-prompt draft.md --stage draft     # 评审 prompt，交给新开的上下文
python3 deai_lint.py rubric-check draft.md rubric.json        # 核对 evidence，不合格的 fail 作废
python3 deai_lint.py test | calibrate [--add-pass P] | profile | legacy FILE
```
gate.pass = 硬禁 0 条 AND 所有 rubric 维度 pass AND 锁定行完好。legacy humanness_score 写进 `legacy` 字段，只报告。
