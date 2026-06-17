"""
LinkedIn Adapter — PR-OS Output Adapter
LinkedIn REST API (OAuth 2.0) でテキスト投稿・記事投稿を実装する。

投稿タイプ:
  TEXT_POST  — テキスト投稿（最大3000文字）
  ARTICLE    — 記事投稿（タイトル + 本文 + URL）

対象アカウント: きむら博士のLinkedIn プロフィール（config.json: defaults.author_urn）

NOTE: 本番投稿前に config.json の enabled を true にし、
      OAuth2 アクセストークンを設定すること。
      テスト時は visibility を CONNECTIONS に変更して限定公開で確認すること。
"""
import json
import os
import re
from typing import Optional

try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_adapter import OutputAdapter, PublishResult, HealthResult

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# LinkedIn API v2 エンドポイント
_API_BASE   = "https://api.linkedin.com/v2"
_UGC_POSTS  = f"{_API_BASE}/ugcPosts"
_USERINFO   = f"{_API_BASE}/userinfo"


def _load_config() -> dict:
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _auth_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }


def _text_to_linkedin_body(text: str, max_len: int = 2900) -> str:
    """Markdown本文をLinkedIn投稿向けプレーンテキストに変換する"""
    # フロントマター除去
    body = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL).strip()
    # Markdown記法除去（見出し・強調・リンク・コードブロック）
    body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    body = re.sub(r"^#{1,4} ", "", body, flags=re.MULTILINE)
    body = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", body)
    body = re.sub(r"`(.+?)`", r"\1", body)
    body = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    if len(body) > max_len:
        body = body[:max_len - 3] + "..."
    return body


