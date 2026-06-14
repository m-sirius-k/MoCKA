"""
phios_integration.tests.test_relay_integration

Phase 11: Relay(時間・セッション継続層)のPHI-OS接続(経路追加のみ)に関するテスト。
"""

from core_kernel.event_contracts import build_event
from core_kernel.phios_integration import JsonMemoryAdapter, PrismBridge
from core_kernel.relay_core import SessionRelay


def _make_event(event_type="change_start", source_module="test_module", **kwargs):
    return build_event(
        event_type=event_type,
        source_module=source_module,
        payload={"detail": "test"},
        **kwargs,
    )


def test_bridge_relay_methods_without_relay_return_none():
    bridge = PrismBridge()

    assert bridge.relay_create_session("session-1") is None
    assert bridge.relay_get_session("session-1") is None

    bridge.initialize_prism()
    context = bridge.analyze_event(_make_event())["result"].context
    assert bridge.relay_append_context("session-1", context) is None


def test_bridge_relay_create_and_get_session():
    relay = SessionRelay()
    bridge = PrismBridge(relay=relay)

    created = bridge.relay_create_session("session-1")
    fetched = bridge.relay_get_session("session-1")

    assert created["session_id"] == "session-1"
    assert fetched == created


def test_bridge_relay_append_context_from_analysis():
    relay = SessionRelay()
    bridge = PrismBridge(relay=relay)
    bridge.initialize_prism()

    analysis = bridge.analyze_event(_make_event())["result"]
    session = bridge.relay_append_context("session-1", analysis.context)

    assert len(session["context_chain"]) == 1
    assert session["context_chain"][0]["context_id"] == analysis.context.context_id


def test_relay_and_memory_are_independent():
    """RelayとMemoryは互いに干渉しない(別々に設定・利用できる)。"""
    relay = SessionRelay()
    memory = JsonMemoryAdapter()
    bridge = PrismBridge(memory_adapter=memory, relay=relay)
    bridge.initialize_prism()

    bridge_result = bridge.analyze_event(_make_event())
    analysis = bridge_result["result"]

    save_result = bridge.save_analysis(bridge_result, session_id="session-1")
    relay_session = bridge.relay_append_context("session-1", analysis.context)

    # Memoryに保存されたレコードはRelayのセッションに含まれず、
    # RelayのセッションもMemoryには保存されない
    assert memory.query(lambda r: r["type"] == "context") == []
    assert relay_session["context_chain"][0]["context_id"] == analysis.context.context_id
    assert save_result["record"]["type"] == "analysis_result"


def test_relay_session_not_persisted_anywhere(tmp_path):
    """Relayのセッションは、Memoryのpersistence fileに一切現れない。"""
    path = tmp_path / "memory.json"
    memory = JsonMemoryAdapter(path=path)
    relay = SessionRelay()
    bridge = PrismBridge(memory_adapter=memory, relay=relay)
    bridge.initialize_prism()

    analysis = bridge.analyze_event(_make_event())["result"]
    bridge.relay_append_context("session-1", analysis.context)

    if path.exists():
        content = path.read_text(encoding="utf-8")
        assert "context_chain" not in content
