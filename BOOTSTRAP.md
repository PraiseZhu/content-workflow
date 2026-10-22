# BOOTSTRAP — 写给接手这份工作的新 Grok Bot

你是一个刚创建的 Grok Bot，在作者（Praise）本人的账号上。读完并执行本文件后，你要能 100% 接手他的写作工作：每周选题、成稿、去 AI 味、出全套中英配图、推公众号和 X 草稿箱（从不发布）、工作日收集 X 配图风格。除了本仓库，你没有其他上下文。**按顺序做，每步都有验证；某步验证失败就停下来修，修不了就告诉作者卡在哪。**

> 铁律（任何时候都成立）：只推草稿，**从不发布/群发**；草稿箱**只新增，不覆盖、不删除**；**没有封面不推**；**不编造**经历和数字；**密钥永远不写进仓库、日志、聊天**——需要时让作者本人在终端输入。

---

## 第 0 步 · 先读（按顺序）
1. `handoff/README.md` — 真实路径、账号、文章与草稿箱状态、进行中事项、密钥在哪（私有，未脱敏）
2. `docs/01-overview.md` → `docs/02` … `docs/11`（全流程；`docs/12-install.md` 第 2 步再看）
3. `config/voice.md` — 作者写作偏好（人读版）；`content/playbook.md` — 写作规则 R001…；`content/automation/image-style.md`、`style-notes.md`（作者改稿留下的风格样本）
4. `knowledge/知识沉淀.md` — 每日工作标准、完成标准、异常处理
5. `skill/wewrite/SKILL.md`、`workflows/article-pipeline/SKILL.md`（真正干活时的操作手册）

验证：能不看文档回答——草稿箱三条铁律是什么；微信方形封面放什么；X 头图尺寸和安全区；header-three 为什么不能用。

## 第 1 步 · 资料卡（profile）
把自己的名称/描述/标题设成 `grokbot/profile.json` 里的值（名称 **知识沉淀**）。没有设置权限就把 JSON 发给作者请他设置。
验证：作者在 bot 列表里看到「知识沉淀」。

## 第 2 步 · 连接器（让作者在设置里连接，你不能代连）
| 连接器 | 用途 | 必需 |
|---|---|---|
| **X**（账号 @PraiseBuild） | 读 X 热门（风格收集、选题）；X 公开读取 | 必需 |
| **GitHub**（PraiseZhu） | 克隆/拉取/推送本私有仓库 | 必需（或作者把 box 上的 `gh auth login` 做好） |
| **作者的 Mac**（Computers / 本地机器） | 读写 `/Users/praise/Obsidian/Praise Space/Praise/公众号`（唯一正文根、history.yaml 权威版）；**在 Mac 上执行微信推草稿**（Mac 出口 IP 在白名单，密钥在 Mac 的 wewrite config.yaml / Keychain） | 强烈建议 |
| Google Calendar / Gmail | 非必需 | 可选 |
验证：`ListMachines` 能看到 Mac；X 工具能 `search` 一条帖子；`gh auth status` 显示 PraiseZhu。

## 第 3 步 · box 安装
```bash
cd /home/box
gh auth status || echo '→ 请作者连接 GitHub 或在 box 终端运行 gh auth login'
gh repo clone PraiseZhu/content-workflow   # 或 git clone https://github.com/PraiseZhu/content-workflow.git
cd content-workflow
bash grokbot/setup.sh          # 建 env 文件、目录、播种内容根、venv、字体、chrome、跑测试、渲染冒烟图
. ~/.content-workflow.env
```
setup.sh 做的事与 `docs/12-install.md` 一致（Linux box 版）。内容根默认在 box 的 `~/content-work/公众号`（Mac 上的 Obsidian 目录仍是权威版本，写正文时以 Mac 为准）。
验证（setup.sh 末尾会打印）：`check_spec OK`；`tests: 81/81 passed`；`pytest … passed`；`[zh] … OK`、`[en] … OK`，并生成 `examples/sample-article/images/zh/cover-wechat-2350x1000.png` 与 `images/en/header-x-2000x800.png`。用 Read 打开封面看一眼。

## 第 4 步 · 记忆
把 `grokbot/memory-seed.md` 里**每一行事实**存成一条记忆（一句话一条，不合并）。
验证：问自己「微信 1:1 封面放什么？」「X 头图安全区？」「能不能覆盖草稿？」——都能从记忆里答对。

## 第 5 步 · 技能
按 `grokbot/skills.md` 保存 9 个技能（article-pipeline、deai-lint、article-image-render、x-trending-style-collection、x-trending-style-weekly-pick、cross-bot-review、html-report-render、wewrite、idea-outline）。
验证：技能列表里能看到这 9 个名字。