class LinkedInAdapter(OutputAdapter):
    """LinkedIn REST API Adapter"""

    adapter_id   = "linkedin"
    adapter_name = "LinkedIn"

    def __init__(self):
        self._config = _load_config()

    def _is_enabled(self) -> bool:
        return self._config.get("enabled", False)

    def _token(self) -> str:
        return self._config.get("auth", {}).get("access_token", "")

    def _author_urn(self) -> str:
        return self._config.get("defaults", {}).get("author_urn", "")

    def _visibility(self) -> str:
        return self._config.get("defaults", {}).get("visibility", "PUBLIC")

    def _post_type(self) -> str:
        return self._config.get("defaults", {}).get("post_type", "TEXT_POST")

    # ── convert ──────────────────────────────────────────────
    def convert(self, ks_record: dict, confirmed_text: str, **kwargs) -> dict:
        """
        KSレコード + 確定テキストを LinkedIn 投稿ペイロードに変換する。
        post_type に応じて TEXT_POST または ARTICLE 形式を選択。
        """
        title      = ks_record.get("title", "")
        tags       = ks_record.get("tags", [])
        post_type  = kwargs.get("post_type", self._post_type())

        # ハッシュタグ生成（タグ → #tag）
        hashtags = " ".join(f"#{t}" for t in tags if t.isalnum() or "_" in t)
        body_text = _text_to_linkedin_body(confirmed_text)

        if post_type == "ARTICLE":
            # 記事投稿: タイトル + 要約 + URLが必要
            summary = ks_record.get("summary", body_text[:200])
            payload = {
                "post_type":    "ARTICLE",
                "title":        title,
                "commentary":   f"{summary}\n\n{hashtags}".strip(),
                "article_url":  kwargs.get("url", ""),
                "thumbnail_url": "",
            }
        else:
            # テキスト投稿: 本文 + ハッシュタグ
            text = f"{title}\n\n{body_text}"
            if hashtags:
                text += f"\n\n{hashtags}"
            payload = {
                "post_type": "TEXT_POST",
                "text":      text[:3000],
            }

        payload["ks_id"]      = ks_record.get("id", "")
        payload["visibility"] = kwargs.get("visibility", self._visibility())
        return payload

    # ── publish ──────────────────────────────────────────────
    def publish(self, converted: dict) -> PublishResult:
        ks_id = converted.get("ks_id", "")

        if not self._is_enabled():
            return self._disabled_result(ks_id)

        if not _REQUESTS_AVAILABLE:
            return PublishResult(
                success=False, adapter_id=self.adapter_id, ks_id=ks_id,
                error="requests ライブラリが必要です: pip install requests"
            )

        token      = self._token()
        author_urn = self._author_urn()
        visibility = converted.get("visibility", "PUBLIC")

        if not token or not author_urn:
            return PublishResult(
                success=False, adapter_id=self.adapter_id, ks_id=ks_id,
                error="access_token と author_urn を config.json に設定してください"
            )

        post_type = converted.get("post_type", "TEXT_POST")
        body      = self._build_api_body(converted, author_urn, visibility)

        try:
            resp = _requests.post(
                _UGC_POSTS,
                headers=_auth_headers(token),
                json=body,
                timeout=15,
            )
            resp.raise_for_status()
            post_id  = resp.headers.get("x-restli-id", "")
            post_url = f"https://www.linkedin.com/feed/update/{post_id}" if post_id else ""
            return PublishResult(
                success=True, adapter_id=self.adapter_id,
                ks_id=ks_id, post_id=post_id, url=post_url
            )
        except Exception as e:
            return PublishResult(
                success=False, adapter_id=self.adapter_id,
                ks_id=ks_id, error=str(e)
            )

    def _build_api_body(self, converted: dict, author_urn: str,
                        visibility: str) -> dict:
        """LinkedIn UGC Posts API v2 リクエストボディを組み立てる"""
        post_type = converted.get("post_type", "TEXT_POST")
        vis_code  = "PUBLIC" if visibility == "PUBLIC" else "CONNECTIONS"

        if post_type == "ARTICLE":
            return {
                "author":     author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": converted.get("commentary", "")
                        },
                        "shareMediaCategory": "ARTICLE",
                        "media": [{
                            "status":      "READY",
                            "description": {"text": converted.get("commentary", "")[:256]},
                            "originalUrl": converted.get("article_url", ""),
                            "title":       {"text": converted.get("title", "")[:200]},
                        }]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": vis_code
                }
            }
        else:
            return {
                "author":     author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": converted.get("text", "")
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": vis_code
                }
            }

    # ── schedule ─────────────────────────────────────────────
    def schedule(self, converted: dict, publish_at: str) -> PublishResult:
        """LinkedIn API は予約投稿非対応のため即時投稿にフォールバック"""
        print(f"[LinkedIn] schedule() → LinkedIn APIは予約投稿非対応。即時投稿します。")
        return self.publish(converted)

    # ── health_check ─────────────────────────────────────────
    def health_check(self) -> HealthResult:
        if not self._is_enabled():
            return self._disabled_health()

        if not _REQUESTS_AVAILABLE:
            return HealthResult(
                adapter_id=self.adapter_id, adapter_name=self.adapter_name,
                status="error", error="requests ライブラリ未インストール"
            )

        token = self._token()
        if not token:
            return HealthResult(
                adapter_id=self.adapter_id, adapter_name=self.adapter_name,
                status="error", error="access_token が設定されていません"
            )

        try:
            resp = _requests.get(
                _USERINFO,
                headers=_auth_headers(token),
                timeout=10
            )
            if resp.status_code == 200:
                return HealthResult(
                    adapter_id=self.adapter_id, adapter_name=self.adapter_name,
                    status="ok", http_status=200
                )
            else:
                return HealthResult(
                    adapter_id=self.adapter_id, adapter_name=self.adapter_name,
                    status="error", http_status=resp.status_code,
                    error=f"HTTP {resp.status_code}"
                )
        except Exception as e:
            return HealthResult(
                adapter_id=self.adapter_id, adapter_name=self.adapter_name,
                status="unreachable", error=str(e)
            )
