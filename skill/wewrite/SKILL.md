---
name: wewrite
description: |
  微信公众号内容全流程助手：热点抓取 → 选题 → 框架 → 内容增强 → 写作 → SEO → 视觉AI → 排版推送草稿箱。
  触发关键词：公众号、推文、微信文章、微信推文、草稿箱、微信排版、选题、热搜、
  热点抓取、封面图、配图、写公众号、写一篇、主题画廊、排版主题、容器语法。
  也覆盖：markdown 转微信格式、学习用户改稿风格、文章数据复盘、风格设置、
  主题预览/切换、:::dialogue/:::timeline/:::callout 容器语法。
  不应被通用的"写文章"、blog、邮件、PPT、抖音/短视频、网站 SEO 触发——
  需要有公众号/微信等明确上下文。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebSearch
  - WebFetch
---

# WeWrite — 公众号文章全流程

## 行为声明

**角色**：用户的公众号内容编辑 Agent。

**模式**：
- **默认全自动**——一口气跑完 Step 1-8，不中途停下。只在出错时停。**封面除外**：Step 6 必须先出 3 张候选等用户选定构图，确认后再出微信/X 两张成品，不得自选封面。**英语/X 除外**：主管道 Step 7 同步 X 前必须先英语成文 + 去 AI 味；走「本周选题」时再加确认点④⑤，不得把英语压缩成发布前一次性重写。
- **交互模式**——用户说"交互模式"/"我要自己选"时，在选题/框架/配图处暂停。

**降级原则**：每一步都有降级方案。Step 1 检测到的降级标记（`skip_publish`、`skip_image_gen`）在后续 Step 自动生效，不重复报错。

**进度追踪**：主管道启动时，用 TaskCreate 为 8 个 Step 创建任务。每开始一个 Step 标记 in_progress，完成后标记 completed。用户可随时看到当前进度。

**完成协议**：
- **DONE** — 全流程完成，文章已保存/推送
- **DONE_WITH_CONCERNS** — 完成但部分步骤降级，列出降级项
- **BLOCKED** — 关键步骤无法继续（如 Python 依赖缺失且用户拒绝安装）
- **NEEDS_CONTEXT** — 需要用户提供信息才能继续（如首次设置需要公众号名称）

**路径约定**：本文档中 `{skill_dir}` 指本 SKILL.md 所在的目录（即 WeWrite 的根目录）。

## 公众号存放合约(硬规则)

- **唯一内容根目录**:`${CONTENT_ROOT}`。正文、选题、预览、发布记录和写作复盘都以这里为事实源。
- `{skill_dir}/output`、`history.yaml`、`playbook.md`、`corpus`、`lessons`、`references/exemplars` 当前均通过 symlink 落到该 Obsidian 根目录。不得把同一正文另存到 skill 目录、`runs/`、临时目录或其他项目。
- **一篇文章一个正文**:`<root>/output/YYYY-MM-DD-<slug>.md`。从 draft → editing → ready → published 只改同一文件和 frontmatter,禁止复制 `-v2`/`-final`/`-publish` 作为新的权威正文。平台专用的发布格式副本若无法避免,必须在 history 同一文章记录的 `publish_file` 声明,且不得反向覆盖正文。
- 正文 frontmatter 至少包含:`title,date,updated,status,topic_id,slug,published_at,published_url,tags`。用户开始终改后标 `status: editing`,自动化不得覆盖;排版前标 `ready`;发布后标 `published`。
- 产物分流:
  - Markdown 正文 → `<root>/output/`
  - 封面/配图 → `<root>/output/assets/<slug>/`(旧文 `output/Attachments/` 仅兼容,新文不再使用)
  - HTML 预览 → `<root>/preview/`
  - evidence/quality/gate report → `<root>/automation/reports/<slug>/`
  - 选题 → `<root>/selections/`;WeWrite 不在 selections 中写正文
- 开始写作前,若目标正文已存在且 `status: editing|ready|published`,必须读取并在同一文件上按用户要求修改;不得新建同题副本。目标存在但内容来源不一致时停下做 diff。
- 收尾前全局检查同 slug/同 topic_id 的 Markdown 正文;存在多个可编辑副本时,本轮不得声称完成,必须保留 Obsidian output 版本并清理或归档外部副本。
- 兼容约束:当前 WeWrite 固定使用 `output/` 与 `history.yaml`;修改 skill 代码并完成迁移验证前,禁止把 output 改名为 articles。

**Onboard 例外**：Onboard 是交互式的（需要问用户问题），不受"全自动"约束。Onboard 完成后回到全自动管道。

