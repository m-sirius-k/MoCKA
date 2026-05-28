# db_helper.py — commit/restore エンジン用 SQLite ヘルパー
# commit-engine.js / restore-engine.js から child_process.spawnSync で呼び出す
import sqlite3
import json
import sys
import os
from datetime import datetime, timezone

# Windows cp932 環境でも UTF-8 で出力する
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

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
    import glob as glob_mod

    params = json.loads(args) if args else {}
    limit_tensions  = params.get("limit_tensions",  5)
    limit_decisions = params.get("limit_decisions", 5)
    limit_events    = params.get("limit_events",   10)

    conn = get_db()
    result = {}

    # ── Fact層: events から最新イベント (what_type 不問) ──
    rows = conn.execute("""
        SELECT event_id, title, short_summary, when_ts, what_type
        FROM events
        ORDER BY when_ts DESC LIMIT ?
    """, (limit_events,)).fetchall()
    result["recent_events"] = [dict(r) for r in rows]

    # ── State層: MOCKA_TODO.json から open/進行中 TODO ──
    TODO_PATH = r"C:\Users\sirok\MOCKA_TODO.json"
    active_todos = []
    if os.path.exists(TODO_PATH):
        try:
            with open(TODO_PATH, encoding="utf-8-sig") as f:
                todo_data = json.load(f)
            todos = todo_data if isinstance(todo_data, list) else todo_data.get("todos", [])
            for d in todos:
                status = d.get("status", "")
                if status not in ("完了", "closed", "done", "DONE"):
                    active_todos.append({
                        "todo_id":  d.get("id", ""),
                        "title":    d.get("title", ""),
                        "priority": d.get("priority", ""),
                        "status":   status,
                    })
        except Exception as e:
            active_todos = [{"todo_id": "ERROR", "title": str(e), "priority": "", "status": ""}]
    # 最高優先度を先頭に、最大30件
    active_todos.sort(key=lambda t: (0 if t["priority"] == "最高" else 1 if t["priority"] == "高" else 2, t["todo_id"]))
    result["active_todos"] = active_todos[:30]

    # ── Causality層: tension_severity >= 3 の未解決違和感 ──
    rows = conn.execute("""
        SELECT tension, tension_severity, tension_at, tags, source_map
        FROM judgement_reason
        WHERE tension_severity >= 3
          AND (tags LIKE '%unresolved%' OR tags LIKE '%tension%' OR tags LIKE '%anomaly%')
        ORDER BY tension_severity DESC, created_at DESC LIMIT ?
    """, (limit_tensions,)).fetchall()
    result["active_tensions"] = [dict(r) for r in rows]

    # ── Intent層 (recent decisions) ──
    rows = conn.execute("""
        SELECT decision, reason, rejected_reason, error_solved, source_map, created_at
        FROM judgement_reason
        ORDER BY created_at DESC LIMIT ?
    """, (limit_decisions,)).fetchall()
    result["recent_decisions"] = [dict(r) for r in rows]

    conn.close()

    # ── IMMUTABLE 層 (ファイルから読む) ──
    ESSENCE_PATH = r"C:\Users\sirok\MoCKA\interface\lever_essence.json"
    try:
        with open(ESSENCE_PATH, encoding="utf-8") as f:
            ess = json.load(f)
        result["immutable"] = ess.get("IMMUTABLE", {})
        result["philosophy_summary"] = ess.get("PHILOSOPHY", "")[:200]
        result["operation_summary"]  = ess.get("OPERATION",  "")[:200]
    except Exception as e:
        result["immutable"] = {}
        result["philosophy_summary"] = f"[READ ERROR: {e}]"

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


def cmd_commit(args):
    """commit_session ペイロード（new_fact/new_decision/remaining_task/tension/next_hook）を
    judgement_reason に保存する。app.py /commit_session から呼ばれる。"""
    data = json.loads(args) if args else {}
    nd = data.get("new_decision", {}) or {}
    decision = nd.get("decision", "保留")
    reason   = nd.get("reason") or data.get("remaining_task") or "セッション引き継ぎ"
    tension_text = None
    tension_sev  = 0
    if data.get("tension"):
        t = data["tension"]
        if isinstance(t, dict):
            tension_text = t.get("text")
            tension_sev  = t.get("severity", 0)
        else:
            tension_text = str(t)
            tension_sev  = 1
    payload = {
        "event_id":         "relay_commit_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        "session_date":     datetime.now().strftime("%Y-%m-%d"),
        "decision":         decision if decision in ("採用", "却下", "保留") else "保留",
        "reason":           reason,
        "error_solved":     nd.get("error_solved"),
        "tension":          tension_text,
        "tension_severity": tension_sev,
        "tags":             "relay,session_commit",
        "source_map":       "relay_handoff_button",
    }
    return cmd_write_judgement(json.dumps(payload))


COMMANDS = {
    "write_judgement":   cmd_write_judgement,
    "read_restore_data": cmd_read_restore_data,
    "query":             cmd_query,
    "commit":            cmd_commit,
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
