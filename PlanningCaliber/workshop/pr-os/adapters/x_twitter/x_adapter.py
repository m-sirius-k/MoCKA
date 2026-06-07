"""
Output Adapter OA-002: X (Twitter)
Twitter API v2 + OAuth 2.0
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

API_BASE = "https://api.twitter.com/2"


def md_to_tweet(text: str, max_chars: int = 280, url: str = "") -> list[str]:
    """
    Markdownテキストをツイート用に変換。
    長文は自動スレッド分割。
    Returns: list of tweet strings
    """
    # フロントマター・見出し記号除去
    clean = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL)
    clean = re.sub(r"^#{1,6}\s+", "", clean, flags=re.MULTILINE)
    clean = re.sub(r"\*\*(.+?)\*\*", r"\1", clean)
    clean = re.sub(r"\*(.+?)\*",     r"\1", clean)
    clean = re.sub(r"`(.+?)`",       r"\1", clean)
    clean = re.sub(r"^[-*]\s+",      "・", clean, flags=re.MULTILINE)
    clean = re.sub(r"\n{3,}",        "\n\n", clean).strip()

    url_part = f"\n\n{url}" if url else ""
    budget = max_chars - len(url_part) - 10  # スレッド番号用余白

    # 段落で分割してスレッド化
    paras = [p.strip() for p in re.split(r"\n\n+", clean) if p.strip()]
    tweets = []
    current = ""
    for para in paras:
        candidate = (current + "\n\n" + para).strip() if current else para
        if len(candidate) <= budget:
            current = candidate
        else:
            if current:
                tweets.append(current)
            # 単一段落が長すぎる場合は文で分割
            if len(para) > budget:
                sentences = re.split(r"(?<=[。！？\.\!\?])", para)
                for s in sentences:
                    if len(current + s) <= budget:
                        current = (current + s).strip()
                    else:
                        if current:
                            tweets.append(current)
                        current = s.strip()
            else:
                current = para

    if current:
        tweets.append(current)

    # スレッド番号付与 + URL付与（最後のツイートに）
    if len(tweets) > 1:
        tweets = [f"[{i+1}/{len(tweets)}] {t}" for i, t in enumerate(tweets)]
    if tweets and url:
        tweets[-1] += url_part

    return tweets or [""]


class XAdapter(OutputAdapter):
    adapter_id   = "OA-002"
    adapter_name = "X (Twitter)"

    def __init__(self):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            self.cfg = json.load(f)

    def _auth(self) -> dict:
        token = self.cfg["auth"].get("access_token", "")
        return {"Authorization": f"Bearer {token}",
                "Content-Type": "application/json"}

    # ── convert ──────────────────────────
    def convert(self, ks_record: dict, confirmed_text: str,
                url: str = "") -> dict:
        max_chars = self.cfg["defaults"].get("max_chars", 280)
        tweets = md_to_tweet(confirmed_text, max_chars=max_chars, url=url)
        return {
            "_ks_id":  ks_record["id"],
            "_tweets": tweets,
            "thread":  len(tweets) > 1,
            "count":   len(tweets),
        }

    # ── publish ───────────────────────────
    def publish(self, converted: dict) -> PublishResult:
        ks_id  = converted.get("_ks_id", "")
        tweets = converted.get("_tweets", [])
        if not self.cfg.get("enabled"):
            return self._disabled_result(ks_id)

        reply_to = None
        first_id = None
        try:
            for i, text in enumerate(tweets):
                payload = {"text": text}
                if reply_to:
                    payload["reply"] = {"in_reply_to_tweet_id": reply_to}
                r = requests.post(f"{API_BASE}/tweets",
                                  headers=self._auth(),
                                  json=payload, timeout=30)
                r.raise_for_status()
                tweet_id = r.json()["data"]["id"]
                if i == 0:
                    first_id = tweet_id
                reply_to = tweet_id

            url = (f"https://twitter.com/i/web/status/{first_id}"
                   if first_id else None)
            return PublishResult(success=True, adapter_id=self.adapter_id,
                                 ks_id=ks_id, post_id=first_id, url=url)
        except Exception as e:
            return PublishResult(success=False, adapter_id=self.adapter_id,
                                 ks_id=ks_id, error=str(e))

    # ── schedule ──────────────────────────
    def schedule(self, converted: dict, publish_at: str) -> PublishResult:
        """Twitter API v2は予約投稿未対応。スケジューラーキューへ登録。"""
        ks_id = converted.get("_ks_id", "")
        if not self.cfg.get("enabled"):
            return self._disabled_result(ks_id)
        # scheduler/queue.json に委譲
        return PublishResult(success=True, adapter_id=self.adapter_id,
                             ks_id=ks_id, scheduled_at=publish_at,
                             error=None,
                             url=None,
                             post_id=f"queued:{publish_at}")

    # ── health_check ──────────────────────
    def health_check(self) -> HealthResult:
        if not self.cfg.get("enabled"):
            return self._disabled_health()
        try:
            r = requests.get(f"{API_BASE}/users/me",
                             headers=self._auth(), timeout=10)
            remaining = int(r.headers.get("x-rate-limit-remaining", -1))
            return HealthResult(adapter_id=self.adapter_id,
                                adapter_name=self.adapter_name,
                                status="ok" if r.status_code == 200 else "error",
                                http_status=r.status_code,
                                rate_limit_remaining=remaining)
        except Exception as e:
            return HealthResult(adapter_id=self.adapter_id,
                                adapter_name=self.adapter_name,
                                status="unreachable", error=str(e))


if __name__ == "__main__":
    a = XAdapter()
    sample_rec  = {"id": "KS_001", "title": "MoCKA v4", "tags": []}
    sample_text = """# MoCKA v4 リリース

PR-OSは知識配信レイヤーです。

AI Gateで品質を保証し、WordPress・X・Instagramへ自動配信。

KS_NNN体系で原本を管理し、バージョン履歴も完全保持します。
"""
    converted = a.convert(sample_rec, sample_text,
                          url="https://example.com/mocka-v4")
    print(f"ツイート数: {converted['count']}")
    for i, t in enumerate(converted["_tweets"]):
        print(f"\n--- Tweet {i+1} ({len(t)}文字) ---")
        print(t)
