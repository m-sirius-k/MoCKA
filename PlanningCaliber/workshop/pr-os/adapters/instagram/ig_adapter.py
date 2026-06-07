"""
Output Adapter OA-003: Instagram
Meta Graph API + Instagram Business Account
"""
import json
import os
import re
import sys
import requests
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_adapter import OutputAdapter, PublishResult, HealthResult

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

GRAPH_BASE = "https://graph.facebook.com/v19.0"


def md_to_caption(text: str, max_chars: int = 2200) -> str:
    """Markdown → Instagram キャプション変換"""
    cap = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL)
    # 見出しを太字風に（Instagramはマークアップ非対応のため装飾）
    cap = re.sub(r"^#{1,3}\s+(.+)$", r"【\1】", cap, flags=re.MULTILINE)
    cap = re.sub(r"\*\*(.+?)\*\*", r"\1", cap)
    cap = re.sub(r"\*(.+?)\*",     r"\1", cap)
    cap = re.sub(r"`(.+?)`",       r"\1", cap)
    cap = re.sub(r"^[-*]\s+",      "▶ ", cap, flags=re.MULTILINE)
    cap = re.sub(r"\n{3,}",        "\n\n", cap).strip()
    if len(cap) > max_chars:
        cap = cap[:max_chars - 3] + "..."
    return cap


def extract_hashtags(tags: list) -> str:
    """タグリストをInstagramハッシュタグに変換"""
    if not tags:
        return ""
    return "\n\n" + " ".join(f"#{t.replace(' ', '_')}" for t in tags)


class InstagramAdapter(OutputAdapter):
    adapter_id   = "OA-003"
    adapter_name = "Instagram"

    def __init__(self):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            self.cfg = json.load(f)
        self.token   = self.cfg["auth"].get("access_token", "")
        self.acct_id = self.cfg["auth"].get("instagram_business_account_id", "")

    def _params(self, extra: dict = None) -> dict:
        p = {"access_token": self.token}
        if extra:
            p.update(extra)
        return p

    # ── convert ──────────────────────────
    def convert(self, ks_record: dict, confirmed_text: str,
                image_url: str = "") -> dict:
        max_chars = self.cfg["defaults"].get("caption_max_chars", 2200)
        caption   = md_to_caption(confirmed_text, max_chars - 200)
        hashtags  = extract_hashtags(ks_record.get("tags", []))
        return {
            "_ks_id":     ks_record["id"],
            "caption":    caption + hashtags,
            "image_url":  image_url,
            "media_type": self.cfg["defaults"].get("media_type", "IMAGE"),
        }

    # ── publish ───────────────────────────
    def publish(self, converted: dict) -> PublishResult:
        ks_id = converted.get("_ks_id", "")
        if not self.cfg.get("enabled"):
            return self._disabled_result(ks_id)
        if not converted.get("image_url"):
            return PublishResult(success=False, adapter_id=self.adapter_id,
                                 ks_id=ks_id,
                                 error="image_url is required for Instagram posts")
        try:
            # Step 1: メディアオブジェクト作成
            r1 = requests.post(
                f"{GRAPH_BASE}/{self.acct_id}/media",
                params=self._params({
                    "image_url": converted["image_url"],
                    "caption":   converted["caption"],
                }),
                timeout=30
            )
            r1.raise_for_status()
            media_id = r1.json()["id"]

            # Step 2: 公開
            r2 = requests.post(
                f"{GRAPH_BASE}/{self.acct_id}/media_publish",
                params=self._params({"creation_id": media_id}),
                timeout=30
            )
            r2.raise_for_status()
            post_id = r2.json()["id"]
            return PublishResult(success=True, adapter_id=self.adapter_id,
                                 ks_id=ks_id, post_id=post_id)
        except Exception as e:
            return PublishResult(success=False, adapter_id=self.adapter_id,
                                 ks_id=ks_id, error=str(e))

    # ── schedule ──────────────────────────
    def schedule(self, converted: dict, publish_at: str) -> PublishResult:
        """Graph API の予約機能（published=false + scheduled_publish_time）"""
        ks_id = converted.get("_ks_id", "")
        if not self.cfg.get("enabled"):
            return self._disabled_result(ks_id)
        if not converted.get("image_url"):
            return PublishResult(success=False, adapter_id=self.adapter_id,
                                 ks_id=ks_id, error="image_url required")
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(publish_at.replace("Z", "+00:00"))
            unix_ts = int(dt.timestamp())
            r = requests.post(
                f"{GRAPH_BASE}/{self.acct_id}/media",
                params=self._params({
                    "image_url":              converted["image_url"],
                    "caption":                converted["caption"],
                    "published":              "false",
                    "scheduled_publish_time": unix_ts,
                }),
                timeout=30
            )
            r.raise_for_status()
            media_id = r.json()["id"]
            return PublishResult(success=True, adapter_id=self.adapter_id,
                                 ks_id=ks_id, post_id=media_id,
                                 scheduled_at=publish_at)
        except Exception as e:
            return PublishResult(success=False, adapter_id=self.adapter_id,
                                 ks_id=ks_id, error=str(e))

    # ── health_check ──────────────────────
    def health_check(self) -> HealthResult:
        if not self.cfg.get("enabled"):
            return self._disabled_health()
        try:
            r = requests.get(
                f"{GRAPH_BASE}/{self.acct_id}",
                params=self._params({"fields": "id,name"}),
                timeout=10
            )
            return HealthResult(adapter_id=self.adapter_id,
                                adapter_name=self.adapter_name,
                                status="ok" if r.status_code == 200 else "error",
                                http_status=r.status_code)
        except Exception as e:
            return HealthResult(adapter_id=self.adapter_id,
                                adapter_name=self.adapter_name,
                                status="unreachable", error=str(e))


if __name__ == "__main__":
    a = InstagramAdapter()
    rec  = {"id": "KS_001", "title": "MoCKA v4", "tags": ["mocka", "ai", "release"]}
    text = "# MoCKA v4\n\nAI Gateで品質保証。PR-OSで全媒体配信。\n\n- 自動校正\n- KS管理\n- WordPress/X連携\n"
    print(a.convert(rec, text, image_url="https://example.com/img.jpg"))
