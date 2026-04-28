# mocka_caliber_sqlite_patch.py
# 適用方法: このファイルをそのまま実行するとパッチを当てる
# python mocka_caliber_sqlite_patch.py

import re
from pathlib import Path

TARGET = Path("C:/Users/sirok/MoCKA/mocka_caliber_server.py")

OLD_IMPORTS = '''import csv, hashlib, json, os, re, shutil'''

NEW_IMPORTS = '''import csv, hashlib, json, os, re, shutil, sqlite3'''

OLD_EVENTS_LINE = '''EVENTS     = ROOT / "data" / "events.csv"'''

NEW_EVENTS_LINE = '''EVENTS     = ROOT / "data" / "events.csv"
EVENTS_DB  = ROOT / "data" / "mocka_events.db"'''

OLD_APPEND = '''def append_event(row):
    with open(EVENTS, "a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(row)'''

NEW_APPEND = '''def append_event(row):
    """CSV(後方互換) + SQLite(制度カーネル)に二重書き込み。"""
    # CSV書き込み（後方互換・既存ツール用）
    try:
        with open(EVENTS, "a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(row)
    except Exception as e:
        print(f"[caliber] CSV write error: {e}")

    # SQLite書き込み（制度カーネル・UTF-8保証）
    try:
        cols = [
            "event_id", "when_ts", "who_actor", "what_type",
            "where_component", "where_path", "why_purpose", "how_trigger",
            "channel_type", "lifecycle_phase", "risk_level", "category_ab",
            "target_class", "title", "short_summary", "before_state",
            "after_state", "change_type", "impact_scope", "impact_result",
            "related_event_id", "trace_id", "free_note",
        ]
        # rowを23カラム分にパディング
        padded = list(row) + [""] * max(0, len(cols) - len(row))
        padded = padded[:len(cols)]

        # 追加カラム
        from datetime import datetime, timezone
        padded_with_meta = padded + [
            datetime.now(timezone.utc).isoformat(),  # _imported_at
            "caliber_server",                         # _source
            "caliber",                                # ai_actor
            "",                                       # session_id
            "normal",                                 # severity
            0.0,                                      # pattern_score
            0,                                        # recurrence_flag
            "caliber_server_v5",                      # verified_by
        ]
        all_cols = cols + ["_imported_at", "_source", "ai_actor", "session_id",
                           "severity", "pattern_score", "recurrence_flag", "verified_by"]

        placeholders = ",".join(["?"] * len(all_cols))
        sql = f"INSERT OR IGNORE INTO events ({','.join(all_cols)}) VALUES ({placeholders})"

        conn = sqlite3.connect(str(EVENTS_DB), timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(sql, padded_with_meta)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[caliber] SQLite write error: {e}")'''

def apply_patch():
    print("[patch] mocka_caliber_server.py SQLite対応パッチ適用開始")
    content = TARGET.read_text(encoding="utf-8")

    # 1. import追加
    if "sqlite3" not in content:
        content = content.replace(OLD_IMPORTS, NEW_IMPORTS, 1)
        print("[patch] ✓ sqlite3 import追加")
    else:
        print("[patch] - sqlite3 import既存")

    # 2. EVENTS_DB定義追加
    if "EVENTS_DB" not in content:
        content = content.replace(OLD_EVENTS_LINE, NEW_EVENTS_LINE, 1)
        print("[patch] ✓ EVENTS_DB パス追加")
    else:
        print("[patch] - EVENTS_DB既存")

    # 3. append_event置換
    if "SQLite" not in content:
        content = content.replace(OLD_APPEND, NEW_APPEND, 1)
        print("[patch] ✓ append_event SQLite二重書き込みに置換")
    else:
        print("[patch] - append_event既存")

    TARGET.write_text(content, encoding="utf-8")
    print("[patch] 完了: " + str(TARGET))

if __name__ == "__main__":
    apply_patch()
