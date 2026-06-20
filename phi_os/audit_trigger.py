#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phi_os/audit_trigger.py (TODO_323)
PHI-OS Gate DB直接書き込み検知トリガー

SQLite TRIGGERで GATE外からのINSERTを検知 -> audit_violationsに記録 + アラート発火
物理的封鎖ではなく「迂回しても即検知」の制度的抑止力。

Usage:
  python phi_os/audit_trigger.py --install   # トリガーとテーブルをDBに設定
  python phi_os/audit_trigger.py --status    # 違反件数確認
  python phi_os/audit_trigger.py --report    # 違反一覧表示
"""
import sys
import io
import sqlite3
import json
import argparse
import datetime
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mocka_events.db"
PREV_QUEUE = ROOT / "data" / "prevention_queue.json"
MCP_URL = "http://localhost:5002/agent/mocka_write_event"

# Gate経由のINSERTを識別するマーカー列名
GATE_MARKER_COLUMN = "channel_type"
GATE_MARKER_VALUE  = "gate"


def install_audit_schema(conn: sqlite3.Connection):
    """audit_violationsテーブルとトリガーをインストール"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_at TEXT NOT NULL,
            table_name TEXT NOT NULL,
            operation TEXT NOT NULL,
            event_id TEXT,
            channel_type TEXT,
            actor TEXT,
            raw_snippet TEXT,
            status TEXT DEFAULT 'NEW',
            resolved_at TEXT
        )
    """)

    # GATE外INSERT検知トリガー
    # channel_type が 'gate' でない INSERTは直接書き込みと判定
    conn.execute("DROP TRIGGER IF EXISTS trg_detect_direct_insert")
    conn.execute("""
        CREATE TRIGGER trg_detect_direct_insert
        AFTER INSERT ON events
        WHEN (NEW.channel_type IS NULL OR NEW.channel_type != 'gate')
        BEGIN
            INSERT INTO audit_violations
                (detected_at, table_name, operation, event_id, channel_type, actor, raw_snippet)
            VALUES (
                datetime('now'),
                'events',
                'DIRECT_INSERT',
                NEW.event_id,
                NEW.channel_type,
                NEW.who_actor,
                substr(coalesce(NEW.title, '') || ' ' || coalesce(NEW.short_summary, ''), 1, 100)
            );
        END
    """)

    # GATE外UPDATE検知トリガー
    # channel_type が 'gate' でない UPDATEは直接書き込みと判定（INSERT判定と同条件）
    conn.execute("DROP TRIGGER IF EXISTS trg_detect_direct_update")
    conn.execute("""
        CREATE TRIGGER trg_detect_direct_update
        AFTER UPDATE ON events
        WHEN (NEW.channel_type IS NULL OR NEW.channel_type != 'gate')
        BEGIN
            INSERT INTO audit_violations
                (detected_at, table_name, operation, event_id, channel_type, actor, raw_snippet)
            VALUES (
                datetime('now'),
                'events',
                'DIRECT_UPDATE',
                NEW.event_id,
                NEW.channel_type,
                NEW.who_actor,
                substr(coalesce(NEW.title, '') || ' ' || coalesce(NEW.short_summary, ''), 1, 100)
            );
        END
    """)

    conn.commit()
    print("[OK] audit_violations table + triggers installed")


def get_violation_count(conn: sqlite3.Connection) -> dict:
    """違反件数サマリーを返す"""
    total = conn.execute("SELECT COUNT(*) FROM audit_violations").fetchone()[0]
    new   = conn.execute(
        "SELECT COUNT(*) FROM audit_violations WHERE status = 'NEW'"
    ).fetchone()[0]
    direct_insert = conn.execute(
        "SELECT COUNT(*) FROM audit_violations WHERE operation = 'DIRECT_INSERT'"
    ).fetchone()[0]
    direct_update = conn.execute(
        "SELECT COUNT(*) FROM audit_violations WHERE operation = 'DIRECT_UPDATE'"
    ).fetchone()[0]
    return {
        "total": total,
        "new": new,
        "direct_insert": direct_insert,
        "direct_update": direct_update,
    }


def push_prevention_alert(count: int):
    """違反があればprevention_queueに投入"""
    PREV_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    try:
        raw = PREV_QUEUE.read_text(encoding="utf-8") if PREV_QUEUE.exists() else '{"queue":[]}'
        data = json.loads(raw)
    except Exception:
        data = {"queue": []}
    data["queue"].append({
        "id": f"PHI_OS_VIOLATION_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "type": "PHI_OS_GATE_VIOLATION",
        "detail": f"DB直接書き込み検知: {count}件の未解決違反",
        "detected_at": datetime.datetime.now().isoformat(),
        "status": "NEW",
    })
    PREV_QUEUE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_event(title: str, desc: str):
    try:
        import urllib.request
        payload = json.dumps({
            "title": title, "description": desc,
            "tags": "phi_os,audit,gate_violation,todo_323",
            "why_purpose": "PHI-OS Gate直接書き込み検知",
            "how_trigger": "phi_os/audit_trigger.py",
        }).encode("utf-8")
        req = urllib.request.Request(
            MCP_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass


def check_and_alert(conn: sqlite3.Connection) -> dict:
    """NEW状態の違反を確認してアラート発火"""
    counts = get_violation_count(conn)
    if counts["new"] > 0:
        push_prevention_alert(counts["new"])
        write_event(
            f"PHI_OS_GATE_VIOLATION: DB直接書き込み {counts['new']}件検知",
            f"audit_violations: total={counts['total']} new={counts['new']} "
            f"insert={counts['direct_insert']} update={counts['direct_update']}"
        )
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PHI-OS Gate Audit Trigger (TODO_323)")
    parser.add_argument("--install", action="store_true", help="トリガーとテーブルをDBに設定")
    parser.add_argument("--status",  action="store_true", help="違反件数確認")
    parser.add_argument("--report",  action="store_true", help="違反一覧表示")
    parser.add_argument("--alert",   action="store_true", help="NEW違反をprevention_queueに投入")
    args = parser.parse_args()

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    try:
        if args.install:
            install_audit_schema(conn)
        elif args.status:
            counts = get_violation_count(conn)
            print(f"audit_violations: {counts}")
        elif args.report:
            rows = conn.execute(
                "SELECT * FROM audit_violations ORDER BY id DESC LIMIT 50"
            ).fetchall()
            for r in rows:
                print(dict(r))
        elif args.alert:
            counts = check_and_alert(conn)
            print(f"alert check: {counts}")
        else:
            install_audit_schema(conn)
    finally:
        conn.close()
