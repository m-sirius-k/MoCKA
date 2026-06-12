# test_execution_gate.py
"""STEP 5: ExecutionGate 検証"""
import pytest

from phios.core import execution_gate
from phios.core.execution_gate import gate_check, require_gate


def test_gate_passes_when_verify_all_ok():
    assert gate_check() is True


def test_gate_blocks_when_verify_all_fails(monkeypatch):
    class _FakeResult:
        returncode = 1
        stdout = "[verify_all] FAIL at something"

    monkeypatch.setattr(execution_gate.subprocess, "run", lambda *a, **k: _FakeResult())
    assert gate_check() is False


def test_require_gate_decorator():
    @require_gate
    def protected():
        return "ok"

    assert protected() == "ok"


def test_critical_ops_require_gate(monkeypatch):
    class _FakeResult:
        returncode = 1
        stdout = "FAIL"

    monkeypatch.setattr(execution_gate.subprocess, "run", lambda *a, **k: _FakeResult())

    @require_gate
    def critical_op():
        return "should not run"

    with pytest.raises(RuntimeError):
        critical_op()
