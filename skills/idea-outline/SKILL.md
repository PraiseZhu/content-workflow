---
name: idea-outline
description: Use when 用户说「想法提纲」「本周想法提纲」,或要从近期 AI 工作记录(session/commit)提炼公众号选题、中心思想、提纲,或对已产出的选题卡说毙掉/改写/选中/看不懂/翻译味 时。只管选题层;成文/排版/推送归 wewrite。
---

# idea-outline · 想法提纲

从近 7 天的真实工作记录里,提炼出「1 张总纲卡 + ≥6 张分卡」,每张卡 = 选题主张 + 中心思想(单句轴)+ 四维定位 + 提纲。**核心原则:规则存数据(config/),判断存台账(evolution/),SKILL.md 只讲流程——自进化改数据,不改散文。**

## 边界(先读)

- **只管选题层**。成文/去 AI 味/配图/排版/推草稿箱归 `wewrite`(其 `references/weekly-topics.md` 交互段)。
- 取材红线:机制可写、业务数据不可写、公司项目不出真名(memory `feedback_wechat-article-redlines` + blacklist grep)。
- 微信 3.27 条合规:本 skill 定位「AI 辅助真人创作」,产出永远停在「等用户筛选」,不碰发布。
- **规则冻结纪律**:每轮自进化最多落地 1 项;judgment 类永不自动落地。

## 公众号存放合约(硬规则)

- **唯一内容根目录**:`${OBSIDIAN_ROOT}/${CONTENT_ROOT}`。公众号选题、正文、预览、发布记录与复盘只能以此目录中的文件为事实源。
- `runs/<YYYY-MM-DD>/` **只放中间产物**:sessions/聚类稿/人话稿/总纲/gate report。禁止把文章正文、用户终改稿或可发布稿留在 runs。
- 本 skill 的正式产物只写:
  - 周选题:`<root>/selections/YYYY-Www-选题.md`
  - 选题池:`<root>/selections/pool.md`
  - 轨迹与自动化状态:`<root>/automation/`
- 用户选中卡后,本 skill 只把选中状态写回 selections/pool/trajectory;**不直接成文**。进入成文时交给 `wewrite`,由其在 `<root>/output/YYYY-MM-DD-<slug>.md` 创建唯一正文。
- 一篇文章只允许一个可编辑 Markdown。外部 skill/runs 产生了试写正文时,必须在本轮结束前迁入 `<root>/output/` 并移除外部副本;目标文件已存在且内容不同时必须停下做 diff,不得覆盖。
- HTML → `<root>/preview/`;封面/配图 → `<root>/output/assets/<slug>/`;evidence/quality/gate 报告 → `<root>/automation/reports/`。不得与正文平铺在 output 根目录。
- 兼容约束:WeWrite 当前通过 symlink 固定读写 `<root>/output/` 与 `<root>/history.yaml`;未完成 WeWrite 路径迁移前,禁止把 output 改名为 articles。

## 运行前

