# phi_os/tests/test_integrity.py
# Phase5-2 Event Integrity Framework -- pytest suite
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "phi_os"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "interface"))

import sqlite3
import pytest

from phi_os import integrity
from gate_policy import ALLOWED_SOURCE_VALUES


# ── fixture: temp sqlite db with full events schema ──────────────────────────
# _sourceはgate_policy.ALLOWED_SOURCE_VALUESに対するCHECK制約付きで作成する。
# schema_audit.audit_schema()がこのCHECK句を解析するため、テストDBも本番と
# 同じ制約形式でなければ"schema_inconsistency"が常に発生してしまう。
_SOURCE_CHECK_VALUES = ", ".join(f"'{v}'" for v in sorted(ALLOWED_SOURCE_VALUES))

EVENTS_SCHEMA = f'''
    CREATE TABLE events (
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
        _source TEXT NOT NULL CHECK (_source IN ({_SOURCE_CHECK_VALUES})),
        ai_actor TEXT,
        session_id TEXT,
        severity TEXT,
        pattern_score REAL,
        recurrence_flag INTEGER,
        verified_by TEXT
    )
'''


@pytest.fixture
def conn(tmp_path):
    db_file = str(tmp_path / 'test_integrity.db')
    c = sqlite3.connect(db_file)
    c.row_factory = sqlite3.Row
    # テスト高速化: tmp_path配下の使い捨てDBなのでfsync/WALログは不要
    c.execute('PRAGMA synchronous = OFF')
    c.execute('PRAGMA journal_mode = MEMORY')
    c.execute(EVENTS_SCHEMA)
    c.commit()
    yield c
    c.close()


def _make_event(event_id: str, **overrides) -> dict:
    base = {
        'event_id': event_id,
        'when_ts': '2026-06-20T00:00:00+00:00',
        'who_actor': 'Claude-sonnet-4-6',
        'what_type': 'record',
        'title': 'test event',
        'short_summary': 'integrity test fixture',
        'before_state': None,
        'after_state': 'created',
        '_source': 'live',
        'free_note': None,
    }
    base.update(overrides)
    return base


def _insert_and_sign(conn, event_id: str, **overrides) -> dict:
    row = _make_event(event_id, **overrides)
    cols = list(row.keys())
    placeholders = ','.join('?' * len(cols))
    conn.execute(
        f'INSERT INTO events ({",".join(cols)}) VALUES ({placeholders})',
        [row[c] for c in cols]
    )
    sig = integrity.sign_event(conn, row)
    conn.commit()
    return sig


# ── 1. normal chain ───────────────────────────────────────────────────────────

def test_normal_chain_verifies_ok(conn):
    for i in range(5):
        _insert_and_sign(conn, f'E_TEST_{i:03d}')
    result = integrity.verify_chain(conn)
    assert result['ok'] is True
    assert result['checked'] == 5
    assert result['anomalies'] == []


# ── 2. chain break ─────────────────────────────────────────────────────────────

def test_chain_break_detected(conn):
    for i in range(3):
        _insert_and_sign(conn, f'E_TEST_{i:03d}')
    # seq=2のprevious_hashを破壊する
    conn.execute(
        "UPDATE event_signatures SET previous_hash = 'corrupted' WHERE seq = 2"
    )
    conn.commit()
    result = integrity.verify_chain(conn)
    assert result['ok'] is False
    types = {a['type'] for a in result['anomalies']}
    assert 'chain_break' in types or 'hash_mismatch' in types


# ── 3. tampering ───────────────────────────────────────────────────────────────

def test_tampering_detected_as_hash_mismatch(conn):
    for i in range(3):
        _insert_and_sign(conn, f'E_TEST_{i:03d}')
    # eventsの内容を署名後に書き換える(改ざんシミュレーション)
    conn.execute("UPDATE events SET title = 'TAMPERED' WHERE event_id = 'E_TEST_001'")
    conn.commit()
    result = integrity.verify_chain(conn)
    assert result['ok'] is False
    assert any(a['type'] == 'hash_mismatch' and a['event_id'] == 'E_TEST_001'
               for a in result['anomalies'])


# ── 4. missing seq (gap) ──────────────────────────────────────────────────────

def test_missing_seq_detected(conn):
    for i in range(4):
        _insert_and_sign(conn, f'E_TEST_{i:03d}')
    conn.execute("DELETE FROM event_signatures WHERE seq = 2")
    conn.commit()
    result = integrity.verify_chain(conn)
    assert result['ok'] is False
    assert any(a['type'] == 'missing_seq' for a in result['anomalies'])