**辅助功能**（按需加载，不在主管道内）：
- 用户说"重新设置风格" → `读取: {skill_dir}/references/onboard.md`
- 用户说"学习我的修改" → `读取: {skill_dir}/references/learn-edits.md`。支持两种来源：
  - **本地修改**（默认）：用户在 `output/` 的 markdown 文件中修改
  - **微信草稿箱同步**：`python3 {skill_dir}/scripts/learn_edits.py --from-wechat`，自动从草稿箱拉回最新内容，与本地原文做纯文本 diff
- 用户说"学习排版"/"学排版" → `python3 {skill_dir}/scripts/learn_theme.py <url> --name <name>`，用户需提供一个公众号文章 URL 和主题名称。提取完成后提示用户设置 `style.yaml` 的 `theme` 字段。
- 用户说"学习这篇文章"/"导入范文" + URL → `python3 {skill_dir}/scripts/fetch_article.py <url> -o /tmp/article.md && python3 {skill_dir}/scripts/extract_exemplar.py /tmp/article.md -s <账号名>`，从公众号文章 URL 提取正文并导入范文库。支持三级降级（requests → Playwright → 手动 HTML）。
- 用户说"看看文章数据" → `读取: {skill_dir}/references/effect-review.md`
- 用户说"本周选题"/"本周选题 选 N" → `读取: {skill_dir}/references/weekly-topics.md`。周选题自动化的交互段:读最新 selections 选题卡 → 用户观点主导重构提纲(✋确认①,中英共用) → 证据包中文成文(✋确认②) → 换家族去 AI 味(中文) → image-gen 配图(微信 16:9 + X 5:2,构图共用) + claude-warm 排版 → 两层脱敏 grep 硬门 → 推草稿箱 → open 公众号后台等用户发布(✋确认③) → 英语母语成文 + 换家族去 AI 味(英语) → ✋确认④英语全文 → publish-x 清洗 → open X 编辑器等用户发布(✋确认⑤)
- 用户说"检查一下"/"自检"/"这篇文章怎么样" → 对最近一篇生成的文章（或用户指定的文章）执行自检，输出生成报告：

  **第一部分：生成档案**（告诉用户这篇文章是怎么来的）
  1. 读取 `history.yaml` 最近一条记录，提取：
     - 使用的框架类型 + 写作人格
     - 激活的维度随机化组合
     - 素材采集来源（WebSearch 还是降级到 LLM）
     - 内容增强策略（角度发现/密度强化/细节锚定/真实体感）
     - 范文风格库是否命中（用了哪几篇 exemplar，还是 fallback 到种子）
     - playbook 中生效的规则条数
  2. 如果 history.yaml 无记录或用户指定了外部文章 → 跳过此部分，提示"这篇文章不是 WeWrite 生成的，只做质量检查"

  **第二部分：质量检查**（告诉用户哪里还能改）
  1. `python3 {skill_dir}/scripts/humanness_score.py {article_path} --json`。英语稿(`lang: en` 或正文几乎无 CJK)必须再跑 `--en-gate`;复合分是中文尺子,不得拿来比较中英「谁更 AI」。
  2. Agent 解读 JSON 中每项得分，翻译为用户可操作的建议，格式：
     - 每条建议定位到具体段落或句子（"第 3 段连续 4 句长度接近"）
     - 给出具体改法（"建议把第 3 句拆成两个短句"、"这里可以加一句你自己的感受"）
     - 按影响度排序，最多 5 条
  3. 如果所有项得分都不错 → "这篇文章质量不错，建议在编辑锚点处加入你的个人内容就可以发了。"

  **输出格式**：自然语言报告，不输出 JSON 或分数（用户不需要看数字）
- 用户说"更新"/"更新 WeWrite"/"升级" → 在 `{skill_dir}` 执行 `git pull origin main`，完成后告知版本变化

---

## 主管道（Step 1-8）

主管道启动时，创建以下 8 个任务用于进度追踪：

```
TaskCreate: "Step 1: 环境 + 配置"
TaskCreate: "Step 2: 选题"
TaskCreate: "Step 3: 框架 + 素材"
TaskCreate: "Step 4: 写作"
TaskCreate: "Step 5: SEO + 验证"
TaskCreate: "Step 6: 视觉 AI"
TaskCreate: "Step 7: 排版 + 发布"
TaskCreate: "Step 8: 收尾"
```

每开始一个 Step → TaskUpdate status=in_progress。完成 → TaskUpdate status=completed。

---

### Step 1: 环境 + 配置

**1.1 环境检查**（静默通过或引导修复）：

```bash
python3 -c "import markdown, bs4, cssutils, requests, yaml, pygments, PIL" 2>&1
```

| 检查项 | 通过 | 不通过 |
|--------|------|--------|
| `config.yaml` 存在 | 静默 | 引导创建，或设 `skip_publish = true` |
| Python 依赖 | 静默 | 提供 `pip install -r requirements.txt` |
| `wechat.appid` + `secret` | 静默 | 设 `skip_publish = true` |
| `image.api_key` 或 `image.providers` 至少一项有效 | 静默 | 设 `skip_image_gen = true` |
| `references/exemplars/index.yaml` | 静默 | 提示："范文库为空。如果你有已发布的文章（markdown），可以说**'导入范文'**建立风格库，写出来的文章会更像你。没有也不影响使用。" |

