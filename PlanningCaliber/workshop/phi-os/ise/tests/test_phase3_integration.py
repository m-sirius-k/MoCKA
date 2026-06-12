# test_phase3_integration.py
"""STEP 5: Phase 3統合テスト"""
import inspect

import pytest

from phios.core.orchestrator import Orchestrator
from phios.core.event_interpreter import InterpretedEvent
from phios.core.decision_synthesis import DecisionSynthesizer
from phios.core import semantic_router, decision_synthesis, event_interpreter
from phios.core import adapter_manager
from phios.adapter.mock_adapter import MockAdapter
from phios.registry.taxonomy import get_taxonomy


@pytest.fixture(autouse=True)
def _reset_registry():
    adapter_manager.reset()
    adapter_manager.register("mock", MockAdapter())
    yield
    adapter_manager.reset()


def test_full_meaning_driven_flow_v1():
    result = Orchestrator().process("STATE_DEGRADED", {"actor": "ISE"})
    assert result["event_type"] == "STATE_DEGRADED"
    assert result["meaning"]["intent"] == "recover"
    assert result["action"]["action_type"] == "delegate"
    assert result["route"]["destination"] == "mock"
    assert result["execution"]["executed"] is True


def test_critical_event_human_gate_log():
    result = Orchestrator().process("AUTHORITY_REVOKE", {"actor": "Human"})
    route = result["route"]
    assert route["requires_human"] is True
    assert route["gate_reason"] == "escalate:AUTHORITY_REVOKE"
    assert route["gate_origin_event"] == "escalate"


def test_meaning_in_registry_not_code():
    event = InterpretedEvent("SEAL", {})
    # meaningはmeaning.pyのマッピングから決定される（_classify_*はコードに存在しない）
    src = inspect.getsource(event_interpreter)
    for forbidden in ("_classify_", "def _classify"):
        assert forbidden not in src
    assert event.meaning["intent"] == "validate"


def test_decision_from_rules_not_code():
    src = inspect.getsource(decision_synthesis)
    assert "if impact ==" not in src
    assert "if intent ==" not in src

    event = InterpretedEvent("AUTHORITY_REVOKE", {})
    action = DecisionSynthesizer().synthesize(event)
    assert action.action_type == "escalate"


def test_router_executor_separation():
    src = inspect.getsource(semantic_router)
    assert "adapter.execute" not in src
    assert ".ack(" not in src
    assert "gate_check" not in src


def test_all_37_events_interpretable():
    taxonomy = get_taxonomy()
    events = taxonomy["events"]
    all_event_types = [
        event_type
        for cat_events in events.values()
        for event_type in cat_events
    ]
    assert len(all_event_types) >= 37

    for event_type in all_event_types:
        event = InterpretedEvent(event_type, {})
        assert event.meaning["intent"] is not None
        assert event.meaning["impact"] is not None
        assert event.meaning["urgency"] in (1, 2, 3)
