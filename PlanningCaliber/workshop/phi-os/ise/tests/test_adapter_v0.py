# test_adapter_v0.py
"""STEP 3: MockAdapter / OpenAIAdapter v0 / AdapterManager 検証"""
import pytest

from phios.adapter.mock_adapter import MockAdapter
from phios.adapter.openai_adapter import OpenAIAdapter
from phios.core import adapter_manager


@pytest.fixture(autouse=True)
def _reset_registry():
    adapter_manager.reset()
    yield
    adapter_manager.reset()


def test_mock_adapter_handshake():
    adapter = MockAdapter()
    result = adapter.handshake()
    assert result["status"] == "ok"
    assert result["ai_id"] == "mock"


def test_mock_adapter_execute():
    adapter = MockAdapter()
    result = adapter.execute({"commission_id": "C1", "task": "ping"})
    assert "result" in result
    assert "ping" in result["result"]


def test_mock_adapter_ack():
    adapter = MockAdapter()
    ack = adapter.ack({"result": "ok"})
    assert ack["ok"] is True
    assert ack["actor"] == "mock"


def test_openai_adapter_handshake():
    adapter = OpenAIAdapter()
    result = adapter.handshake()
    assert "taxonomy_validation" in result["capabilities"]


def test_adapter_manager_register():
    adapter_manager.register("mock", MockAdapter())
    assert "mock" in adapter_manager.list_adapters()
    assert isinstance(adapter_manager.get("mock"), MockAdapter)


def test_adapter_manager_get_unknown_raises():
    with pytest.raises(KeyError):
        adapter_manager.get("does_not_exist")


def test_openai_is_baseline_adapter():
    adapter = OpenAIAdapter(api_key=None)
    assert adapter.receive_commission({"task": "summarize"}) is True
    assert adapter.receive_commission({}) is False
    ack = adapter.ack(adapter.execute({"task": "summarize"}))
    assert ack["ok"] is True
    assert ack["actor"] == "openai"
