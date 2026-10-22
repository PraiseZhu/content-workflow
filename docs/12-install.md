# 12 · 安装 Install

**Linux / Grok Bot box 一键版**：`bash grokbot/setup.sh`（做完下面所有步骤并跑测试与渲染冒烟测试，详见 [grokbot/MIGRATION.md](../grokbot/MIGRATION.md)）。

以下是手动步骤（macOS / Linux）。所有 `<...>` 都是占位符，换成你自己的值；**不要把任何密钥提交进仓库**。

## 1. 克隆与路径变量
```bash
git clone <this-repo> content-workflow && cd content-workflow
export WEWRITE_DIR="$PWD/skill/wewrite"
export CONTENT_ROOT="$HOME/Documents/公众号"          # 文章根目录：output/ selections/ preview/ history.yaml
export ARTICLES_DIR="$HOME/articles"                  # 按文章分目录的工作区
export STYLE_LIBRARY_DIR="$HOME/style-library/x-trending"
export FONT_DIR="$HOME/.local/share/fonts"            # macOS 可用 ~/Library/Fonts
export SECRETS_DIR="$HOME/.secrets"                   # mode 700，绝不入库
mkdir -p "$CONTENT_ROOT"/{output,selections,preview} "$ARTICLES_DIR/config" "$STYLE_LIBRARY_DIR" "$SECRETS_DIR" && chmod 700 "$SECRETS_DIR"
```
把这些写进 `~/.zshrc` / `~/.bashrc`。

播种内容根（规则文件、playbook、image-style、选题池）：
```bash
cp -rn content/. "$CONTENT_ROOT/"
cd skill/wewrite && for n in output history.yaml playbook.md; do ln -sfn "$CONTENT_ROOT/$n" $n; done && cd -
```

## 2. Python 环境
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r skill/wewrite/requirements.txt pyyaml
python -m camoufox fetch        # 可选：scripts/fetch_article.py 抓公众号文章用
```
需要 Python ≥3.10。

## 3. 配置文件
```bash
cp skill/wewrite/style.example.yaml          skill/wewrite/style.yaml
cp skill/wewrite/writing-config.example.yaml skill/wewrite/writing-config.yaml   # 已附作者当前版本，可直接用
cp config/private-names.example.txt          config/private-names.txt           # 填你的公司/产品/同事名（已 .gitignore）
# 编辑 config/voice.md（写作偏好、本地受众规则）、config/glossary.json、config/channels.yaml
```

## 4. 微信公众号 AppID / AppSecret
1. 公众号后台 → 设置与开发 → 基本配置：拿到 AppID，生成 AppSecret。
2. **IP 白名单**：加入本机出口 IP（`curl -s ifconfig.me`）。不加会报 40164；家用宽带 IP 会变，复发就再加。
3. 存密钥（二选一）：
   ```bash
   # a) 配置文件（推荐跨平台）
   cp skill/wewrite/config.example.yaml "$SECRETS_DIR/wewrite-config.yaml" && chmod 600 "$_"
   # 编辑填入 appid / secret，然后软链给 skill：
   ln -s "$SECRETS_DIR/wewrite-config.yaml" skill/wewrite/config.yaml
   # b) macOS Keychain
   security add-generic-password -a "$USER" -s <WECHAT_APPSECRET_SERVICE> -w
   ```
4. 干跑：`python skill/wewrite/toolkit/cli.py preview <some.md> --no-open -o /tmp/p.html`

## 5. X 开发者应用（X Articles 草稿）
1. developer.x.com 建 Project + App；User authentication settings：
   - App permissions：Read and write
   - Type：Web App / Automated App（confidential client）
   - **Callback URI：`http://127.0.0.1:8765/callback`**
   - Website：任意你的主页
2. 账号需要能使用 X Articles（Premium）。
3. OAuth 2.0 授权（macOS，会把 token 存入 Keychain 服务 `x-articles-client-id` / `x-articles-client-secret` / `x-articles-access-token` / `x-articles-refresh-token`）：
   ```bash
   cd "$WEWRITE_DIR" && python toolkit/x_oauth_setup.py   # 浏览器里用 @<YOUR_X_HANDLE> 登录并 Authorize
   ```
   或 OAuth 1.0a：`python toolkit/x_oauth1_setup.py`。
4. 干跑：`python toolkit/cli.py x-draft <en.md> --payload-out /tmp/x.json`（不加 `--push` 不会建草稿；每 24h 最多建 10 篇，且无法用 API 删除）。
> Linux 没有 `security` 命令时，`toolkit/x_api.py` 自动改用文件存储：`$X_SECRETS_DIR`（默认 `$SECRETS_DIR/x/`），每项一个 600 权限文件。macOS 上也可设 `WEWRITE_SECRET_BACKEND=file` 强制使用。

## 6. 字体
- 中文：**MiSans**（Regular/Medium/Semibold/Bold）放到 `$FONT_DIR/misans/`；思源黑体 / 思源宋体（Noto Sans/Serif CJK SC）作后备。
- 英文：**Inter**、JetBrains Mono（代码/数字）。
- 安装后 `fc-cache -f`（Linux）。`renderer/article-image-styles/house-dark/src/*.html` 里的 `file://${FONT_DIR}` 需要按你的路径替换。

## 7. Headless Chrome（配图渲染）
```bash
# macOS
brew install --cask google-chrome   # 或 chromium
export CHROMIUM="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# Linux
sudo apt-get install -y chromium || sudo apt-get install -y google-chrome-stable
export CHROMIUM=chromium CHROME_PATH=/usr/bin/google-chrome
# 长图/PDF 渲染器
cd renderer/html-render && npm install && cd -
```
验证：在仓库根目录运行
```bash
python3 specs/image-sizes/check_spec.py
python3 renderer/article-image-template/lib/render.py <article_dir> --check
```
（render.py 默认从当前目录读 `specs/image-sizes/sizes.json` 和 `renderer/article-image-styles`；可用 `SIZES_JSON` / `STYLES_DIR` 覆盖。）

## 8. 去 AI 味工具
```bash
python3 deai-lint/deai_lint.py test                     # 跑规则测试
python3 deai-lint/deai_lint.py lint some.md             # 单篇检查
python3 skill/wewrite/scripts/humanness_score.py some.md
```

## 9. 接入 agent
- Claude Code 等：把 `skill/wewrite` 链到 `~/.claude/skills/wewrite`；`workflows/*` 链到 skills 目录。
- 定时任务：见 [11-routines](11-routines.md)。
