# test_semantic_router_v1.py
"""STEP 3: SemanticRouter v1.1 検証（routing専念）"""
import pytest

from phios.core.decision_synthesis import Action
from phios.core.semantic_router import SemanticRouter
from phios.core import adapter_manager
from phios.adapter.mock_adapter import MockAdapter


@pytest.fixture(autouse=True)
def _reset_registry():
    adapter_manager.reset()
    yield
    adapter_manager.reset()


def test_noop_not_routable():
    action = Action("noop", "ledger", 1, "noop:STATE_INIT")
    result = SemanticRouter().route(action)
    assert result["routable"] is False
    assert result["destination"] == "ledger"


def test_human_gate_not_routable():
    action = Action("escalate", "human_gate", 3, "escalate:AUTHORITY_REVOKE")
    result = SemanticRouter().route(action)
    assert result["routable"] is False
    assert result["destination"] == "human_gate"


def test_human_gate_has_gate_reason():
    action = Action("escalate", "human_gate", 3, "escalate:AUTHORITY_REVOKE")
    result = SemanticRouter().route(action)
    assert result["gate_reason"] == "escalate:AUTHORITY_REVOKE"


def test_human_gate_has_gate_origin_event():
    action = Action("escalate", "human_gate", 3, "escalate:AUTHORITY_REVOKE")
    result = SemanticRouter().route(action)
    assert result["gate_origin_event"] == "escalate"


def test_known_adapter_routable():
    adapter_manager.register("mock", MockAdapter())
    action = Action("delegate", "mock", 2, "delegate:STATE_DEGRADED")
    result = SemanticRouter().route(action)
    assert result["routable"] is True
    assert result["destination"] == "mock"


def test_unknown_adapter_fallback_destination():
    action = Action("delegate", "unknown_ai", 2, "delegate:STATE_DEGRADED")
    result = SemanticRouter().route(action)
    assert result["routable"] is True
    assert result["destination"] == "mock_fallback"


def test_router_does_not_execute():
    action = Action("seal", "verify_all", 1, "seal:SEAL")
    result = SemanticRouter().route(action)
    assert "ok" not in result
    assert "result" not in result
