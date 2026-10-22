---
title: 配图风格规范（实测定稿）
created: 2026-07-25
calibrated: 2026-07-27
status: ✅ 已定稿 — 从本号历史配图实测反推（output/Attachments/ 2026-04~05 已发布文章配图）
decided_by: 用户 2026-07-27（「图片没有指定风格 也没有指定尺寸比例，你去看下过去文章的配图风格和尺寸，明确强制这一点」）
---

# 配图风格规范

> **强制项，不是建议项。** 出图前必读本文件；出图后必须过下方「机械校验」，不合规不得进排版。
> 依据：本号 2026-04~05 已发布文章的真实配图（`output/Attachments/`），色值经采样,构图与尺寸经实测。**不再使用占位 prompt。**
>
> **两支风格，同一色板。默认用 S-B。**（2026-07-27 用户拍板：给了 5 张 Anthropic 官方卡片图，评价「简洁且优雅」）
> - **S-B｜极简单物件**（第二节 B）— **默认**。单色满底 + 画面正中一个奶油白物件 + 粗黑手绘线。用于正文节点图、以及绝大多数场景。
> - **S-A｜编辑插画**（第二节 A）— 仅当一张图必须表达「前后对比 / 混乱→有序」的转折时才用。信息量大，容易失控。
> 单篇文章内**只锁一支**，不混用。

## 一、色板（采样自历史配图，一致性极高）

| 角色 | 色值 | 实测占比 |
|---|---|---|
| 陶土橙（主色，混乱/问题侧） | `#CA6743` ~ `#D06843` | 单图最高 11% |
| 鼠尾草绿（副色，有序/解法侧） | `#ADBCA5` ~ `#B2C0A7` | 单图最高 9.9% |
| 奶油白（底色/图形填充） | `#FAF6EA` ~ `#FBF8EF` | 大面积 |
| 墨黑（手绘线条） | 近黑，粗描边 | 线条专用 |

**只用这四色。** 不加第五个色相。

## 二、构图公式

### B. S-B｜极简双物叠置（**默认**）

依据:用户 2026-07-27 提供的 5 张 Anthropic 官方卡片图。**先立设计原则,再由原则推 prompt**——下面六条每条都从画面事实反推,不是审美偏好。

**样例台账(原始事实)**

| 图 | 底色 | 主体 | 结构关系 |
|---|---|---|---|
| 1 | 陶土橙 | 手 + 节点网络 | 手在下托着网络 |
| 2 | 淡粉 | 手 + 打开的书 + 折线 | 手托书,折线长在书页里 |
| 3 | 陶土橙 | 苹果 + 合上的书 | 苹果压在书上 |
| 4 | 鼠尾草绿 | 手 + 放大镜 + 纸 | 手持镜看纸 |
| 5 | 陶土橙 | 同 4(仅换底色) | 同 4 |

**六条设计原则**

1. **一图一念**:每张只表达一个概念,不表达过程、不表达对比。图 3 是「学习」,不是「从不懂到懂」。判据:这张图能否用一个名词短语说完?
2. **概念必须落成实物**:抽象概念一律翻译成日常可见的实物——知识→书,观察→放大镜,成长→折线,连接→节点网络。**禁止用抽象符号表示抽象概念**(不画箭头表示「流程」,不画齿轮表示「机制」)。
3. **人以手为代**:要表达「人在做这件事」时只画手,不画人、脸、身体。手既代表人,又不引入身份/性别/年龄等无关信息。画法固定:**几道平行弯曲的粗线当手指(像梳齿)**,不画写实手掌。5/5 样例中 4 张用此法。
4. **双物叠置构关系**:主体不是孤立一件,而是**两件东西的叠置**(手托网络/手托书/苹果压书/手持镜看纸)。**关系由物理位置表达,不靠箭头、不靠连线**。要点是「叠成一体的两件」,不是「并列摆放的两件」。
   > ⚠️ 2026-07-27 首版曾误写成「主体只有一个」——复核 5 张样例后更正:全部是两件咬合物。