## 第 6 步 · 定时任务（Routines）
| 名称 | cron | 时区 | Prompt（整段粘贴） |
|---|---|---|---|
| 每周10个选题 | `4 8 * * 5`（周五 08:04） | Asia/Shanghai | `grokbot/routines/weekly-topics.prompt.txt` |
| X热门长文配图风格收集 | `4 10 * * 1-5`（工作日 10:04） | Asia/Shanghai | `grokbot/routines/daily-style-collection.prompt.txt` |
创建前先确认作者同意启用（旧 bot 上同名任务要由作者停掉，避免重复）。
验证：routine 列表显示两条，下次运行时间分别是最近的周五 08:04 和下一个工作日 10:04（Asia/Shanghai）。

## 第 7 步 · 密钥（只能作者本人做）
告诉作者：
- **微信**：推荐继续在 Mac 上推（Mac 的 wewrite 目录里已有 config.yaml，IP 在白名单）。命令：在 Mac 上 `cd ~/AI-Agent/Claude/capabilities/source/skills/claude-active/wewrite && python3 toolkit/cli.py publish …`。若要在 box 推：作者自己在 box 终端创建 `~/.secrets/wewrite/config.yaml`（照 `skill/wewrite/config.example.yaml`，chmod 600），再把 box 出口 IP（`curl -s ifconfig.me`）加入公众号白名单。
- **X 草稿 API**：Mac Keychain 里已有 `x-articles-*`；在 box 上需要作者自己运行 `cd $WEWRITE_DIR && python toolkit/x_oauth_setup.py`（回调 `http://127.0.0.1:8765/callback`，要在 box 浏览器里登录 @PraiseBuild），token 自动存到 `~/.secrets/x/`（600）。**提醒作者：之前泄露过的 X Client Secret / Consumer Key 还没重置，先在 developer.x.com 重置再授权。**
验证：干跑 `python $WEWRITE_DIR/toolkit/cli.py x-draft <某英文稿> --payload-out /tmp/x.json`（不加 --push 不会建草稿）；微信侧作者同意后才做一次真实推送，并且只推一篇带封面的新草稿。

## 第 8 步 · 接手当前状态
读 `handoff/README.md` §3–§4，然后给作者发一条交接确认：
- 已发/草稿文章清单（§3 表）和 history.yaml 位置；
- 进行中：① 贴图 newspic 推送未实现（问作者要不要做）② 风格库 W43 已 41 组，周五需再收 10 组并出 Top 5 ③ X 密钥待重置 ④ 每周 50 组的稳定性；
- 待作者决定的事项。
验证：作者回复确认。

## 第 9 步 · 自检清单（全部 ✅ 才算接手完成）
- [ ] 读完第 0 步所有文件
- [ ] profile 已设
- [ ] X / GitHub / Mac 已连
- [ ] setup.sh 全绿，冒烟图已看过
- [ ] 记忆已写（memory-seed 每行一条）
- [ ] 9 个技能已存
- [ ] 2 个 routine 已建（Asia/Shanghai）
- [ ] 作者已录入/确认密钥路径（你没有碰过任何密钥值）
- [ ] 交接确认已发

---

## 日常怎么干活（速查）
- **正文存放（硬规则）**：权威内容根是作者 Mac 上的 `/Users/praise/Obsidian/Praise Space/Praise/公众号`（通过 Mac 机器的 Shell/Read 读写）。box 上的 `~/content-work/公众号` 只是工具用的工作副本；Mac 离线时可先写 box，Mac 上线后同步回去，并告诉作者。
- **两份 wewrite**：Mac 上 `~/AI-Agent/Claude/capabilities/source/skills/claude-active/wewrite` 是推微信草稿用的生产副本（有密钥）；仓库里的 `skill/wewrite` 是同一套代码的脱敏版。改工具时两边都改，并在仓库提交。
- 写一篇：`workflows/article-pipeline/SKILL.md` 1→9 步；每篇文章目录见该 skill 的 Article folder；锁定行写 `article.yaml`。
- 去 AI 味：`python deai-lint/deai_lint.py gate <稿> --stage draft --article article.yaml`；`python skill/wewrite/scripts/humanness_score.py <稿>` < 30。
- 配图：写 `render/slots.zh.json` / `slots.en.json` → `python renderer/article-image-template/lib/render.py <文章目录> --check` → 渲染 → `--safe-overlay` 自检。示例：`examples/sample-article/`。
- 预览/推送：`docs/07`、`docs/08`。推送后更新 history.yaml（Mac 上的权威版本）。
- 仓库更新：改了规则/文档就在 `/home/box/content-workflow` 提交并 push（仓库保持私有）。
