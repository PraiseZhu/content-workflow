# 04 · 成稿与写作规则 Writing & style rules

## 作者不喜欢（硬禁）
- AI 免责声明、「作为一个 AI」类句子
- 翻译腔（名词化主语、被动堆叠、书面连接词）
- 一句话塞两个意思
- 纯口语、无信息量的闲聊
- 不解释的术语（首次出现 30 字内给解释或中英对照，见 `config/glossary.json`）
- 夸大的判断（给过满判断加边界：对谁、什么条件下成立）
- 「不是…而是」句式（全文 0 次）
- 点名公司 / 产品 / 项目（换成泛称，如「一套自动化 QA 系统」；名单放 `config/private-names.txt`）
- 松散排版（段落等长、空行堆叠、加粗标签列表）
- X 上出现原始 markdown 表格

## 作者喜欢
- X 热门长文结构：开场 3 句进冲突、拔高的论点、短章节名、每节首句即判断、必有反面一节、一句判断收口
- 组织 / 机制视角
- 作者的标题和结论句**逐字保留**（locked lines）
- 朴素的小标题（不编号、不 Title Case 堆砌）

## 其他
- **不编造**故事、经历、数字；缺料标 `[待作者补]`。
- **本地受众规则（可配置）**：在 `config/voice.md` 里写明，例如「不引用某地区的推文或人物」。
- 中文先走完（确认② + 去 AI 味 + 作者改稿），英文再从同一提纲用英语重写；亲历口吻（`I was in` / `we ran`，不写 `I observed`），不要 syllabus 式开头。
- 中英文、数字之间：遵循 `config/voice.md`（作者当前偏好为不加空格；贴图标题例外见 06）。

完整规范：[skill/wewrite/references/writing-guide.md](../skill/wewrite/references/writing-guide.md)、[config/voice.md](../config/voice.md)、[config/voice-anchors.md](../config/voice-anchors.md)、[config/style-profile.json](../config/style-profile.json)。
