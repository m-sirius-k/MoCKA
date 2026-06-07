"""
PR-OS TSI — Technical Status Inspector
全Adapterの定期ヘルスチェック・変更検知・アラート管理
"""
import json
import os
import sys
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TSI_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tsi_log.json")


# ─────────────────────────────────────────
# Data Model
# ─────────────────────────────────────────
@dataclass
class TSIRecord:
    adapter_id:   str
    adapter_name: str
    status:       str               # ok | disabled | unreachable | error
    checked_at:   str
    prev_status:  Optional[str] = None
    changed:      bool = False      # 前回から状態変化があったか
    http_status:  Optional[int] = None
    error:        Optional[str] = None
    rate_limit:   Optional[int] = None
    consecutive_failures: int = 0

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


# ─────────────────────────────────────────
# Log I/O
# ─────────────────────────────────────────
def _load_log() -> dict:
    if os.path.exists(TSI_LOG_PATH):
        with open(TSI_LOG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"last_run": None, "adapters": {}, "alerts": []}


def _save_log(data: dict):
    data["last_run"] = datetime.now(timezone.utc).isoformat()
    with open(TSI_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────
# Adapter Registry
# ─────────────────────────────────────────
def _get_adapters() -> list:
    """利用可能な全Adapterインスタンスを返す"""
    adapters = []
    try:
        from adapters.wordpress.wp_adapter import WordPressAdapter
        adapters.append(WordPressAdapter())
    except Exception as e:
        print(f"[TSI] WordPress load error: {e}")
    try:
        from adapters.x_twitter.x_adapter import XAdapter
        adapters.append(XAdapter())
    except Exception as e:
        print(f"[TSI] X load error: {e}")
    try:
        from adapters.instagram.ig_adapter import InstagramAdapter
        adapters.append(InstagramAdapter())
    except Exception as e:
        print(f"[TSI] Instagram load error: {e}")
    try:
        from adapters.github_pages.gh_adapter import GitHubPagesAdapter
        adapters.append(GitHubPagesAdapter())
    except Exception:
        pass
    try:
        from adapters.newsletter.nl_adapter import NewsletterAdapter
        adapters.append(NewsletterAdapter())
    except Exception:
        pass
    return adapters


# ─────────────────────────────────────────
# Alert Engine
# ─────────────────────────────────────────
ALERT_RULES = [
    {
        "id": "adapter_down",
        "condition": lambda r: r.status in ("unreachable", "error"),
        "severity": "error",
        "message": lambda r: f"{r.adapter_name} が応答しません (status={r.status})"
    },
    {
        "id": "status_changed",
        "condition": lambda r: r.changed and r.prev_status == "ok",
        "severity": "warning",
        "message": lambda r: f"{r.adapter_name} のステータスが {r.prev_status} → {r.status} に変化"
    },
    {
        "id": "rate_limit_low",
        "condition": lambda r: r.rate_limit is not None and r.rate_limit < 10,
        "severity": "warning",
        "message": lambda r: f"{r.adapter_name} レート制限残り {r.rate_limit} 回"
    },
    {
        "id": "consecutive_failures",
        "condition": lambda r: r.consecutive_failures >= 3,
        "severity": "critical",
        "message": lambda r: f"{r.adapter_name} が{r.consecutive_failures}回連続で失敗"
    },
]

def _generate_alerts(records: list[TSIRecord]) -> list:
    alerts = []
    for rec in records:
        for rule in ALERT_RULES:
            try:
                if rule["condition"](rec):
                    alerts.append({
                        "rule_id":    rule["id"],
                        "severity":   rule["severity"],
                        "adapter_id": rec.adapter_id,
                        "message":    rule["message"](rec),
                        "timestamp":  datetime.now(timezone.utc).isoformat()
                    })
            except Exception:
                pass
    return alerts


# ─────────────────────────────────────────
# Main: Run Check
# ─────────────────────────────────────────
def run(verbose: bool = True) -> dict:
    """
    全Adapterのヘルスチェックを実行。
    前回結果と比較し変化を検知。アラートを生成。
    """
    log      = _load_log()
    prev_map = log.get("adapters", {})
    adapters = _get_adapters()
    now      = datetime.now(timezone.utc).isoformat()

    records  = []
    new_map  = {}

    for adapter in adapters:
        health = adapter.health_check()
        prev   = prev_map.get(health.adapter_id, {})

        failures = prev.get("consecutive_failures", 0)
        if health.status not in ("ok", "disabled"):
            failures += 1
        else:
            failures = 0

        rec = TSIRecord(
            adapter_id=health.adapter_id,
            adapter_name=health.adapter_name,
            status=health.status,
            checked_at=now,
            prev_status=prev.get("status"),
            changed=prev.get("status") is not None and prev.get("status") != health.status,
            http_status=health.http_status,
            error=health.error,
            rate_limit=health.rate_limit_remaining,
            consecutive_failures=failures,
        )
        records.append(rec)
        new_map[health.adapter_id] = rec.to_dict()

        if verbose:
            icon = "✓" if rec.status == "ok" else ("○" if rec.status == "disabled" else "✗")
            change = f" [変化: {rec.prev_status}→{rec.status}]" if rec.changed else ""
            print(f"  {icon} {rec.adapter_id} {rec.adapter_name:<16} [{rec.status}]{change}")

    alerts   = _generate_alerts(records)
    log_data = {
        "last_run":  now,
        "adapters":  new_map,
        "alerts":    (log.get("alerts", []) + alerts)[-100:],  # 直近100件保持
    }
    _save_log(log_data)

    summary = {
        "checked_at": now,
        "total":      len(records),
        "ok":         sum(1 for r in records if r.status == "ok"),
        "disabled":   sum(1 for r in records if r.status == "disabled"),
        "error":      sum(1 for r in records if r.status in ("error", "unreachable")),
        "alerts":     len(alerts),
        "new_alerts": alerts,
        "records":    [r.to_dict() for r in records],
    }
    return summary


def get_log() -> dict:
    """最新のTSIログを返す"""
    return _load_log()


def get_alerts(unresolved_only: bool = True, limit: int = 20) -> list:
    """アラート一覧を返す"""
    log    = _load_log()
    alerts = log.get("alerts", [])
    return list(reversed(alerts))[:limit]


def clear_alerts():
    """アラートをクリア"""
    log = _load_log()
    log["alerts"] = []
    _save_log(log)
    print("[TSI] Alerts cleared.")


if __name__ == "__main__":
    print("=" * 50)
    print("[TSI] ヘルスチェック実行")
    print("=" * 50)
    summary = run()
    print(f"\n--- Summary ---")
    print(f"  Total: {summary['total']} | OK: {summary['ok']} | "
          f"Disabled: {summary['disabled']} | Error: {summary['error']}")
    if summary["new_alerts"]:
        print(f"\n--- Alerts ({len(summary['new_alerts'])}) ---")
        for a in summary["new_alerts"]:
            print(f"  [{a['severity'].upper()}] {a['message']}")