**1.2 版本检查**（静默通过或提醒）：

```bash
cd {skill_dir} && git fetch origin main --quiet 2>/dev/null
```

比对本地 `{skill_dir}/VERSION` 与远程 `git show origin/main:VERSION`：
- 相同 → 静默通过
- 不同 → 提示用户："WeWrite 有新版本可用（当前 X → 最新 Y），说「更新」即可升级。"**不阻断流程**，继续 1.3
- git 不可用（无 .git 目录或 fetch 失败）→ 静默跳过

**1.3 加载风格**：

```
检查: {skill_dir}/style.yaml
```

- 存在 → 提取 `name`、`topics`、`tone`、`voice`、`blacklist`、`theme`、`cover_style`、`author`、`content_style`
- 不存在 → `读取: {skill_dir}/references/onboard.md`，完成后回到 Step 1

如果用户直接给了选题 → 跳到 Step 3（仍需框架选择和素材采集，不可跳过）。

---

### Step 2: 选题

**2.1 热点抓取**：

```bash
python3 {skill_dir}/scripts/fetch_hotspots.py --limit 30
```

**降级**：脚本报错 → WebSearch "今日热点 {topics第一个垂类}"

**2.2 历史分析 + SEO**：

```
读取: {skill_dir}/history.yaml（不存在则跳过）
```

```bash
python3 {skill_dir}/scripts/seo_keywords.py --json {关键词}
```

历史分析（有 stats 数据时）：
- 统计哪种 `framework` 的文章表现最好（阅读量/分享率）→ 推荐框架时加权
- 统计哪种 `enhance_strategy` 的文章表现最好 → 增强策略选择时参考
- 近 7 天已写的关键词降分（去重）

**降级**：SEO 脚本报错 → LLM 判断；history 无 stats → 跳过效果分析，仅做去重

**2.3 生成选题**：

```
读取: {skill_dir}/references/topic-selection.md
```

生成 **10 个选题**，其中：
- **7-8 个热点选题**：基于 2.1 的热点，按 topic-selection.md 规则评分
- **2-3 个常青选题**：不依赖热点，从用户的 `topics` 领域生成长尾内容（教程/方法论/经验总结/工具推荐），标注为"常青"。适合 content_style 为干货型/测评型的用户

每个选题含标题、评分、点击率潜力、SEO 友好度、推荐框架。

- 自动模式 → 选最高分
- 交互模式 → 展示全部，等用户选

---

### Step 3: 框架 + 素材

**3.1 框架选择**：

```
读取: {skill_dir}/references/frameworks.md
```

7 套框架（痛点/故事/清单/对比/热点解读/纯观点/复盘），自动选推荐指数最高的。

**3.2 素材采集 + 内容增强**（合并执行，共用搜索结果）：

```
读取: {skill_dir}/references/content-enhance.md
```

根据 3.1 选定的框架类型，一次搜索同时完成素材采集和内容增强：

| 框架 | 搜索策略 | 从结果中提取 |
|------|---------|-------------|
| 热点解读 / 纯观点 | `"{关键词} site:mp.weixin.qq.com OR site:36kr.com"` + `"{关键词} 观点 OR 评论"` | 真实素材（数据/引述）**+** 已有文章的主流观点（供角度发现） |
| 痛点 / 清单 | `"{关键词} 教程 OR 工具 OR 实操"` + `"{关键词} 数据 报告"` | 真实素材 **+** 具体工具名/步骤/参数（供密度强化） |
| 故事 / 复盘 | `"{人物/事件} 采访 OR 专访 OR 细节"` + `"{关键词} 数据 报告"` | 真实素材 **+** 时间锚/数字锚/对话锚/感官锚（供细节锚定） |
| 对比 | `"{方案A} vs {方案B} 评测 OR 体验"` + `"{方案A OR 方案B} 踩坑 OR 缺点 site:v2ex.com OR site:zhihu.com"` | 真实素材 **+** 真实用户评价和踩坑信息（供真实体感） |

每次搜索 2 轮，从结果中**同时**提取：
1. **素材**：5-8 条真实素材（具名来源 + 具体数据/引述/案例）。**禁止编造**。
2. **增强材料**：按 content-enhance.md 对应策略的要求提取（角度/密度要点/细节/用户声音）。

两者并入框架大纲，一起传入 Step 4 写作。

**降级**：WebSearch 不可用 → 用 LLM 训练数据中可验证的公开信息。但需告知用户："素材采集未能使用 WebSearch，建议在编辑锚点处多加入你自己的内容。"密度强化不依赖搜索，始终执行。

