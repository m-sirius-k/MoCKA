"""
orchestra.tests.test_orchestra_engine

セッション管理/イベント処理/ノード実行/外部IF/SQLite永続化/Replayの動作テスト。

テスト用エンジンは ":memory:" SQLiteを使い、リポジトリ内に
DBファイルを作成しない。
"""

import time

from core_kernel.orchestra import Event, OrchestraEngine, ReplayEngine, SQLiteStore
from core_kernel.orchestra.orchestra_engine import OrchestraEngine as _Engine


def _store():
    return SQLiteStore(db_path=":memory:")


def _event(event_type="USER_MESSAGE", session_id="session-001", payload=None):
    return Event(
        event_id=str(time.time()),
        event_type=event_type,
        session_id=session_id,
        timestamp=time.time(),
        payload=payload or {},
    )


def test_get_session_creates_and_reuses_session():
    engine = OrchestraEngine(store=_store())

    session1 = engine.get_session("session-001")
    session2 = engine.get_session("session-001")

    assert session1 is session2
    assert session1.session_id == "session-001"


def test_on_event_updates_session_event_log():
    engine = OrchestraEngine(store=_store())
    event = _event()

    engine.on_event(event)

    session = engine.get_session("session-001")
    assert session.event_log == [event]
    assert session.execution_log == []
    assert session.output_log == []


def test_on_event_publishes_to_subscribed_handlers():
    engine = OrchestraEngine(store=_store())
    received = []
    engine.bus.subscribe("USER_MESSAGE", received.append)

    event = _event()
    results = engine.on_event(event)

    assert received == [event]
    assert results == [None]


def test_on_event_routes_to_target_node():
    engine = OrchestraEngine(store=_store())

    def test_node(ctx):
        return {
            "message": "Orchestra is running",
            "session": ctx["session_id"],
            "event": ctx["event"].event_type,
        }

    engine.register_node("root", test_node)

    event = _event(payload={"target_node": "root", "text": "hello"})
    result = engine.on_event(event)

    assert result == {
        "message": "Orchestra is running",
        "session": "session-001",
        "event": "USER_MESSAGE",
    }

    session = engine.get_session("session-001")
    assert len(session.execution_log) == 1
    assert session.execution_log[0]["node_id"] == "root"
    assert session.output_log == [result]


def test_on_event_unknown_node_raises():
    engine = OrchestraEngine(store=_store())
    event = _event(payload={"target_node": "missing"})

    try:
        engine.on_event(event)
        assert False, "expected Exception"
    except Exception as exc:
        assert "missing" in str(exc)


def test_external_api_emit_and_register_node():
    from core_kernel.orchestra import orchestrator_api

    # 既存グローバルengineを汚さないよう、テスト専用エンジンに差し替える
    original_engine = orchestrator_api.engine
    orchestrator_api.engine = _Engine(store=_store())
    try:
        def test_node(ctx):
            return {
                "message": "Orchestra is running",
                "session": ctx["session_id"],
                "event": ctx["event"].event_type,
            }

        orchestrator_api.register_node("root", test_node)

        result = orchestrator_api.emit_event(
            "USER_MESSAGE",
            "session-001",
            {"target_node": "root", "text": "hello"},
        )

        assert result == {
            "message": "Orchestra is running",
            "session": "session-001",
            "event": "USER_MESSAGE",
        }
    finally:
        orchestrator_api.engine = original_engine


# ----------------------------------------------------------------------
# SQLite永続化 / Replay
# ----------------------------------------------------------------------

def test_on_event_persists_event_to_store():
    store = _store()
    engine = OrchestraEngine(store=store)
    event = _event(payload={"text": "hello"})

    engine.on_event(event)

    rows = store.load_session_events("session-001")
    assert len(rows) == 1
    assert rows[0][0] == event.event_id
    assert rows[0][1] == "session-001"
    assert rows[0][2] == "USER_MESSAGE"


def test_on_event_persists_execution_and_output():
    store = _store()
    engine = OrchestraEngine(store=store)
    engine.register_node("root", lambda ctx: {"ok": True})

    event = _event(payload={"target_node": "root"})
    engine.on_event(event)

    conn = store._connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM executions")
    executions = cur.fetchall()
    cur.execute("SELECT * FROM outputs")
    outputs = cur.fetchall()
    conn.close()

    assert len(executions) == 1
    assert executions[0][2] == "root"
    assert len(outputs) == 1


def test_replay_session_reconstructs_events_in_order():
    store = _store()
    engine = OrchestraEngine(store=store)

    first = _event(event_type="A", payload={"n": 1})
    time.sleep(0.001)
    second = _event(event_type="B", payload={"n": 2})

    engine.on_event(first)
    engine.on_event(second)

    replay = ReplayEngine(store=store)
    reconstructed = replay.replay_session("session-001")

    assert [r["event_type"] for r in reconstructed] == ["A", "B"]
    assert reconstructed[0]["payload"] == {"n": 1}
    assert reconstructed[1]["payload"] == {"n": 2}


def test_replay_session_unknown_returns_empty():
    store = _store()
    replay = ReplayEngine(store=store)

    assert replay.replay_session("no-such-session") == []
