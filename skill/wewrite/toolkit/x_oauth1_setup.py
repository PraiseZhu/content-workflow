"""Store X OAuth 1.0a keys in macOS Keychain for X Articles drafts.

Run in your own Terminal:
  cd ${WEWRITE_DIR}
  .venv/bin/python toolkit/x_oauth1_setup.py
All four inputs are hidden. Then verifies the account via /2/users/me.
"""
import getpass
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from x_api import KEY_O1, _keychain_set, verify_me  # noqa: E402

labels = ["API Key", "API Key Secret", "Access Token", "Access Token Secret"]
vals = [getpass.getpass(f"{l}（输入不显示，粘贴后回车）: ").strip() for l in labels]
if not all(vals):
    sys.exit("四项都不能为空")
for k, v in zip(KEY_O1, vals):
    _keychain_set(k, v)
try:
    me = verify_me()
    print("完成：已写入钥匙串，授权账号 @" + me.get("data", {}).get("username", "?"))
except Exception as e:  # noqa: BLE001
    print("已写入钥匙串，但验证失败：", str(e)[:300])
