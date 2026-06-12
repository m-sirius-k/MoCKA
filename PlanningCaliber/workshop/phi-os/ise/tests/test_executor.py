# test_executor.py
"""STEP 3b: Executor 検証"""
import pytest

from phios.core.decision_synthesis import Action
from phios.core.executor import Executor
from phios.core import adapter_manager
from phios.adapter.mock_adapter import MockAdapter


@pytest.fixture(autouse=True)
def _reset_registry():
    adapter_manager.reset()
    adapter_manager.register("mock", MockAdapter())
    yield
    adapter_manager.reset()


def test_executor_noop_not_executed():
    action = Action("noop", "ledger", 1, "noop:STATE_INIT")
    route_result = {"destination": "ledger", "routable": False}
    result = Executor().execute(route_result, action)
    assert result["executed"] is False


def test_executor_verify_all_executed():
    action = Action("seal", "verify_all", 1, "seal:SEAL")
    route_result = {"destination": "verify_all", "routable": True}
    result = Executor().execute(route_result, action)
    assert result["executed"] is True
    assert result["destination"] == "verify_all"
    assert "ok" in result


def test_executor_adapter_executed():
    action = Action("delegate", "mock", 2, "delegate:STATE_DEGRADED")
    route_result = {"destination": "mock", "routable": True}
    result = Executor().execute(route_result, action)
    assert result["executed"] is True
    assert result["destination"] == "mock"
    assert "ack" in result


def test_executor_fallback_to_mock():
    action = Action("delegate", "unknown_ai", 2, "delegate:STATE_DEGRADED")
    route_result = {"destination": "mock_fallback", "routable": True}
    result = Executor().execute(route_result, action)
    assert result["executed"] is True
    assert result["destination"] == "mock"


def test_executor_error_handled():
    adapter_manager.reset()
    action = Action("delegate", "missing", 2, "delegate:STATE_DEGRADED")
    route_result = {"destination": "missing", "routable": True}
    result = Executor().execute(route_result, action)
    assert result["executed"] is False
    assert "error" in result
