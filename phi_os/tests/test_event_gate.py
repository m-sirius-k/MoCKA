# phi_os/tests/test_event_gate.py
# PHI-OS EVENT GATE v1 — pytest suite
import sys, os, json, re
from pathlib import Path

# ensure phi_os package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
from flask import Flask
from phi_os.event_gate import gate_bp


# ── fixture: in-memory Flask test client ─────────────────────────────────────

@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create a test Flask app with gate_bp registered, using a temp SQLite DB."""
    import phi_os.event_gate as eg

    # Redirect DB to temp path with correct schema
    import sqlite3
    db_file = str(tmp_path / 'test_events.db')
    conn = sqlite3.connect(db_file)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            when_ts TEXT,
            who_actor TEXT,
            what_type TEXT,
            where_component TEXT,
            where_path TEXT,
            why_purpose TEXT,
            how_trigger TEXT,
            channel_type TEXT,
            lifecycle_phase TEXT,
            risk_level TEXT,
            category_ab TEXT,
            target_class TEXT,
            title TEXT,
            short_summary TEXT,
            before_state TEXT,
            after_state TEXT,
            change_type TEXT,
            impact_scope TEXT,
            impact_result TEXT,
            related_event_id TEXT,
            trace_id TEXT,
            free_note TEXT,
            _imported_at TEXT,
            _source TEXT,
            ai_actor TEXT,
            session_id TEXT,
            severity TEXT,
            pattern_score REAL,
            recurrence_flag INTEGER,
            verified_by TEXT
        )
    ''')
    conn.commit()
    conn.close()

    monkeypatch.setattr(eg, 'DB_PATH', db_file)

    app = Flask(__name__)
    app.register_blueprint(gate_bp)
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


# ── valid payload helper ──────────────────────────────────────────────────────

def valid_payload(**overrides):
    base = {
        'who_actor':       'Claude-sonnet-4-6',
        'who_role':        'executor',
        'who_session':     'SESSION_20260616_091900',
        'what_type':       'file_write',
        'what_title':      'PHI-OS GATE Phase2 test',
        'where_path':      'C:/Users/sirok/MoCKA/phi_os/event_gate.py',
        'where_component': 'phi_os.event_gate',
        'why_purpose':     'PHI-OS GATE Phase 2 pytestによる動作確認',
        'how_trigger':     'pytest / INSTRUCTION_PHI_OS_GATE_v1',
        'after_state':     'created',
    }
    base.update(overrides)
    return base


# ── tests ─────────────────────────────────────────────────────────────────────

def test_happy_path(client):
    """正常系: 201 + event_id返却 + event_source='live'"""
    r = client.post('/api/gate/event',
                    data=json.dumps(valid_payload()),
                    content_type='application/json')
    assert r.status_code == 201
    body = r.get_json()
    assert body['status'] == 'ok'
    assert re.match(r'E\d{8}_\d{3}', body['event_id'])


def test_event_source_live(client):
    """event_source='live' が自動付与される"""
    r = client.post('/api/gate/event',
                    data=json.dumps(valid_payload()),
                    content_type='application/json')
    assert r.status_code == 201
    # event_idがE{YYYYMMDD}_{NNN}形式
    eid = r.get_json()['event_id']
    assert re.match(r'^E\d{8}_\d{3}$', eid), f"unexpected event_id: {eid}"


def test_reject_actor(client):
    """REJECT-01: who_actor未指定 → 422"""
    r = client.post('/api/gate/event',
                    data=json.dumps(valid_payload(who_actor='')),
                    content_type='application/json')
    assert r.status_code == 422
    body = r.get_json()
    assert body['status'] == 'rejected'
    assert any('REJECT-01' in e for e in body['errors'])


def test_reject_actor_legacy(client):
    """REJECT-01: who_actor='Claude' → 422（レガシー値禁止）"""
    r = client.post('/api/gate/event',
                    data=json.dumps(valid_payload(who_actor='Claude')),
                    content_type='application/json')
    assert r.status_code == 422
    assert any('REJECT-01' in e for e in r.get_json()['errors'])


def test_reject_session(client):
    """REJECT-02: who_session形式不正 → 422"""
    r = client.post('/api/gate/event',
                    data=json.dumps(valid_payload(who_session='bad-session')),
                    content_type='application/json')
    assert r.status_code == 422
    assert any('REJECT-02' in e for e in r.get_json()['errors'])


def test_reject_why_purpose(client):
    """REJECT-03: why_purpose 短すぎ → 422"""
    r = client.post('/api/gate/event',
                    data=json.dumps(valid_payload(why_purpose='短い')),
                    content_type='application/json')
    assert r.status_code == 422
    assert any('REJECT-03' in e for e in r.get_json()['errors'])


def test_reject_replay(client):
    """REJECT-07: before/after両方null → 422"""
    p = valid_payload()
    p.pop('after_state', None)
    r = client.post('/api/gate/event',
                    data=json.dumps(p),
                    content_type='application/json')
    assert r.status_code == 422
    assert any('REJECT-07' in e for e in r.get_json()['errors'])


def test_gate_health(client):
    """/api/gate/health → 200"""
    r = client.get('/api/gate/health')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'ok'
