# phi_os/human_gate.py
# PHI-OS Human Gate State Model v1
# 仕様根拠: docs/governance/control_map_v2.md, MOCKA_TODO: PHI-OS-HUMAN-GATE-STATE-MODEL-V1
#
# 基本原則: PHI-OSがHuman Gateの唯一の状態管理責務を持つ。
# GL7およびApp層はHuman Gate状態を保持しない(本モジュールが単一の真実)。
#
# 永続ルール: stateそのものは保存しない。eventのみ保存する。
# stateはevent列から都度再構築する(イベントソーシング)。
from flask import Blueprint, request, jsonify
import sqlite3
import time
import secrets
import json
from datetime import datetime, timezone
from pathlib import Path

human_gate_bp = Blueprint('human_gate', __name__)

_REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(_REPO_ROOT / 'data' / 'mocka_events.db')

STATES = {"PENDING", "APPROVED", "REJECTED", "EXPIRED", "CANCELED"}

# action -> 許可されるprevious_stateの集合。Noneは「新規生成(previous_stateなし)」を表す。
TRANSITIONS = {
    "submit":  {None},
    "approve": {"PENDING"},
    "reject":  {"PENDING"},
    "expire":  {"PENDING"},
    "cancel":  {"PENDING", "APPROVED", "REJECTED"},
}

ACTION_NEXT_STATE = {
    "submit": "PENDING",
    "approve": "APPROVED",
    "reject": "REJECTED",
    "expire": "EXPIRED",
    "cancel": "CANCELED",
}


class HumanGateError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table(conn) -> None:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS human_gate_events (
            event_id TEXT PRIMARY KEY,
            timestamp TEXT,
            type TEXT,
            action TEXT,
            request_id TEXT,
            payload TEXT,
            previous_state TEXT,
            next_state TEXT
        )
    ''')


def _next_event_id() -> str:
    d = datetime.now(timezone.utc).strftime('%Y%m%d')
    micros_of_day = time.time_ns() // 1000 % 1_000_000_000
    return f'HG{d}_{micros_of_day:09d}{secrets.token_hex(2)}'


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _latest_event(conn, request_id: str):
    row = conn.execute(
        'SELECT * FROM human_gate_events WHERE request_id = ? ORDER BY timestamp DESC, event_id DESC LIMIT 1',
        (request_id,)
    ).fetchone()
    return row


def get_state(request_id: str, conn=None) -> str | None:
    """request_idの現在状態をevent列から再構築する。eventが無ければNone。"""
    owns_conn = conn is None
    if owns_conn:
        conn = _get_conn()
    try:
        _ensure_table(conn)
        row = _latest_event(conn, request_id)
        return row['next_state'] if row else None
    finally:
        if owns_conn:
            conn.close()


def _record_transition(conn, action: str, request_id: str, payload: dict, previous_state: str | None) -> dict:
    next_state = ACTION_NEXT_STATE[action]
    event = {
        "event_id": _next_event_id(),
        "timestamp": _now_iso(),
        "type": "HUMAN_GATE_EVENT",
        "action": action,
        "request_id": request_id,
        "payload": json.dumps(payload, ensure_ascii=False, sort_keys=True),
        "previous_state": previous_state,
        "next_state": next_state,
    }
    conn.execute(
        '''INSERT INTO human_gate_events
           (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (event["event_id"], event["timestamp"], event["type"], event["action"],
         event["request_id"], event["payload"], event["previous_state"], event["next_state"]),
    )
    conn.commit()
    return event


def submit(payload: dict, conn=None) -> dict:
    """新規Human Gateリクエストを生成し、PENDING状態のeventを記録する。"""
    owns_conn = conn is None
    if owns_conn:
        conn = _get_conn()
    try:
        _ensure_table(conn)
        request_id = payload.get("request_id") or _next_event_id()
        existing = get_state(request_id, conn=conn)
        if existing is not None:
            raise HumanGateError(f"request_id already exists with state={existing}")
        return _record_transition(conn, "submit", request_id, payload, previous_state=None)
    finally:
        if owns_conn:
            conn.close()


