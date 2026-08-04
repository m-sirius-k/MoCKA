# phi_os/tests/test_event_write_integrity_boundary.py
# PHI-OS EVENT GATE — Event creation integrity boundary (R01 AUTHORIZED fix)
#
# events行と event_signatures は必ず対で成立させ、片方だけを残さないことを保証する。
#
# 修正前の挙動:
#   _write() の INSERT OR IGNORE が CHECK制約違反・PK重複を握りつぶすため、
#   行が入らないまま integrity.sign_event() が実行され、
#   "存在しないイベントの署名" (Signature != Evidence)が残留していた。
#   呼び出し元には status=ok が返るため、記録されていないことが検知できなかった。
#
# 修正後に保証すること:
#   1. events行が成立しなかった場合、署名は生成されない
#   2. 呼び出し元には status="error" が返る (okを返さない)
#   3. verify_chain が missing_event_row を報告する状態を作らない
#   4. batch経路では、失敗イベントが兄弟イベントの書き込みを巻き添えにしない
#   5. 失敗したイベントの idempotency_key は記録されない (再送を殺さない)
import sqlite3
import sys
from pathlib import Path

import pytest
from flask import Flask

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "interface"))

from gate_policy import ALLOWED_SOURCE_VALUES  # noqa: E402

BAD_SOURCE = "definitely_not_an_allowed_source"


def _valid_payload(**overrides):
    p = {
        "who_actor": "Claude-opus-5",
        "who_role": "executor",
        "who_session": "SESSION_20260804_000000",
        "what_type": "claude_mcp",
        "what_title": "TEST: integrity boundary",
        "where_path": "phi_os/event_gate.py",
        "where_component": "event_gate",
        "why_purpose": "Event creation integrity boundary の検証",
        "how_trigger": "pytest",
        "after_state": "written",
    }
    p.update(overrides)
    return p


@pytest.fixture
def gate(tmp_path, monkeypatch):
    """_source CHECK制約つきの本番同形DBを用意し、event_gateをそこへ向ける"""
    import phi_os.event_gate as eg

    values = ", ".join("'%s'" % v for v in sorted(ALLOWED_SOURCE_VALUES))
    db = tmp_path / "events.db"
    con = sqlite3.connect(str(db))
    con.execute("""
        CREATE TABLE events (
            event_id TEXT PRIMARY KEY, when_ts TEXT NOT NULL, who_actor TEXT,
            what_type TEXT, where_component TEXT, where_path TEXT,
            why_purpose TEXT, how_trigger TEXT, channel_type TEXT,
            lifecycle_phase TEXT, risk_level TEXT, title TEXT, short_summary TEXT,
            before_state TEXT, after_state TEXT, related_event_id TEXT,
            trace_id TEXT, free_note TEXT,
            _source TEXT NOT NULL CHECK (_source IN (%s)),
            session_id TEXT
        )
    """ % values)
    # 本番DBには既にsignatures表が存在するため、同条件に揃える
    # (失敗時に表が作られないこと自体を検証対象にしない)
    import phi_os.integrity as integ
    integ.ensure_signatures_table(con)
    con.commit()
    con.close()

    monkeypatch.setattr(eg, "DB_PATH", str(db))
    return eg, db


def _count(db, sql, params=()):
    con = sqlite3.connect(str(db))
    try:
        return con.execute(sql, params).fetchone()[0]
    finally:
        con.close()


# -- 1. 単発経路 (process_event) ----

def test_failed_write_returns_error_not_ok(gate):
    eg, _ = gate
    res = eg.process_event(_valid_payload(), event_source=BAD_SOURCE)
    assert res["status"] == "error", res
    assert res["errors"], res


def test_failed_write_leaves_no_event_and_no_signature(gate):
    eg, db = gate
    res = eg.process_event(_valid_payload(), event_source=BAD_SOURCE)
    eid = res["event_id"]
    assert _count(db, "SELECT COUNT(*) FROM events WHERE event_id=?", (eid,)) == 0
    assert _count(db, "SELECT COUNT(*) FROM event_signatures WHERE event_id=?", (eid,)) == 0


def test_failed_write_does_not_break_hash_chain(gate):
    """失敗イベントの後も、正常イベントのチェーンが健全であること"""
    import phi_os.integrity as integ
    eg, db = gate

    ok1 = eg.process_event(_valid_payload(what_title="first"), event_source="live")
    bad = eg.process_event(_valid_payload(what_title="bad"), event_source=BAD_SOURCE)
    ok2 = eg.process_event(_valid_payload(what_title="second"), event_source="live")

    assert ok1["status"] == "ok" and ok2["status"] == "ok"
    assert bad["status"] == "error"

    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    chain = integ.verify_chain(con)
    con.close()
    assert not any(a["type"] == "missing_event_row" for a in chain["anomalies"]), chain["anomalies"]
    assert chain["checked"] == 2, chain


def test_duplicate_event_id_is_reported_not_silently_ignored(gate):
    """
    PK重複も INSERT OR IGNORE に握りつぶされていた。
    2回目は status=error になり、署名が二重に積まれないこと。
    """
    eg, db = gate
    first = eg.process_event(_valid_payload(event_id="E20260804_FIXED"), event_source="live")
    second = eg.process_event(_valid_payload(event_id="E20260804_FIXED"), event_source="live")

    assert first["status"] == "ok", first
    assert second["status"] == "error", second
    assert "duplicate" in second["errors"][0]
    assert _count(db, "SELECT COUNT(*) FROM events WHERE event_id=?", ("E20260804_FIXED",)) == 1
    assert _count(db, "SELECT COUNT(*) FROM event_signatures WHERE event_id=?",
                  ("E20260804_FIXED",)) == 1


