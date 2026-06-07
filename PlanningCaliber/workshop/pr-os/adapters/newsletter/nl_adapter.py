"""
Output Adapter OA-006: Newsletter
Mailchimp / Brevo (旧SendinBlue) 対応。
config.json の provider で切り替え。
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


# ─────────────────────────────────────────
# MD → HTML email
# ─────────────────────────────────────────
EMAIL_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <style>
    body  {{ font-family:'Segoe UI',sans-serif; max-width:600px; margin:0 auto;
             padding:24px; color:#1a1a2e; background:#f8f9fa; }}
    h1    {{ color:#0a2463; border-bottom:2px solid #3e92cc; padding-bottom:8px; }}
    h2,h3 {{ color:#1b4f72; }}
    a     {{ color:#3e92cc; }}
    ul    {{ padding-left:1.5em; }}
    li    {{ margin-bottom:4px; }}
    .footer {{ margin-top:32px; padding-top:16px; border-top:1px solid #dee2e6;
               font-size:12px; color:#6c757d; }}
    .ks-id {{ font-family:monospace; background:#e9ecef;
              padding:2px 6px; border-radius:4px; font-size:12px; }}
  </style>
</head>
<body>
{body}
<div class="footer">
  <span class="ks-id">{ks_id}</span> ·
  MoCKA PR-OS · <a href="{{{{unsubscribe}}}}">配信停止</a>
</div>
</body>
</html>
"""

def md_to_email_html(text: str) -> str:
    h = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL).strip()
    h = re.sub(r"^### (.+)$", r"<h3>\1</h3>", h, flags=re.MULTILINE)
    h = re.sub(r"^## (.+)$",  r"<h2>\1</h2>", h, flags=re.MULTILINE)
    h = re.sub(r"^# (.+)$",   r"<h1>\1</h1>", h, flags=re.MULTILINE)
    h = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", h)
    h = re.sub(r"\*(.+?)\*",     r"<em>\1</em>", h)
    h = re.sub(r"`(.+?)`",       r"<code>\1</code>", h)
    h = re.sub(r"^- (.+)$",      r"<li>\1</li>", h, flags=re.MULTILINE)
    h = re.sub(r"(<li>(?:.*\n?)*?</li>\n?)+",
               lambda m: f"<ul>{m.group()}</ul>\n", h)
    blocks = re.split(r"\n{2,}", h.strip())
    return "\n".join(
        f"<p>{b}</p>" if b and not re.match(r"^<[hH\d\<]", b) else b
        for b in blocks if b.strip()
    )


