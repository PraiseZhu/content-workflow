# 06 · 配图 Images

唯一真源：[specs/image-sizes/](../specs/image-sizes/)（`sizes.json` 机器读，`SPEC.md` 人读，`check_spec.py` 校验两者一致）。渲染只按图位 ID 引用（如 `wechat.cover`、`x.article_header`），不写死像素。

## 尺寸表

| 平台 | 图位 | 像素 | 比例 | 规则 |
|---|---|---|---|---|
| 微信 | 头条封面 `wechat.cover` | **2350×1000** | 2.35:1 | 中文；四周留 6%；与 X header 元素一致 |
| 微信 | 方形封面 `wechat.square` | **1000×1000**（最低 383×383） | 1:1 | **只放一个核心符号/数字，不放标题/副标题/tag**；缩到 200px 和 120px 检查 |
| 微信 | 贴图封面 `wechat.newspic` | **1080×1440** | 3:4 | 中文标题 2–4 行，≥96px，每行 ≤7 字；内容在 x 90–990、y 140–1300，标题主体在 y 360–1080 |
| 微信 | 正文配图 | 1600×900 | 16:9 | **仅 jpg/png，<1MB**（超了转 JPG q85）；小字 ≥24px |
| X | Article header `x.article_header` | **2000×800** | 5:2 | **安全区：左右各 10%、上 20%、下 15%**（x 200–1800，y 160–680）；顶部 20% 与四角只放背景 |
| X | 正文配图 | **1600×900** | 16:9 | 四周 ≥5%；小字 ≥22px |
| X | ~~1500×600~~ | — | — | **已停用**，渲染脚本遇到会报错 |

## 文字总纲
- **X 只放英文图，微信只放中文图**；中英两套**镜像**（同构图、同元素，只换语言）。
- 同一语言的封面变体（微信头条 / X header）携带相同元素（标题、tag、主体、主视觉、核心符号）；比例紧张时只缩放/重排，不删内容。唯一例外：微信方形封面。
- 直接按目标尺寸渲染，**禁止 PIL 补边/裁切硬改比例**。

## 风格系统
- 默认风格包：**暗色网格**（`renderer/article-image-styles/dark-grid-photo`，`ACTIVE` 文件指定当前包）。备选 `house-dark`。
- 风格包 = `style.json`（色板、字体、纹理 token）+ `tokens.css` + `STYLE.md`（人读说明）。
- 新风格从风格库（[10](10-style-library.md)）挑出来再固化成风格包。

## 流程
1. **定风格**：选风格包（默认暗色网格），确定主色、强调色。
2. **列图清单**（`render/slots.zh.json` / `slots.en.json`）：
   - 封面信息：2–4 个字的核心信息 / 一个核心符号；
   - 每节 3–5 张信息图（流程、对比、门槛、收敛路径等）；
   - 图上文字**逐字**取自正文（verbatim），不另写。
3. **渲染中文**：`python3 renderer/article-image-template/lib/render.py <article> --lang zh`
4. **渲染英文**：同上 `--lang en`
5. **自检**（`--check`、`--safe-overlay`）：
   - 尺寸与 sizes.json 一致；
   - 文件大小（微信正文 <1MB）；
   - 文字溢出 / 截断；
   - 私名泄露（公司/产品/项目名）；
   - 中英一致（同元素、同数字）；
   - 缩略图可读（方图 200/120px，贴图 360/180px，X header 安全区叠框）。
6. **交付**：`images/zh/`、`images/en/` 固定文件名（`cover-wechat-2350x1000.png`、`cover-square-1000x1000.png`、`header-x-2000x800.png`、`figN-*.png`）。

方法详见 [workflows/article-image-render/SKILL.md](../workflows/article-image-render/SKILL.md)；示例：[examples/article-build/](../examples/article-build/)（slots + manifest + build 脚本）和 [examples/image-generation/](../examples/image-generation/)（独立 Python+HTML 出图脚本）。AI 生图 prompt 规范：[skill/wewrite/references/visual-prompts.md](../skill/wewrite/references/visual-prompts.md)、[image-specs.md](../skill/wewrite/references/image-specs.md)。
