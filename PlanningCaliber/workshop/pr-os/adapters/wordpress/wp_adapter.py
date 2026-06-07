"""
Output Adapter OA-001: WordPress
WordPress REST API v2 + Application Password認証
"""
import json
import os
import re
import sys
import requests
from base64 import b64encode
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_adapter import OutputAdapter, PublishResult, HealthResult

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


# ─────────────────────────────────────────
# Markdown → HTML 変換
# ─────────────────────────────────────────
def md_to_html(text: str) -> str:
    h = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL).strip()
    h = re.sub(r"^#### (.+)$", r"<h4>\1</h4>", h, flags=re.MULTILINE)
    h = re.sub(r"^### (.+)$",  r"<h3>\1</h3>", h, flags=re.MULTILINE)
    h = re.sub(r"^## (.+)$",   r"<h2>\1</h2>", h, flags=re.MULTILINE)
    h = re.sub(r"^# (.+)$",    r"<h1>\1</h1>", h, flags=re.MULTILINE)
    h = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", h)
    h = re.sub(r"\*\*(.+?)\*\*",     r"<strong>\1</strong>", h)
    h = re.sub(r"\*(.+?)\*",         r"<em>\1</em>", h)
    h = re.sub(r"`(.+?)`",           r"<code>\1</code>", h)
    h = re.sub(r"^- (.+)$", r"<li>\1</li>", h, flags=re.MULTILINE)
    h = re.sub(r"(<li>(?:.*\n?)*?</li>\n?)+",
               lambda m: f"<ul>\n{m.group()}</ul>\n", h)
    h = re.sub(r"^\d+\. (.+)$", r"<li>\1</li>", h, flags=re.MULTILINE)
    blocks = re.split(r"\n{2,}", h.strip())
    result = []
    for b in blocks:
        b = b.strip()
        if b and not re.match(r"^<[hH\d]|^<ul|^<ol|^<li|^<blockquote", b):
            b = f"<p>{b}</p>"
        result.append(b)
    return "\n\n".join(result)


# ─────────────────────────────────────────
class WordPressAdapter(OutputAdapter):
    adapter_id   = "OA-001"
    adapter_name = "WordPress"

    def __init__(self):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            self.cfg = json.load(f)
        base = self.cfg.get("api_endpoint", "").rstrip("/")
        self.api = f"{base}/wp-json/wp/v2"

    def _auth(self) -> dict:
        u = self.cfg["auth"]["username"]
        p = self.cfg["auth"]["password"]
        token = b64encode(f"{u}:{p}".encode()).decode()
        return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

    # ── convert ──────────────────────────
    def convert(self, ks_record: dict, confirmed_text: str) -> dict:
        return {
            "_ks_id":   ks_record["id"],
            "title":    ks_record["title"],
            "content":  md_to_html(confirmed_text),
            "status":   self.cfg["defaults"].get("status", "draft"),
            "tags":     ks_record.get("tags", []),
            "author":   self.cfg["defaults"].get("author_id", 1),
        }

    # ── publish ───────────────────────────
    def publish(self, converted: dict) -> PublishResult:
        ks_id = converted.get("_ks_id", "")
        if not self.cfg.get("enabled"):
            return self._disabled_result(ks_id)
        try:
            r = requests.post(f"{self.api}/posts",
                              headers=self._auth(),
                              json={k: v for k, v in converted.items() if not k.startswith("_")},
                              timeout=30)
            r.raise_for_status()
            d = r.json()
            return PublishResult(success=True, adapter_id=self.adapter_id,
                                 ks_id=ks_id, post_id=str(d.get("id")), url=d.get("link"))
        except Exception as e:
            return PublishResult(success=False, adapter_id=self.adapter_id,
                                 ks_id=ks_id, error=str(e))

    # ── schedule ──────────────────────────
    def schedule(self, converted: dict, publish_at: str) -> PublishResult:
        ks_id = converted.get("_ks_id", "")
        if not self.cfg.get("enabled"):
            return self._disabled_result(ks_id)
        payload = {**{k: v for k, v in converted.items() if not k.startswith("_")},
                   "status": "future", "date": publish_at}
        try:
            r = requests.post(f"{self.api}/posts", headers=self._auth(),
                              json=payload, timeout=30)
            r.raise_for_status()
            d = r.json()
            return PublishResult(success=True, adapter_id=self.adapter_id,
                                 ks_id=ks_id, post_id=str(d.get("id")),
                                 scheduled_at=publish_at)
        except Exception as e:
            return PublishResult(success=False, adapter_id=self.adapter_id,
                                 ks_id=ks_id, error=str(e))

    # ── health_check ──────────────────────
    def health_check(self) -> HealthResult:
        if not self.cfg.get("enabled"):
            return self._disabled_health()
        try:
            r = requests.get(self.api, timeout=10)
            return HealthResult(adapter_id=self.adapter_id,
                                adapter_name=self.adapter_name,
                                status="ok" if r.status_code == 200 else "error",
                                http_status=r.status_code)
        except Exception as e:
            return HealthResult(adapter_id=self.adapter_id,
                                adapter_name=self.adapter_name,
                                status="unreachable", error=str(e))


if __name__ == "__main__":
    a = WordPressAdapter()
    print(json.dumps(a.health_check().to_dict(), ensure_ascii=False, indent=2))
    sample_rec  = {"id": "KS_001", "title": "テスト", "tags": ["test"]}
    sample_text = "# テスト\n\nHello **World**.\n\n- item1\n- item2\n"
    print(json.dumps(a.convert(sample_rec, sample_text), ensure_ascii=False, indent=2))
