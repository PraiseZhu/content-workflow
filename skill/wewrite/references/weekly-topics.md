# 本周选题 → 成文 → 发布(周选题自动化 · 交互段)

> 触发:用户说「本周选题」(列卡)或「本周选题 选 N」+ 观点想法(进入成文)。
> 上游:`{skill_dir}/output/../selections/2026-Wxx-选题.md`(每周六 22:00 定时任务产出;实际路径 `${CONTENT_ROOT}/selections/`)。
> 设计权威:`公众号/automation/2026-07-25-weekly-topics-automation-设计.md`;红线见 memory `feedback_wechat-article-redlines`。
> 中文/微信三个确认点:①提纲 ②全文 ③发布(永远人工点,系统只开后台页);英语/X 另有两个确认点:④英语全文 ⑤英语发布,见 ## 6。
> **中英分工(2026-08-20 改定)**:不是逐步镜像。选题 / 提纲① / 配图共用;成文 / 去 AI 味 / 全文确认 / 发布闸门英语另走独立支线。英语支线**必须等中文全链路走完**(确认点② + 去 AI 味 + 用户改稿全部落入唯一正文)才开工,提前写会导致中英脱节。英语不再是发布闸门里一次性重写的附属步骤。
> **存放硬规则**:公众号唯一根目录=`${CONTENT_ROOT}`;正文只写 `output/YYYY-MM-DD-<slug>.md`,同题只保留一份;HTML→`preview/`,封面/配图→`output/assets/<slug>/`,证据与质量报告→`automation/reports/<slug>/`。worker/runs 里的成文产物必须在确认点②前迁回 output 并移除副本。
> **合规姿势(微信《运营规范》3.27 条,2026-03 新增,封号级)**:本流程定位永远是「AI 辅助真人创作」——中文三个人工确认点即微信侧合规证据,英语④⑤是 X 侧对应闸门;禁全自动发布;保持周更单篇节奏(同号一天多篇会触发「自动化批量发布」误判,有实案)。文档与对外表述禁用「全自动替代」类措辞。

## 0. 入口路由(硬顺序,禁跳步——先读红线再动笔)
1. 读最新 `selections/2026-Wxx-选题.md`;用户没带编号 → 列出全部卡片(主张+优先级+门槛自评)等选择,**到此为止**。
2. 用户给了「选 N」→ 读该卡完整内容 + **`源判断原句` 栏** + 证据附录 + `automation/blacklist.txt` + playbook.md。该栏为空或缺 → 标「⚠️ 补或删」,禁止空心 what 节;不得回读字幕/长文全文(contextBudget 红线,全文只在 idea-outline Step 3 读过)。
3. 红线自检:本卡「脱敏项」逐条确认成文策略(统一泛化「一个公司项目」)。
4. **中英分工**:本步共用,语言无关。英语不另做选题。

## 1. 观点合并 → 提纲重构(**两段式,2026-07-26 改定**:先 opus-5/xhigh 重排论证结构,再派 Orca worker `moonshot/kimi-k3`(effort medium)按 runbook「人话闸门」表把提纲文字改成人话——只改怎么说,不改判断与数字;worker 产出须落文件,回传只当完成信号)
- **用户观点做主导**:覆盖卡上「最反常识观点」,提纲围绕用户判断重排。
- **what 层先于 how**:提纲前两节必须能回指 `源判断原句`(交接是什么/为什么总会薄 这类定义层)。后半才写薄在哪、怎么修。源判断原句进证据包,禁只带提纲+数字。
- 证据重新分配到各节;缺一手证据的节标「⚠️ 补或删」,禁止空心节。
- 提纲必须满足:L3 主张打头 / 2-4 论点咬合(R006)/ 每节挂证据 / 收尾行动导向(R005)。
- 当前会话模型若非 opus-5,提示一句「建议 /model claude-opus-5」但不阻塞。
- ✋ **确认点①**:提纲展示,等用户确认/修改。
- **中英分工**:论证结构只排一次、只确认一次。英语不另出提纲、不另做确认点①。