---

### Step 4: 写作

```
读取: {skill_dir}/references/writing-guide.md
读取: {skill_dir}/playbook.md（如果存在，按 confidence 分级执行）
读取: {skill_dir}/history.yaml（最近 3 篇的 dimensions + closing_type 字段）
读取: {skill_dir}/references/exemplars/index.yaml（如果存在）
```

**4.1 维度随机化**：

从以下维度池随机激活 2-3 个维度，让每篇文章的表达方式不同。如果 history.yaml 有最近 3 篇的 `dimensions` 字段，避免使用相同组合。

| 维度 | 选项 |
|------|------|
| 叙事视角 | 第一人称亲历 / 旁观者分析 / 对话体 / 自问自答 |
| 时间线 | 正序 / 倒叙 / 插叙 |
| 类比域 | 作者自己的领域（设计 / 摄影 / 研发流程）；全文最多 1 个类比，没有合适的就不用（2026-10-12：不再随机抽类比域） |
| 情绪基调 | 克制冷静 / 直接评论（每个 H2 有代价的判断，不唱苦情戏，见 playbook R001） |
| 节奏 | 长叙述慢推 / 长短交替 / 慢开头快收尾（不用"短句密集"，连续超短句是 AI 味） |

**4.2 加载写作人格**：

```
读取: {skill_dir}/personas/{style.yaml 的 writing_persona 字段}.yaml
如果 style.yaml 没有 writing_persona 字段 → 默认 midnight-friend
```

人格文件定义了：语气浓度、数据呈现方式、情绪弧线、段落节奏、不确定性表达模板等。作为写作的硬性约束执行。

**优先级**：playbook.md（confidence ≥ 5 的规则）> persona > 范文风格 > writing-guide.md。writing-guide 是底线（基础写作规范），范文提供风格示范（句长节奏、情绪表达方式），persona 在此基础上特化风格参数（语气浓度、数据呈现），playbook 中高置信度规则是用户个性化的最终覆盖。playbook 中 confidence < 5 的规则作为软性参考。

**4.3 范文风格注入**（有 `references/exemplars/index.yaml` 时执行）：

从 index.yaml 筛选 category 匹配当前框架类型的范文，取 top 3。读取对应 .md 文件的片段内容。

在写作 prompt 中注入：

> 以下是该公众号风格的真实段落示例，模仿其句长节奏、情绪强度和口语化程度：
>
> 【开头风格】
> {exemplar_1 的开头钩子段}
>
> 【情绪段风格】
> {exemplar_2 的情绪高峰段}
>
> 【转折风格】
> {exemplar_2 或 exemplar_3 的转折/自纠段（如有）}
>
> 【收尾风格】
> {exemplar_3 的收尾段}

Category 映射规则：

| 框架类型 | exemplar category |
|----------|-------------------|
| 痛点型 | tech-opinion |
| 故事型 / 复盘型 | story-emotional |
| 清单型 / 对比型 | list-practical |
| 热点解读型 / 纯观点型 | hot-take |
| 其他 | general |

如果匹配到的范文不足 3 篇，用 general category 补足。

**Fallback（范文库为空时）**：读取 `{skill_dir}/references/exemplar-seeds.yaml`，从每个段落类型中随机选 1 个注入 prompt。种子段落只示范人类写作的结构模式（句长方差、情绪锐度、自我纠正、非总结式收尾），不携带特定风格。注入时使用：

> 以下是人类写作的结构模式示例，注意模仿其句长节奏和情绪表达方式（不要模仿具体内容或风格）：
>
> 【开头模式】{seeds.opening_hooks 随机 1 个}
>
> 【情绪段模式】{seeds.emotional_peaks 随机 1 个}
>
> 【转折模式】{seeds.transitions 随机 1 个}
>
> 【收尾模式】{seeds.closings 随机 1 个}

建库命令：`python3 {skill_dir}/scripts/extract_exemplar.py article.md`

**4.4 写文章**：
- H1 标题（20-28 字） + H2 结构，1500-2500 字
- **素材 + 增强约束**：Step 3.2 的素材和增强材料分散嵌入各 H2 段落。增强策略的核心输出（角度/密度要点/细节/用户声音）必须贯穿全文，不只装饰性出现一次
- **写作人格**：按 4.2 加载的人格参数写作（数据呈现方式、个人声音浓度、不确定性表达等）
- **收尾方式**：persona 的 `closing_tendency` 仅作为倾向参考。根据文章内容和情绪弧线自行判断最自然的收尾方式。如果 history.yaml 中最近 3 篇有 `closing_type` 字段，避免使用相同的收尾类型
- **写作规范**：writing-guide.md 中的基础规则（分档禁用词、句式骨架禁区、真实锚定、中英之间不加空格等）在初稿阶段生效
- 2-3 个编辑锚点：`<!-- ✏️ 编辑建议：在这里加一句你自己的经历/看法 -->`；需要作者亲历、数字的地方写 `[待作者补：…]`，不替作者编
- 可选容器语法：`:::dialogue`、`:::timeline`、`:::callout`、`:::quote`

