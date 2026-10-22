# image-sizes CHANGELOG

One line per change: date (PT unless noted) · what · why / evidence.

- 2026-10-17 · 定稿固定导出套装：微信 2350×1000 头条、1000×1000 方形（不放标题）、1600×900 正文；X 2000×800 Article header（安全区 200,160–1800,680）、1600×900 正文。X 由 1500×600 升到 2000×800 · 依据：SPEC.md「X Article 封面安全区是怎么来的」手机截图实测（1320×2868）+ 文末来源。原文件 ${WORKSPACE}/specs/图片尺寸规范.md.bak-20261018-tietu（存档于 ${WORKSPACE}/specs/_archive-20261018/）。
- 2026-10-18 (BJT 早) · 新增「贴图（newspic）封面」1080×1440 3:4 · 依据：服务号「贴图」区截图实测 223×297≈3:4 + 微信派 / 数英 / 开放社区来源（SPEC.md 文末）。
- 2026-10-18 · 迁到 specs/image-sizes/ 作为唯一真源；新增机读 sizes.json（图位 ID）和 check_spec.py；1500×600 X header 正式停用（sizes.json 里 status=retired，渲染器拒绝）；${WORKSPACE}/specs/ 下两份同文文件改为指针，原件和 .bak 存档于 ${WORKSPACE}/specs/_archive-20261018/ · 原因：同一规范两个文件名、无机读版本、像素手写在各篇 build.py 里。
