# 01 · 总览 Overview

一篇文章 = 一对稿件：**中文长文（微信公众号）+ 英文 X Article**。两边共用选题、提纲、论证结构和配图构图；英文从同一提纲用英语重写，不逐句翻译。

## 流水线

| # | 阶段 | 产物 | 闸门 | 文档 |
|---|---|---|---|---|
| 1 | 选题 | 每周 10 个中英选题卡 | 作者挑选 | [02](02-topic-selection.md) |
| 2 | 提纲 + 作者口述补料 | `drafts/outline.zh.md` / `.en.md` | `deai_lint gate --stage outline`；✋确认① | [03](03-outline-and-briefing.md) |
| 3 | 成稿（草稿，不发给作者） | `drafts/draft.<lang>.md` | `gate --stage draft` + rubric | [04](04-writing-and-style-rules.md) |
| 4 | 终稿（作者第一次看到的版本） | `content/<lang>.md` | `gate --stage final`；锁定行逐字；✋确认② | [04](04-writing-and-style-rules.md) [05](05-de-ai-scoring.md) |
| 5 | 去 AI 味与评分 | lint 报告 + humanness 分数 < 30 | 内嵌在 2/3/4 | [05](05-de-ai-scoring.md) |
| 6 | 配图 | `images/zh/` `images/en/` 固定尺寸全套 | `render.py --check` | [06](06-images.md) |
| 7 | 中英交叉核对 + 预览 | 不一致清单 / HTML 预览 | 修完才预览 | [07](07-crosscheck-preview.md) |
| 8 | 推草稿箱 | 微信草稿 + X Article 草稿 | 有封面才推；不覆盖；从不发布；✋确认③ 作者手动发布 | [08](08-publish-to-drafts.md) |
| 9 | 记录与复盘 | `history.yaml` + 发布满一周数据复盘 | — | [09](09-history-and-review.md) |
| — | 风格库（每日收集） | `style-library/x-trending/<date>/` | 每周 ≥50 组 | [10](10-style-library.md) |
| — | 定时任务 | 周五选题、工作日风格收集 | — | [11](11-routines.md) |

## 仓库里每块东西对应哪一步

- `skill/wewrite/` — 主 skill（基于开源 WeWrite，MIT）：SKILL.md 总流程、references/ 写作规范与去 AI 味规则、toolkit/ 排版+微信草稿+X 草稿 CLI、scripts/ humanness 评分等。
- `workflows/` — 方法层 skill：article-pipeline（全流程）、deai-lint（去 AI 味闸门）、article-image-render（配图渲染）、x-trending-style-collection / weekly-pick（风格收集）、cross-bot-review、html-report-render。
- `deai-lint/` + `deai-rules/` — 规则引擎与规则数据（zh/en/personal/rubric + 测试 + 校准）。
- `renderer/` — HTML→PNG 配图模板（slots.json 合约 + render.py）、风格包（dark-grid-photo、house-dark）、headless Chrome 渲染器。
- `specs/image-sizes/` — 图片尺寸唯一真源（sizes.json + SPEC.md + check_spec.py）。
- `config/` — 作者偏好（voice.md）、渠道（channels.yaml）、术语表、风格锚点、私名清单示例。
- `examples/` — 一篇文章的配图构建脚本（article-build）和一个独立出图脚本示例（image-generation）。
- `style-library/` — 风格库 index 模板 + 一个 style.md 示例。
- `routines/` — 两个定时任务的完整 prompt。
- `knowledge/` — 每日工作标准（完成标准、异常处理、需作者决定的事）。

## 路径变量

所有个人路径都换成了变量，安装时自己设定（见 [12-install](12-install.md)）：

| 变量 | 含义 |
|---|---|
| `${CONTENT_ROOT}` | 文章根目录（如 Obsidian 里的「公众号」文件夹），含 output/ selections/ preview/ history.yaml |
| `${WEWRITE_DIR}` | wewrite skill 安装目录 |
| `${ARTICLES_DIR}` | 按文章分目录的工作区（article.yaml / content / images / render） |
| `${STYLE_LIBRARY_DIR}` | X 热门风格库目录 |
| `${STYLE_LIBRARY_ROOT}` `${WORKSPACE}` `${BOX_HOME}` `${HOME}` | 其他工作目录 |
| `${FONT_DIR}` | 字体目录（MiSans 等） |
| `${SECRETS_DIR}` | 密钥目录（不入库，mode 700） |
