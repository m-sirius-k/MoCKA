"""
TSI Health Checker v1.0
NTP保険マスターデータの品質スコア(TSI)劣化チェッカー

TSIスコア劣化ロジック:
  - 14日経過: -0.2
  - 28日経過: -0.2 (累計 -0.4)
  - 42日経過: -0.3 (累計 -0.7)
  - 42日超  : DEAD (0.0)

ステータス判定:
  TRUSTED : tsi >= 0.8
  WARNING : 0.5 <= tsi < 0.8
  DANGER  : 0.2 <= tsi < 0.5
  DEAD    : tsi < 0.2
"""
import json
from datetime import datetime, date, timedelta
from pathlib import Path

DEFAULT_MASTER = Path(__file__).parent.parent.parent / "data" / "insurers" / "master_20260604_v4.json"
HEALTH_DIR = Path(__file__).parent.parent.parent / "data"


def calc_tsi(base_tsi: float, days: int) -> float:
    """経過日数に応じてTSIを劣化させる。"""
    if days < 0:
        days = 0
    if days >= 42:
        return 0.0
    degraded = base_tsi
    if days >= 14:
        degraded -= 0.2
    if days >= 28:
        degraded -= 0.2
    if days >= 42:
        degraded -= 0.3
    return round(max(0.0, degraded), 4)


def calc_status(tsi: float, days: int = 0) -> str:
    """TSIスコアとステータス文字列を返す。"""
    effective = calc_tsi(tsi, days)
    if effective >= 0.8:
        return "TRUSTED"
    if effective >= 0.5:
        return "WARNING"
    if effective >= 0.2:
        return "DANGER"
    return "DEAD"


def _days_since(date_str: str, today: date = None) -> int:
    """last_verified から今日までの経過日数。"""
    if today is None:
        today = date.today()
    try:
        verified = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        return (today - verified).days
    except Exception:
        return 0


def run_health_check(master_path: Path = DEFAULT_MASTER, today: date = None) -> dict:
    """
    マスターJSONを読み込み、全商品のTSI劣化チェックを実行する。

    Returns:
        health_report dict
    """
    if today is None:
        today = date.today()

    with open(master_path, encoding="utf-8") as f:
        data = json.load(f)

    report_plans = []
    summary = {"TRUSTED": 0, "WARNING": 0, "DANGER": 0, "DEAD": 0, "total": 0}

    for company in data.get("companies", []):
        for p in company.get("plans", []):
            base_tsi = p.get("tsi", 1.0)
            last_verified = p.get("last_verified", str(today))
            days = _days_since(last_verified, today)

            # DEAD商品（discontinued）は劣化計算しない
            if p.get("discontinued") or p.get("tsi_status") == "DEAD":
                effective_tsi = 0.0
                status = "DEAD"
            else:
                effective_tsi = calc_tsi(base_tsi, days)
                status = calc_status(base_tsi, days)

            summary[status] += 1
            summary["total"] += 1

            needs_update = days >= 14 or effective_tsi < base_tsi
            report_plans.append({
                "company_id": company["company_id"],
                "plan_id": p["plan_id"],
                "plan_name": p.get("plan_name", ""),
                "base_tsi": base_tsi,
                "effective_tsi": effective_tsi,
                "base_status": p.get("tsi_status", ""),
                "current_status": status,
                "last_verified": last_verified,
                "days_since_verified": days,
                "needs_update": needs_update,
                "next_check_due": p.get("next_check_due", ""),
            })

    report = {
        "generated_at": today.strftime("%Y-%m-%dT%H:%M:%S"),
        "master_version": data.get("version", "?"),
        "master_path": str(master_path),
        "summary": summary,
        "alerts": [r for r in report_plans if r["needs_update"]],
        "all_plans": report_plans,
    }
    return report


def save_report(report: dict, out_dir: Path = HEALTH_DIR) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = "health_report_" + report["generated_at"][:10].replace("-", "") + ".json"
    out_path = out_dir / fname
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return out_path


def print_report(report: dict) -> None:
    s = report["summary"]
    print("=== TSI Health Report ===")
    print("generated: " + report["generated_at"])
    print("total=" + str(s["total"]) +
          " TRUSTED=" + str(s["TRUSTED"]) +
          " WARNING=" + str(s["WARNING"]) +
          " DANGER=" + str(s["DANGER"]) +
          " DEAD=" + str(s["DEAD"]))
    alerts = report["alerts"]
    if alerts:
        print("--- Alerts (needs_update=" + str(len(alerts)) + ") ---")
        for a in alerts:
            print("  " + a["plan_id"] + " " + a["plan_name"][:20] +
                  " days=" + str(a["days_since_verified"]) +
                  " tsi=" + str(a["base_tsi"]) + "->" + str(a["effective_tsi"]) +
                  " " + a["current_status"])
    else:
        print("No alerts.")


if __name__ == "__main__":
    import sys
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MASTER
    report = run_health_check(path)
    print_report(report)
    out = save_report(report)
    print("Report saved: " + str(out))