def _transition(action: str, request_id: str, payload: dict | None, conn=None) -> dict:
    payload = payload or {}
    owns_conn = conn is None
    if owns_conn:
        conn = _get_conn()
    try:
        _ensure_table(conn)
        current = get_state(request_id, conn=conn)
        if current is None:
            raise HumanGateError(f"request_id not found: {request_id}")
        if current not in TRANSITIONS[action]:
            raise HumanGateError(
                f"invalid transition: action={action} current_state={current} "
                f"allowed_from={sorted(TRANSITIONS[action])}"
            )
        return _record_transition(conn, action, request_id, payload, previous_state=current)
    finally:
        if owns_conn:
            conn.close()


def approve(request_id: str, payload: dict | None = None, conn=None) -> dict:
    return _transition("approve", request_id, payload, conn=conn)


def reject(request_id: str, payload: dict | None = None, conn=None) -> dict:
    return _transition("reject", request_id, payload, conn=conn)


def expire(request_id: str, payload: dict | None = None, conn=None) -> dict:
    return _transition("expire", request_id, payload, conn=conn)


def cancel(request_id: str, payload: dict | None = None, conn=None) -> dict:
    return _transition("cancel", request_id, payload, conn=conn)


def list_pending(conn=None) -> list:
    """pending_queueは存在しない。event列からPENDING状態のrequest_idを動的に再構築する。"""
    owns_conn = conn is None
    if owns_conn:
        conn = _get_conn()
    try:
        _ensure_table(conn)
        rows = conn.execute('''
            SELECT e.* FROM human_gate_events e
            WHERE e.event_id IN (
                SELECT event_id FROM (
                    SELECT event_id, request_id,
                           ROW_NUMBER() OVER (
                               PARTITION BY request_id
                               ORDER BY timestamp DESC, event_id DESC
                           ) AS rn
                    FROM human_gate_events
                ) WHERE rn = 1
            ) AND e.next_state = 'PENDING'
            ORDER BY e.timestamp ASC
        ''').fetchall()
        return [dict(r) for r in rows]
    finally:
        if owns_conn:
            conn.close()


# ── HTTP API(App層からのUIトリガ用) ──────────────────────────────────

@human_gate_bp.route('/api/human_gate/submit', methods=['POST'])
def http_submit():
    payload = request.get_json(force=True) or {}
    try:
        event = submit(payload)
        return jsonify({"status": "ok", "event": event}), 201
    except HumanGateError as e:
        return jsonify({"status": "rejected", "reason": e.reason}), 422


@human_gate_bp.route('/api/human_gate/approve', methods=['POST'])
def http_approve():
    payload = request.get_json(force=True) or {}
    request_id = payload.get("request_id", "")
    try:
        event = approve(request_id, payload)
        return jsonify({"status": "ok", "event": event}), 200
    except HumanGateError as e:
        return jsonify({"status": "rejected", "reason": e.reason}), 422


@human_gate_bp.route('/api/human_gate/reject', methods=['POST'])
def http_reject():
    payload = request.get_json(force=True) or {}
    request_id = payload.get("request_id", "")
    try:
        event = reject(request_id, payload)
        return jsonify({"status": "ok", "event": event}), 200
    except HumanGateError as e:
        return jsonify({"status": "rejected", "reason": e.reason}), 422


@human_gate_bp.route('/api/human_gate/status/<request_id>', methods=['GET'])
def http_status(request_id):
    state = get_state(request_id)
    if state is None:
        return jsonify({"status": "not_found"}), 404
    return jsonify({"status": "ok", "request_id": request_id, "state": state}), 200


@human_gate_bp.route('/api/human_gate/pending', methods=['GET'])
def http_pending():
    return jsonify({"status": "ok", "pending": list_pending()}), 200
