"""
phios_integration.tests.test_adapters

Memory/Relay/Orchestra のno-op Adapterに関するテスト。

すべて副作用ゼロ・実行されないことを確認する。
"""

from core_kernel.event_contracts import build_event
from core_kernel.phios_integration import (
    NoOpMemoryAdapter,
    NoOpOrchestraAdapter,
    NoOpRelayAdapter,
    PrismBridge,
)


def _analysis_result():
    bridge = PrismBridge()
    bridge.initialize_prism()
    event = build_event(
        event_type="change_start",
        source_module="test_module",
        payload={"detail": "test"},
    )
    return bridge.analyze_event(event)["result"]


# ----------------------------------------------------------------------
# Memory
# ----------------------------------------------------------------------

def test_memory_adapter_write_analysis_returns_none():
    adapter = NoOpMemoryAdapter()
    analysis = _analysis_result()

    assert adapter.write_analysis(analysis) is None


def test_memory_adapter_write_context_and_observation_no_side_effects():
    adapter = NoOpMemoryAdapter()
    analysis = _analysis_result()

    assert adapter.write_context(analysis.context) is None
    assert adapter.write_observation(analysis.observation) is None


def test_memory_adapter_has_no_persistent_state():
    adapter = NoOpMemoryAdapter()
    analysis = _analysis_result()

    adapter.write_analysis(analysis)
    adapter.write_context(analysis.context)
    adapter.write_observation(analysis.observation)

    # no-op実装は属性を一切保持しない(副作用ゼロ)
    assert vars(adapter) == {}


# ----------------------------------------------------------------------
# Relay
# ----------------------------------------------------------------------

def test_relay_adapter_push_context_returns_none():
    adapter = NoOpRelayAdapter()
    analysis = _analysis_result()

    assert adapter.push_context(analysis.context) is None


def test_relay_adapter_pull_context_returns_none():
    adapter = NoOpRelayAdapter()

    assert adapter.pull_context("session-1") is None


def test_relay_adapter_merge_context_returns_dummy_result():
    adapter = NoOpRelayAdapter()
    analysis = _analysis_result()

    merged = adapter.merge_context(analysis.context, analysis.context)

    assert merged["merged"] is False
    assert merged["context_a"] is analysis.context
    assert merged["context_b"] is analysis.context


# ----------------------------------------------------------------------
# Orchestra
# ----------------------------------------------------------------------

def test_orchestra_adapter_plan_is_not_implemented():
    adapter = NoOpOrchestraAdapter()
    analysis = _analysis_result()

    result = adapter.plan(analysis.observation)

    assert result == {"status": "not_implemented", "plan": None}


def test_orchestra_adapter_suggest_actions_is_not_implemented():
    adapter = NoOpOrchestraAdapter()
    analysis = _analysis_result()

    result = adapter.suggest_actions(analysis.context)

    assert result == {"status": "not_implemented", "actions": []}


def test_orchestra_adapter_evaluate_state_is_not_implemented():
    adapter = NoOpOrchestraAdapter()
    analysis = _analysis_result()

    result = adapter.evaluate_state(analysis.cognitive_state)

    assert result == {"status": "not_implemented", "evaluation": None}


def test_orchestra_adapter_does_not_execute_anything():
    """plan/suggest_actions/evaluate_stateのいずれも実行制御を持たないことを確認する。"""
    adapter = NoOpOrchestraAdapter()
    analysis = _analysis_result()

    for result in (
        adapter.plan(analysis.observation),
        adapter.suggest_actions(analysis.context),
        adapter.evaluate_state(analysis.cognitive_state),
    ):
        assert result["status"] == "not_implemented"
