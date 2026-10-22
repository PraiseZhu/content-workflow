"""One-time X OAuth 2.0 (PKCE) setup for X Articles drafts.

Run in your own Terminal:
  cd ${WEWRITE_DIR}
  .venv/bin/python toolkit/x_oauth_setup.py

Prompts for Client ID / Client Secret (hidden input), opens the X consent page
in your browser, catches the callback on 127.0.0.1:8765, and stores the four
x-articles-* items in macOS Keychain. Nothing is printed except status.
"""
from __future__ import annotations

import base64
import getpass
import hashlib
import http.server
import secrets
import sys
import threading
import urllib.parse
import webbrowser

import requests

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from x_api import (  # noqa: E402
    KEY_ACCESS, KEY_CLIENT_ID, KEY_CLIENT_SEC, KEY_REFRESH,
    TOKEN_URL, _basic_auth_header, _keychain_set,
)

REDIRECT = "http://127.0.0.1:8765/callback"
AUTH_URL = "https://x.com/i/oauth2/authorize"
SCOPES = "tweet.read tweet.write users.read media.write offline.access"


def main() -> None:
    client_id = input("X Client ID: ").strip()
    client_sec = getpass.getpass("X Client Secret (hidden): ").strip()
    if not client_id or not client_sec:
        sys.exit("Client ID / Secret 不能为空")

    verifier = base64.urlsafe_b64encode(secrets.token_bytes(48)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    result: dict = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("授权完成，可以关掉这个页面回到终端。".encode())
            threading.Thread(target=srv.shutdown, daemon=True).start()

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 8765), H)
    url = AUTH_URL + "?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": client_id, "redirect_uri": REDIRECT,
        "scope": SCOPES, "state": state, "code_challenge": challenge,
        "code_challenge_method": "S256",
    })
    print("正在打开浏览器，请用 @<YOUR_X_HANDLE> 登录并点 Authorize app ……")
    webbrowser.open(url)
    print("如果浏览器没打开，手动访问：\n" + url)
    srv.serve_forever()

    if result.get("state") != state or "code" not in result:
        sys.exit(f"授权失败：{result.get('error', '没拿到 code')}")

    resp = requests.post(TOKEN_URL, headers={
        "Authorization": _basic_auth_header(client_id, client_sec),
        "Content-Type": "application/x-www-form-urlencoded",
    }, data={
        "grant_type": "authorization_code", "code": result["code"],
        "redirect_uri": REDIRECT, "code_verifier": verifier, "client_id": client_id,
    }, timeout=30)
    if resp.status_code != 200:
        sys.exit(f"换 token 失败 {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    if not data.get("refresh_token"):
        sys.exit("没拿到 refresh_token，检查 App 是否勾了 offline.access")

    _keychain_set(KEY_CLIENT_ID, client_id)
    _keychain_set(KEY_CLIENT_SEC, client_sec)
    _keychain_set(KEY_ACCESS, data["access_token"])
    _keychain_set(KEY_REFRESH, data["refresh_token"])

    me = requests.get("https://api.x.com/2/users/me",
                      headers={"Authorization": f"Bearer {data['access_token']}"}, timeout=30)
    who = me.json().get("data", {}).get("username", "?") if me.ok else f"(验证失败 {me.status_code})"
    print(f"完成：4 项已写入钥匙串，授权账号 @{who}，scope={data.get('scope')}")


if __name__ == "__main__":
    main()