1. `node scripts/sync-skill-repo.mjs pull`(拿最新规则与台账)。
2. 读 `config/taste-rules.json`、`config/pipeline.json`、`references/taste-profile.md`、`references/output-style.md`、`EVOLUTION.md` 的口味组——这五样是口味与风格的全部事实源。标题/提纲的语言从第一步就按 output-style 写(中文、一段一意、首句即判断),不要等成文才换风格。
3. 建 `runs/<YYYY-MM-DD>/` 作为本轮工作目录。**上下文纪律(pipeline.json#contextBudget):阶段产物一律落文件,主会话只读摘要段,任一阶段要读 >64KB 即停下拆分**——2026-07-26 实测违反此条的代价是 35.9 万 token 崩塌 + 单日 $164。

## 流程(七步)

### 1. 取数(脚本,零 LLM)
用户点名单卡 + 给了视频/长文/字幕 → **跳过本步与第 2 步**,走「外部长论证入口」(见下)。否则:`agent_helper list_sessions {from: 今-7天, to: 今}` 落盘 `runs/<d>/sessions.json`(hasMore 则翻页拿全);`git log --since/--until` 拉各活跃项目 commit。数字口径按周,标 `[近7天]`。

### 2. 过滤(脚本,零 LLM)
`python3 scripts/filter_sessions.py runs/<d>/sessions.json runs/<d>/cluster-input.json`(实测代码,勿重写)。

### 3. 聚类 + 判断挖掘(当前会话模型)
把有效 session 归成 6-12 个事件主题,**必须引用 msgs 数字当证据**。每个候选过:
- **思考阶梯** L1 事实(带数字) → L2 结构性变化 → L3 行业判断(=选题主张)
- **源判断原句**(必填,taste-rules.json#sourceJudgments):从本卡证据源(session 原话/视频字幕/长文)逐字摘 2–4 句 what 层判断,原句照录不改写。L3 是改写,不是源判断;下游成文只能看见这栏,看不见字幕全文
- **深层 5 问** 对照/性质(只是快→降级)/角色/代价/可证伪预测
- **四维定位**(时间/行业/角色/未来;lens=AI 时代的行业规则变化,判据在 taste-rules.json#fourDimensions;缺任一不进 S 级)
- 证据深挖优先「判断时刻」(为什么这么改/争议怎么裁/哪个方案被毙及理由)——亲历是证据样本,不是选题边界;运维黑话(工作树/分支细节)不得刷屏
- 读 trajectory.md 对老线索 +1 印证;baseline 空缺标「⚠️待校准」
本步允许表达粗糙——只负责想对。产物落 `runs/<d>/6a.md`。每张卡必须带 `源判断原句:` 栏。

**外部长论证入口**(点名单卡 + 视频/长文/字幕):跳过 Step 1–2。先读源全文,抽出 2–4 句源判断原句,再按第 3 步其余项出卡。禁止把源论证消化成机制口号后丢掉原句。字幕/长文全文只在本步读一次,不进 6b/成文上下文(contextBudget 红线)。

### 4. 人话改写(跨家族,pipeline.json#models.humanize)
派 Orca worker(kimi-k3/medium),工单:按 taste-rules.json 逐条重写主张/中心思想/标题/提纲,**只改怎么说,禁改判断与数字、禁改「源判断原句」栏**(该栏原句照录);产出**先写** `runs/<d>/6b.md`,回传只当完成信号。worker 不可用 → 主会话自改 + 下一步机械校验兜底,产物标「⚠️ 同家族自改」。

### 5. 总纲提炼(同 worker 通道)
抄轴(只抄各卡中心思想一句)→ 提炼**一句总纲判断**(同受人话闸门约束)→ 建树(每卡填归属分支)→ 验树(taste-rules.json#masterCard.treeRules:禁硬挂/总纲不可被单卡整句替代/不可全挂一支)。产出 `runs/<d>/6c.md`。

### 6. 机械校验(脚本)
```bash
node scripts/check-gates.mjs runs/<d>/6b.md; node scripts/check-gates.mjs runs/<d>/6c.md
bash -c 'PAT=$(mktemp); grep -vE "^\s*(#|$)" <blacklist> > "$PAT"; grep -n -i -f "$PAT" runs/<d>/6b.md runs/<d>/6c.md'  # 脱敏闸门,命中即停
```
**各闸门命令之间一律用 `;` 不用 `&&`**——2026-07-28 实测:check-gates 非零退出把 `&&` 链短路,blacklist 从未真跑却报了零命中。命中 → 打回第 4/5 步重写对应卡,**不许标注解释后放行**。另做复述测试:中心思想读一遍能凭记忆复述,复述不出=打回。每张卡缺 `源判断原句:` 栏或该栏不是 2–4 条独立摘录 → 打回第 3 步,不进人话改写。

### 7. 落盘 + 交付
写 `<公众号根>/selections/YYYY-Www-选题.md`(文件头 30 秒速览表:首行总纲,分卡按归属分支分组);更新 `<公众号根>/automation/trajectory.md`(当周行更新不追加)与 `<公众号根>/selections/pool.md`(按主张语义去重;与上期主张相同 → 有新进展写「续·卡X」,无进展只 +1 印证不占名额)。**禁止写成相对当前 CWD 的 `selections/` 或把正式选题留在 runs。**
**落盘后必须对 selections 终稿再跑一遍 Step 6 的两道闸门**(check-gates + blacklist),报告落 `runs/<d>/gate-report.json`;终稿检出 6b 阶段之外的新增命中 → 打回重写,命中未清零不得声称通过。
**交付消息必须自带**:总纲句+分支 → 速览表 → 逐卡「标题+中心思想+完整提纲」全量 → 推荐前 3+理由 → 选卡指令(「本周选题 选 N」交给 wewrite)。禁「已生成,详见文件」。

## 筛选与口味采样(skill 的进化燃料,一次都不许漏记)

用户对产出的每个动作都要当场入账(`scripts/evo-note.mjs add`):

| 用户动作 | 记账 | 攒够后 |
|---|---|---|
| 毙卡 + 理由 | `--tier taste --quote "<原话>"`,指纹按根因归并 | occurrences≥2 → 升级进 taste-rules.json(改数据+set-status adopted --landed-in) |
| 改写中心思想/标题 | 同上,detail 记 before→after | 同上;正反例同步补进 taste-profile.md |
| **选中一张卡** | taste 正样本(比负样本稀缺,必记) | 累积「什么算好」判据 |
| 说 看不懂/翻译味/太窄 | taste 或 mechanism | 达阈值提案 |
| 流程本身出问题 | `--tier mechanism` | 可当轮落地(见下) |

同指纹返回 `isNew=false` 时只计数,不重复分析。`canPromote=true` 时向用户提一句「这条口味出现第 2 次,我把它升级成硬规则?」——**升级动作要用户点头**。

## 自进化落地规则(抄自 review-pr §8.3,全满足才动)

1. tier=judgment 一律不动,只写提案;拿不准算哪类=judgment。
2. taste 升级只改 `config/taste-rules.json` 数据;mechanism 改脚本必须过 `node --check`,失败即恢复原样降级为提案。
3. **每轮最多自动落地 1 项**(防抖——2026-07-26 一夜八轮修订的教训)。
4. 落地单独 commit(前缀 `evo:`,正文带指纹),然后 `node scripts/sync-skill-repo.mjs push --message "evo: <fingerprint>"`。推送失败不回滚,如实汇报。
5. 被否决过的提案(status=rejected)不再重复提出。

## 台账新陈代谢(2026-07-27 参照 example-org/dash blog skill 实验台消化规则,按本 skill **周更**节奏改装)

台账只有入口没有出口就会重演规则饱和。每轮收尾时顺手过一遍:

1. **open 条目上限 10 条**(只算 taste/judgment 的 open;adopted/landed 是已生效规则的家谱,不算库存)。超限先消化——升级、合并或归档——再收新条目。
2. 升级双轨,一条管深度一条管高度:**同指纹 ≥2 次 → 升级为硬规则**(已有);**跨指纹同主题 ≥3 条 → 合并上移成一条更高阶规则**,新条目 detail 点名来源指纹,子条目 set-status archived。
3. **add 之前先查现有条目**:新观察与某条现有原则精神一致、只是换了个例子 → 不开新指纹,往旧指纹 add 自增计数(或什么都不动——原则已覆盖)。
4. **open 条目 45 天(≈6 个周更期)未更新 lastSeen → set-status archived**。归档不是删除——留档防止同一教训被重新"发现"(这是与 dash 原版「直接删」的有意差异,采的是 review-pr 的留档传统)。
5. **只记可复用的口味/机制教训**;一次性事实变更(改路径、换模型 id、修错别字)直接改 config/文档,不进台账。

## 冲突裁决(两份文件打架时谁赢)

- 口味与风格:以 `config/taste-rules.json`(数据)为准,`taste-profile.md`/`output-style.md` 是它的解释与例证层。
- 执行协议与安全红线:以本 SKILL.md 为准。
- 数据文件与散文冲突 → **数据赢**;发现冲突本身要记一条 mechanism 台账。

## 红线自查(收尾必过)

- [ ] 台账正文无 token/凭证/内部绝对路径/公司真名,选题只写机制不写业务数据
- [ ] 本轮自动落地 ≤1 项;judgment 零自动落地
- [ ] 交付消息含全量「标题+中心思想+提纲」
- [ ] 用户的每次否决/改写/选中都已 evo-note 入账