# ─────────────────────────────────────────
class NewsletterAdapter(OutputAdapter):
    adapter_id   = "OA-006"
    adapter_name = "Newsletter"

    def __init__(self):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            self.cfg = json.load(f)
        self.provider = self.cfg.get("provider", "mailchimp").lower()
        self.api_key  = self.cfg["auth"].get("api_key", "")
        self.list_id  = self.cfg["defaults"].get("list_id", "")
        self.from_name  = self.cfg["defaults"].get("from_name", "")
        self.from_email = self.cfg["defaults"].get("from_email", "")

    # ── convert ──────────────────────────
    def convert(self, ks_record: dict, confirmed_text: str) -> dict:
        body     = md_to_email_html(confirmed_text)
        html     = EMAIL_TEMPLATE.format(body=body, ks_id=ks_record["id"])
        # プレーンテキスト（fallback）
        plain = re.sub(r"<[^>]+>", "", confirmed_text)
        plain = re.sub(r"\n{3,}", "\n\n", plain).strip()
        return {
            "_ks_id":     ks_record["id"],
            "subject":    ks_record["title"],
            "html":       html,
            "plain_text": plain,
            "from_name":  self.from_name,
            "from_email": self.from_email,
            "list_id":    self.list_id,
        }

    # ── publish ───────────────────────────
    def publish(self, converted: dict) -> PublishResult:
        ks_id = converted.get("_ks_id", "")
        if not self.cfg.get("enabled"):
            return self._disabled_result(ks_id)
        if self.provider == "mailchimp":
            return self._mailchimp_send(converted)
        elif self.provider in ("brevo", "sendinblue"):
            return self._brevo_send(converted)
        return PublishResult(success=False, adapter_id=self.adapter_id,
                             ks_id=ks_id, error=f"Unknown provider: {self.provider}")

    def _mailchimp_send(self, converted: dict) -> PublishResult:
        ks_id = converted["_ks_id"]
        # Mailchimp API v3
        dc = self.api_key.split("-")[-1]
        url = f"https://{dc}.api.mailchimp.com/3.0/campaigns"
        try:
            # Step 1: キャンペーン作成
            r1 = requests.post(url,
                auth=("anystring", self.api_key),
                json={
                    "type": "regular",
                    "recipients": {"list_id": converted["list_id"]},
                    "settings": {
                        "subject_line": converted["subject"],
                        "from_name":    converted["from_name"],
                        "reply_to":     converted["from_email"],
                    }
                }, timeout=30)
            r1.raise_for_status()
            campaign_id = r1.json()["id"]

            # Step 2: コンテンツ設定
            requests.put(
                f"{url}/{campaign_id}/content",
                auth=("anystring", self.api_key),
                json={"html": converted["html"],
                      "plain_text": converted["plain_text"]},
                timeout=30
            ).raise_for_status()

            # Step 3: 送信
            requests.post(
                f"{url}/{campaign_id}/actions/send",
                auth=("anystring", self.api_key),
                timeout=30
            ).raise_for_status()

            return PublishResult(success=True, adapter_id=self.adapter_id,
                                 ks_id=ks_id, post_id=campaign_id)
        except Exception as e:
            return PublishResult(success=False, adapter_id=self.adapter_id,
                                 ks_id=ks_id, error=str(e))

    def _brevo_send(self, converted: dict) -> PublishResult:
        ks_id = converted["_ks_id"]
        try:
            r = requests.post(
                "https://api.brevo.com/v3/emailCampaigns",
                headers={"api-key": self.api_key,
                         "Content-Type": "application/json"},
                json={
                    "name":    converted["subject"],
                    "subject": converted["subject"],
                    "sender":  {"name":  converted["from_name"],
                                "email": converted["from_email"]},
                    "type":    "classic",
                    "htmlContent": converted["html"],
                    "textContent": converted["plain_text"],
                    "recipients":  {"listIds": [int(converted["list_id"])]},
                    "scheduledAt": datetime.now(timezone.utc).strftime(
                        "%Y-%m-%dT%H:%M:%S.000Z")
                },
                timeout=30
            )
            r.raise_for_status()
            return PublishResult(success=True, adapter_id=self.adapter_id,
                                 ks_id=ks_id, post_id=str(r.json().get("id")))
        except Exception as e:
            return PublishResult(success=False, adapter_id=self.adapter_id,
                                 ks_id=ks_id, error=str(e))

    # ── schedule ──────────────────────────
    def schedule(self, converted: dict, publish_at: str) -> PublishResult:
        ks_id = converted.get("_ks_id", "")
        if not self.cfg.get("enabled"):
            return self._disabled_result(ks_id)
        # Brevo は scheduledAt で予約可
        if self.provider in ("brevo", "sendinblue"):
            modified = {**converted}
            modified["_publish_at"] = publish_at
            return self._brevo_send(modified)
        # Mailchimp は schedule_time で予約
        return PublishResult(success=True, adapter_id=self.adapter_id,
                             ks_id=ks_id, scheduled_at=publish_at,
                             post_id=f"queued:{publish_at}")

    # ── health_check ──────────────────────
    def health_check(self) -> HealthResult:
        if not self.cfg.get("enabled"):
            return self._disabled_health()
        try:
            if self.provider == "mailchimp":
                dc = self.api_key.split("-")[-1]
                r  = requests.get(
                    f"https://{dc}.api.mailchimp.com/3.0/ping",
                    auth=("anystring", self.api_key), timeout=10)
            else:
                r = requests.get(
                    "https://api.brevo.com/v3/account",
                    headers={"api-key": self.api_key}, timeout=10)
            return HealthResult(adapter_id=self.adapter_id,
                                adapter_name=self.adapter_name,
                                status="ok" if r.status_code == 200 else "error",
                                http_status=r.status_code)
        except Exception as e:
            return HealthResult(adapter_id=self.adapter_id,
                                adapter_name=self.adapter_name,
                                status="unreachable", error=str(e))
