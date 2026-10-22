# Skills to save in the new Grok Bot

Save each as a workflow skill (copy the SKILL.md into the bot's workflows folder — on a Grok Bot box that is `/home/box/agent-data/workflows/<name>/SKILL.md` — or use the bot's "save skill" feature with the file's full text).

| Skill name | Source file in repo | Used for |
|---|---|---|
| article-pipeline | `workflows/article-pipeline/SKILL.md` | 一篇文章从选题到草稿箱的全流程 |
| deai-lint | `workflows/deai-lint/SKILL.md` | 去 AI 味闸门（outline/draft/final/author_final） |
| article-image-render | `workflows/article-image-render/SKILL.md` | 按尺寸规范渲染全套中英配图 |
| x-trending-style-collection | `workflows/x-trending-style-collection/SKILL.md` | 工作日风格收集 |
| x-trending-style-weekly-pick | `workflows/x-trending-style-weekly-pick/SKILL.md` | 周五 Top 5 |
| cross-bot-review | `workflows/cross-bot-review/SKILL.md` | 另一个 bot 交叉评审（可选） |
| html-report-render | `workflows/html-report-render/SKILL.md` | HTML → 长图/PDF（复盘报告等） |
| wewrite | `skill/wewrite/SKILL.md` (+ whole `skill/wewrite/` dir stays in the repo) | 排版、微信草稿、X 草稿 CLI、写作规范 |
| idea-outline | `skills/idea-outline/SKILL.md` | 选题 → 提纲（含 X 长文骨架 output-style.md） |

Path note: these files reference repo paths like `renderer/…`, `specs/image-sizes/…`, `deai-lint/…`; they resolve relative to `$CW_REPO` (the clone). Always `cd $CW_REPO` and `. ~/.content-workflow.env` before running commands.

Copy command (run on the box after cloning):
```bash
. ~/.content-workflow.env
for d in "$CW_REPO"/workflows/*/ "$CW_REPO"/skills/idea-outline/; do n=$(basename "$d"); mkdir -p /home/box/agent-data/workflows/$n; cp "$d/SKILL.md" /home/box/agent-data/workflows/$n/SKILL.md; done
mkdir -p /home/box/agent-data/workflows/wewrite && cp "$CW_REPO/skill/wewrite/SKILL.md" /home/box/agent-data/workflows/wewrite/SKILL.md
```