## 2. 成文(**主笔 = `moonshot/kimi-k3`,effort medium**;2026-07-26 改定:替代原 fable-5(Claude 系中文翻译腔)与原定的 qwen3.7-max(worker 回传不稳);**Claude Sonnet 5 转做事实审校岗**:成文后逐条核对数字与证据是否与证据包一致。素材源=证据包,禁全网搜。worker 产出须落文件,回传只当完成信号)
- 走 wewrite Step 4 写作规范,但 **Step 3 素材采集替换为读证据包**(卡上 `源判断原句` + 提纲 + 已核实数字;what 层必须能回指原句,禁只复述 how)。WebSearch 仅补公开佐证。worker 工单写明:what 层必须能回指这些原句。
- 风格锁定:《目标驱动链》基准范文 + playbook R001-R006 + 六门槛自检(写完逐项过)+ **读 `automation/style-notes.md`(用户历史改稿 diff,存在即必读——用户亲手改过的句子是最高优先级风格样本)**。
- **文章骨架与语言(2026-07-26 用户指定)**:必读 idea-outline skill 的 `references/output-style.md`(源:`~/.claude/skills/idea-outline/references/output-style.md`)——<参考作者> 式（X 热门长文）结构(开场3句/短章节名/每节首句即判断/必有反面一节/一句判断收口)+ 中文转写表(禁名词化主语/禁被动堆叠/禁书面连接词)。**产出永远是中文;英文语料只作证据不作模板。**
- 事实与数字全部锚定证据包,禁编造;「⚠️待校准」数字须向用户口头确认或删除。
- ✋ **确认点②**:全文展示,等用户确认。展示前必须将正文写入 `<公众号根>/output/YYYY-MM-DD-<slug>.md` 并把 status 标为 `editing`;禁止只在聊天中展示或把正文留在 worker/runs。用户后续改写始终编辑这一个文件。
- **中英分工**:本步只出中文唯一正文。英语不成文于此——等中文去 AI 味 + 用户改稿全部落定后,才在 ## 6 用英语重写。提前写英语会导致后续中文改动不同步。

## 3. 去 AI 味(**换家族原则不变,但主笔已是 kimi-k3 → 本步改派 `deepseek/deepseek-v4-pro`(effort high)做跨家族润色**;2026-07-26 改定:原 qwen3.7-max 因 worker 回传不稳退出。硬要求:润色者与主笔必须不同家族——同家族改不掉同家族的语言习惯)
- 原则「风格只影响 HOW 不影响 WHAT」:只动句长/口语/节奏,事实数字锁死。
- **长度规则(2026-07-25 实测修正)**:去 AI 味必然大幅缩字数(实测 -53%,因为 AI 味的载体就是冗余修辞)——**缩短是特征不是缺陷,不设 ±% 约束**。需要回填篇幅时只允许「具体判断/证据」回填(如补一句 baseline 对照),禁止修辞回填。
- 禁忌表(三源合并):AI 高频词/破折号滥用/rule of three/否定排比/过度连接词;B 端黑话;通用名/假数字/填充词。
- **五步机械清单(2026-07-26 业界方法论调研引入,逐条过、逐条标 ✅,不许一句「已检查」带过)**:①删空背景开头 ②给过满判断加边界(对谁/什么条件下成立) ③压承接词 ④补具体对象/动作/场景 ⑤结尾改收口(谁适合+下一步)。针对读者识破 AI 的三大特征:段落等长、模板承接词、无个人经历。
- worker 不可用 → 跳过润色,**如实标注「未去 AI 味」**,禁用原模型自润充数。
- **中英分工**:本步只润中文。英语去 AI 味见 ## 6,派同一跨家族 worker(`deepseek/deepseek-v4-pro`)。禁忌表概念通用(rule of three / 否定排比 / 过度连接词在英语里同样是 ChatGPT 痕迹),英语支线套同一张表,不另造清单。

