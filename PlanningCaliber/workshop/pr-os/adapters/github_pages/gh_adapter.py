"""
Output Adapter OA-005: GitHub Pages
GitHub Contents API でMarkdownをリポジトリにプッシュ → GitHub Pages公開
"""
import base64
import json
import os
import sys
import requests
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_adapter import OutputAdapter, PublishResult, HealthResult

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
API_BASE    = "https://api.github.com"


class GitHubPagesAdapter(OutputAdapter):
    adapter_id   = "OA-005"
    adapter_name = "GitHub Pages"

    def __init__(self):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            self.cfg = json.load(f)
        self.owner  = self.cfg["repo"]["owner"]
        self.repo   = self.cfg["repo"]["name"]
        self.branch = self.cfg["repo"].get("branch", "main")
        self.path   = self.cfg["repo"].get("content_path", "content/")

    def _headers(self) -> dict:
        return {
            "Authorization": f"token {self.cfg['auth']['token']}",
            "Accept":        "application/vnd.github.v3+json",
            "Content-Type":  "application/json"
        }

    def _file_path(self, ks_id: str) -> str:
        slug = ks_id.lower().replace("_", "-")
        return f"{self.path.rstrip('/')}/{slug}.md"

    def _get_existing_sha(self, file_path: str) -> str | None:
        """既存ファイルのSHAを取得（更新時に必要）"""
        try:
            r = requests.get(
                f"{API_BASE}/repos/{self.owner}/{self.repo}/contents/{file_path}",
                headers=self._headers(),
                params={"ref": self.branch},
                timeout=15
            )
            if r.status_code == 200:
                return r.json().get("sha")
        except Exception:
            pass
        return None

    # ── convert ──────────────────────────
    def convert(self, ks_record: dict, confirmed_text: str) -> dict:
        """Jekyll/Hugo フロントマター付きMarkdownを生成"""
        slug    = ks_record["id"].lower().replace("_", "-")
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        tags    = ks_record.get("tags", [])
        cat     = ks_record.get("category", "")

        # フロントマターが既にあれば置換、なければ追加
        import re
        has_fm = confirmed_text.strip().startswith("---")
        if has_fm:
            content = confirmed_text
        else:
            fm = (f"---\n"
                  f"layout: post\n"
                  f"title: \"{ks_record['title']}\"\n"
                  f"date: {now_str}\n"
                  f"categories: [{cat}]\n"
                  f"tags: [{', '.join(tags)}]\n"
                  f"ks_id: {ks_record['id']}\n"
                  f"---\n\n")
            content = fm + confirmed_text

        return {
            "_ks_id":    ks_record["id"],
            "_slug":     slug,
            "content":   content,
            "file_path": self._file_path(ks_record["id"]),
            "message":   f"PR-OS: publish {ks_record['id']} - {ks_record['title']}"
        }

    # ── publish ───────────────────────────
    def publish(self, converted: dict) -> PublishResult:
        ks_id = converted.get("_ks_id", "")
        if not self.cfg.get("enabled"):
            return self._disabled_result(ks_id)

        file_path = converted["file_path"]
        content_b64 = base64.b64encode(
            converted["content"].encode("utf-8")
        ).decode()
        sha = self._get_existing_sha(file_path)

        payload = {
            "message": converted["message"],
            "content": content_b64,
            "branch":  self.branch,
        }
        if sha:
            payload["sha"] = sha  # 更新の場合は必須

        try:
            r = requests.put(
                f"{API_BASE}/repos/{self.owner}/{self.repo}/contents/{file_path}",
                headers=self._headers(),
                json=payload,
                timeout=30
            )
            r.raise_for_status()
            html_url = r.json().get("content", {}).get("html_url")
            pages_url = (f"https://{self.owner}.github.io/{self.repo}/"
                         f"{converted['_slug']}")
            return PublishResult(success=True, adapter_id=self.adapter_id,
                                 ks_id=ks_id, url=pages_url,
                                 post_id=file_path)
        except Exception as e:
            return PublishResult(success=False, adapter_id=self.adapter_id,
                                 ks_id=ks_id, error=str(e))

    # ── schedule ──────────────────────────
    def schedule(self, converted: dict, publish_at: str) -> PublishResult:
        """GitHub Pages に予約投稿機能はないため、スケジューラーキューへ登録"""
        ks_id = converted.get("_ks_id", "")
        if not self.cfg.get("enabled"):
            return self._disabled_result(ks_id)
        return PublishResult(success=True, adapter_id=self.adapter_id,
                             ks_id=ks_id, scheduled_at=publish_at,
                             post_id=f"queued:{publish_at}")

    # ── health_check ──────────────────────
    def health_check(self) -> HealthResult:
        if not self.cfg.get("enabled"):
            return self._disabled_health()
        try:
            r = requests.get(
                f"{API_BASE}/repos/{self.owner}/{self.repo}",
                headers=self._headers(),
                timeout=10
            )
            return HealthResult(adapter_id=self.adapter_id,
                                adapter_name=self.adapter_name,
                                status="ok" if r.status_code == 200 else "error",
                                http_status=r.status_code,
                                rate_limit_remaining=int(
                                    r.headers.get("X-RateLimit-Remaining", -1)))
        except Exception as e:
            return HealthResult(adapter_id=self.adapter_id,
                                adapter_name=self.adapter_name,
                                status="unreachable", error=str(e))