保存到 `{skill_dir}/output/{date}-{slug}.md`(symlink 后实际位于 Obsidian 公众号根的 `output/`)。写入前检查同名文件/frontmatter 状态:不存在才新建;已存在则在同一正文继续,不得生成 `-v2`/`-final` 平行副本。新建时写入存放合约规定的完整 frontmatter。

**4.5 快速自检**（写完后立即执行，减少 Step 5 重写概率）：

对初稿做 5 项快速扫描，**当场修复**，不留到 Step 5：

**写作层面**：
1. **禁用词扫描**：检查 writing-guide.md 2.1 的禁用词列表，命中的直接替换
2. **句式骨架**：扫 writing-guide 2.2（"不是…而是" 0 次、对照变体 ≤1、格言、强凑三项、预告句、段尾盖章），命中就直接改写成陈述

**内容层面**：
3. **开头**：第一段是否直接给出问题或判断？如果是背景铺垫或演场景（R001），就重写
4. **增强贯穿**：增强策略的核心输出是否只出现在一段？如果是，在其他 H2 中补充
5. **判断句检查**（2026-10-12 替换"金句检查"）：每个 H2 是否至少有 1 句有代价的具体判断？没有就补，缺料就标 `[待作者补]`。不补对仗金句

LLM 自行完成，不需要调用脚本。

---

### Step 5: SEO + 验证

```
读取: {skill_dir}/references/seo-rules.md
```

**5.1 SEO**：3 个备选标题 + 摘要（≤40 字）+ 5 标签 + 关键词密度优化

**5.2 质量验证**（两个维度，每项逐一检查）：

**A. 写作质量**（writing-guide.md 基础规则）：

| 检查项 | 标准 | 规则 |
|--------|------|------|
| 句长方差 | 不连续 3 句长度相近；没有连续超短句堆叠 | 1.1 |
| 语体 | 书面技术语为主，口头禅全文 ≤1 次（取代"词汇温度"配额） | 1.2 |
| 段落节奏 | 各 H2 详略不均、内部结构不重复 | 1.3/1.6 |
| 立场与代价 | 每个 H2 ≥1 处有代价的判断（取代"负面情绪 ≥2 处"） | 1.4 |
| 禁用词 | 硬禁 = 0；句首禁用 = 0；限 1 次的词 ≤1；无同段扎堆 | 2.1 |
| 句式骨架 | "不是…而是" = 0；对照变体 ≤1；格言 = 0；无预告句 | 2.2 |
| 格式 | 中英/数字之间无空格；小标题不编号；无公司/项目名；无 AI 声明 | 格式要求 |
| 真实锚定 | 每个 H2 ≥ 1 条真实素材，零编造 | 3.1 |
| 具体性 | 每 500 字 ≥ 2 处具体细节 | 3.2 |

**B. 内容质量**（基于 Step 3.2 的增强策略检查）：

| 检查项 | 标准 | 适用框架 |
|--------|------|---------|
| 增强贯穿 | 增强策略的核心输出（角度/密度/细节/体感）在全文可见，不只出现在一段 | 所有 |
| 开头 | 第一段直接给问题或判断（不是背景铺垫，不演场景） | 所有 |
| 判断密度 | 每个 H2 至少 1 处有代价的具体判断（取代"金句密度"；对仗金句不算） | 所有 |
| 操作密度 | 每个 H2 有可操作要点（工具/步骤/参数） | 痛点/清单 |
| 角度锐度 | 核心观点能引发同意或反对，不是"两面都有道理" | 热点解读/纯观点 |
| 场景感 | 至少 2 处有时间/地点/对话等画面细节 | 故事/复盘 |
| 真实声音 | 至少 1 处引用真实用户评价或体验 | 对比 |

不通过 → **定向修复**：只替换不达标的具体句子/段落，不动已通过的部分。每轮最多改 3 处，改完立即重新检查该项。2 轮仍不过 → 标注跳过，继续下一项。

**5.3 脚本辅助验证**（补充 5.2 的逐项检查）：

Agent 在 5.2 检查过程中同步完成综合评估（各 H2 之间的语气差异度、信息密度的高低交替、段落间的节奏变化、整体阅读流畅度），产出 0-1 分数。

```bash
python3 {skill_dir}/scripts/humanness_score.py {article_path} --json --tier3 {agent_tier3_score}
```

