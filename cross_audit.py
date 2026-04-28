"""
cross_audit.py v1.0
MoCKA クロス監査エンジン — 複数AI相互検証基盤

設計原則:
  - 外部API呼び出しゼロ（完全内製）
  - Agent REST API（port:5002）を基盤として活用
  - 同一タスクを記録・差異検出・events.dbに記録
  - TRDP原則: Trust but Record, Detect, Penalize

配置先: C:/Users/sirok/MoCKA/interface/cross_audit.py
起動: app.pyに /cross_audit/* エンドポイントを追加して使用

Author: Claude（執行官）  Date: 2026-04-28
"""

import hashlib
import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

# ─── 設定 ────────────────────────────────────────────────────────────────────

ROOT     = Path("C:/Users/sirok/MoCKA")
DB       = ROOT / "data" / "mocka_events.db"
AUDIT_DB = ROOT / "data" / "cross_audit.db"

UTC = timezone.utc

# 登録済みAIエージェント（内製エンドポイント）
AGENTS = {
    "claude":      "http://localhost:5002/agent",   # MCP Agent REST
    "caliber":     "http://localhost:5679/health",  # Caliber
    "runtime_b":   "http://localhost:5003/b/health",# Go Runtime B
}


# ─── DB初期化 ────────────────────────────────────────────────────────────────

