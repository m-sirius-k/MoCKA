import csv
import os
import datetime

EVENTS = r"C:\Users\sirok\MoCKA\data\events.csv"
FAIL_LOG = r"C:\Users\sirok\MoCKA\data\failure_log.csv"
FIELDNAMES = ["event_id","when","who_actor","what_type","where_component",
              "where_path","why_purpose","how_trigger","channel_type",
              "lifecycle_phase","risk_level","category_ab","target_class",
              "title","short_summary","before_state","after_state",
              "change_type","impact_scope","impact_result",
              "related_event_id","trace_id","free_note"]

FAIL_KEYWORDS = ["ERROR","FAIL","blocked","WARNING","DANGER","CRITICAL",
                 "audit_mode","share_blocked","collaborate_blocked"]

def scan_failures():
    failures = []
    if not os.path.exists(EVENTS):
        print("[ERROR] events.csv not found")
        return

    with open(EVENTS, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_str = str(row)
            if any(kw in row_str for kw in FAIL_KEYWORDS):
                failures.append(row)

    # failure_log.csv書き出し
    with open(FAIL_LOG, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in failures:
            writer.writerow({k: row.get(k, "N/A") for k in FIELDNAMES})

    print(f"[failure_log] {len(failures)}件の失敗を検出")
    print(f"[出力] {FAIL_LOG}")

    # サマリー表示
    if failures:
        print("\n--- 失敗サマリー ---")
        for f in failures[-5:]:
            print(f"  {f.get('event_id','')} | {f.get('what_type','')} | {f.get('free_note','')[:60]}")
    else:
        print("[OK] 失敗ログなし")

scan_failures()