解读 JSON 中 `composite_score`（0=质量高, 100=问题多）和 `de_ai_gate`：
- < 30 **且** `de_ai_gate.ok = true` → 通过，继续 5.4
- `de_ai_gate.ok = false` → 不管总分多少，先按 `de_ai_gate.blocking` 和 `tier2b_de_ai_lint` 给出的行号定点修
- `param_scores` 里已不含 broken_sentences / self_correction / word_temperature_mix / negative_emotion_ratio（2026-10-12 起只报告不计分），不要为了这几项加"嗯。"、表演纠错或负面情绪
- 30-50 → 查看 `param_scores` 中最低分的 1-2 项，只修复对应的具体句子（不重写整段），改完重新打分。1 轮即可
- \> 50 → 取 `param_scores` 最低的 2-3 项，逐项定向修复（每项只改最相关的 1-2 处），最多 2 轮。仍 > 50 则标记 DONE_WITH_CONCERNS 继续

配了风格基线（`references/style-baseline.yaml` 里填了 3–5 篇作者旧文）的话，加 `--baseline` 参数，看 `style_baseline.off_baseline` 里列出的偏离项。还没配就跳过。

**5.4 去AI味流程**（正式稿 → 推送之间，必须执行）：按 writing-guide.md「去AI味流程」的 8 步执行：冻结稿子并列事实账本 → 反向大纲 → 作者补料 → 机检 → 换模型家族独立审稿（只标问题，不重写）→ 定点改写 + 残留二扫 → 朗读 → 术语与排版 → diff 回灌 playbook。第 2 步"补料"必须由作者本人完成，AI 不代写。X 英文版从大纲直接用英文写，不翻译中文终稿，机检改跑 `--en-gate`。

---

### Step 6: 视觉 AI

**如果 `skip_image_gen = true`** → 只执行 6.1。

```
读取: {skill_dir}/references/visual-prompts.md
读取: {skill_dir}/references/image-specs.md   # 固定导出尺寸/安全区/格式大小（每篇必按此表）
```

**6.1 实体提取**：从终稿中提取 3-5 个**具体实体**（人物、产品名、场景、数据点、行业术语）。后续所有提示词必须包含至少 2 个实体。

**6.2 封面生成（两步硬停，2026-08-19）**：
1. 先出 3 张 **16:9** 候选，只给用户选构图。未确认不得出成品、不得推草稿。
2. 用户选定后，按语言出成品（2026-10-17 更新，取代旧的「微信+X 两张」）：
   - **中文套（只给微信，X 永不出中文版）**= 微信头条封面 2.35:1 `cover-wechat-2350x1000.png` + **方形封面 1:1 `cover-square-1000x1000.png`** + **贴图封面 3:4 `cover-tietu-1080x1440.png`**（图片消息 newspic 首图，用于「贴图」双列瀑布流；中文标题须在缩略图下可读，规格见 image-specs.md「贴图」节，2026-10-18）+ 内文配图。中文套**不出** X header。
   - **英文套（只给 X）**= X Article 封面 `header-x-2000x800.png`（5:2，关键内容只放安全区 x200–1800 / y160–680；旧 1500×600 停用）+ 英文内文配图 1600×900。
   - **所有成品尺寸、安全区、格式与大小上限以 `references/image-specs.md` 为准（固定导出套装，2026-10-17）**；与本节冲突时以该文件为准。
   - **同一语言的封面变体必须携带相同元素**（标题、tag、主体/目标框、主视觉）：比例紧张时只允许缩放/重新排位，**不得删内容**。唯一例外是方形封面（见下）。
   - 生成 X 版若模型不支持目标比例，用选定封面作参考图按目标比例重绘；禁止 PIL 补边/裁切硬改比例。
3. **方形封面 1:1（必出）**：用于公众号主页、聊天/朋友圈分享卡片、次条，实际显示约 120–383px。规格：最低 383×383（常用 500×500），**导出 1000×1000** 保证清晰。**方形不放任何标题文字**（无主标题、无副标题、无 tag、无清单/导航行）：只留 HUD 背景母题（底图色调、网格、橙色横线）+ 一个放在具体主体上的橙色目标框（可带一个小 chip，如 `P1 · VERIFYING`）+ **一个核心符号/数字**（如「P0/P1」「8/8」），放大作为唯一主元素（这是对「同元素」规则的唯一豁免——方形显示太小）。
   - **可读性检查（硬性）**：把方形图缩到 200px 和 120px 各看一次，核心符号/数字必须一眼可读、目标框可辨；不可读就放大核心元素/删次要元素再出。
   - 推草稿时用 `--cover-square` 传入（见 Step 8）：微信 draft/add 只有一个 `thumb_media_id`，方形只能通过 `pic_crop_1_1` 裁剪坐标指定，toolkit 会把 2.35:1 和 1:1 上下拼成一张图上传并自动填好 `pic_crop_235_1` / `pic_crop_1_1`。推送后到后台草稿确认方形封面显示正确（社区反馈 1:1 裁剪偶尔被忽略、退化为居中裁剪），不对就在后台手动重选方形裁剪区域。

