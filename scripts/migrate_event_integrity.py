#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/migrate_event_integrity.py -- Phase5-2 Event Integrity Framework Migration

既存data/mocka_events.dbの全イベントへevent_signatures(署名+ハッシュチェーン)を
遡及的に付与する。migrate_source_check.pyと同じ手順パターンに従う:

  1. event_signaturesが既に存在し全件署名済みならスキップ(idempotent)。
  2. DBファイルをバックアップする。
  3. event_signaturesテーブルを作成する(未存在時)。
  4. 既存eventsをwhen_ts, event_id順(現実的な時系列順)に走査し、
     1件ずつ integrity.sign_event でチェーンを構築する。
  5. 構築直後に integrity.verify_chain で整合性を検証する。
  6. JSONレポートを保存する。
"""

import json
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "phi_os"))
sys.path.insert(0, str(_REPO_ROOT / "interface"))

import integrity  # noqa: E402

DB_PATH = _REPO_ROOT / "data" / "mocka_events.db"
REPORT_PATH = _REPO_ROOT / "data" / "migrate_event_integrity_report.json"

MIGRATION_VERSION = "migrate_event_integrity_v1"


def _signed_count(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='event_signatures'"
    ).fetchone()
    if not row:
        return -1
    return conn.execute("SELECT COUNT(*) FROM event_signatures").fetchone()[0]


def run_migration(dry_run: bool = False) -> dict:
    if not DB_PATH.exists():
        return {"status": "error", "detail": f"DB not found: {DB_PATH}"}

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        total_events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        signed = _signed_count(conn)

        if signed == total_events and signed >= 0:
            return {
                "status": "skipped",
                "detail": "event_signatures already covers all events",
                "total_events": total_events,
                "signed_count": signed,
            }

        report = {
            "status": "pending",
            "migration_version": MIGRATION_VERSION,
            "signature_version": integrity.SIGNATURE_VERSION,
            "algorithm": integrity.DEFAULT_ALGORITHM,
            "total_events": total_events,
            "already_signed": max(signed, 0),
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }

        if dry_run:
            report["status"] = "dry_run_ok"
            report["detail"] = (
                f"{total_events - max(signed, 0)} events would be signed/backfilled."
            )
            REPORT_PATH.write_text(
                json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            return report

        # バックアップ
        backup_path = DB_PATH.with_name(
            DB_PATH.stem + f"_pre_event_integrity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        conn.commit()
        shutil.copy2(DB_PATH, backup_path)

        integrity.ensure_signatures_table(conn)

        # 既に署名済みのevent_idは再署名しない(idempotent / チェーン破壊防止)
        already_signed_ids = {
            r["event_id"] for r in conn.execute("SELECT event_id FROM event_signatures")
        }

        unsigned_rows = conn.execute(
            "SELECT * FROM events ORDER BY when_ts ASC, event_id ASC"
        ).fetchall()

        signed_now = 0
        for row in unsigned_rows:
            row = dict(row)
            if row["event_id"] in already_signed_ids:
                continue
            integrity.sign_event(conn, row)
            signed_now += 1

        conn.commit()

        verify_result = integrity.verify_chain(conn)

        final_signed = conn.execute("SELECT COUNT(*) FROM event_signatures").fetchone()[0]
        report["status"] = "done" if verify_result["ok"] else "done_with_anomalies"
        report["backup_path"] = str(backup_path)
        report["signed_now"] = signed_now
        report["final_signed_count"] = final_signed
        report["verify_result"] = verify_result
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
    if result.get("status") in ("error", "done_with_anomalies"):
        sys.exit(1)
