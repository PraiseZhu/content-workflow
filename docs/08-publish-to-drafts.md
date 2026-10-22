# 08 · 推草稿箱 Publish to drafts

> 铁律：**只推草稿，从不发布**；**不覆盖、不删除**已有草稿（每次新建）；**没有封面不推**（没封面 = 没写完）；发布永远由作者手动点。

## 微信公众号（草稿 API）
- 命令：`python3 skill/wewrite/toolkit/cli.py publish <zh.md> --cover cover-wechat-2350x1000.png --cover-square cover-square-1000x1000.png --theme <theme>`
  - toolkit 把 2350×1000 与 1000×1000 上下拼成一张永久素材，并填 `pic_crop_235_1` / `pic_crop_1_1` 坐标；正文图走 `media/uploadimg`（jpg/png <1MB）。
- 推完到后台核对两种封面裁剪（接口偶发忽略 1:1 裁剪）。
- **40164**：本机出口 IP 不在白名单。`curl -s ifconfig.me` 拿到出口 IP，作者到 公众号后台 → 设置与开发 → 基本配置 → IP 白名单 加入；家用宽带 IP 会漂移，复发正常。
- **贴图（newspic）**：`draft/add` 传 `article_type: "newspic"`，`image_info.image_list[].image_media_id`（永久素材，首张即封面，最多 20 张，1080×1440）；`content` 纯文本；title ≤32 字。当前 toolkit 尚未实现这条路径（`image-post` 子命令是旧的小绿书接口），需要时新增。

### 密钥使用模式（不入库）
- AppID / AppSecret 不写进仓库。两种方式任选：
  1. `config.yaml`（复制 `config.example.yaml`）放在 `${SECRETS_DIR}/wewrite/config.yaml`，再软链到 skill 目录；
  2. macOS Keychain：
     ```bash
     security add-generic-password -a "$USER" -s <WECHAT_SECRET_SERVICE_NAME> -w   # 交互输入
     security find-generic-password -a "$USER" -s <WECHAT_SECRET_SERVICE_NAME> -w # 读取（只在进程内用）
     ```
- 不打印、不写日志、不发聊天。

## X Articles（草稿 API）
- 命令：`python3 skill/wewrite/toolkit/cli.py x-draft <en.md> --push --cover header-x-2000x800.png`（不带 `--push` 为干跑）。
- 格式映射：`##` → `header-one`，`###` → `header-two`。**`header-three` 会让 X 返回 503**，不要用。无原始 markdown 表格。
- 限额：**每 24 小时最多创建 10 篇草稿**；503 先查格式，再重试 ≤3 次。
- **没有 list / delete 草稿的 API**：每次 push 都会新建，务必先干跑，避免重复。
- 凭据：OAuth 2.0（`toolkit/x_oauth_setup.py`）或 OAuth 1.0a（`toolkit/x_oauth1_setup.py`），存 macOS Keychain，服务名 `x-articles-client-id` / `x-articles-client-secret` / `x-articles-access-token` / `x-articles-refresh-token`。

## 推送成功后
- 写 `history.yaml`（见 [09](09-history-and-review.md)），打开后台页，✋ 确认③：作者手动发布。
