---
title: 公众号工作区
created: 2026-04-18
updated: 2026-07-28
tags:
  - workspace
  - wewrite
  - wechat
---

# 公众号工作区

这是公众号内容的**唯一根目录**。选题、正文、预览、发布记录和写作复盘都以这里的文件为准；`~/.claude/skills/**/runs/` 只能保存中间产物和校验报告，不能保存另一份可编辑正文。

## 内容流转

```text
selections/pool.md
  → selections/YYYY-Www-选题.md
  → output/YYYY-MM-DD-<slug>.md
  → 用户修改 / 校对 / 排版
  → 微信草稿箱或发布
  → history.yaml 更新发布与复盘记录
```

正文从草稿到发布始终使用 `output/` 内同一个 Markdown 文件，不再复制 `draft-v2`、`final`、`publish` 等多份正文。确实需要保留发布格式副本时，必须在 `history.yaml` 的同一文章记录里声明，不把它当成另一篇文章。

## 目录职责

| 路径 | 唯一职责 | 可以放 | 不应放 |
|------|----------|--------|--------|
| `selections/` | 选题阶段 | 选题池、周选题、被选中的卡片 | 正文、HTML、封面 |
| `output/` | 正文事实源（兼容 WeWrite 当前路径） | 一篇文章一个 Markdown | 证据报告、质量报告、HTML、散落图片 |
| `output/Attachments/` | 旧文章附件（兼容现有 Obsidian 链接） | 旧图片、视频 | 新文章正文 |
| `output/assets/` | 新文章素材 | 封面、配图，建议按文章 slug 分目录 | Markdown 正文 |
| `preview/` | 可再生预览 | HTML 预览 | 权威正文 |
| `automation/` | 选题与写作流水线的状态、规则和报告 | trajectory、baseline、报告、归档 | 正文 |
| `corpus/` | 外部语料 | 原始参考资料 | 用户正文 |
| `exemplars/` | 范文风格库 | 范文与索引 | 用户正文 |
| `lessons/` | 用户写作复盘 | 经确认的长期写作规则 | 临时改稿意见 |
| `history.yaml` | WeWrite 兼容元数据账本 | 生成/发布/复盘记录 | 正文内容 |
| `playbook.md` | WeWrite 写作规则 | 从用户修改中沉淀的规则 | 单篇草稿 |

## 正文命名与状态

正文统一命名：

```text
output/YYYY-MM-DD-<english-slug>.md
```

新正文 frontmatter 至少包含：

```yaml
title: "文章标题"
date: 2026-07-28
updated: 2026-07-28
status: draft       # draft | editing | ready | published | archived
topic_id: W32-05    # 没有选题卡时可为 null
slug: design-development-acceptance
published_at: null
published_url: null
tags: []
```

状态含义：

| 状态 | 含义 |
|------|------|
| `draft` | AI 初稿或结构稿，尚未由用户终改 |
| `editing` | 用户正在修改；自动化不得覆盖 |
| `ready` | 内容定稿，等待排版或推送 |
| `published` | 已发布或已进入确认的草稿箱，填写 URL/时间/媒体 ID |
| `archived` | 历史文章，仅保留，不再进入当前生产队列 |

## 唯一正文规则

1. 一篇文章只允许一个可编辑 Markdown 正文。
2. `selections/` 只记录“写什么”，`output/` 才记录“文章怎么写”。
3. HTML、封面和质量报告都不能反向成为正文来源。
4. 用户开始修改后，将 `status` 改为 `editing`；AI 后续修改必须在同一文件上进行。
5. 发布只更新 frontmatter 和 `history.yaml`，不复制另一份“最终稿”。
6. 若外部 runs 中生成了正文，任务完成前必须迁回 `output/` 并移除外部正文副本。

## 当前兼容关系

WeWrite 当前仍以 `output/` 和 `history.yaml` 为固定接口，因此本轮保留这两个名称：

```text
~/.claude/skills/wewrite/output       -> 本目录/output/
~/.claude/skills/wewrite/history.yaml -> 本目录/history.yaml
~/.claude/skills/wewrite/playbook.md  -> 本目录/playbook.md
```

不要删除或改名这些路径。未来若把正文目录改为 `articles/`，必须先修改并验证 WeWrite 的路径契约，不能只移动文件。

## 每篇文章的最小收尾动作

- [ ] 正文只存在于 `output/` 一处
- [ ] frontmatter 的 `status` 与真实阶段一致
- [ ] `history.yaml` 有对应记录且路径唯一
- [ ] HTML 位于 `preview/`
- [ ] 封面/配图位于 `output/assets/<slug>/` 或兼容附件目录
- [ ] evidence / quality / gate 报告位于 `automation/reports/`
- [ ] 发布后补 `published_at`、`published_url` 或微信媒体 ID
