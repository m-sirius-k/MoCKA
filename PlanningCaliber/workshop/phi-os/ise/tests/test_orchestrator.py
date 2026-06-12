# test_orchestrator.py
"""STEP 4: Orchestrator 検証"""
import pytest

from phios.core.orchestrator import Orchestrator
from phios.core import adapter_manager
from phios.adapter.mock_adapter import MockAdapter


@pytest.fixture(autouse=True)
def _reset_registry():
    adapter_manager.reset()
    adapter_manager.register("mock", MockAdapter())
    yield
    adapter_manager.reset()


def test_orchestrator_noop_event():
    result = Orchestrator().process("STATE_INIT")
    assert result["action"]["action_type"] == "noop"
    assert result["execution"]["executed"] is False


def test_orchestrator_critical_event_goes_to_human_gate():
    result = Orchestrator().process("AUTHORITY_REVOKE")
    assert result["action"]["action_type"] == "escalate"
    assert result["route"]["destination"] == "human_gate"
    assert result["execution"]["executed"] is False


def test_orchestrator_recover_event_delegates():
    result = Orchestrator().process("STATE_DEGRADED")
    assert result["action"]["action_type"] == "delegate"
    assert result["execution"]["destination"] == "mock"
    assert result["execution"]["executed"] is True


def test_orchestrator_seal_triggers_verify_all():
    result = Orchestrator().process("SEAL")
    assert result["action"]["action_type"] == "seal"
    assert result["execution"]["destination"] == "verify_all"


def test_orchestrator_result_shape():
    result = Orchestrator().process("STATE_INIT")
    assert set(result.keys()) == {"event_type", "meaning", "action", "route", "execution"}