5. **二色一线**:底色一色铺满 + 实心形状为奶油白 + 线条为墨黑。**总共两个色相加一个黑**,无第三色相、无渐变、无阴影、无纹理。
6. **实心与线条混搭,绝不统一**(2026-07-27 用户补充):同一张图里,**一部分物体是纯实心白块(无描边),另一部分是纯黑线勾出的形**。禁止两种极端:
   - ❌ 全是实心色块(变成剪贴画,没有笔触)
   - ❌ 全是线稿(变成简笔画,没有分量)
   - 样例复核:图 3 苹果=纯实心白**无描边**,书=纯线条;图 1 节点球=实心,连线=线;图 4 纸=实心,放大镜与手=线。**5/5 都是两种手法各承担一部分。**
   - 分配原则:**承载概念主体的那件用实心**(有分量、抢视觉),**表达关系与动作的那件用线条**(轻、灵活)。
7. **黑线是造型语言,不是描边工具**(2026-07-27 用户补充):黑线的职责是**勾轮廓、切负形、做剪影、交代物体之间的关系**——它自己就是一个形。**绝不给每个图形无脑勾一圈边**。
   - ❌ 反面:实心白块外面再套一圈黑边(这是描边思维,出图最容易犯)
   - ✅ 正面:黑线独立画出一个物体的外形(书、放大镜、手);或用一根线穿过、托住、连接实心块;或靠黑线与底色夹出一块负形白
8. **实心块是手绘剪影,不是几何图元**(2026-07-27 用户指出「实心图形毫无美感」后补):实心白块的美感全部来自**轮廓本身被画出来**,而不是拿标准图元去占位。
   - ❌ 反面(本轮翻车实测):书用线条画好了,上面压一个**标准白色圆角矩形**当纸;绿底门旁边贴一个**等边白三角**;实心块小、孤立、像补丁。
   - ✅ 正面(样例复核):苹果实心白,但轮廓有**顶部凹陷 + 叶子缺口**,形状自己就说清了是苹果;纸实心白,但**边缘有卷角与透视变形**,不是标准矩形。
   - 四条硬要求:
     1. **遮住底色只看白形,必须能认出是什么东西**——认不出=几何图元=重出。
     2. **边缘是手剪/手撕出来的**:不规则、微抖、不对称,不用直尺不用圆规。
     3. **必须带物件特征**:凹口、缺角、卷边、厚度、开口——让剪影自己承担辨识,这也是「不用描边」得以成立的前提。
     4. **实心块是画面主角**:尺寸不小于线条物,且与线条物**咬合**(压住/穿过/被托住),不能只是搭在旁边。
   - 唯一例外:物件本身就是规则形时可用规则形(如节点球用圆),但须**成组出现构成节奏**,不可孤立一个。
9. **徒手感优于精确**:线条粗细不匀、有抖动、收笔处可不闭合,像马克笔一笔画成。**这是刻意的**——把「人画的」这个信号留在画面里,与 AI 的光滑矢量感区别开。

> ⚠️ 样例图下方的中文条(「下载 Claude｜由 Anthropic 提供」)是**网页 UI 叠加的说明条,不是图内文字**——图本身零文字,禁文字规则无例外。

### A. S-A｜编辑插画（仅表达前后对比时用，历史配图 3/3 同构）

1. **左右分色块叙事**：画面左右各一色块（橙 / 绿），左=混乱、发散、问题；右=有序、收束、解法。中间用一条粗黑线穿过两侧连接。
2. **抽象几何体**：立方体、方块、三角、圆环、同心圆靶心——**不画具象人物、不画机器人、不画屏幕界面**。
3. **纹理三件套**：纸质颗粒 + 半调网点渐变（halftone dots）+ 网格纸方块（graph paper square）。
4. **手绘感黑线**：粗细不匀的墨线勾边与路径，允许轻微抖动，不要矢量硬边。
5. **完全无文字**：中文渲染不可靠，任何文字标签一律禁止（历史图 3/3 零文字）。

## 三、尺寸（实测,按用途固定）