# ── 5. duplicate / unsigned event ─────────────────────────────────────────────

def test_unsigned_event_detected(conn):
    _insert_and_sign(conn, 'E_TEST_000')
    # event_signaturesを経由せずeventsへ直接挿入(署名漏れシミュレーション)
    conn.execute(
        "INSERT INTO events (event_id, when_ts, title, _source) "
        "VALUES ('E_TEST_UNSIGNED', '2026-06-20T01:00:00+00:00', 'x', 'live')"
    )
    conn.commit()
    result = integrity.verify_chain(conn)
    assert result['ok'] is False
    assert any(a['type'] == 'unsigned_event' and a['event_id'] == 'E_TEST_UNSIGNED'
               for a in result['anomalies'])


def test_duplicate_seq_rejected_by_unique_constraint(conn):
    _insert_and_sign(conn, 'E_TEST_000')
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO event_signatures "
            "(event_id, seq, timestamp, previous_hash, current_hash, "
            "signature_version, algorithm) VALUES (?, 1, 'x', '', 'dup', '1.0', 'sha256')",
            ('E_TEST_DUP',)
        )


# ── 6. signature version / algorithm validation ───────────────────────────────

def test_invalid_signature_version_detected(conn):
    _insert_and_sign(conn, 'E_TEST_000')
    conn.execute("UPDATE event_signatures SET signature_version = '999.0'")
    conn.commit()
    result = integrity.verify_chain(conn)
    assert result['ok'] is False
    assert any(a['type'] == 'invalid_signature_version' for a in result['anomalies'])


def test_invalid_algorithm_detected(conn):
    _insert_and_sign(conn, 'E_TEST_000')
    conn.execute("UPDATE event_signatures SET algorithm = 'md5_legacy_unknown'")
    conn.commit()
    result = integrity.verify_chain(conn)
    assert result['ok'] is False
    assert any(a['type'] == 'invalid_algorithm' for a in result['anomalies'])


# ── 7. diagnose / recovery support ────────────────────────────────────────────

def test_diagnose_returns_candidate_cause_and_repair(conn):
    for i in range(3):
        _insert_and_sign(conn, f'E_TEST_{i:03d}')
    conn.execute("UPDATE events SET title = 'TAMPERED' WHERE event_id = 'E_TEST_001'")
    conn.commit()
    result = integrity.verify_chain(conn)
    report = integrity.diagnose(result['anomalies'])
    assert len(report) == len(result['anomalies'])
    for d in report:
        assert d['candidate_cause']
        assert d['candidate_repair']


# ── 8. post-migration consistency ─────────────────────────────────────────────

def test_migration_backfill_consistency(tmp_path, monkeypatch):
    """legacy行(署名なし)をmigrate_event_integrity.run_migrationで遡及署名し、
    結果がverify_chainでOKになることを確認する"""
    import scripts.migrate_event_integrity as mig

    db_file = tmp_path / 'legacy_events.db'
    c = sqlite3.connect(str(db_file))
    c.execute(EVENTS_SCHEMA)
    for i in range(5):
        c.execute(
            "INSERT INTO events (event_id, when_ts, title, _source) "
            "VALUES (?, ?, ?, 'legacy')",
            (f'E_LEGACY_{i:03d}', f'2026-06-1{i}T00:00:00+00:00', f'legacy event {i}')
        )
    c.commit()
    c.close()

    report_file = tmp_path / 'report.json'
    monkeypatch.setattr(mig, 'DB_PATH', db_file)
    monkeypatch.setattr(mig, 'REPORT_PATH', report_file)

    result = mig.run_migration(dry_run=False)
    assert result['status'] == 'done'
    assert result['signed_now'] == 5
    assert result['verify_result']['ok'] is True


# ── 9. performance smoke ──────────────────────────────────────────────────────

def test_performance_chain_of_2000_events(conn):
    start = time.time()
    for i in range(2000):
        _insert_and_sign(conn, f'E_PERF_{i:05d}')
    sign_elapsed = time.time() - start

    start = time.time()
    result = integrity.verify_chain(conn)
    verify_elapsed = time.time() - start

    assert result['ok'] is True
    assert result['checked'] == 2000
    assert sign_elapsed < 10.0
    assert verify_elapsed < 10.0
