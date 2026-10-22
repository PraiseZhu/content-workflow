# 07 · 中英交叉核对与预览 Cross-check & preview

## 交叉核对（预览前必须做）
- 中英：同样的论点、数字、图、锁定行；
- 图文：图上文字与正文一致（逐字）；
- 私名：`deai_lint.py` 的 `p.leak.names` + 人工 grep `config/private-names.txt`；
- 列出所有不一致，修完才进入预览。

## 预览
- 中文：`python3 skill/wewrite/toolkit/cli.py preview <zh.md> --theme <theme> --no-open -o ${CONTENT_ROOT}/preview/<date>-<slug>.html`
- 英文：`python3 skill/wewrite/toolkit/cli.py x-draft <en.md> --stdout`（或 `--payload-out` 干跑查看 X Article JSON）；`deai_lint.py lint --x` 确认无原始 markdown。
- 作者看预览，有意见直接改终稿文件（一篇文章一个正文，不另存 -v2/-final）。

可选：[workflows/cross-bot-review/SKILL.md](../workflows/cross-bot-review/SKILL.md)（另一个 bot 交叉评审）。
