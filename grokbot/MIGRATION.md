# MIGRATION — 把写作工作迁到新的 Grok Bot（给作者本人看）

1. **新建 bot**（个人账号）。
2. **连接器**：在新 bot 设置里连 X（@PraiseBuild）、GitHub（PraiseZhu）、你的 Mac（Computers）。可选 Google Calendar。
3. **给新 bot 发这一句**（直接粘贴）：
   > 克隆私有仓库 PraiseZhu/content-workflow 到 /home/box/content-workflow，然后严格按仓库根目录的 BOOTSTRAP.md 从第 0 步做到第 9 步，每步做完告诉我验证结果；需要我操作的（连接器、密钥、启用定时任务）停下来问我。
4. **新 bot 跑完第 3 步后**，box 上已有：`~/content-workflow`（仓库）、`~/.content-workflow.env`、`.venv`、MiSans 字体、`~/content-work/公众号`（内容根副本）、风格库目录。
   手动命令（等价于 setup.sh）：
   ```bash
   cd /home/box && gh repo clone PraiseZhu/content-workflow && cd content-workflow
   bash grokbot/setup.sh && . ~/.content-workflow.env
   ```
5. **定时任务**：确认新 bot 建好两条 routine 后，**在旧 bot 上停掉同名任务**（每周10个选题、X热门长文配图风格收集），避免重复跑。
6. **密钥（只有你能做）**
   - 微信：继续在 Mac 上推（无需操作）；或在新 box 终端 `mkdir -p ~/.secrets/wewrite && cp $WEWRITE_DIR/config.example.yaml ~/.secrets/wewrite/config.yaml && chmod 600 ~/.secrets/wewrite/config.yaml`，填 AppID/AppSecret，并把 `curl -s ifconfig.me` 的 IP 加进公众号白名单。
   - X：先在 developer.x.com **重置**之前泄露的 Client Secret / Consumer Key；Mac 上 `python toolkit/x_oauth_setup.py` 更新 Keychain；如要在 box 推，在 box 上也跑一次（回调 http://127.0.0.1:8765/callback）。
7. **风格库图片**（可选）：旧 box `/home/box/style-library/x-trending/` 下的图片没有进仓库。想保留就从旧 bot 打包下载，解压到新 box `~/content-work/style-library/x-trending/`。
8. **公开仓库前**：删掉 `handoff/`（私有资料）和 `content/automation/trajectory.md` 等你不想公开的文件，并重写 git 历史（`git filter-repo --path handoff --invert-paths`）。
