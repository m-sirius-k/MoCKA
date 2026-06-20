#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/migrate_source_check.py -- Phase5-1.5 Schema Integrity Hardening

events._source列を制度（interface/gate_policy.ALLOWED_SOURCE_VALUES）と
完全一致させるためのMigration。

実施内容:
  1. 既存data/mocka_events.dbの_source値を全件検査し、
     ALLOWED_SOURCE_VALUES外の不正値があれば一覧を報告する（実行は中断）。
  2. 不正値が無い場合のみ、eventsテーブルを再構築する:
     - _source TEXT DEFAULT 'new'        (旧)
     -> _source TEXT NOT NULL CHECK (...)  (新)
  3. 実行前にDBファイルをバックアップする。
  4. 実行結果をJSONレポートとして保存する。

SQLiteはALTER TABLEでCHECK制約を追加できないため、
「新テーブル作成 -> データコピー -> 旧テーブル削除 -> リネーム」方式で再構築する。
"""

import json
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "interface"))
from gate_policy import ALLOWED_SOURCE_VALUES, POLICY_VERSION  # noqa: E402

DB_PATH = _REPO_ROOT / "data" / "mocka_events.db"
REPORT_PATH = _REPO_ROOT / "data" / "migrate_source_check_report.json"

# events.dbの現行カラム定義（_source以外は変更しない）
_BASE_COLUMNS_SQL = """
    event_id            TEXT PRIMARY KEY,
    when_ts             TEXT NOT NULL,
    who_actor           TEXT,
    what_type           TEXT,
    where_component     TEXT,
    where_path          TEXT,
    why_purpose         TEXT,
    how_trigger         TEXT,
    channel_type        TEXT,
    lifecycle_phase     TEXT,
    risk_level          TEXT,
    category_ab         TEXT,
    target_class        TEXT,
    title               TEXT,
    short_summary       TEXT,
    before_state        TEXT,
    after_state         TEXT,
    change_type         TEXT,
    impact_scope        TEXT,
    impact_result       TEXT,
    related_event_id    TEXT,
    trace_id            TEXT,
    free_note           TEXT,
    _imported_at        TEXT,
    {source_column},
    ai_actor            TEXT,
    session_id          TEXT,
    severity            INTEGER,
    pattern_score       REAL,
    recurrence_flag     INTEGER DEFAULT 0,
    verified_by         TEXT,
    data_integrity      TEXT DEFAULT 'normal',
    integrity_note      TEXT,
    recovered_short_summary TEXT
"""

_ALL_COLUMNS = [
    "event_id", "when_ts", "who_actor", "what_type", "where_component",
    "where_path", "why_purpose", "how_trigger", "channel_type",
    "lifecycle_phase", "risk_level", "category_ab", "target_class",
    "title", "short_summary", "before_state", "after_state", "change_type",
    "impact_scope", "impact_result", "related_event_id", "trace_id",
    "free_note", "_imported_at", "_source", "ai_actor", "session_id",
    "severity", "pattern_score", "recurrence_flag", "verified_by",
    "data_integrity", "integrity_note", "recovered_short_summary",
]


def _check_clause() -> str:
    values = ", ".join(f"'{v}'" for v in sorted(ALLOWED_SOURCE_VALUES))
    return f"_source TEXT NOT NULL CHECK (_source IN ({values}))"


def audit_existing_values(conn: sqlite3.Connection) -> dict:
    rows = conn.execute(
        "SELECT _source, COUNT(*) AS n FROM events GROUP BY _source"
    ).fetchall()
    violations = {}
    null_count = 0
    for source, n in rows:
        if source is None:
            null_count = n
            continue
        if source not in ALLOWED_SOURCE_VALUES:
            violations[source] = n
    return {"violations": violations, "null_count": null_count, "rows": dict(rows)}


def already_hardened(conn: sqlite3.Connection) -> bool:
    sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE name='events'"
    ).fetchone()[0]
    return "_source TEXT NOT NULL CHECK" in sql


def run_migration(dry_run: bool = False) -> dict:
    if not DB_PATH.exists():
        return {"status": "error", "detail": f"DB not found: {DB_PATH}"}

    conn = sqlite3.connect(str(DB_PATH))
    try:
        if already_hardened(conn):
            return {"status": "skipped", "detail": "_source already NOT NULL CHECK"}

        audit = audit_existing_values(conn)
        report = {
            "status": "pending",
            "policy_version": POLICY_VERSION,
            "allowed_source_values": sorted(ALLOWED_SOURCE_VALUES),
            "audit": audit,
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }

        if audit["violations"] or audit["null_count"]:
            report["status"] = "blocked"
            report["detail"] = (
                "ALLOWED_SOURCE_VALUES外の値またはNULLが存在するため移行を中断した。"
                "下記violationsを確認し、自動修正方針を決めてから再実行すること。"
            )
            REPORT_PATH.write_text(
                json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            return report

        if dry_run:
            report["status"] = "dry_run_ok"
            report["detail"] = "違反なし。実行時には再構築を行う。"
            REPORT_PATH.write_text(
                json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            return report

        # バックアップ
        backup_path = DB_PATH.with_name(
            DB_PATH.stem + f"_pre_source_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        conn.commit()
        shutil.copy2(DB_PATH, backup_path)

        cols_sql = _BASE_COLUMNS_SQL.format(source_column=_check_clause())
        col_list = ", ".join(_ALL_COLUMNS)

        conn.execute("BEGIN")
        conn.execute(f"CREATE TABLE events_new ({cols_sql})")
        conn.execute(
            f"INSERT INTO events_new ({col_list}) SELECT {col_list} FROM events"
        )
        conn.execute("DROP TABLE events")
        conn.execute("ALTER TABLE events_new RENAME TO events")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_when_ts ON events(when_ts)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_what_type ON events(what_type)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_risk_level ON events(risk_level)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_who_actor ON events(who_actor)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_lifecycle ON events(lifecycle_phase)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_source ON events(_source)"
        )
        conn.commit()

        final_count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        report["status"] = "done"
        report["backup_path"] = str(backup_path)
        report["final_row_count"] = final_count
        REPORT_PATH.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return report
    except Exception as e:
        conn.rollback()
        return {"status": "error", "detail": str(e)}
    finally:
        conn.close()


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    result = run_migration(dry_run=dry)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("status") in ("error", "blocked"):
        sys.exit(1)
