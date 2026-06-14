"""
orchestra.tests.test_orchestra_engine

最小オーケストレーション(セッション管理/イベント処理/ノード実行/外部IF)の動作テスト。
"""

import time

from core_kernel.orchestra import Event, OrchestraEngine
from core_kernel.orchestra.orchestra_engine import OrchestraEngine as _Engine


def _event(event_type="USER_MESSAGE", session_id="session-001", payload=None):
    return Event(
        event_id=str(time.time()),
        event_type=event_type,
        session_id=session_id,
        timestamp=time.time(),
        payload=payload or {},
    )


def test_get_session_creates_and_reuses_session():
    engine = OrchestraEngine()

    session1 = engine.get_session("session-001")
    session2 = engine.get_session("session-001")

    assert session1 is session2
    assert session1.session_id == "session-001"


def test_on_event_updates_session_history():
    engine = OrchestraEngine()
    event = _event()

    engine.on_event(event)

    session = engine.get_session("session-001")
    assert session.history == [event]


def test_on_event_publishes_to_subscribed_handlers():
    engine = OrchestraEngine()
    received = []
    engine.bus.subscribe("USER_MESSAGE", received.append)

    event = _event()
    results = engine.on_event(event)

    assert received == [event]
    assert results == [None]


def test_on_event_routes_to_target_node():
    engine = OrchestraEngine()

    def test_node(ctx):
        return {
            "message": "Orchestra is running",
            "session": ctx["session"].session_id,
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


def test_on_event_unknown_node_raises():
    engine = OrchestraEngine()
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
    orchestrator_api.engine = _Engine()
    try:
        def test_node(ctx):
            return {
                "message": "Orchestra is running",
                "session": ctx["session"].session_id,
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
