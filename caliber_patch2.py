import sqlite3, csv
from pathlib import Path
from datetime import datetime, timezone

TARGET = Path("C:/Users/sirok/MoCKA/caliber/chat_pipeline/mocka_caliber_server.py")

content = TARGET.read_text(encoding="utf-8")

OLD = 'def append_event(row):\n    with open(EVENTS, "a", encoding="utf-8", newline="") as f:\n        csv.writer(f).writerow(row)'

NEW = '''def append_event(row):
    try:
        with open(EVENTS, "a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(row)
    except Exception as e:
        print(f"[caliber] CSV error: {e}")
    try:
        db = Path("C:/Users/sirok/MoCKA/data/mocka_events.db")
        cols = ["event_id","when_ts","who_actor","what_type","where_component","where_path","why_purpose","how_trigger","channel_type","lifecycle_phase","risk_level","category_ab","target_class","title","short_summary","before_state","after_state","change_type","impact_scope","impact_result","related_event_id","trace_id","free_note"]
        padded = (list(row) + [""]*23)[:23]
        padded += [datetime.now(timezone.utc).isoformat(),"caliber_server","caliber","","normal",0.0,0,"caliber_v5"]
        all_cols = cols + ["_imported_at","_source","ai_actor","session_id","severity","pattern_score","recurrence_flag","verified_by"]
        ph = ",".join(["?"]*len(all_cols))
        sql = f"INSERT OR IGNORE INTO events ({','.join(all_cols)}) VALUES ({ph})"
        conn = sqlite3.connect(str(db), timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(sql, padded)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[caliber] SQLite error: {e}")'''

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    TARGET.write_text(content, encoding="utf-8")
    print("OK: patch applied")
else:
    print("NG: pattern not found")
    for i, line in enumerate(content.splitlines()):
        if "append_event" in line or "csv.writer" in line:
            print(f"  {i}: {line}")