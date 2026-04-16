"""
run_experiment_A_v4.py
======================
MoCKA Experiment Type A — No-MoCKA Baseline (再現率測定) v4
修正: インシデント判定を risk_level IN (WARNING, CRITICAL, ERROR) のみに変更
出力: experiment_A_result_v4.json
"""

import csv
import json
import hashlib
import datetime
from pathlib import Path

EVENTS_CSV  = Path(r"C:\Users\sirok\MoCKA\data\events.csv")
OUTPUT_DIR  = Path(r"C:\Users\sirok\MoCKA\data\experiments")
OUTPUT_FILE = OUTPUT_DIR / "experiment_A_result_v4.json"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EXPERIMENT_ID          = "EXP_A_v4"
CONDITION              = "no_mocka_baseline"
RECURRENCE_WINDOW_DAYS = 30
INCIDENT_LEVELS        = {"WARNING", "CRITICAL", "ERROR"}

def sha256_of(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def parse_dt(s):
    try:
        return datetime.datetime.fromisoformat(s)
    except Exception:
        return None

def load_events(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def detect_recurrences(events):
    # インシデントのみ抽出
    incidents = [
        e for e in events
        if e.get("risk_level", "").strip() in INCIDENT_LEVELS
        and parse_dt(e.get("when", ""))
    ]
    incidents.sort(key=lambda e: parse_dt(e["when"]))

    print(f"  → インシデント一覧:")
    for e in incidents:
        print(f"    [{e['risk_level']}] {e['event_id']} | {e['when'][:10]} | {e.get('title','')[:40]}")

    # 同一キー(what_type, where_component, risk_level)で30日以内の再発を検出
    last_seen = {}
    recurrence_events = []

    for ev in incidents:
        key = (ev.get("what_type",""), ev.get("where_component",""), ev.get("risk_level",""))
        ts  = parse_dt(ev["when"])

        if key in last_seen:
            delta = (ts - last_seen[key]).days
            if delta <= RECURRENCE_WINDOW_DAYS:
                recurrence_events.append({
                    "event_id"        : ev["event_id"],
                    "when"            : ev["when"],
                    "key"             : f"{key[0]}|{key[1]}|{key[2]}",
                    "days_since_last" : delta,
                    "title"           : ev.get("title", ""),
                })

        last_seen[key] = ts  # 常に最新で更新（独立カウント方式）

    total     = len(incidents)
    rec_count = len(recurrence_events)
    rate      = round(rec_count / total * 100, 2) if total > 0 else 0.0

    return {
        "total_incidents"    : total,
        "recurrence_count"   : rec_count,
        "recurrence_rate_pct": rate,
        "recurrence_events"  : recurrence_events,
    }

def main():
    print(f"[{EXPERIMENT_ID}] Loading {EVENTS_CSV} ...")
    events = load_events(EVENTS_CSV)
    print(f"  → {len(events)} rows loaded.")

    print(f"[{EXPERIMENT_ID}] Detecting recurrences (levels={INCIDENT_LEVELS}, window={RECURRENCE_WINDOW_DAYS}d) ...")
    result = detect_recurrences(events)

    print(f"\n  → total_incidents    : {result['total_incidents']}")
    print(f"  → recurrence_count   : {result['recurrence_count']}")
    print(f"  → recurrence_rate    : {result['recurrence_rate_pct']} %")

    output = {
        "experiment_id"    : EXPERIMENT_ID,
        "condition"        : CONDITION,
        "executed_at"      : datetime.datetime.now().isoformat(),
        "parameters"       : {
            "source_csv"            : str(EVENTS_CSV),
            "incident_levels"       : list(INCIDENT_LEVELS),
            "recurrence_window_days": RECURRENCE_WINDOW_DAYS,
        },
        "summary"          : {
            "total_events_loaded": len(events),
            "total_incidents"    : result["total_incidents"],
            "recurrence_count"   : result["recurrence_count"],
            "recurrence_rate_pct": result["recurrence_rate_pct"],
        },
        "recurrence_events": result["recurrence_events"],
        "integrity"        : {"sha256": sha256_of(result)},
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[{EXPERIMENT_ID}] ✓ Result saved → {OUTPUT_FILE}")
    print(f"  SHA256: {output['integrity']['sha256']}")

if __name__ == "__main__":
    main()
