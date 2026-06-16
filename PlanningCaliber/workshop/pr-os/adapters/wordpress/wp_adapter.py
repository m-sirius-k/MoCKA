"""
Output Adapter OA-001: WordPress
WordPress REST API v2 + Application Password認証
SEO-CENTER拡張対応版：SEO metadata / HTML body / JSON-LD サポート
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
# Markdown → HTML 変換（SEO-CENTER非使用時のフォールバック）
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


def _inject_json_ld(html_body: str, json_ld: dict) -> str:
    """HTML bodyの先頭にJSON-LDスクリプトタグを挿入"""
    if not json_ld:
        return html_body
    script = (
        '<script type="application/ld+json">\n'
        + json.dumps(json_ld, ensure_ascii=False, indent=2)
        + '\n</script>\n\n'
    )
    return script + html_body


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

    def _resolve_tags(self, tag_names: list[str]) -> list[int]:
        """タグ名 → WordPress タグID変換（存在しなければ作成）"""
        if not tag_names:
            return []
        ids = []
        try:
            for name in tag_names:
                r = requests.get(f"{self.api}/tags",
                                 params={"search": name, "per_page": 1},
                                 headers=self._auth(), timeout=10)
                data = r.json()
                if data:
                    ids.append(data[0]["id"])
                else:
                    cr = requests.post(f"{self.api}/tags",
                                       headers=self._auth(),
                                       json={"name": name}, timeout=10)
                    if cr.status_code in (200, 201):
                        ids.append(cr.json()["id"])
        except Exception:
            pass
        return ids

    def _resolve_category(self, category_name: str) -> list[int]:
        """カテゴリ名 → WordPress カテゴリID変換（存在しなければ作成）"""
        if not category_name:
            return []
        try:
            r = requests.get(f"{self.api}/categories",
                             params={"search": category_name, "per_page": 1},
                             headers=self._auth(), timeout=10)
            data = r.json()
            if data:
                return [data[0]["id"]]
            cr = requests.post(f"{self.api}/categories",
                               headers=self._auth(),
                               json={"name": category_name}, timeout=10)
            if cr.status_code in (200, 201):
                return [cr.json()["id"]]
        except Exception:
            pass
        return []

    # ── convert ──────────────────────────────────────────
    def convert(self, ks_record: dict, confirmed_text: str,
                seo_result=None) -> dict:
        """
        原本を WordPress投稿フォーマットに変換。

        seo_result (SEOResult) が渡された場合:
          - html:        SEO-CENTER生成HTMLを使用
          - slug:        SEO最適スラッグを使用
          - description: meta descriptionをexcerptとして設定
          - json_ld:     HTML先頭に<script type="application/ld+json">を挿入

        渡されない場合: フォールバックとしてmd_to_htmlを使用
        """
        if seo_result is not None:
            html_body = _inject_json_ld(seo_result.html, seo_result.json_ld)
            slug      = seo_result.slug
            excerpt   = seo_result.description
            tags_raw  = seo_result.tags
            category  = seo_result.category
        else:
            html_body = md_to_html(confirmed_text)
            slug      = ""
            excerpt   = ""
            tags_raw  = ks_record.get("tags", [])
            category  = ks_record.get("category", "")

        return {
            "_ks_id":    ks_record["id"],
            "_tags_raw": tags_raw,
            "_category": category,
            "title":     ks_record["title"],
            "content":   html_body,
            "excerpt":   excerpt,
            "slug":      slug,
            "status":    self.cfg["defaults"].get("status", "draft"),
            "author":    self.cfg["defaults"].get("author_id", 1),
        }

    def _build_payload(self, converted: dict) -> dict:
        """WordPress REST API投稿ペイロードを構築（タグ/カテゴリIDを解決）"""
        payload = {k: v for k, v in converted.items()
                   if not k.startswith("_") and v != ""}

        # タグID解決
        tag_ids = self._resolve_tags(converted.get("_tags_raw", []))
        if tag_ids:
            payload["tags"] = tag_ids

        # カテゴリID解決
        cat_ids = self._resolve_category(converted.get("_category", ""))
        if cat_ids:
            payload["categories"] = cat_ids

        return payload

    # ── publish ──────────────────────────────────────────
    def publish(self, converted: dict) -> PublishResult:
        ks_id = converted.get("_ks_id", "")
        if not self.cfg.get("enabled"):
            return self._disabled_result(ks_id)
        try:
            payload = self._build_payload(converted)
            r = requests.post(f"{self.api}/posts",
                              headers=self._auth(),
                              json=payload, timeout=30)
            r.raise_for_status()
            d = r.json()
            return PublishResult(success=True, adapter_id=self.adapter_id,
                                 ks_id=ks_id, post_id=str(d.get("id")),
                                 url=d.get("link"))
        except Exception as e:
            return PublishResult(success=False, adapter_id=self.adapter_id,
                                 ks_id=ks_id, error=str(e))

    # ── schedule ─────────────────────────────────────────
    def schedule(self, converted: dict, publish_at: str) -> PublishResult:
        ks_id = converted.get("_ks_id", "")
        if not self.cfg.get("enabled"):
            return self._disabled_result(ks_id)
        try:
            payload = {**self._build_payload(converted),
                       "status": "future", "date": publish_at}
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

    # ── health_check ─────────────────────────────────────
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
    sample_rec  = {"id": "KS_001", "title": "テスト", "tags": ["test"], "category": "dev"}
    sample_text = "# テスト\n\n## 概要\n\nHello **World**.\n\n- item1\n- item2\n\n## 結論\n\nOK.\n"
    print(json.dumps(a.convert(sample_rec, sample_text), ensure_ascii=False, indent=2))
