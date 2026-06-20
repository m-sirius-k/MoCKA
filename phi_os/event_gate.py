# phi_os/event_gate.py
# PHI-OS EVENT GATE v1 — Single Entry Point for all MoCKA events
# v2: Local Buffer + async flush対応のbatch ingestion追加（TODO_347）
from flask import Blueprint, request, jsonify
from .gate_validator import validate, validate_operational
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
            'SELECT trace_id FROM events ORDER BY rowid DESC LIMIT 1'
        ).fetchone()
        return row['trace_id'] if row and row['trace_id'] else ''
    except Exception:
        return ''
    finally:
        conn.close()


def _write(payload: dict, conn=None) -> None:
    # GATEペイロードを実DBスキーマ列にマッピング
    # title/descriptionはgovernance write(what_title/description)と
    # operational telemetry(title/free_note/short_summary)の両方の
    # キー名を受け付ける（Local Buffer経由イベントとの互換のため）
    row = {
        'event_id':        payload.get('event_id', ''),
        'when_ts':         payload.get('when_ts') or payload.get('when', ''),
        'who_actor':       payload.get('who_actor', ''),
        'what_type':       payload.get('what_type', ''),
        'where_component': payload.get('where_component', ''),
        'where_path':      payload.get('where_path', ''),
        'why_purpose':     payload.get('why_purpose', ''),
        'how_trigger':     payload.get('how_trigger', ''),
        'before_state':    payload.get('before_state', ''),
        'after_state':     payload.get('after_state', ''),
        'title':           payload.get('what_title') or payload.get('title', ''),
        'short_summary':   payload.get('description') or payload.get('short_summary', ''),
        'session_id':      payload.get('who_session') or payload.get('session_id', ''),
        '_source':         payload.get('event_source', 'live'),
        'trace_id':        payload.get('event_hash', ''),
        'related_event_id':payload.get('prev_hash', ''),
        'free_note': '|'.join(filter(None, [
            payload.get('tags', '') or payload.get('free_note', ''),
            f"who_role={payload.get('who_role','')}",
            f"event_source={payload.get('event_source','live')}",
            f"orig_channel={payload['channel_type']}" if payload.get('channel_type') and payload.get('channel_type') != 'gate' else '',
        ])),
        'channel_type':    'gate',
        'lifecycle_phase': 'in_operation',
        'risk_level':      'normal',
    }
    # 空文字列はNoneに変換して保存
    row = {k: (v if v != '' else None) for k, v in row.items()}
    owns_conn = conn is None
    if owns_conn:
        conn = _get_conn()
    try:
        cols = list(row.keys())
        placeholders = ','.join('?' * len(cols))
        vals = [row[c] for c in cols]
        conn.execute(
            f'INSERT OR IGNORE INTO events ({",".join(cols)}) VALUES ({placeholders})',
            vals
        )
        if owns_conn:
            conn.commit()
    finally:
        if owns_conn:
            conn.close()


def _ensure_idempotency_table(conn) -> None:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS gate_idempotency (
            idempotency_key TEXT PRIMARY KEY,
            event_id TEXT,
            created_at TEXT
        )
    ''')


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


@gate_bp.route('/api/gate/event/batch', methods=['POST'])
def receive_event_batch():
    """
    Local Event Buffer用のbatch ingestionエンドポイント（TODO_347）。
    単発の/api/gate/eventはAI主体のgovernance writeの厳格検証(validate)を
    維持するため変更しない。本エンドポイントはhandshake/chat等の高頻度
    operational telemetry専用で、validate_operational()による軽量検証と
    idempotency_keyによる重複防止(リトライ時の二重書き込み防止)を行う。
    """
    payload = request.get_json(force=True) or {}
    events = payload.get('events', [])
    if not isinstance(events, list):
        return jsonify({'status': 'rejected', 'errors': ['events must be a list']}), 422

    conn = _get_conn()
    accepted, rejected, duplicate_count = [], [], 0
    try:
        _ensure_idempotency_table(conn)
        for ev in events:
            idem_key = ev.get('idempotency_key')
            if idem_key:
                dup = conn.execute(
                    'SELECT 1 FROM gate_idempotency WHERE idempotency_key = ?', (idem_key,)
                ).fetchone()
                if dup:
                    duplicate_count += 1
                    continue

            errors = validate_operational(ev)
            if errors:
                rejected.append({'idempotency_key': idem_key, 'errors': errors})
                continue

            req_id = ev.get('event_id')
            dup_id = conn.execute(
                'SELECT 1 FROM events WHERE event_id = ?', (req_id,)
            ).fetchone() if req_id else None
            eid = req_id if (req_id and not dup_id) else _next_event_id()

            ev['event_id'] = eid
            ev['when_ts'] = ev.get('when_ts') or ev.get('when') or datetime.now(timezone.utc).isoformat()
            ev['event_source'] = ev.get('event_source', 'buffered')
            ev['event_hash'] = _hash(ev)
            ev['prev_hash'] = _last_hash()

            _write(ev, conn=conn)

            if idem_key:
                conn.execute(
                    'INSERT OR IGNORE INTO gate_idempotency (idempotency_key, event_id, created_at) '
                    'VALUES (?, ?, ?)',
                    (idem_key, eid, datetime.now(timezone.utc).isoformat())
                )
            accepted.append(eid)
        conn.commit()
    finally:
        conn.close()

    return jsonify({
        'status': 'ok',
        'accepted_count': len(accepted),
        'accepted': accepted,
        'duplicate_count': duplicate_count,
        'rejected': rejected,
    }), 200


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
