# db_helper.py — commit/restore エンジン用 SQLite ヘルパー
# commit-engine.js / restore-engine.js から child_process.spawnSync で呼び出す
import sqlite3
import json
import sys
import os
from datetime import datetime, timezone

DB_PATH = r"C:\Users\sirok\MoCKA\data\mocka_events.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def cmd_write_judgement(args):
    """judgement_reason テーブルへ1件書き込む"""
    data = json.loads(args)
    required = ("event_id", "session_date", "decision", "reason")
    for k in required:
        if not data.get(k):
            return {"error": f"必須フィールド不足: {k}"}

    if data["decision"] == "却下" and not data.get("rejected_reason"):
        return {"error": "decision=却下 のとき rejected_reason は必須"}

    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO judgement_reason
            (event_id, session_date, decision, rejected_reason, reason,
             error_solved, tension, tension_severity, tension_at, source_map, tags)
            VALUES (:event_id, :session_date, :decision, :rejected_reason, :reason,
                    :error_solved, :tension, :tension_severity, :tension_at, :source_map, :tags)
        """, {
            "event_id":         data["event_id"],
            "session_date":     data["session_date"],
            "decision":         data["decision"],
            "rejected_reason":  data.get("rejected_reason"),
            "reason":           data["reason"],
            "error_solved":     data.get("error_solved"),
            "tension":          data.get("tension"),
            "tension_severity": data.get("tension_severity", 0),
            "tension_at":       data.get("tension_at"),
            "source_map":       data.get("source_map"),
            "tags":             data.get("tags"),
        })
        conn.commit()
        row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"ok": True, "id": row_id}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        conn.close()


def cmd_read_restore_data(args):
    """Restore Packet 生成用データを4層から取得する"""
    params = json.loads(args) if args else {}
    session_date = params.get("session_date", datetime.now().strftime("%Y-%m-%d"))
    limit_tensions = params.get("limit_tensions", 5)
    limit_decisions = params.get("limit_decisions", 5)

    conn = get_db()
    result = {}

    # Fact層: events から最新ファクト
    rows = conn.execute("""
        SELECT event_id, title, short_summary, when_ts
        FROM events
        WHERE session_date(when_ts) >= date('now', '-7 days')
          AND what_type IN ('CHANGE_DONE', 'CHANGE_START', 'FACT')
        ORDER BY when_ts DESC LIMIT 10
    """).fetchall()
    result["recent_events"] = [dict(r) for r in rows]

    # State層: Causality から最新decisions
    rows = conn.execute("""
        SELECT decision, reason, rejected_reason, error_solved, source_map, created_at
        FROM judgement_reason
        ORDER BY created_at DESC LIMIT ?
    """, (limit_decisions,)).fetchall()
    result["recent_decisions"] = [dict(r) for r in rows]

    # Causality層: tension_severity >= 3 の未解決違和感
    rows = conn.execute("""
        SELECT tension, tension_severity, tension_at, tags, source_map
        FROM judgement_reason
        WHERE tension_severity >= 3
          AND (tags LIKE '%unresolved%' OR tags LIKE '%tension%')
        ORDER BY tension_severity DESC, created_at DESC LIMIT ?
    """, (limit_tensions,)).fetchall()
    result["active_tensions"] = [dict(r) for r in rows]

    conn.close()
    return result


def cmd_query(args):
    """汎用SELECT（読み取り専用）"""
    params = json.loads(args)
    sql = params.get("sql", "")
    binds = params.get("binds", [])
    if not sql.strip().upper().startswith("SELECT"):
        return {"error": "SELECT のみ許可"}
    conn = get_db()
    rows = conn.execute(sql, binds).fetchall()
    conn.close()
    return {"rows": [dict(r) for r in rows]}


COMMANDS = {
    "write_judgement":  cmd_write_judgement,
    "read_restore_data": cmd_read_restore_data,
    "query":            cmd_query,
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: db_helper.py <command> [args_json]"}))
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2] if len(sys.argv) > 2 else "{}"

    if cmd not in COMMANDS:
        print(json.dumps({"error": f"unknown command: {cmd}"}))
        sys.exit(1)

    out = COMMANDS[cmd](args)
    print(json.dumps(out, ensure_ascii=False))
