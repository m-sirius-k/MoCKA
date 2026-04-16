"""
run_experiment_A_v3.py
======================
MoCKA Experiment Type A — No-MoCKA Baseline (再現率測定)
対象: events.csv から過去インシデントを抽出し、MoCKAなし条件で再発率を算出
出力: experiment_A_result_v3.json

CSV列定義 (events.csv):
  event_id, when, who_actor, what_type, where_component, where_path,
  why_purpose, how_trigger, channel_type, lifecycle_phase, risk_level,
  category_ab, target_class, title, short_summary, before_state,
  after_state, change_type, impact_scope, impact_result,
  related_event_id, trace_id, free_note
"""

import csv
import json
import hashlib
import datetime
from pathlib import Path
from collections import defaultdict

# ── パス設定 ──────────────────────────────────────────────
EVENTS_CSV   = Path(r"C:\Users\sirok\MoCKA\data\events.csv")
OUTPUT_DIR   = Path(r"C:\Users\sirok\MoCKA\data\experiments")
OUTPUT_FILE  = OUTPUT_DIR / "experiment_A_result_v3.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── 定数 ──────────────────────────────────────────────────
EXPERIMENT_ID   = "EXP_A_v3"
CONDITION       = "no_mocka_baseline"
RECURRENCE_WINDOW_DAYS = 30   # 同一カテゴリの再発とみなす期間

# ── ユーティリティ ─────────────────────────────────────────
def sha256_of(obj: object) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()

def parse_dt(s: str) -> datetime.datetime | None:
    try:
        return datetime.datetime.fromisoformat(s)
    except Exception:
        return None

# ── CSVロード ─────────────────────────────────────────────
def load_events(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

# ── 再発判定ロジック ──────────────────────────────────────
def detect_recurrences(events: list[dict]) -> dict:
    """
    同一 (what_type, where_component, risk_level) の組合せが
    RECURRENCE_WINDOW_DAYS 以内に再発した場合を「再発イベント」とみなす。
    MoCKAなし条件 = recurrence_registry による抑止なし。
    """
    # タイムスタンプでソート
    sorted_events = sorted(
        [e for e in events if parse_dt(e.get("when", ""))],
        key=lambda e: parse_dt(e["when"])
    )

    # キー別に最終発生日時を追跡
    last_seen: dict[tuple, datetime.datetime] = {}
    recurrence_events: list[dict] = []
    total_incidents = 0

    for ev in sorted_events:
        risk = ev.get("risk_level", "normal")
        wtype = ev.get("what_type", "")
        wcomp = ev.get("where_component", "")
        key = (wtype, wcomp, risk)
        ts = parse_dt(ev["when"])

        # インシデント扱い (risk_level が normal 以外、または category_ab が B)
        is_incident = (risk != "normal") or (ev.get("category_ab", "A") == "B")
        if not is_incident:
            continue

        total_incidents += 1

        if key in last_seen:
            delta = (ts - last_seen[key]).days
            if delta <= RECURRENCE_WINDOW_DAYS:
                recurrence_events.append({
                    "event_id"   : ev["event_id"],
                    "when"       : ev["when"],
                    "key"        : f"{wtype}|{wcomp}|{risk}",
                    "days_since_last": delta,
                    "title"      : ev.get("title", ""),
                })

        last_seen[key] = ts

    recurrence_rate = (
        len(recurrence_events) / total_incidents * 100
        if total_incidents > 0 else 0.0
    )

    return {
        "total_incidents"   : total_incidents,
        "recurrence_count"  : len(recurrence_events),
        "recurrence_rate_pct": round(recurrence_rate, 2),
        "recurrence_events" : recurrence_events,
    }

# ── メイン ────────────────────────────────────────────────
def main():
    print(f"[{EXPERIMENT_ID}] Loading events from {EVENTS_CSV} ...")
    events = load_events(EVENTS_CSV)
    print(f"  → {len(events)} rows loaded.")

    print(f"[{EXPERIMENT_ID}] Detecting recurrences (window={RECURRENCE_WINDOW_DAYS}d) ...")
    result = detect_recurrences(events)

    print(f"  → total_incidents    : {result['total_incidents']}")
    print(f"  → recurrence_count   : {result['recurrence_count']}")
    print(f"  → recurrence_rate    : {result['recurrence_rate_pct']} %")

    # ── 出力JSON構築 ─────────────────────────────────────
    output = {
        "experiment_id"    : EXPERIMENT_ID,
        "condition"        : CONDITION,
        "executed_at"      : datetime.datetime.now().isoformat(),
        "parameters": {
            "source_csv"           : str(EVENTS_CSV),
            "recurrence_window_days": RECURRENCE_WINDOW_DAYS,
        },
        "summary": {
            "total_events_loaded"  : len(events),
            "total_incidents"      : result["total_incidents"],
            "recurrence_count"     : result["recurrence_count"],
            "recurrence_rate_pct"  : result["recurrence_rate_pct"],
        },
        "recurrence_events": result["recurrence_events"],
        "integrity": {
            "sha256": sha256_of(result)
        }
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[{EXPERIMENT_ID}] ✓ Result saved → {OUTPUT_FILE}")
    print(f"  SHA256: {output['integrity']['sha256']}")

if __name__ == "__main__":
    main()
