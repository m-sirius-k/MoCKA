# phi_os/event_gate.py
# PHI-OS EVENT GATE v1 — Single Entry Point for all MoCKA events
from flask import Blueprint, request, jsonify
from .gate_validator import validate
import sqlite3, hashlib, json
from datetime import datetime, date, timezone
from pathlib import Path

gate_bp = Blueprint('event_gate', __name__)

# Single Truth DB — data/mocka_events.db (絶対パス解決)
_REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(_REPO_ROOT / 'data' / 'mocka_events.db')


# ── helpers ──────────────────────────────────────────────────────────────────

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _next_event_id() -> str:
    d = date.today().strftime('%Y%m%d')
    conn = _get_conn()
    try:
        n = conn.execute(
            'SELECT COUNT(*) FROM events WHERE event_id LIKE ?',
            (f'E{d}_%',)
        ).fetchone()[0]
    finally:
        conn.close()
    return f'E{d}_{n + 1:03d}'


def _hash(payload: dict) -> str:
    canon = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canon.encode('utf-8')).hexdigest()[:16]


def _last_hash() -> str:
    conn = _get_conn()
    try:
        row = conn.execute(
            'SELECT event_hash FROM events ORDER BY rowid DESC LIMIT 1'
        ).fetchone()
        return row['event_hash'] if row and row['event_hash'] else ''
    except Exception:
        return ''
    finally:
        conn.close()


def _write(payload: dict) -> None:
    conn = _get_conn()
    try:
        cols = list(payload.keys())
        placeholders = ','.join('?' * len(cols))
        vals = [payload[c] for c in cols]
        conn.execute(
            f'INSERT OR IGNORE INTO events ({",".join(cols)}) VALUES ({placeholders})',
            vals
        )
        conn.commit()
    finally:
        conn.close()


# ── endpoint ──────────────────────────────────────────────────────────────────

@gate_bp.route('/api/gate/event', methods=['POST'])
def receive_event():
    payload = request.get_json(force=True) or {}

    errors = validate(payload)
    if errors:
        return jsonify({'status': 'rejected', 'errors': errors}), 422

    # Gate自動付与フィールド
    payload['event_id'] = _next_event_id()
    payload['when_ts'] = datetime.now(timezone.utc).isoformat()
    payload['event_source'] = 'live'
    payload['event_hash'] = _hash(payload)
    payload['prev_hash'] = _last_hash()

    _write(payload)

    return jsonify({'status': 'ok', 'event_id': payload['event_id']}), 201


@gate_bp.route('/api/gate/health', methods=['GET'])
def gate_health():
    conn = _get_conn()
    try:
        count = conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]
        return jsonify({'status': 'ok', 'db': DB_PATH, 'event_count': count}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'detail': str(e)}), 500
    finally:
        conn.close()