**6.3 封面验证（硬停）**：展示 3 张候选，等用户选。自检只用于候选质量（实体是否可识别；提示词过泛则换一组重试 1 次），**不能代替用户选定**。选定后再出双平台成品。

**6.3b 风格锚定**：封面确认后，提取视觉锚点（色板 hex、风格关键词、画面调性），后续所有内文配图的提示词必须引用这组锚点，保证全文视觉一致。

**6.4 内文配图**：分析文章结构，为每个需要配图的段落选择图片类型（infographic/scene/flowchart/comparison/framework/timeline），使用对应的结构化提示词模板生成 3-6 张配图提示词（按 visual-prompts.md）。批量调用 image_gen.py，替换 Markdown 占位符。

**降级**：image_gen.py 支持多 provider 自动 fallback（按 config.yaml 中 providers 列表顺序尝试）。全部失败 → 输出提示词 + 备选图库关键词，继续。

---

### Step 7: 排版 + 发布

**7.1 Metadata 预检**（发布前必须通过）：

| 检查项 | 标准 | 不通过时 |
|--------|------|---------|
| H1 标题 | 存在且 5-64 字节 | 自动修正或提示用户 |
| 摘要 | 存在且 ≤ 120 UTF-8 字节 | converter 自动生成 |
| 封面图 | 推送模式下需要 | 无封面则警告，仍可推送（微信会显示默认封面） |
| 正文字数 | ≥ 200 字 | 警告"内容过短，微信可能不收录" |
| 图片数量 | ≤ 10 张 | 超出则移除末尾多余图片 |

预检全部通过后才进入排版。

**7.2 排版 + 发布**：

**如果 `skip_publish = true`** → 直接走 preview。

```
读取: {skill_dir}/references/wechat-constraints.md
```

Converter 自动处理：加粗标点外移（CJK 自动加空格已于 2026-10-12 关闭：中英之间不加空格是固定规则；需要时设环境变量 `WEWRITE_CJK_SPACING=1` 才会重新打开）、列表转 section、外链转脚注、暗黑模式、容器语法。

```bash
# 发布
python3 {skill_dir}/toolkit/cli.py publish {markdown} --cover {cover_wechat_2.35} --cover-square {cover_square_1x1} --theme {theme} --title "{title}" --digest "{digest}"

# 降级：本地预览(HTML 必须落 preview/,禁止与正文平铺)
python3 {skill_dir}/toolkit/cli.py preview {markdown} --theme {theme} --no-open -o "${CONTENT_ROOT}/preview/{date}-{slug}.html"

# 同步 X Article(英语独立支线,细则见 weekly-topics.md ## 6):
# 1. 中文终稿落定后,从同一份大纲用英语直接写到 output/x/{slug}-en.md(不翻译中文终稿,禁逐句英译;机检跑 --en-gate)
# 2. 换家族去 AI 味(deepseek/deepseek-v4-pro);走「本周选题」时 ✋确认点④
# 3. 再清洗成 X 稿。默认只出本地稿;加 --push 才建未发布草稿,永不 publish
publish-x output/x/{slug}-en.md --output output/x/{slug}.md --title "{english_title}"
```

**X 排版硬规则(`toolkit/x_converter.py` 的 `apply_x_spacing()` 已机器化,勿手工另排)**:

| 规则 | Markdown 形态 | X 编辑器实际效果 |
|---|---|---|
| 段与段 | 空 **1** 行 | 相邻两个 block,原生间距 28px ≈ 1 行 |
| `##` / `###` 上方 | 空 **2** 行 | 标题上方多一个空 block ≈ 2 行 |
| 连续列表项 | **不空行** | 列表行紧贴 |

不要把 `\n{3,}` 压回 `\n\n`——那会抹掉标题上方的空行,粘进 X 后大标题贴住上一段。反之也不要在段间多塞空行:X 已自带 28px,再加一个空 block 就变成 2-3 行的大洞(用户 2026-08-20 反馈的「段间距还是很大」正是这个)。

**粗体**:X Article **支持**真粗体,渲染为 `font-weight: 700` 的 span(不是 `<strong>`/`<b>` 标签——用标签选择器查会误判成"没有粗体")。但 `--push` 走的 `POST /2/articles/draft` OpenAPI schema 严格,带 `inlineStyleRanges` 会 400,所以 API 建出的草稿**丢粗体**;`**...**` 只保留在本地 `output/x/{slug}.md`。要粗体就在浏览器编辑器里粘贴本地稿,或推完后手动重新加粗。

---

### Step 8: 收尾