# -- 2. 正常経路が変わっていないこと ----

def test_normal_path_is_unchanged(gate):
    eg, db = gate
    res = eg.process_event(_valid_payload(), event_source="live")
    assert res["status"] == "ok"
    assert "errors" not in res

    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM events WHERE event_id=?", (res["event_id"],)).fetchone()
    sig = con.execute("SELECT * FROM event_signatures WHERE event_id=?",
                      (res["event_id"],)).fetchone()
    con.close()
    assert row["_source"] == "live"
    assert sig is not None
    assert row["trace_id"] == sig["current_hash"]
    assert row["related_event_id"] == sig["previous_hash"]


def test_validation_rejection_is_still_rejected_not_error(gate):
    """Validation拒否(DBに触れない)と書き込み失敗(error)を取り違えないこと"""
    eg, db = gate
    res = eg.process_event(_valid_payload(who_actor="claude"), event_source="live")
    assert res["status"] == "rejected", res
    assert any("REJECT-01" in e for e in res["errors"])
    assert _count(db, "SELECT COUNT(*) FROM events") == 0


# -- 3. HTTPルートのステータスコード ----

@pytest.fixture
def client(gate):
    eg, db = gate
    app = Flask(__name__)
    app.register_blueprint(eg.gate_bp)
    return app.test_client(), db


def test_http_route_returns_500_on_write_failure(client):
    """
    書き込み失敗を201(Created)で返さないこと。
    ルート側はevent_source='live'固定のため、同一event_idの再送(PK重複)で誘発する。
    """
    c, db = client
    first = c.post("/api/gate/event", json=_valid_payload(event_id="E_HTTP_DUP"))
    assert first.status_code == 201

    second = c.post("/api/gate/event", json=_valid_payload(event_id="E_HTTP_DUP"))
    assert second.status_code == 500, (second.status_code, second.get_json())
    assert second.get_json()["status"] == "error"
    # 署名が二重に積まれていないこと
    assert _count(db, "SELECT COUNT(*) FROM event_signatures") == 1


def test_http_route_still_returns_201_on_success(client):
    c, _ = client
    r = c.post("/api/gate/event", json=_valid_payload())
    assert r.status_code == 201, r.get_json()
    assert r.get_json()["status"] == "ok"


def test_http_route_still_returns_422_on_validation_reject(client):
    c, _ = client
    r = c.post("/api/gate/event", json=_valid_payload(who_actor=""))
    assert r.status_code == 422


# -- 4. batch経路 (共有conn / SAVEPOINT) ----

def _op_event(**overrides):
    ev = {
        "who_actor": "orchestra-extension",
        "what_type": "handshake",
        "where_component": "extension",
        "why_purpose": "operational telemetry",
        "title": "batch event",
    }
    ev.update(overrides)
    return ev


def test_batch_failure_does_not_roll_back_sibling_events(gate):
    """
    共有connでの失敗が、同一バッチ内の正常イベントを巻き添えにしないこと
    (当該イベント分のSAVEPOINTのみを巻き戻す)。
    """
    eg, db = gate
    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    eg._ensure_idempotency_table(con)

    r_ok1 = eg.process_buffered_event(_op_event(title="sibling-1"), con)
    r_bad = eg.process_buffered_event(
        _op_event(title="bad", event_source=BAD_SOURCE, idempotency_key="KEY_BAD"), con)
    r_ok2 = eg.process_buffered_event(_op_event(title="sibling-2"), con)
    con.commit()
    con.close()

    assert r_ok1["status"] == "ok", r_ok1
    assert r_bad["status"] == "error", r_bad
    assert r_ok2["status"] == "ok", r_ok2
    # 兄弟イベントは残り、失敗イベントは残らない
    assert _count(db, "SELECT COUNT(*) FROM events") == 2
    assert _count(db, "SELECT COUNT(*) FROM event_signatures") == 2


def test_failed_batch_event_does_not_record_idempotency_key(gate):
    """
    失敗したイベントのidempotency_keyを記録しないこと。
    記録すると再送時に duplicate として握りつぶされ、イベントが永久に失われる。
    """
    eg, db = gate
    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    eg._ensure_idempotency_table(con)

    bad = eg.process_buffered_event(
        _op_event(event_source=BAD_SOURCE, idempotency_key="KEY_RETRY"), con)
    assert bad["status"] == "error"
    con.commit()
    assert _count(db, "SELECT COUNT(*) FROM gate_idempotency WHERE idempotency_key=?",
                  ("KEY_RETRY",)) == 0

    # 同じキーで再送すると(今度は正常なsourceで)受け付けられること
    retry = eg.process_buffered_event(_op_event(idempotency_key="KEY_RETRY"), con)
    con.commit()
    con.close()
    assert retry["status"] == "ok", retry


def test_batch_endpoint_counts_failure_as_rejected(gate):
    """レスポンス形状は変えず、失敗イベントをacceptedに数えないこと"""
    eg, _ = gate
    app = Flask(__name__)
    app.register_blueprint(eg.gate_bp)
    r = app.test_client().post("/api/gate/event/batch", json={"events": [
        _op_event(title="good"),
        _op_event(title="bad", event_source=BAD_SOURCE, idempotency_key="K1"),
    ]})
    body = r.get_json()
    assert r.status_code == 200
    assert set(body) == {"status", "accepted_count", "accepted",
                         "duplicate_count", "rejected"}   # 形状不変
    assert body["accepted_count"] == 1, body
    assert len(body["rejected"]) == 1, body