| 用途 | 尺寸 | 比例 | 出处 |
|---|---|---|---|
| 封面候选(选型用) | 1920×1080 | **16:9** | 先出 3 张给用户选构图,不直接当双平台封面 |
| 微信封面 | 1920×1080 | **16:9** | 用户选定后单独出 → `cover.png` |
| X Article 封面 | 1920×768 | **5:2** | 用户选定后单独出 → `cover-x-5x2.png`;禁止把 16:9 补边/裁切凑数 |
| 正文宽图（主力） | 1584×672 | **33:14 ≈ 2.36:1** | 3 张历史图均为此比例 |
| 正文常规图 | 1376×768 | ≈16:9 | image_20260504022859 等 |
| 方图（少用） | 1024×1024 | 1:1 | image_20260419172731 |

**默认（硬停）**：① 先出 3 张 16:9 候选给用户选构图;② 用户确认后,**同一构图分别按微信 16:9 与 X 5:2 各出一张成品**。未确认不得出成品、不得推草稿。禁止用 PIL 补边/裁切把一张图硬改比例(2026-08-19 实测:16:9 补成 5:2 会露出陶土色竖条)。正文一律 2.36:1 宽图。

## 四、出图 prompt 模板

### S-B（默认）

**写 prompt 前先做两步概念工作**(这是全部功夫所在,做不到就别写 prompt):

**第一步 · 一句名词短语说完这张图**(原则一)。说不完 → 概念没想透,回去想,不许靠堆元素补。

**第二步 · 拆成「主物 + 关系物」两件实物**(原则二+四)。左边是概念,右边是它该长成的样子:

**第三步 · 给两件物分配造型手法,并写出实心块的「辨识特征」**(原则六+七+八)。
主体用**实心白**、关系物用**黑线**;**实心块必须能写出至少一条剪影特征,写不出就换物件**——这一栏是防「白色圆角矩形」的唯一保险。

| 概念 | 主物(实心白,无描边) | **剪影特征(必填)** | 关系物(黑线) | 叠置方式 |
|---|---|---|---|---|
| 知识/学习 | 苹果 | 顶部凹陷 + 叶子缺口 | 一本书 | 苹果压在书上(=样例图 3) |
| 说不清就改不动 | 一张纸 | 卷角 + 手撕毛边 | 一支笔 | 笔尖戳进纸里 |
| 验收清单 | 一张打勾的纸 | 缺角 + 边缘起伏 | 一只手 | 手指托住纸的下沿 |
| 工具装太多 | 一堆方块 | 大小不一、边缘歪斜、成堆咬合 | 一只手 | 托不住,方块从指间漏下 |
| 审查看不见界面 | 一张纸 | 卷边 + 折痕缺口 | 放大镜 | 镜片压在纸上并盖住一部分 |

**每句 prompt 对应哪条原则(逐句可查)**:

```
Minimal editorial illustration, Anthropic house style.                  ← 总纲
Flat solid <BG: terracotta #CA6743 | dusty pink #EBD3D3 | sage #ADBCA5>
  background, one single color filling the entire frame.                ← 原则五
Subject: <关系物> and <主物>, physically stacked — <叠置方式>.            ← 原则四
  Two objects only, touching or overlapping as one visual unit,
  their relationship shown by position alone, no arrows, no connectors. ← 原则四
MIXED rendering, deliberately inconsistent between the two objects:      ← 原则六
  <主物> is a FLAT SOLID cream white (#FAF6EA) silhouette with NO outline
    around it — the shape reads by its own edge against the background;
  <关系物> is drawn ONLY as thick black hand-drawn marker lines, no fill.
  Never outline the solid shape. Never draw everything in line only.
The solid silhouette must be a HAND-CUT SHAPE, not a geometric primitive: ← 原则八
  its contour alone identifies the object, with defining features cut
  into it (<此物的特征:如 notch / curl / torn edge / opening>),
  edges irregular and slightly wobbly as if cut with scissors by hand.
  It is the visual protagonist: as large as or larger than the line
  object, and physically interlocked with it — never a small patch
  placed beside it.
NO plain rounded rectangle, NO equilateral triangle, NO perfect circle
  standing in for an object.                                            ← 原则八
The black line is a drawing element, not a border: it forms silhouettes,  ← 原则七
  carves negative space, and shows how the two objects relate —
  it must never be a stroke traced around a filled shape.
Line quality: uneven weight, visible wobble, ends may stay open,         ← 原则八
  drawn in one confident pass.
<若含手> the hand drawn as several parallel curved thick strokes
  (like comb teeth), never a realistic palm.                            ← 原则三
Centered, generous empty margin, subject occupies about 40% of frame.   ← 原则一(视觉聚焦)
NO gradient, NO texture, NO shadow, NO third color.                     ← 原则五
NO outline stroke around filled shapes, NO uniform treatment of all
  objects, NO all-solid composition, NO all-line composition.          ← 原则六/七
NO text, NO letters, NO abstract symbols for abstract ideas (no gears,
  no arrows, no lightbulbs), NO realistic human, NO robot, NO UI screen,
  NO dark background, NO neon glow, NO stock-photo look.                ← 原则二/三
```

