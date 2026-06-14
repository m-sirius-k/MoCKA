"""
phios_integration.tests.test_memory_integration

Phase 10: Memory実装フェーズ(最小永続化層 + PHI-OS読み取り統合)に関するテスト。
"""

from core_kernel.event_contracts import build_event
from core_kernel.memory_core import MemoryStore
from core_kernel.phios_integration import JsonMemoryAdapter, PrismBridge


def _make_event(event_type="change_start", source_module="test_module", **kwargs):
    return build_event(
        event_type=event_type,
        source_module=source_module,
        payload={"detail": "test"},
        **kwargs,
    )


# ----------------------------------------------------------------------
# JsonMemoryAdapter
# ----------------------------------------------------------------------

def test_json_memory_adapter_in_memory_write_and_load():
    adapter = JsonMemoryAdapter()
    bridge = PrismBridge()
    bridge.initialize_prism()
    analysis = bridge.analyze_event(_make_event())["result"]

    record = adapter.write_analysis(analysis)

    assert record["type"] == "analysis_result"
    assert record["version"] == "1.0"
    assert "context" in record["payload"]
    assert "observation" in record["payload"]
    assert "cognitive_state" in record["payload"]
    assert "annotations" in record["payload"]

    loaded = adapter.load(record["id"])
    assert loaded == record


def test_json_memory_adapter_write_context_and_observation():
    adapter = JsonMemoryAdapter()
    bridge = PrismBridge()
    bridge.initialize_prism()
    analysis = bridge.analyze_event(_make_event())["result"]

    context_record = adapter.write_context(analysis.context)
    observation_record = adapter.write_observation(analysis.observation)

    assert context_record["type"] == "context"
    assert context_record["payload"]["context_id"] == analysis.context.context_id

    assert observation_record["type"] == "observation"
    assert observation_record["payload"]["observation_id"] == analysis.observation.observation_id


def test_json_memory_adapter_persists_to_file(tmp_path):
    path = tmp_path / "memory.json"
    adapter = JsonMemoryAdapter(path=path)

    bridge = PrismBridge()
    bridge.initialize_prism()
    analysis = bridge.analyze_event(_make_event())["result"]

    record = adapter.write_analysis(analysis)

    assert path.exists()

    adapter2 = JsonMemoryAdapter(path=path)
    assert adapter2.load(record["id"]) == record


def test_json_memory_adapter_can_be_constructed_with_existing_store():
    store = MemoryStore()
    adapter = JsonMemoryAdapter(store=store)

    bridge = PrismBridge()
    bridge.initialize_prism()
    analysis = bridge.analyze_event(_make_event())["result"]

    record = adapter.write_analysis(analysis)
    assert store.load(record["id"]) == record


# ----------------------------------------------------------------------
# PHI-OS統合(PrismBridge経由のMemory読み書き)
# ----------------------------------------------------------------------

def test_bridge_save_analysis_without_memory_adapter_returns_error():
    bridge = PrismBridge()
    bridge.initialize_prism()
    bridge_result = bridge.analyze_event(_make_event())

    result = bridge.save_analysis(bridge_result)

    assert result["status"] == "error"
    assert result["error_type"] == "memory_not_configured"


def test_bridge_save_and_load_analysis_via_adapter():
    adapter = JsonMemoryAdapter()
    bridge = PrismBridge(memory_adapter=adapter)
    bridge.initialize_prism()

    bridge_result = bridge.analyze_event(_make_event())
    save_result = bridge.save_analysis(bridge_result, session_id="session-1")

    assert save_result["status"] == "ok"
    record = save_result["record"]
    assert record["session_id"] == "session-1"

    loaded = bridge.load_memory(record["id"])
    assert loaded == record


def test_bridge_save_analysis_with_error_result_does_not_save():
    adapter = JsonMemoryAdapter()
    bridge = PrismBridge(memory_adapter=adapter)
    bridge.initialize_prism()

    invalid_event = {"event_type": "change_start"}
    bridge_result = bridge.analyze_event(invalid_event)

    result = bridge.save_analysis(bridge_result)

    assert result["status"] == "error"
    assert result["error_type"] == "no_result"
    assert adapter.query() == []


def test_bridge_query_memory_via_adapter():
    adapter = JsonMemoryAdapter()
    bridge = PrismBridge(memory_adapter=adapter)
    bridge.initialize_prism()

    bridge.save_analysis(bridge.analyze_event(_make_event()), session_id="session-a")
    bridge.save_analysis(
        bridge.analyze_event(_make_event(event_type="change_done")), session_id="session-b",
    )

    session_a = bridge.query_memory(lambda r: r.get("session_id") == "session-a")

    assert len(session_a) == 1
    assert session_a[0]["session_id"] == "session-a"


def test_bridge_query_memory_without_adapter_returns_empty_list():
    bridge = PrismBridge()
    assert bridge.query_memory() == []


def test_bridge_load_memory_without_adapter_returns_none():
    bridge = PrismBridge()
    assert bridge.load_memory("anything") is None


# ----------------------------------------------------------------------
# Prism/Orchestra非破壊確認
# ----------------------------------------------------------------------

def test_memory_integration_does_not_affect_prism_analysis():
    adapter = JsonMemoryAdapter()
    bridge = PrismBridge(memory_adapter=adapter)
    bridge.initialize_prism()

    result_with_memory = bridge.analyze_event(_make_event())["result"]

    bridge_without = PrismBridge()
    bridge_without.initialize_prism()
    result_without_memory = bridge_without.analyze_event(_make_event())["result"]

    assert result_with_memory.cognitive_state.state == result_without_memory.cognitive_state.state
