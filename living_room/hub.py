"""
living_room/hub.py — Living Room Hub v0.1 (read-only / dry_run mode)
=====================================================================
ChatGPT（GPT Adapter Chrome拡張）と MoCKA をつなぐ最小Hub。

ポート: localhost:8765
モード: dry_run=True（/eventは検証のみ、実DB書き込みは行わない）

本番書き込み有効化は博士確認後に DRY_RUN = False に変更する。

セキュリティ原則（2026-04-05型インシデント再発防止）:
- /event のみが書き込みエンドポイント
- Gate検証(gate_validator.validate)を通過しない限りDB書き込みは行わない
- フォールバック経路なし: 検証失敗=503、書き込みなし
- インフラファイル自体を公開するAPIは持たない
"""

import sys
import json
import sqlite3
import hashlib
from datetime import datetime, date, timezone
from pathlib import Path

# CWD = C:\Users\sirok\MoCKA を前提としてFlask/phi_osをインポート
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from flask import Flask, request, jsonify
from phi_os.gate_validator import validate

app = Flask(__name__)

# --- 設定 -------------------------------------------------------------------

HUB_PORT = 8765
DRY_RUN  = True   # False にすると /event が実際にDBへ書き込む

DB_PATH = str(_REPO_ROOT / "data" / "mocka_events.db")
OVERVIEW_PATH = Path(r"C:\Users\sirok\MOCKA_OVERVIEW.json")


# --- DB ヘルパー ------------------------------------------------------------

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _next_event_id() -> str:
    d = date.today().strftime("%Y%m%d")
    conn = _get_conn()
    try:
        n = conn.execute(
            "SELECT COUNT(*) FROM events WHERE event_id LIKE ?",
            (f"E{d}_%",),
        ).fetchone()[0]
    finally:
        conn.close()
    return f"E{d}_{n + 1:03d}"


def _last_hash() -> str:
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT trace_id FROM events ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        return row["trace_id"] if row and row["trace_id"] else ""
    except Exception:
        return ""
    finally:
        conn.close()


def _event_hash(payload: dict) -> str:
    canon = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def _write_event(payload: dict) -> None:
    row = {
        "event_id":        payload.get("event_id", ""),
        "when_ts":         payload.get("when_ts", ""),
        "who_actor":       payload.get("who_actor", ""),
        "what_type":       payload.get("what_type", ""),
        "where_component": payload.get("where_component", ""),
        "where_path":      payload.get("where_path", ""),
        "why_purpose":     payload.get("why_purpose", ""),
        "how_trigger":     payload.get("how_trigger", ""),
        "before_state":    payload.get("before_state", ""),
        "after_state":     payload.get("after_state", ""),
        "title":           payload.get("what_title", ""),
        "short_summary":   payload.get("description", ""),
        "session_id":      payload.get("who_session", ""),
        "_source":         "living_room",
        "trace_id":        payload.get("event_hash", ""),
        "related_event_id": payload.get("prev_hash", ""),
        "free_note":       "|".join(filter(None, [
            payload.get("tags", ""),
            "channel=living_room",
        ])),
        "channel_type":    "gate",
        "lifecycle_phase": "in_operation",
        "risk_level":      "normal",
    }
    row = {k: (v if v != "" else None) for k, v in row.items()}
    conn = _get_conn()
    try:
        cols = list(row.keys())
        placeholders = ",".join("?" * len(cols))
        vals = [row[c] for c in cols]
        conn.execute(
            f"INSERT OR IGNORE INTO events ({','.join(cols)}) VALUES ({placeholders})",
            vals,
        )
        conn.commit()
    finally:
        conn.close()


# --- エンドポイント ---------------------------------------------------------

