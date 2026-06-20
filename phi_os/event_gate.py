# phi_os/event_gate.py
# PHI-OS EVENT GATE v1 — Single Entry Point for all MoCKA events
# v2: Local Buffer + async flush対応のbatch ingestion追加（TODO_347）
from flask import Blueprint, request, jsonify
from .gate_validator import validate, validate_operational
import sqlite3, hashlib, json, time, secrets, sys
from datetime import datetime, date, timezone
from pathlib import Path

gate_bp = Blueprint('event_gate', __name__)

# Single Truth DB — data/mocka_events.db (絶対パス解決)
_REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(_REPO_ROOT / 'data' / 'mocka_events.db')

sys.path.insert(0, str(_REPO_ROOT / 'interface'))
from gate_policy import POLICY_VERSION as GATE_POLICY_VERSION  # Phase5-1 Gate Policy


# ── helpers ──────────────────────────────────────────────────────────────────

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _next_event_id() -> str:
    """
    time-ordered unique id（TODO_347 TASK1）。
    SELECT COUNT(*)/MAX(id)+1方式は並列書き込みで衝突するため廃止。
    日内マイクロ秒（time-ordered）+ ランダム4hex（衝突防止）でDB問い合わせ不要・
    並列安全・衝突率ゼロ設計とする。
    """
    d = date.today().strftime('%Y%m%d')
    micros_of_day = time.time_ns() // 1000 % 1_000_000_000
    return f'E{d}_{micros_of_day:09d}{secrets.token_hex(2)}'


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

    # TEMP-TRACE: remove after investigation
    try:
        import traceback, threading, os as _os, json as _json
        from datetime import datetime as _dt, timezone as _tz
        _src_val = row.get('_source')
        _stack = traceback.extract_stack()
        _frames = [f"{f.filename}:{f.lineno}:{f.name}" for f in _stack[-8:]]
        with open(r"C:\Users\sirok\MoCKA\gate_trace_temp.log", "a", encoding="utf-8") as _tf:
            _tf.write(_json.dumps({
                "ts": _dt.now(_tz.utc).isoformat(),
                "pid": _os.getpid(),
                "thread_ident": threading.get_ident(),
                "thread_name": threading.current_thread().name,
                "func": "event_gate._write",
                "_source_value": _src_val,
                "event_id": row.get("event_id"),
                "where_component": row.get("where_component"),
                "what_type": row.get("what_type"),
                "stack": _frames,
                "full_row": {k: row.get(k) for k in row},
            }, ensure_ascii=False) + "\n")
            _tf.flush()
    except Exception:
        pass
    # END TEMP-TRACE

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


# Gate確立日（health_check.py GATE_LAUNCH_DATEと同一基準）。
# 確立以前の旧データを「non_gate_events」に含めると、現在進行中の
# direct write違反と過去の歴史的バックログが混同され、UI上の異常検知が
# 誤警告になる（TODO_347 vFinal運用で発覚）。
GATE_LAUNCH_DATE = "2026-06-16"


@gate_bp.route('/api/gate/audit', methods=['GET'])
def gate_audit():
    """
    TODO_347 TASK6 / vFinal / Phase5-1: real-time(live) / buffered / 許可Direct / 違反Direct
    の4分類表示。合算した単一指標は提供しない。
    集計対象はGATE_LAUNCH_DATE以降のイベントのみ（健全性監視はhealth_check.py
    check_phi_os_auditと同一基準に揃える）。
    Phase5-1 Gate Policy: 許可されたDirect Write(_source='direct_allowed:{channel}')は
    監査上violationとしない。それ以外でGate未経由（live/buffered以外）のものは
    すべて制度違反(violation)として検出する。
    """
    conn = _get_conn()
    try:
        total = conn.execute(
            'SELECT COUNT(*) FROM events WHERE when_ts >= ?', (GATE_LAUNCH_DATE,)
        ).fetchone()[0]
        live = conn.execute(
            "SELECT COUNT(*) FROM events WHERE _source='live' AND when_ts >= ?", (GATE_LAUNCH_DATE,)
        ).fetchone()[0]
        buffered = conn.execute(
            "SELECT COUNT(*) FROM events WHERE _source='buffered' AND when_ts >= ?", (GATE_LAUNCH_DATE,)
        ).fetchone()[0]
        allowed_direct = conn.execute(
            "SELECT COUNT(*) FROM events WHERE _source LIKE 'direct_allowed:%' AND when_ts >= ?",
            (GATE_LAUNCH_DATE,)
        ).fetchone()[0]
        legacy_total = conn.execute(
            'SELECT COUNT(*) FROM events WHERE when_ts < ?', (GATE_LAUNCH_DATE,)
        ).fetchone()[0]
    finally:
        conn.close()
    gate_routed = live + buffered
    violation = max(total - gate_routed - allowed_direct, 0)
    rate = round(gate_routed / total * 100, 2) if total else 0.0
    return jsonify({
        'status': 'ok',
        'policy_version': GATE_POLICY_VERSION,
        'gate_launch_date': GATE_LAUNCH_DATE,
        'real_time_events': {'count': live, 'source': '/api/gate/event'},
        'buffered_events': {'count': buffered, 'source': '/api/gate/event/batch'},
        'allowed_direct_events': {'count': allowed_direct, 'note': '許可チャネル(bootstrap/maintenance/migration/restore/recovery)経由のDirect Write'},
        'violation_events': {'count': violation, 'note': f'{GATE_LAUNCH_DATE}以降でGate未経由・許可チャネルでもない制度違反件数'},
        'legacy_events': {'count': legacy_total, 'note': f'{GATE_LAUNCH_DATE}以前のGate確立前バックログ（監査対象外）'},
        'gate_passthrough_rate_percent': rate,
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