### S-A（仅前后对比场景）

```
Editorial illustration in Anthropic house style. Split composition: left half terracotta
orange (#CA6743) showing <CONCEPT 的混乱/问题侧>, right half sage green (#ADBCA5) showing
<CONCEPT 的有序/解法侧>, cream white (#FAF6EA) background and shapes. Abstract geometric
objects only — cubes, squares, triangles, concentric-circle targets, graph-paper square.
Thick hand-drawn black ink outlines, uneven line weight. Paper grain texture and halftone
dot gradients. One continuous black line connecting left to right.
NO text, NO letters, NO人物, NO robots, NO UI screens, NO dark background, NO neon glow,
NO gradient mesh, NO stock-photo look.
```

出图通道:image-gen(`ghost_call` → <COMPANY> ImageGen,`submit_gen_image` → `poll_result`),ratio 按上表。

## 五、机械校验（出图后必过，不合规重出）

**S-B 专属六问（每问对回一条设计原则，逐条答，不许"整体看着还行"放行）**：

| # | 问 | 对应原则 | 不合格即 |
|---|---|---|---|
| 1 | 这张图能用一个名词短语说完吗? | 一图一念 | 重出 |
| 2 | 画面里有没有抽象符号(齿轮/箭头/灯泡)在表示抽象概念? | 概念落成实物 | 有 → 重出 |
| 3 | 出现人了吗?(只允许梳齿状的手) | 人以手为代 | 有脸/身体 → 重出 |
| 4 | 两件物体是叠在一起的,还是并排摆着的? | 双物叠置 | 并排 → 重出 |
| 5 | 除底色与奶油白外还有第三个色相吗?有渐变/阴影/纹理吗? | 二色一线 | 有 → 重出 |
| 6 | **实心块外面有没有被套一圈黑边?** | 黑线是造型语言 | 有 → 重出(这是描边思维,最高频错误) |
| 7 | **是不是全实心、或者全线稿?** | 实心与线条混搭 | 是 → 重出(必须两种手法各承担一部分) |
| 8 | **遮住底色只看白形,认得出是什么东西吗?** | 实心块是手绘剪影 | 认不出(是圆角矩形/三角/圆) → 重出 |
| 9 | **白形边缘是尺规画的,还是手剪的(不规则微抖)?** | 同上 | 尺规感 → 重出 |
| 10 | **实心块是主角还是补丁?**(尺寸是否 ≥ 线条物、是否与它咬合) | 同上 | 小而孤立 → 重出 |
| 11 | 线条是光滑矢量感,还是粗细不匀有抖动? | 徒手感 | 光滑 → 重出 |

**通用三道**：

1. **尺寸/比例**:`python3 -c "from PIL import Image;im=Image.open('<图>');w,h=im.size;print(w,h,round(w/h,2))"` → 必须匹配第三节表中某一行（±0.02）。
2. **无文字**:肉眼确认零文字/零字母。出现任何标签即重出（2026-07-27 翻车案例:图中被画上「CI 流程」「PR 分支」中文标签）。
3. **色板**:采样主色必须落在第一节区间内。**出现深色背景、冷蓝灰、霓虹即判废**（2026-07-27 翻车案例:深蓝灰底 + 机械臂 + STOP 手势,四色板一个都没中）。

## 六、降级

image-gen 出图失败 → 文中留「配图位 + 完整 prompt」占位（格式照 `_dryrun/fallback-example.md`），不阻塞推送。**但风格不合规不算失败,必须重出,不许拿不合规的图凑数。**
