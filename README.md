# content-workflow · 个人内容写作工作流

一套把「一个选题」变成「微信公众号中文长文 + X 英文 Article」成对草稿的完整工作流：选题 → 提纲与作者口述 → 成稿 → 去 AI 味与评分 → 固定尺寸全套配图 → 中英交叉核对与预览 → 推草稿箱（从不自动发布）→ 记录与复盘；外加每日 X 热门配图风格收集与每周选题两个定时任务。

> 这里的一切都是**方法 + 工具 + 规则数据**。所有密钥、账号、公司/项目名、个人路径都已脱敏为占位符（见下方「脱敏说明」）。

## 快速开始
1. 读 [docs/01-overview.md](docs/01-overview.md) 了解全流程；
2. 按 [docs/12-install.md](docs/12-install.md) 安装（venv、依赖、路径变量、微信 AppID/Secret、X OAuth、字体、headless Chrome）；
3. 改 [config/voice.md](config/voice.md) 成你自己的写作偏好；
4. 让 agent 按 [workflows/article-pipeline/SKILL.md](workflows/article-pipeline/SKILL.md) + [skill/wewrite/SKILL.md](skill/wewrite/SKILL.md) 跑一篇。

## 文档
| | |
|---|---|
| [01 总览](docs/01-overview.md) | 流水线、目录对应关系、路径变量 |
| [02 选题](docs/02-topic-selection.md) | 每周 10 个中英选题卡 + 一周数据复盘 |
| [03 提纲与口述](docs/03-outline-and-briefing.md) | 拔高论点、机制视角、锁定行、作者补料清单 |
| [04 写作规则](docs/04-writing-and-style-rules.md) | 不喜欢 / 喜欢 清单、不编造、本地受众规则 |
| [05 去 AI 味与评分](docs/05-de-ai-scoring.md) | deai-lint 闸门 + humanness_score（<30） |
| [06 配图](docs/06-images.md) | 完整尺寸表、安全区、中英镜像、风格系统、出图流程与自检 |
| [07 交叉核对与预览](docs/07-crosscheck-preview.md) | 中英一致、图文一致、私名检查 |
| [08 推草稿箱](docs/08-publish-to-drafts.md) | 微信草稿 API、40164、密钥模式、X Articles API（header 映射、限额）、贴图 |
| [09 记录与复盘](docs/09-history-and-review.md) | history.yaml、一周数据 |
| [10 风格库](docs/10-style-library.md) | X 热门配图收集结构与 style.md |
| [11 定时任务](docs/11-routines.md) | 周五选题、工作日风格收集 |
| [12 安装](docs/12-install.md) | 一步步安装 |

## 目录
```
skill/wewrite/        主 skill：SKILL.md、references/（写作指南、去AI味、image-specs、visual-prompts…）、toolkit/（排版、微信草稿、X 草稿 CLI）、scripts/（humanness 评分等）
workflows/            方法层 skills：article-pipeline、deai-lint、article-image-render、x-trending-style-collection、x-trending-style-weekly-pick、cross-bot-review、html-report-render
deai-lint/ deai-rules/  去 AI 味规则引擎 + 规则数据/测试/校准
renderer/             HTML→PNG 配图模板（slots 合约 + render.py）、风格包、headless Chrome 渲染器
specs/image-sizes/    图片尺寸唯一真源（sizes.json / SPEC.md / check_spec.py）；specs/legacy/ 旧版规范
config/               voice.md、channels.yaml、glossary.json、style-profile.json、voice-anchors.md、private-names.example.txt
examples/             article-build（一篇文章的 slots/manifest/build 脚本）、image-generation（独立出图脚本示例）、history.example.yaml
style-library/        风格库 index 模板 + style.md 示例
routines/             两个定时任务的完整 prompt
knowledge/            每日工作标准（完成标准、异常处理、需作者决定的事）
```

## 核心铁律
- 只推草稿，**从不发布**；不覆盖、不删除已有草稿；没有封面不推。
- X 只放英文图，微信只放中文图；中英镜像。
- 作者的标题和结论句逐字保留；不编造经历、数字、故事；不点公司/产品/项目名。
- 密钥只放 `${SECRETS_DIR}` 或系统钥匙串，绝不进仓库、日志、聊天。

## 脱敏说明
公司/产品/项目名 → `<COMPANY>` / `Example Studio` / `example.com` 等；个人路径 → `${CONTENT_ROOT}` 等变量；X 账号 → `@<YOUR_X_HANDLE>`；第三方创作者账号 → `<creator_handle>`；草稿 ID → `<WECHAT_DRAFT_MEDIA_ID>` / `<X_ARTICLE_ID>`；作者名 → 「作者 / the author」。未包含：密钥、config.yaml、history.yaml 真实内容、已发布文章、下载的风格库图片、.venv。

## 致谢
`skill/wewrite/` 基于开源项目 WeWrite（MIT，见 `skill/wewrite/LICENSE`），在其上加了 X Articles 草稿、封面拼图、去 AI 味闸门、尺寸规范等。

---

## English summary

**content-workflow** is a complete personal writing pipeline that turns one topic into a matched pair of drafts: a Chinese long-form WeChat Official Account article and an English X Article. Steps: weekly topic selection (10 CN+EN picks from X AI trends with an opening conflict and a list of what the author must supply) → outline with an elevated thesis and organisation/mechanism angle → draft → de-AI gates (`deai-lint`) and a humanness score (<30) → a fixed image set rendered from HTML at exact sizes (WeChat 2350×1000 cover, 1000×1000 symbol-only square, 1080×1440 image-post cover, inline 1600×900 <1MB; X 2000×800 header with a 10%/20%/15% safe zone, inline 1600×900; English images on X only) → CN/EN cross-check and preview → push to the WeChat draft box and X Articles drafts (never publish, never overwrite, cover required; `###`→`header-two`, `##`→`header-one` because `header-three` returns 503; 10 X drafts per 24h) → history and a one-week performance review. Two routines run on schedule: weekly topics (Fri 08:04 Asia/Shanghai) and daily X trending image-style collection (weekdays 10:04, 10 sets/day, ≥50/week, Friday top-5).

Start with `docs/01-overview.md`, install with `docs/12-install.md`. All secrets, account IDs, personal paths and company/project names are replaced by placeholders. MIT licensed; `skill/wewrite` derives from the MIT-licensed WeWrite project.
