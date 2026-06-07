"""
PR-OS Analytics — Google Analytics 4 Connector
GA4 Data API v1 を使い KS別パフォーマンスを取得する
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Optional

# google-analytics-data が入っていない環境向けフォールバック付き
try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange, Dimension, Metric, RunReportRequest
    )
    GA_AVAILABLE = True
except ImportError:
    GA_AVAILABLE = False

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
CACHE_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache.json")


# ─────────────────────────────────────────
# Config
# ─────────────────────────────────────────
DEFAULT_CONFIG = {
    "enabled": False,
    "property_id": "",
    "credentials_path": "",
    "cache_ttl_minutes": 30
}

def _load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG

def _save_config(cfg: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────
# Cache
# ─────────────────────────────────────────
def _load_cache() -> dict:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_cache(data: dict):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _cache_key(report_type: str, days: int) -> str:
    return f"{report_type}_{days}d"

def _is_fresh(cache: dict, key: str, ttl_min: int) -> bool:
    entry = cache.get(key)
    if not entry:
        return False
    ts = datetime.fromisoformat(entry["cached_at"])
    return (datetime.now(timezone.utc) - ts).total_seconds() < ttl_min * 60


# ─────────────────────────────────────────
# GA4 Query
# ─────────────────────────────────────────
def _run_report(property_id: str, creds_path: str,
                dimensions: list, metrics: list,
                start_days: int = 30) -> list:
    """GA4 Data API でレポートを実行"""
    if not GA_AVAILABLE:
        raise ImportError("google-analytics-data が未インストールです。"
                          "pip install google-analytics-data でインストールしてください。")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(
            start_date=f"{start_days}daysAgo",
            end_date="today"
        )],
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
    )
    response = client.run_report(request)

    rows = []
    for row in response.rows:
        r = {}
        for i, dim in enumerate(dimensions):
            r[dim] = row.dimension_values[i].value
        for i, met in enumerate(metrics):
            r[met] = row.metric_values[i].value
        rows.append(r)
    return rows


# ─────────────────────────────────────────
# Public API
# ─────────────────────────────────────────
def get_overview(days: int = 30, use_cache: bool = True) -> dict:
    """
    サイト全体の概要指標を取得。
    Returns: {sessions, pageviews, bounce_rate, avg_session_duration, ...}
    """
    cfg = _load_config()
    if not cfg["enabled"]:
        return _mock_overview(days)

    key   = _cache_key("overview", days)
    cache = _load_cache()
    if use_cache and _is_fresh(cache, key, cfg["cache_ttl_minutes"]):
        return cache[key]["data"]

    try:
        rows = _run_report(
            cfg["property_id"], cfg["credentials_path"],
            dimensions=["date"],
            metrics=["sessions", "screenPageViews", "bounceRate",
                     "averageSessionDuration", "newUsers"],
            start_days=days
        )
        total = {"sessions": 0, "pageviews": 0, "new_users": 0,
                 "bounce_rate": 0.0, "avg_duration": 0.0, "days": days}
        for r in rows:
            total["sessions"]   += int(r.get("sessions", 0))
            total["pageviews"]  += int(r.get("screenPageViews", 0))
            total["new_users"]  += int(r.get("newUsers", 0))
        if rows:
            total["bounce_rate"] = round(
                sum(float(r.get("bounceRate", 0)) for r in rows) / len(rows), 3)
            total["avg_duration"] = round(
                sum(float(r.get("averageSessionDuration", 0)) for r in rows) / len(rows), 1)

        result = {**total, "fetched_at": datetime.now(timezone.utc).isoformat()}
        cache[key] = {"data": result, "cached_at": datetime.now(timezone.utc).isoformat()}
        _save_cache(cache)
        return result
    except Exception as e:
        return {"error": str(e), "mock": True, **_mock_overview(days)}


def get_top_pages(days: int = 30, limit: int = 10, use_cache: bool = True) -> list:
    """上位ページ一覧を取得"""
    cfg = _load_config()
    if not cfg["enabled"]:
        return _mock_top_pages(limit)

    key   = _cache_key("top_pages", days)
    cache = _load_cache()
    if use_cache and _is_fresh(cache, key, cfg["cache_ttl_minutes"]):
        return cache[key]["data"]

    try:
        rows = _run_report(
            cfg["property_id"], cfg["credentials_path"],
            dimensions=["pagePath", "pageTitle"],
            metrics=["screenPageViews", "averageSessionDuration",
                     "bounceRate", "newUsers"],
            start_days=days
        )
        rows.sort(key=lambda r: int(r.get("screenPageViews", 0)), reverse=True)
        result = rows[:limit]
        cache[key] = {"data": result, "cached_at": datetime.now(timezone.utc).isoformat()}
        _save_cache(cache)
        return result
    except Exception as e:
        return _mock_top_pages(limit)


def get_traffic_sources(days: int = 30, use_cache: bool = True) -> list:
    """流入元別セッション数"""
    cfg = _load_config()
    if not cfg["enabled"]:
        return _mock_traffic_sources()

    key   = _cache_key("sources", days)
    cache = _load_cache()
    if use_cache and _is_fresh(cache, key, cfg["cache_ttl_minutes"]):
        return cache[key]["data"]

    try:
        rows = _run_report(
            cfg["property_id"], cfg["credentials_path"],
            dimensions=["sessionDefaultChannelGroup"],
            metrics=["sessions", "newUsers", "bounceRate"],
            start_days=days
        )
        rows.sort(key=lambda r: int(r.get("sessions", 0)), reverse=True)
        cache[key] = {"data": rows, "cached_at": datetime.now(timezone.utc).isoformat()}
        _save_cache(cache)
        return rows
    except Exception as e:
        return _mock_traffic_sources()


def get_ks_performance(ks_id: str, days: int = 30) -> dict:
    """
    特定KSの公開後パフォーマンス。
    KS_NNN に対応するURLパスのデータを取得。
    """
    cfg = _load_config()
    if not cfg["enabled"]:
        return _mock_ks_performance(ks_id)

    # KSレコードからURLパス取得
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from knowledge_store.ks_manager import get_record
        rec = get_record(ks_id)
        wp_url = rec.get("files", {}).get("wordpress_url", "")
        if not wp_url:
            return {"ks_id": ks_id, "error": "WordPress URL未設定", "mock": True}
    except Exception:
        return _mock_ks_performance(ks_id)

    # URLパスでフィルタリングしたレポート
    try:
        rows = _run_report(
            cfg["property_id"], cfg["credentials_path"],
            dimensions=["pagePath"],
            metrics=["screenPageViews", "averageSessionDuration",
                     "bounceRate", "newUsers"],
            start_days=days
        )
        path = wp_url.split("/")[-2] if wp_url.endswith("/") else wp_url.split("/")[-1]
        matched = [r for r in rows if path in r.get("pagePath", "")]
        if matched:
            m = matched[0]
            return {
                "ks_id": ks_id,
                "pageviews":       int(m.get("screenPageViews", 0)),
                "avg_duration":    float(m.get("averageSessionDuration", 0)),
                "bounce_rate":     float(m.get("bounceRate", 0)),
                "new_users":       int(m.get("newUsers", 0)),
                "fetched_at":      datetime.now(timezone.utc).isoformat()
            }
    except Exception as e:
        pass
    return _mock_ks_performance(ks_id)


# ─────────────────────────────────────────
# Mock Data（GA未設定時のデモ）
# ─────────────────────────────────────────
def _mock_overview(days: int) -> dict:
    return {
        "sessions": 0, "pageviews": 0, "new_users": 0,
        "bounce_rate": 0.0, "avg_duration": 0.0,
        "days": days, "mock": True,
        "message": "analytics/config.json で GA4を設定してください"
    }

def _mock_top_pages(limit: int) -> list:
    return [{"mock": True, "message": "GA4未設定"}]

def _mock_traffic_sources() -> list:
    return [{"mock": True, "message": "GA4未設定"}]

def _mock_ks_performance(ks_id: str) -> dict:
    return {"ks_id": ks_id, "pageviews": 0, "mock": True,
            "message": "GA4未設定"}


# ─────────────────────────────────────────
# Setup helper
# ─────────────────────────────────────────
def setup(property_id: str, credentials_path: str):
    """GA4設定を保存"""
    cfg = {
        "enabled": True,
        "property_id": property_id,
        "credentials_path": credentials_path,
        "cache_ttl_minutes": 30
    }
    _save_config(cfg)
    print(f"[GA] 設定完了: property_id={property_id}")


def status() -> dict:
    cfg = _load_config()
    return {
        "enabled":        cfg["enabled"],
        "property_id":    cfg.get("property_id", ""),
        "ga_library":     GA_AVAILABLE,
        "cache_exists":   os.path.exists(CACHE_PATH),
        "install_cmd":    "pip install google-analytics-data" if not GA_AVAILABLE else "installed"
    }


if __name__ == "__main__":
    print("=== GA Connector Status ===")
    print(json.dumps(status(), ensure_ascii=False, indent=2))
    print("\n=== Overview (mock) ===")
    print(json.dumps(get_overview(), ensure_ascii=False, indent=2))