**8.0 单一正文与分流检查(必须通过)**:
1. 解析本次正文的 `slug` 与 `topic_id`,搜索 Obsidian 公众号根和本轮 runs/临时目录中的 Markdown。
2. 同一 slug/topic_id 只允许 `<root>/output/{date}-{slug}.md` 一个可编辑中文正文;外部副本迁回后移除。内容冲突则停下做 diff,禁止静默覆盖。英语可编辑稿只许 `output/x/{slug}-en.md` 一份 + `output/x/{slug}.md` 一份清洗稿,发现 `-en-v2` 等副本必须迁回或删除。
3. `output/` 根不得出现 HTML、PNG/JPG、`*-evidence.md`、`*-quality.md`;按存放合约分流后才能继续。
4. 根据真实阶段更新正文 status:用户待终改=`editing`,内容定稿待发布=`ready`,推送成功=`published`。

**8.1 写入历史**（推送成功或降级都要写，文件不存在则创建）：

```yaml
# → {skill_dir}/history.yaml
- date: "{日期}"
  title: "{标题}"
  topic_source: "热点抓取"  # 或 "用户指定"
  topic_keywords: ["{词1}", "{词2}"]
  output_file: "{output 文件路径}"  # e.g. output/2026-03-31-zhangxue-slow-accumulation.md
  x_en_file: "output/x/{slug}-en.md"  # 英语可编辑稿;未做英语支线则省略
  x_status: drafted  # drafted/polished/confirmed/pushed/skipped
  framework: "{框架}"
  enhance_strategy: "{增强策略}"  # angle_discovery/density_boost/detail_anchoring/real_feel
  word_count: {字数}
  media_id: "{id}"  # 降级时 null
  writing_persona: "{人格名}"
  dimensions:
    - "{维度}: {选项}"
  closing_type: "{收尾类型}"  # trailing_off/unanswered/scene_revert/abrupt_stop/anti_conclusion/image
  composite_score: {Step 5.3 的 composite_score}  # 0=质量高, 100=问题多
  writing_config_snapshot:  # 本次使用的关键参数（从 writing-config.yaml 提取）
    sentence_variance: {值}
    paragraph_rhythm: "{值}"
    emotional_arc: "{值}"
    word_temperature_bias: "{值}"
    broken_sentence_rate: {值}
    tangent_frequency: "{值}"
    style_drift: {值}
    negative_emotion_floor: {值}
  stats: null
```

**8.2 回复用户**：

- 最终标题 + 2 备选 + 摘要 + 5 标签 + media_id
- 编辑建议："文章有 2-3 个编辑锚点，建议加入你自己的话。你可以在本地 markdown 里改，也可以直接在微信草稿箱改——改完后说**'学习我的修改'**，WeWrite 都能学到你的风格。"

**8.3 后续操作**：

| 用户说 | 动作 |
|--------|------|
| 润色/缩写/扩写/换语气 | 编辑文章 |
| 封面换暖色调 | 重新生图 |
| 用框架 B 重写 | 回到 Step 4 |
| 换一个选题 | 回到 Step 2.3 |
| 看看有什么主题 | `python3 {skill_dir}/toolkit/cli.py gallery` |
| 换成 XX 主题 | 重新渲染 |
| 看看文章数据 | `读取: {skill_dir}/references/effect-review.md` |
| 学习我的修改 | `读取: {skill_dir}/references/learn-edits.md`。支持本地 markdown 修改和微信草稿箱同步（`--from-wechat`） |
| 学习排版 / 学排版 | `python3 {skill_dir}/scripts/learn_theme.py <url> --name <name>` |
| 做一个小绿书/图片帖 | `python3 {skill_dir}/toolkit/cli.py image-post img1.jpg img2.jpg -t "标题"` |
| 检查一下 / 自检 / 这篇文章怎么样 | 生成报告（生成档案 + 质量检查，见辅助功能） |
| 导入范文 / 建范文库 | `python3 {skill_dir}/scripts/extract_exemplar.py article.md` |
| 查看范文库 | `python3 {skill_dir}/scripts/extract_exemplar.py --list` |

---

## 错误处理

| 步骤 | 降级 |
|------|------|
| 环境检查 | 逐项引导，设降级标记 |
| 热点抓取 | WebSearch 替代 |
| 选题为空 | 请用户手动给选题 |
| SEO 脚本 | LLM 判断 |
| 素材采集（WebSearch） | LLM 训练数据中可验证的公开信息 |
| 维度随机化 | history 空时跳过去重 |
| Persona 文件不存在 | 回退到 midnight-friend（默认） |
| 范文库为空 | Fallback 到 exemplar-seeds.yaml（通用模式） |
| 去 AI 验证 | 2 轮定向修复不过则跳过该项 |
| 生图失败 | 输出提示词 |
| 推送失败 | 本地 HTML |
| 历史写入 | 警告不阻断 |
| 效果数据 | 告知等 24h |
| Playbook 不存在 | 用 writing-guide.md |