@app.route("/health")
def health():
    try:
        conn = _get_conn()
        count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        conn.close()
        db_ok = True
    except Exception as e:
        count = -1
        db_ok = False
    return jsonify({
        "status":    "ok",
        "hub":       "living_room v0.1",
        "port":      HUB_PORT,
        "dry_run":   DRY_RUN,
        "db_ok":     db_ok,
        "db_events": count,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/context")
def context():
    """
    GPTセッション開始時に呼ぶ現在状態エンドポイント。
    - 直近イベント5件
    - MOCKA_OVERVIEW.json の概要（存在する場合）
    """
    # 直近5件
    try:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT event_id, when_ts, who_actor, what_type, title, short_summary "
            "FROM events ORDER BY rowid DESC LIMIT 5"
        ).fetchall()
        conn.close()
        recent = [dict(r) for r in rows]
    except Exception as e:
        recent = [{"error": str(e)}]

    # OVERVIEW
    overview = {}
    if OVERVIEW_PATH.exists():
        try:
            overview = json.loads(OVERVIEW_PATH.read_text(encoding="utf-8"))
        except Exception:
            overview = {"error": "parse_failed"}

    return jsonify({
        "hub":          "living_room v0.1",
        "dry_run":      DRY_RUN,
        "recent_events": recent,
        "overview":     overview,
        "timestamp":    datetime.now(timezone.utc).isoformat(),
    })


@app.route("/memory")
def memory():
    """
    過去イベント検索。q=キーワード で title/short_summary/free_note を検索。
    """
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "q parameter required"}), 400

    try:
        conn = _get_conn()
        like = f"%{q}%"
        rows = conn.execute(
            "SELECT event_id, when_ts, who_actor, what_type, title, short_summary "
            "FROM events "
            "WHERE title LIKE ? OR short_summary LIKE ? OR free_note LIKE ? "
            "ORDER BY rowid DESC LIMIT 20",
            (like, like, like),
        ).fetchall()
        conn.close()
        results = [dict(r) for r in rows]
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "query":   q,
        "count":   len(results),
        "results": results,
    })


@app.route("/event", methods=["POST"])
def receive_event():
    """
    GPTからのイベント書き込みエンドポイント。

    必須フィールド (gate_validator.validate に従う):
      who_actor      : 必須 (例: "gpt-4o")。"gpt" で始まるIDを推奨
      who_session    : SESSION_YYYYMMDD_HHMMSS 形式
      why_purpose    : 10文字以上
      how_trigger    : 必須
      where_path     : 必須
      what_type      : ALLOWED_WHAT_TYPES に含まれる値
      before_state or after_state: どちらか必須

    dry_run=True (現在の設定) の場合:
      - 検証のみ実行、DBへの書き込みは行わない
      - 検証通過時は {"status": "dry_run_ok", "would_be_id": "..."} を返す

    フォールバックなし:
      - 検証失敗 → 503 (書き込みなし)
      - DRY_RUN=True → 書き込みなし（設計意図）
    """
    payload = request.get_json(force=True) or {}

    # who_actor が gpt 系であることを確認（Living Room専用ガード）
    actor = payload.get("who_actor", "")
    if not actor.lower().startswith("gpt"):
        return jsonify({
            "status": "rejected",
            "errors": ["LIVING_ROOM-01: who_actor must start with 'gpt' (e.g. gpt-4o)"],
        }), 422

    # Event Gate検証（フォールバックなし）
    errors = validate(payload)
    if errors:
        return jsonify({"status": "rejected", "errors": errors}), 503

    if DRY_RUN:
        would_be_id = _next_event_id()
        return jsonify({
            "status":       "dry_run_ok",
            "would_be_id":  would_be_id,
            "message":      "Gate validation passed. DRY_RUN=True: no DB write performed.",
            "dry_run":      True,
        }), 200

    # 本番書き込み (DRY_RUN=False 時のみ到達)
    payload["event_id"]     = _next_event_id()
    payload["when_ts"]      = datetime.now(timezone.utc).isoformat()
    payload["event_source"] = "living_room"
    payload["event_hash"]   = _event_hash(payload)
    payload["prev_hash"]    = _last_hash()

    _write_event(payload)

    return jsonify({
        "status":   "ok",
        "event_id": payload["event_id"],
        "dry_run":  False,
    }), 201


# --- 起動 -------------------------------------------------------------------

if __name__ == "__main__":
    print(f"[Living Room Hub] Starting on http://localhost:{HUB_PORT}")
    print(f"[Living Room Hub] DRY_RUN={DRY_RUN} (write disabled)")
    print(f"[Living Room Hub] DB={DB_PATH}")
    app.run(host="127.0.0.1", port=HUB_PORT, debug=False)
