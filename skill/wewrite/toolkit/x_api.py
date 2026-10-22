"""X Articles draft API + Keychain token refresh.

Never calls POST /2/articles/{id}/publish.
Tokens live in macOS Keychain, same pattern as wewrite-wechat-secret.
"""

from __future__ import annotations

import base64
import json
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


TOKEN_URL = "https://api.x.com/2/oauth2/token"
DRAFT_URL = "https://api.x.com/2/articles/draft"
MEDIA_UPLOAD_URL = "https://api.x.com/2/media/upload"
ME_URL = "https://api.x.com/2/users/me"

KEY_CLIENT_ID = "x-articles-client-id"
KEY_CLIENT_SEC = "x-articles-client-secret"
KEY_ACCESS = "x-articles-access-token"
KEY_REFRESH = "x-articles-refresh-token"


class XAuthError(RuntimeError):
    pass


class XApiError(RuntimeError):
    def __init__(self, status: int, body: str):
        self.status = status
        self.body = body
        super().__init__(f"X API error {status}: {body[:400]}")


def _keychain_get(service: str) -> str:
    r = subprocess.run(
        ["security", "find-generic-password", "-a", _user(), "-s", service, "-w"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise XAuthError(f"Keychain 里没有 {service}。先配 OAuth 2.0。")
    value = r.stdout.strip()
    if not value:
        raise XAuthError(f"Keychain {service} 是空的")
    return value


def _keychain_set(service: str, value: str) -> None:
    r = subprocess.run(
        [
            "security",
            "add-generic-password",
            "-a",
            _user(),
            "-s",
            service,
            "-w",
            value,
            "-U",
        ],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise XAuthError(f"写入 Keychain {service} 失败: {r.stderr.strip()[:200]}")


def _user() -> str:
    r = subprocess.run(["id", "-un"], capture_output=True, text=True, check=True)
    return r.stdout.strip()


KEY_O1 = (
    "x-articles-oauth1-api-key",
    "x-articles-oauth1-api-secret",
    "x-articles-oauth1-access-token",
    "x-articles-oauth1-access-secret",
)


def _oauth1():
    """OAuth 1.0a user context, used when all four oauth1 items are in Keychain."""
    vals = []
    for k in KEY_O1:
        r = subprocess.run(
            ["security", "find-generic-password", "-a", _user(), "-s", k, "-w"],
            capture_output=True, text=True,
        )
        if r.returncode != 0 or not r.stdout.strip():
            return None
        vals.append(r.stdout.strip())
    from requests_oauthlib import OAuth1
    return OAuth1(vals[0], vals[1], vals[2], vals[3])


def _basic_auth_header(client_id: str, client_sec: str) -> str:
    raw = f"{client_id}:{client_sec}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def refresh_access_token() -> str:
    client_id = _keychain_get(KEY_CLIENT_ID)
    client_sec = _keychain_get(KEY_CLIENT_SEC)
    refresh = _keychain_get(KEY_REFRESH)
    resp = requests.post(
        TOKEN_URL,
        headers={
            "Authorization": _basic_auth_header(client_id, client_sec),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh,
            "client_id": client_id,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        raise XAuthError(f"刷新 token 失败 {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    access = data.get("access_token")
    if not access:
        raise XAuthError(f"刷新结果没有 access_token: {data}")
    _keychain_set(KEY_ACCESS, access)
    new_refresh = data.get("refresh_token")
    if new_refresh:
        _keychain_set(KEY_REFRESH, new_refresh)
    return access


def get_user_access_token(force_refresh: bool = False) -> str:
    if force_refresh:
        return refresh_access_token()
    return _keychain_get(KEY_ACCESS)


def _request(
    method: str,
    url: str,
    *,
    json_body: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    retry_refresh: bool = True,
) -> requests.Response:
    o1 = _oauth1()
    if o1 is not None:
        return requests.request(
            method, url, auth=o1, json=json_body, params=params, timeout=30
        )
    token = get_user_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    resp = requests.request(
        method, url, headers=headers, json=json_body, params=params, timeout=30
    )
    if resp.status_code in (401, 403) and retry_refresh:
        token = refresh_access_token()
        headers["Authorization"] = f"Bearer {token}"
        resp = requests.request(
            method, url, headers=headers, json=json_body, params=params, timeout=30
        )
    return resp


def verify_me() -> Dict[str, Any]:
    resp = _request("GET", ME_URL, params={"user.fields": "username,name,verified"})
    if resp.status_code != 200:
        raise XApiError(resp.status_code, resp.text)
    return resp.json()


@dataclass
class DraftResult:
    article_id: str
    title: str
    raw: Dict[str, Any]


def upload_image(path: str) -> str:
    """Upload one image via POST /2/media/upload (multipart, tweet_image). Returns media id.

    Needs media.write (OAuth 2.0) or an OAuth 1.0a user token. Images must be <= 5 MB.
    """
    import mimetypes
    from pathlib import Path as _P

    fp = _P(path)
    if not fp.exists():
        raise ValueError(f"图片不存在: {path}")
    if fp.stat().st_size > 5 * 1024 * 1024:
        raise ValueError(f"图片超过 5 MB（X tweet_image 上限）: {path}")
    mime = mimetypes.guess_type(fp.name)[0] or "application/octet-stream"

    def _send(auth=None, headers=None):
        with fp.open("rb") as fh:
            return requests.post(
                MEDIA_UPLOAD_URL,
                auth=auth,
                headers=headers or {},
                files={"media": (fp.name, fh, mime)},
                data={"media_category": "tweet_image"},
                timeout=120,
            )

    o1 = _oauth1()
    if o1 is not None:
        resp = _send(auth=o1)
    else:
        resp = _send(headers={"Authorization": f"Bearer {get_user_access_token()}"})
        if resp.status_code in (401, 403):
            resp = _send(headers={"Authorization": f"Bearer {refresh_access_token()}"})
    if resp.status_code not in (200, 201):
        raise XApiError(resp.status_code, resp.text)
    data = resp.json()
    inner = data.get("data") or data
    media_id = inner.get("id") or inner.get("media_id_string") or inner.get("media_id")
    if not media_id:
        raise XApiError(resp.status_code, f"missing media id: {json.dumps(data)[:400]}")
    return str(media_id)


def create_article_draft(
    title: str,
    content_state: Dict[str, Any],
    cover_media_id: Optional[str] = None,
) -> DraftResult:
    """Create an unpublished X Article draft. Does not publish.

    The Articles API has no update/delete endpoint (only POST /2/articles/draft and
    POST /2/articles/{id}/publish), so every push creates a NEW draft.
    """
    if not title or not title.strip():
        raise ValueError("title 不能空")
    if not content_state.get("blocks"):
        raise ValueError("content_state.blocks 不能空")
    for ent in content_state.get("entities") or []:
        for it in (ent.get("value", {}).get("data", {}) or {}).get("media_items") or []:
            if not str(it.get("media_id", "")).isdigit():
                raise ValueError(f"图片还没上传，media_id 无效: {it.get('media_id')}")
    payload: Dict[str, Any] = {
        "title": title.strip(),
        "content_state": content_state,
    }
    if cover_media_id:
        payload["cover_media"] = {"media_category": "tweet_image", "media_id": str(cover_media_id)}
    resp = _request("POST", DRAFT_URL, json_body=payload)
    if resp.status_code not in (200, 201):
        raise XApiError(resp.status_code, resp.text)
    data = resp.json()
    inner = data.get("data") or data
    article_id = inner.get("id") or inner.get("article_id")
    if not article_id:
        raise XApiError(resp.status_code, f"missing article id: {json.dumps(data)[:400]}")
    return DraftResult(
        article_id=str(article_id),
        title=inner.get("title") or title,
        raw=data,
    )