## 4. 配图(image-gen 通道)+ 排版
- **必读 `automation/image-style.md`(2026-07-27 已从历史配图实测定稿,强制项)**:四色板(陶土橙 #CA6743 / 鼠尾草绿 #ADBCA5 / 奶油白 #FAF6EA / 墨黑线)+ 左右分色块叙事构图 + 抽象几何体(禁人物/机器人/界面)+ 纸质颗粒与半调网点 + **完全无文字**;尺寸见该文件第三节。直接用该文件第四节的 prompt 模板,只替换 `<CONCEPT>`。
- **封面两步出图(2026-08-19 用户拍板,硬停)**:① 先出 3 张 16:9 候选给用户选构图,未确认不得出成品、不得推草稿;② 用户选定后,**同一构图分别按微信 16:9(1920×1080)与 X 5:2(1920×768)各出一张成品**,落 `output/assets/<slug>/cover.png` 与 `cover-x-5x2.png`。禁止把一张图补边/裁切硬改比例(会露出色条)。正文图仍按 2.36:1。
- `ghost_call`(ghost_id: <image-gen-plugin>)出头图 + 节点图,ratio 按尺寸表。
- **出图后必过三道机械校验(image-style.md 第五节):比例匹配 / 零文字 / 主色在四色板内。任一不过即重出,禁止拿不合规的图凑数**——2026-07-27 翻车实例:出了深蓝灰底 + 机械臂 + STOP 手势 + 中文标签的图,四色板一个没中。
- **降级分支(2026-07-25 实测定型)**:`errorCode: IMAGE_API_KEY_MISSING`(或任何出图失败)→ 文中留「配图位+prompt」占位,格式照抄 `automation/_dryrun/fallback-example.md` 模板(位置/子风格编号/完整 prompt/失败原因四字段,grep「【配图位」可定位全部待补位),**不阻塞推送**;并提醒用户:主界面「插件」→「图像生成插件」详情页填 插件 API key(<IMAGE_PLUGIN_SITE> 右上角 MCP 按钮获取)。禁止 fallback 到其它绘图通道。
- 排版:wewrite 主题 `claude-warm`。
- **中英分工**:构图共用一次确认;微信 16:9 与 X 5:2 成品已在本步出齐。英语支线不再重出图,只用 `cover-x-5x2.png`。

## 5. 发布闸门(硬门,顺序不可换)
1. **脱敏 grep(命中即停,列行号,不自动改写)**:
   ```bash
   PAT=$(mktemp); grep -vE '^\s*(#|$)' <automation>/blacklist.txt > "$PAT"
   grep -n -i -f "$PAT" <终稿.md>   # exit 0=命中→硬停; exit 1=放行
   ```
2. **AI 辅助声明(合规硬项,《人工智能生成合成内容标识办法》2025-09-01 施行)**:终稿文末必须有固定一行「本文为 AI 辅助创作,观点与事实由作者本人确认」——缺该行不得推送。
3. 推草稿箱(wewrite 现有推送脚本),outbox 纪律:同稿 dedupe(标题+日期做 key,重复推送先问)/失败重试≤5/记录最后错误码。
4. 仍失败 → 存本地成品(md+排版 html)+ 告知用户手动上传,附错误码。**errcode=40164 专项**(2026-07-25 实测过的高发故障):说明是「本机出口 IP 不在公众号白名单」,顺手跑 `curl -s ifconfig.me` 把当前出口 IP 给用户,指引:公众号后台→设置与开发→基本配置→IP 白名单 加入该 IP;家用/移动宽带 IP 会漂移,复发属预期。
5. 推送成功 → `open https://mp.weixin.qq.com` ✋ **确认点③:用户手动点发布**。
6. **中英分工**:本闸门只服务微信中文稿。英语/X 见 ## 6,不得在本步夹带英语重写或 `publish-x`。

## 6. 英语版(X)成文与发布(2026-08-20 改定:独立支线,不是发布闸门附属项)

前置:中文唯一正文已走完确认点② + ## 3 去 AI 味 + 用户改稿。未落定则禁止开工。选题 / 提纲 / 配图不重做。

1. **英语母语成文**(lead 会话模型执笔,不派中文主笔 kimi-k3):X 稿不是中文剥结构,也不是逐句英译。从已确认的中文终稿出发,按**同一论证结构 / 证据 / 数字**用英语重写。学 idea-outline `output-style.md` 的英文骨架(短章节名 / 每节首句即判断 / 必有反面一节 / 一句判断收口),丢掉中文句法再写,禁翻译腔。落 `output/x/<slug>-en.md`(frontmatter 必含 `lang: en` / `source_slug` / `platform: x`)。中文 `output/YYYY-MM-DD-<slug>.md` 仍是唯一正文,英语稿是平台副本,不得反向覆盖中文终稿。同 slug 只许这一份英语可编辑稿,禁 `-en-v2` / `-en-final` 另起权威副本。
   **英语 HOW 硬规则(2026-08-20,handoff-thin 实测翻车后写入;只改说法,不改论证)**:
   - **亲历口吻**:中文「我最近经历」不得写成 `I recently watched` / `I observed`。当事人变旁观者,深度掉一档。用 `I was in` / `we ran` / `I lived through`。
   - **禁 syllabus 开头**:删 `This piece is four things` / `This article covers`。H2 自己就是目录,正文第一句进判断。中文「这篇想说清楚四件事」是口语预告,英语写成 TOC 就是 AI 味。
   - **em-dash ≤5**:超过就改句号或逗号。14 处破折号是 ChatGPT 指纹,不是节奏。
   - **否定排比 ≤2**:`It looks like X. It is not. It is Y` / `was never the brief. It was` 这类 not-X-it-is-Y 全文最多两处。多了像 brief,不像判断。
   - **交接用 handoff,不用 brief**:`thin brief` 是 HR/文档腔;中文「交代」是口头交接。
   - **历史包袱不要压成 mess**:`historical mess` 把「继承约束」压扁了。用 `old baggage` 或 `legacy constraints`。
   - **一个节拍不要写两遍**:`lost in silence, lost into a wall of green` 比中文「丢得一声不响,丢成一片绿灯」更文学。一句即可。
   - **PreWalk 三步拆成三条短句**,不要揉进一段流程说明。
   - **地图/现场比喻只说一次**,后文不要再解释「map vs scene」。
2. **英语去 AI 味**(派 `deepseek/deepseek-v4-pro`,effort high;与英语执笔不同家族,满足跨家族原则,不另引入第三模型):套 ## 3 同一张禁忌表——AI 高频词 / em-dash 滥用 / rule of three / 否定排比 / 过度连接词;B 端黑话;通用名 / 假数字 / 填充词。原则同样是「只改 HOW 不改 WHAT」。worker 不可用 → 跳过并如实标注「英语未去 AI 味」,禁用执笔模型自润充数。
   **去 AI 味后机械闸门(确认点④之前必跑,fail-closed)**:
   ```bash
   python3 {skill_dir}/scripts/humanness_score.py output/x/<slug>-en.md --en-gate
   ```
   退出码 2 = 未过(syllabus / watched / em-dash>5 / thin brief / historical mess / 文学双拍 / 正文含 CJK)。列 findings,当场改 HOW,不得把失败稿拿去确认④。退出码 0 才展示全文。
   **禁止用中文 humanness 复合分判断英语稿**(脚本按 CJK 校准,英文会虚高,2026-08-20 实测 60.9 vs 中文 33.4,不是「英文更 AI」的证据)。英语质量看 `--en-gate` + 人工读,不看那个 0–100。
3. ✋ **确认点④:英语全文展示,等用户确认/修改**。展示前必须写入 `output/x/<slug>-en.md`;禁止只在聊天里贴一段英语。用户改写始终编辑这一个文件。
4. **英语发布闸门**(顺序不可换):
   1. 英语稿过同一份 `blacklist.txt`(Layer 1 公司名已含拉丁文,不另造英语黑名单;Layer 2 微信违禁词对 X 不适用,命中微信词不阻塞 X)。
   2. 英语文末必须有 AI 辅助声明一行(`This article was drafted with AI assistance; the judgments and facts were confirmed by the author.` 或等价表述)——缺该行不得清洗/推送。
   3. 跑 `publish-x output/x/<slug>-en.md --output output/x/<slug>.md --title "<English title>"` 出本地 X 排版稿。`publish-x` / `x_converter.py` 只做结构清洗,不做翻译。
   4. 用户明确说「推 X 草稿」才加 `--push`(只调 `POST /2/articles/draft`,**永不**调 publish)。然后 `open https://x.com/compose/articles`。
   5. X 封面用 `cover-x-5x2.png`(## 4 已出的那张),不要用微信 16:9。封面图需 `media.write` 后才走 API 上传;当前 token 无此 scope 时在编辑器里手动挂图。正文图片与外链 URL 默认剥掉。
5. ✋ **确认点⑤:用户手动点英语发布**。系统只开 X 编辑器,永不代发。
6. **X 排版与粗体(2026-08-20 实测定死,已机器化在 `toolkit/x_converter.py` 的 `apply_x_spacing()`)**:
   - 段与段空 **1** 行;`##` / `###` 上方空 **2** 行;连续列表项**不空行**。X 编辑器每个 block 自带 28px(≈1 行)间距,段间再多塞一个空 block 就是 2-3 行的大洞——用户反馈的「段间距还是很大」就是这么来的。
   - 反向也不许:`\n{3,}` 不得压回 `\n\n`,否则大标题贴住上一段。
   - 粗体 X **支持**,渲染成 `font-weight: 700` 的 span(**不是** `<strong>`/`<b>`;用标签选择器验证会得出"无粗体"的错结论)。但 `--push` 的 `POST /2/articles/draft` schema 严格,`inlineStyleRanges` 会 400 → API 草稿丢粗体,`**...**` 只活在本地 `output/x/<slug>.md`。要粗体:粘贴本地稿进编辑器,或推完手动补。

## 7. 收尾登记
- **唯一正文检查**:按本 skill「公众号存放合约」检查同 slug/topic_id 全局只有 output 中一份可编辑中文正文;preview/assets/reports 已分流;不通过不得收尾。
- **英语副本检查**:同 slug 只许 `output/x/<slug>-en.md` 一份可编辑英语稿 + `output/x/<slug>.md` 一份清洗稿;发现 `-en-v2` / 聊天落盘副本必须迁回或删除,禁止静默留多份。
- **改稿 diff 归档(风格库飞轮,2026-07-26 引入)**:确认点②前后用户改动过的每一处,按「原句 → 用户改后」对照追加进 `automation/style-notes.md`;这是成文环节最贵的风格训练数据,禁止丢弃。确认点④的英语改稿按同样格式另段归档,标注 `lang: en`。
- `history.yaml` 追加本篇记录(framework/persona/evidence_source=weekly-topics;英语支线写 `x_en_file` / `x_status`: `drafted` / `polished` / `confirmed` / `pushed` / `skipped`)。
- `selections/pool.md`:该卡移入「已出池登记」;`automation/trajectory.md`「已写/已毙」登记。
- 提醒:发布 3 天后回填 stats(阅读量),喂传播潜力校准。
