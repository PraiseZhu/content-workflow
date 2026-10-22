# handoff/ — 私有交接资料（PRIVATE · 未脱敏 · 只给作者本人的新 Grok Bot 用）

> ⚠️ 本目录**故意保留真实信息**（路径、账号、草稿 ID、私名清单、已发文章记录），用于作者本人账号上的新 bot 接手。
> **仓库公开前必须删除整个 handoff/ 目录**（`git rm -r handoff && git commit`，并考虑重写历史）。
> 本目录**不含任何密钥 / token / AppSecret**；需要时按「密钥重新录入」一节由作者本人重新输入。

## 1. 真实路径（替换 docs 里的变量）
| 变量 | 真实值 |
|---|---|
| `${CONTENT_ROOT}` | Mac：`/Users/praise/Obsidian/Praise Space/Praise/公众号`（Obsidian 库，唯一正文根目录） |
| `${WEWRITE_DIR}`（Mac 生产副本） | `~/AI-Agent/Claude/capabilities/source/skills/claude-active/wewrite`（其 output/、history.yaml、playbook.md、corpus、lessons、references/exemplars 都 symlink 到 ${CONTENT_ROOT}） |
| 英文稿 | `${CONTENT_ROOT}/crosspost/x/<日期>-<slug>/`，旧稿在 `${CONTENT_ROOT}/output/x/` |
| 旧 box（被替换的 bot） | 文章工作区 `/workspace/articles/<date-slug>/`；风格库 `/home/box/style-library/x-trending/`；尺寸规范 `/home/box/specs/image-sizes/`；配图模板 `/home/box/style-library/article-image-template/` |
| Mac 机器 | 「PraisedeMacBook-Air」，在新 bot 里通过 Computers/ListMachines 重新连接后得到新的 machineId |

## 2. 账号
- X：**@PraiseBuild**（发 X Article 草稿的账号；X API 每 24h 最多建 10 篇草稿）
- GitHub：**PraiseZhu**（本仓库 PraiseZhu/content-workflow，私有）
- 微信公众号：账号名由作者确认；AppID/AppSecret 只在 Mac 上（见 §5）。

## 3. 文章与草稿箱状态（来自 history.yaml，2026-10-22）
| 日期 | 标题 | 状态 | 微信 media_id | X article_id | 正文文件 |
|---|---|---|---|---|---|
| 2026-08-19 | 贵的模型出脑子,便宜的模型干活,有可能一开始你就错了 | draft_created / X:polished | C_eLnWpNiNGCxzIiiWYqbVQbkrYYZmCLjfmZRmY_vXUaSjbJAZ0q39PCue-p5pXa |  | output/2026-08-19-handoff-thin.md |
| 2026-07-28 | 当设计、开发、测试同时开始，设计师在做什么？ | draft_created / X: | C_eLnWpNiNGCxzIiiWYqbWCzrPI-9d5sHEkOjoggLNc1mWSu0-HXVuX6TuwqzNtj |  | output/2026-07-28-design-development-acceptance.md |
| 2026-04-18 | 用 Claude Code 搭完一年知识库,我看清了设计师未来该叫什么 |  / X: |  |  | output/2026-04-18-cursor-figma-uiux-designer-future.md |
| 2026-04-19 | 设计流程没有死,它只是被压扁了 |  / X: |  |  | output/2026-04-19-design-process-flattened.md |
| 2026-05-04 | 我给Claude做了一条"目标驱动链" | draft_created / X: | C_eLnWpNiNGCxzIiiWYqbWpON5fdhCsMl2HuuTA7MQGHlr4gtPlXuCQIu7alBszv |  | output/2026-05-04-Claude-goal-chain-v2.md |
| 2026-05-04 | 我给Claude做了一条"目标驱动链" | draft_created_revision / X: | C_eLnWpNiNGCxzIiiWYqbS7EIXUaGLNXWvpWVkyve_oQDcaoz9rqnCQSTqnlHeou |  | output/2026-05-04-Claude-goal-chain-v2.md |
| 2026-07-27 | 自动审 PR 最重要的能力，是知道什么时候别审 | local_only_wechat_secret_missing / X: |  |  | output/2026-07-27-automation-pipeline-governance.md |
| 2026-10-11 | Grok Bot 自动化 QA 实践经验和复盘 | draft_created / X:pushed | C_eLnWpNiNGCxzIiiWYqbWAhGxOV5fTEhUFss7uBU-xyXZzZCrDIZSHGOHVaYawz | 2109342826853216256 | output/2026-10-11-automated-qa.md |
| 2026-10-16 | 下个月出新模型，你的工作流变好还是变坏？ | draft_created / X:pushed | C_eLnWpNiNGCxzIiiWYqbY2S4zKmdLkmCi54RWl7eJLDAYb8ayT1gnkZspzNXsB1 | 2111184957389656064 | output/2026-10-16-model-upgrade-workflow.md |
| 2026-10-17 | 让 AI 审查 AI，最怕它们互相点头 | draft_created / X:pushed | C_eLnWpNiNGCxzIiiWYqbQsFLI0Tyts1YAE1hxeEhq8jqEmXlEu5hLLjK1mT3YHn | 2111461008090996736 | output/2026-10-17-ai-review-ai.md |