def init_audit_db():
    """クロス監査専用DBを初期化する。"""
    conn = sqlite3.connect(str(AUDIT_DB), timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_tasks (
            task_id     TEXT PRIMARY KEY,
            task_text   TEXT NOT NULL,
            created_at  TEXT NOT NULL,
            status      TEXT DEFAULT 'pending',
            agents      TEXT,
            summary     TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_results (
            result_id   TEXT PRIMARY KEY,
            task_id     TEXT NOT NULL,
            agent_name  TEXT NOT NULL,
            response    TEXT,
            score       REAL DEFAULT 0.0,
            submitted_at TEXT,
            verified    INTEGER DEFAULT 0,
            discrepancy TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_discrepancies (
            disc_id     TEXT PRIMARY KEY,
            task_id     TEXT NOT NULL,
            agent_a     TEXT,
            agent_b     TEXT,
            field       TEXT,
            value_a     TEXT,
            value_b     TEXT,
            severity    TEXT DEFAULT 'INFO',
            detected_at TEXT
        )
    """)
    conn.commit()
    conn.close()


# ─── タスク管理 ──────────────────────────────────────────────────────────────

def create_task(task_text: str, agents: list = None) -> dict:
    """クロス監査タスクを作成する。"""
    if agents is None:
        agents = list(AGENTS.keys())

    ts = datetime.now(UTC).isoformat()
    task_id = "AUDIT_" + datetime.now(UTC).strftime("%Y%m%d_%H%M%S") + "_" + \
              hashlib.sha256(task_text.encode()).hexdigest()[:6].upper()

    conn = sqlite3.connect(str(AUDIT_DB), timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        "INSERT INTO audit_tasks (task_id, task_text, created_at, agents) VALUES (?,?,?,?)",
        [task_id, task_text, ts, json.dumps(agents)]
    )
    conn.commit()
    conn.close()

    # mocka_events.dbにも記録
    _record_to_main_db(task_id, "cross_audit_task_created", task_text[:200])

    return {"task_id": task_id, "task_text": task_text, "agents": agents, "created_at": ts}


def submit_result(task_id: str, agent_name: str, response: str, score: float = 0.0) -> dict:
    """エージェントの回答を登録する。"""
    ts = datetime.now(UTC).isoformat()
    result_id = f"{task_id}_{agent_name}_{datetime.now(UTC).strftime('%H%M%S')}"

    conn = sqlite3.connect(str(AUDIT_DB), timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        "INSERT OR REPLACE INTO audit_results (result_id, task_id, agent_name, response, score, submitted_at) VALUES (?,?,?,?,?,?)",
        [result_id, task_id, agent_name, response, score, ts]
    )
    conn.commit()
    conn.close()

    return {"result_id": result_id, "task_id": task_id, "agent": agent_name, "submitted_at": ts}


def run_discrepancy_check(task_id: str) -> list:
    """
    登録済み全エージェント回答の差異を検出する。
    差異検出ルール:
      - 回答長の極端な差（3倍以上）
      - キーワード一致率が低い（30%未満）
      - スコア差が0.3以上
    """
    conn = sqlite3.connect(str(AUDIT_DB), timeout=10)
    rows = conn.execute(
        "SELECT agent_name, response, score FROM audit_results WHERE task_id=?",
        [task_id]
    ).fetchall()
    conn.close()

    if len(rows) < 2:
        return []

    discrepancies = []
    agents_data = [{"agent": r[0], "response": r[1] or "", "score": r[2]} for r in rows]

    for i in range(len(agents_data)):
        for j in range(i + 1, len(agents_data)):
            a = agents_data[i]
            b = agents_data[j]

            disc_list = []

            # 1. 回答長差異チェック
            len_a = len(a["response"])
            len_b = len(b["response"])
            if len_a > 0 and len_b > 0:
                ratio = max(len_a, len_b) / max(min(len_a, len_b), 1)
                if ratio >= 3.0:
                    disc_list.append({
                        "field": "response_length",
                        "value_a": str(len_a),
                        "value_b": str(len_b),
                        "severity": "WARNING"
                    })

            # 2. キーワード一致率チェック
            words_a = set(a["response"].split())
            words_b = set(b["response"].split())
            if words_a and words_b:
                union = words_a | words_b
                intersection = words_a & words_b
                similarity = len(intersection) / max(len(union), 1)
                if similarity < 0.30:
                    disc_list.append({
                        "field": "keyword_similarity",
                        "value_a": f"{similarity:.2f}",
                        "value_b": "threshold:0.30",
                        "severity": "DANGER"
                    })

            # 3. スコア差チェック
            score_diff = abs(a["score"] - b["score"])
            if score_diff >= 0.3:
                disc_list.append({
                    "field": "score_diff",
                    "value_a": str(round(a["score"], 3)),
                    "value_b": str(round(b["score"], 3)),
                    "severity": "WARNING"
                })

            for d in disc_list:
                disc_id = f"DISC_{task_id}_{a['agent']}_{b['agent']}_{d['field']}"
                ts = datetime.now(UTC).isoformat()
                disc = {
                    "disc_id": disc_id,
                    "task_id": task_id,
                    "agent_a": a["agent"],
                    "agent_b": b["agent"],
                    "field": d["field"],
                    "value_a": d["value_a"],
                    "value_b": d["value_b"],
                    "severity": d["severity"],
                    "detected_at": ts
                }
                discrepancies.append(disc)

                # DB記録
                conn2 = sqlite3.connect(str(AUDIT_DB), timeout=10)
                conn2.execute("PRAGMA journal_mode=WAL")
                conn2.execute(
                    "INSERT OR REPLACE INTO audit_discrepancies VALUES (?,?,?,?,?,?,?,?,?)",
                    [disc_id, task_id, a["agent"], b["agent"],
                     d["field"], d["value_a"], d["value_b"], d["severity"], ts]
                )
                conn2.commit()
                conn2.close()

                # DANGER以上はmocka_events.dbに記録
                if d["severity"] in ("DANGER", "CRITICAL"):
                    _record_to_main_db(
                        task_id,
                        "cross_audit_discrepancy",
                        f"{a['agent']} vs {b['agent']} | {d['field']} | {d['severity']}"
                    )

    # タスクステータス更新
    status = "completed_with_discrepancy" if discrepancies else "completed_clean"
    conn3 = sqlite3.connect(str(AUDIT_DB), timeout=10)
    conn3.execute(
        "UPDATE audit_tasks SET status=?, summary=? WHERE task_id=?",
        [status, json.dumps({"discrepancies": len(discrepancies)}), task_id]
    )
    conn3.commit()
    conn3.close()

    return discrepancies


def get_task_report(task_id: str) -> dict:
    """タスクの全レポートを取得する。"""
    conn = sqlite3.connect(str(AUDIT_DB), timeout=10)
    task = conn.execute(
        "SELECT * FROM audit_tasks WHERE task_id=?", [task_id]
    ).fetchone()
    results = conn.execute(
        "SELECT agent_name, response, score, submitted_at FROM audit_results WHERE task_id=?",
        [task_id]
    ).fetchall()
    discs = conn.execute(
        "SELECT agent_a, agent_b, field, value_a, value_b, severity FROM audit_discrepancies WHERE task_id=?",
        [task_id]
    ).fetchall()
    conn.close()

    if not task:
        return {"error": "task not found"}

    return {
        "task_id": task[0],
        "task_text": task[1],
        "created_at": task[2],
        "status": task[3],
        "results": [
            {"agent": r[0], "response_preview": (r[1] or "")[:200], "score": r[2], "submitted_at": r[3]}
            for r in results
        ],
        "discrepancies": [
            {"agent_a": d[0], "agent_b": d[1], "field": d[2],
             "value_a": d[3], "value_b": d[4], "severity": d[5]}
            for d in discs
        ],
        "clean": len(discs) == 0
    }


def list_tasks(limit: int = 20) -> list:
    """最近の監査タスク一覧を返す。"""
    conn = sqlite3.connect(str(AUDIT_DB), timeout=10)
    rows = conn.execute(
        "SELECT task_id, task_text, created_at, status FROM audit_tasks ORDER BY created_at DESC LIMIT ?",
        [limit]
    ).fetchall()
    conn.close()
    return [{"task_id": r[0], "task_text": r[1][:80], "created_at": r[2], "status": r[3]} for r in rows]


# ─── メインDB連携 ─────────────────────────────────────────────────────────────

def _record_to_main_db(task_id: str, event_type: str, summary: str):
    """クロス監査イベントをmocka_events.dbにも記録する。"""
    try:
        ts = datetime.now(UTC).isoformat()
        eid = f"XAUDIT_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        conn = sqlite3.connect(str(DB), timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            INSERT OR IGNORE INTO events
            (event_id, when_ts, who_actor, what_type, where_component,
             title, short_summary, _imported_at, _source, ai_actor, severity)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, [eid, ts, "cross_audit", event_type, "cross_audit_engine",
              task_id, summary[:500], ts, "cross_audit", "claude", "normal"])
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[cross_audit] main DB write error: {e}")


# ─── Flask統合用エンドポイント定義（app.pyに追加する） ───────────────────────

FLASK_ENDPOINTS = '''
# ── cross_audit エンドポイント（app.pyに追加） ──────────────────────────────
from interface.cross_audit import (
    init_audit_db, create_task, submit_result,
    run_discrepancy_check, get_task_report, list_tasks
)
init_audit_db()

@app.route("/cross_audit/task", methods=["POST"])
def cross_audit_task():
    data = request.json or {}
    task_text = data.get("task", "")
    agents = data.get("agents", None)
    if not task_text:
        return jsonify({"error": "task required"}), 400
    result = create_task(task_text, agents)
    return jsonify(result)

@app.route("/cross_audit/submit", methods=["POST"])
def cross_audit_submit():
    data = request.json or {}
    task_id  = data.get("task_id", "")
    agent    = data.get("agent", "")
    response = data.get("response", "")
    score    = float(data.get("score", 0.0))
    if not task_id or not agent:
        return jsonify({"error": "task_id and agent required"}), 400
    result = submit_result(task_id, agent, response, score)
    return jsonify(result)

@app.route("/cross_audit/check/<task_id>")
def cross_audit_check(task_id):
    discs = run_discrepancy_check(task_id)
    return jsonify({"task_id": task_id, "discrepancies": discs, "count": len(discs)})

@app.route("/cross_audit/report/<task_id>")
def cross_audit_report(task_id):
    return jsonify(get_task_report(task_id))

@app.route("/cross_audit/list")
def cross_audit_list():
    return jsonify(list_tasks())
# ────────────────────────────────────────────────────────────────────────────
'''

# ─── 初期化 ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("[cross_audit] DB初期化...")
    init_audit_db()
    print(f"[cross_audit] AUDIT_DB: {AUDIT_DB}")
    print("[cross_audit] OK")
    print()
    print("=== app.pyに追加するエンドポイント ===")
    print(FLASK_ENDPOINTS)
