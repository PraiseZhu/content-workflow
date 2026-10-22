# deai-rules CHANGELOG

格式：日期 · 文件@版本 · 改了什么 · 为什么 · 校准结果变化。工具：`deai-lint/deai_lint.py`。

## 2026-10-18 · zh@2026-10-18.2 · 用作者早期人写文章校准 · ⚠️ 仍是 PROVISIONAL

用作者早期人写文章（作者确认过的干货文章：品牌传播一、二，视觉竞品分析）校准过一轮。作者还没认可过任何 AI 时代的终稿，所以门槛仍然是暂定的。
- pass 集：`${ARTICLES_DIR}/early-human/{brand-1,brand-2,visual-competitive-analysis}.md`。
- 改动前：3 篇全部没过，命中 cjk_latin_space ×4、fake_candor ×1、loose_layout ×2、contrast.bu_shi_er_shi ×1。
- 改动：
  - `zh.cjk_latin_space` 从 ban 降为 warn：3 篇人写文章都有中英间空格，误报率 100%。这是排版习惯，不是 AI 特征。R007 的排版要求以后在发布前统一格式化时处理。
  - `zh.fake_candor` 收窄：`不得不说` 只在后面紧跟逗号时才算口头禅。brand-1 L25「不得不说“概念设计”的重要性」意思是"不得不提"，属于正常用法。
  - `zh.loose_layout` 收窄：单句段只统计以句末标点结尾的段落；图注、伪小标题、标题行不算（brand-1 L1、L29）。
- **没改** `zh.contrast.bu_shi_er_shi`（仍是 ban）：visual-competitive-analysis L73「我个人关注的不是当事人的专业水平如何，而是…」是人写的，但这是作者点名禁的句式，也是典型 AI 骨架，所以不为了让文章通过而放宽。计为已知命中，等作者决定：放进 allow，或者接受"以后写作不用这个句式"。
- 改动后：pass 集通过 2/3（67%），visual-competitive-analysis 卡在上面这一条。fail 集拦截 4/4（100%），每篇 ≥2 条 ban（11、20、13、4）。tests 81/81 通过。
- 达到暂定线（pass 集 100% 加拦截率 ≥90%）：**否**，原因只有上面这一条，而且是有意保留的。
- warn 级在人写文章里的命中（不进门槛）：cjk_latin_space ×4、translationese ×1、essence_anchor ×1、parallel_pair ×1。
- style-profile.json 用这 3 篇重新计算（n=3）。voice-anchors.md 填了 5 段原文。

## 2026-10-18 · zh/en/personal/rubric @2026-10-18 · 首版 · ⚠️ PROVISIONAL（暂定门槛）

- 规则从旧 `de-ai-research/deai_lint.py` 的 ZH/EN/LIMITS 原样导出到 `zh.json`/`en.json` 的 `legacy` 段；`deai_lint.py legacy` 在 v1、v2、v5、QA 英文稿、10-16 英文稿上与旧脚本输出逐字一致（文本 + JSON）。
- 新增门槛规则（`rules` 段）：DEAI-DESIGN §2.1–2.3 全部条目，zh 19 条、en 15 条、personal 3 条；每条都有 `tests/` 命中/不命中样例（78/78 通过）。
- 修已知误报：`en.real_inflation` 收窄为 `the real (question|problem|story|issue|reason|point)`，"Start the real service" 不再命中。引号/代码/表格不扫；锁定行内命中降为 warn。
- `zh.signpost.xian_shuo_jie_lun`（"先说结论"）保持 **warn**，等作者决定是否加 allow 或升 ban。
- 格式：用 JSON 而不是设计稿写的 YAML（box 上没有 PyYAML，PLAN §1.2 也写的是 `.json`）。`article.yaml` 只读 `locked:` 列表，用的是内置的小解析器。
- 私名和术语表放在数据层：`config/private-names.txt`、`glossary.json`，**待作者 删改**。
- legacy `humanness_score` 每次 gate 都会跑，结果写进报告 JSON 的 `legacy` 字段，**只报告，不进门槛**。

### 暂定门槛（PROVISIONAL）
- 规则：人写 pass 集通过率 = 100%，并且 AI 味 fail 集拦截率 ≥ 90%。
- **pass 集为空**：作者还没有满意的终稿，box 上也没找到他早期自己写的干货文章（只找到线索：4 月那篇《设计流程没有死，它只是被压扁了》在他 Mac 的 Obsidian 里，不在 box 上）。所以通过率**没测**，误报率也算不出来。
- fail 集（v1、v2、v3、装人味样稿）拦截率 4/4 = 100%，每篇硬禁命中 ≥2 条（分别 12、20、14、4 条）。
- 额外观察（不在 fail 集里）：v4 被拦（10 条）、v5 被拦（12 条）、QA 英文稿被拦（4 条），10-16 英文稿**没被拦**（0 条 ban，1 条 warn "quietly"）。
- 在 pass 集有内容之前，规则只能证明"能拦住"，证明不了"不误伤"。

### 怎么重新校准（作者指定满意文章后）
1. 把文章放到 box 上，然后跑一条命令：`python3 deai-lint/deai_lint.py calibrate --add-pass /abs/path/article.md`（会写入 pass.txt，跑校准，并重算 style-profile.json）
2. 看输出里的 `FP <rule>` 行：误报率 >20% 的 ban 规则改成 warn，或者给它加 `allow`；改完给对应规则文件升 `version`。
3. 再跑一次 `deai_lint.py test` 和 `calibrate`，要求 pass_rate=1.0、catch_rate≥0.9。
4. 从这篇文章里挑 3–5 段原文写进 `config/voice-anchors.md`（R7 评审要用）。
5. 在这里记一条新记录，写清楚版本、结果和变化；两边结果都达标后，把这次的 PROVISIONAL 标记去掉。

## 2026-10-18.3
- zh.contrast.bu_shi_er_shi（不是…而是 等对比句式）：作者 明确定为所有公众号内容的永久硬禁，不设例外（视觉竞品分析 L73 不开白名单）。新增 outline:true，大纲、初稿、定稿三个阶段都拦。
- 修复：短中文文本被误判为英文、跳过中文规则（语言判断改为中文字数≥阈值或多于英文词数）。