补充事实：
- 10-17《让 AI 审查 AI，最怕它们互相点头》微信已由作者发布；该草稿 thumb 字段读回为空（已不影响）。
- 10-17 公众号草稿箱曾被不明原因清空，原因未查明（无发布记录读取权限，报 48001）。**规则仍是：只新增，不覆盖、不删除。**
- X 草稿无 list/delete API：上表 X article_id 是唯一记录。
- 完整记录：`handoff/history.yaml`（含 x_media_ids、cover 路径等，非密钥）。Mac 上的同名文件是权威版本。
- 全部正文文件清单：`handoff/output-list.txt`、`handoff/crosspost-list.txt`。

## 4. 进行中 / 待作者决定（2026-10-22）
1. **贴图（newspic）推送未实现**：toolkit 没有 `article_type: newspic` 代码路径；已问作者要不要做，未回复。实现要点见 docs/08。
2. **风格库 W43 进度**：10-19 10 组、10-20 11 组、10-21 10 组、10-22 10 组 = **41 组**；周五 10-23 再收 10 组 → 51（目标 ≥50），并出 weekly-2026-W43.md Top 5。旧库在旧 box `/home/box/style-library/x-trending/`（图片未入库；新 bot 从 W44 起在自己的 box 重新积累，或作者手动迁移图片）。
3. **X 泄露过的 Client Secret / Consumer Key 尚未重置**（等作者在 developer.x.com 重置；重置后重跑 x_oauth_setup.py）。
4. 每周 50 组能否稳定达成不确定：X 公开搜索热度偏低时放宽到近 7 天。
5. 作者决定项（永远问）：任何发布/群发；删除或覆盖草稿；没有封面的文章不推；标题、作者本人写的结论句、选题。

## 5. 密钥重新录入（不在仓库里，永远不要提交）
| 用途 | 原来在哪 | 新 bot 怎么做 |
|---|---|---|
| 微信 AppID / AppSecret | Mac：wewrite 目录下 `config.yaml`（也曾用 macOS Keychain）；旧 box：`/home/box/.secrets/wewrite/config.yaml` | 推荐：继续**在 Mac 上执行 publish**（Mac 出口 IP 已在白名单）。若要在新 box 推：作者在新 box 终端自己创建 `~/.secrets/wewrite/config.yaml`（600），并把新 box 出口 IP 加进白名单（否则 40164） |
| X OAuth（client id/secret, access/refresh token） | Mac Keychain：`x-articles-client-id` / `x-articles-client-secret` / `x-articles-access-token` / `x-articles-refresh-token` | Mac 上照常用；新 box 上作者自己跑 `python toolkit/x_oauth_setup.py`（Linux 自动存到 `~/.secrets/x/`，600） |
| X 公开读取 | Grok Bot 内置 X 工具 | 新 bot 连接 X connector |

## 6. 私有数据文件
- `private-config/private-names.txt`、`private-config/blacklist.txt`：真实私名/黑名单 → 安装时拷到 `config/private-names.txt` 与 `${CONTENT_ROOT}/automation/blacklist.txt`
- `early-human/`：作者早期亲手写的 3 篇文章（风格锚点、style-profile 的样本）→ 拷到 `${ARTICLES_DIR}/early-human/`
- `fixtures/`：handoff-thin 中英稿（humanness 英文闸门测试样本）→ `${CONTENT_ROOT}/output/x/`
- `selections/`：选题池 pool.md 与最近选题；`2026-10-17-weekly-topics-v2.md`：最近一周选题
- `third-party/`：第三方范文（WeChat exemplars、X 长文 style-corpus），只作风格参考，不得公开
