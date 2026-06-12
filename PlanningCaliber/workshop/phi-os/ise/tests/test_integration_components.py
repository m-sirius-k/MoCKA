# test_integration_components.py
"""
[Phase 4] 個別コンポーネント単位の統合試験

Phase 3で追加した phi_os_core / adapter / verification の
動作を、ISEの既存モジュールと組み合わせて検証する。
"""
import pytest

from .. import decision_ledger, fluid_connector
from ..state_machine import ISEState

from phi_os_core import PHIOSCore
from adapter.openai_adapter import OpenAIAdapter
from adapter.anthropic_adapter import AnthropicAdapter
from verification.verify_api import verify


@pytest.fixture
def isolated_ledger(tmp_path, monkeypatch):
    ledger_path = tmp_path / "decision_ledger.jsonl"
    monkeypatch.setattr(decision_ledger, "LEDGER_PATH", ledger_path)
    return ledger_path


@pytest.fixture
def isolated_trajectory(tmp_path, monkeypatch):
    trajectory_path = tmp_path / "trajectory.csv"
    monkeypatch.setattr(fluid_connector, "TRAJECTORY_PATH", trajectory_path)
    return trajectory_path


# --- PHIOSCore ---------------------------------------------------------

def test_phi_os_core_initial_state(isolated_ledger, isolated_trajectory):
    core = PHIOSCore()
    assert core.state == ISEState.INITIALIZING


def test_phi_os_core_start_transitions_to_active(isolated_ledger, isolated_trajectory):
    core = PHIOSCore()
    new_state = core.start(actor="Claude", event_id="E_CORE_001")
    assert new_state == ISEState.ACTIVE
    assert core.state == ISEState.ACTIVE


def test_phi_os_core_start_records_decision(isolated_ledger, isolated_trajectory):
    core = PHIOSCore()
    core.start(actor="Claude", event_id="E_CORE_002")
    entries = decision_ledger.read_ledger()
    assert len(entries) == 1
    assert entries[0]["type"] == "state_transition"
    assert entries[0]["before"] == "initializing"
    assert entries[0]["after"] == "active"


def test_phi_os_core_start_records_trajectory(isolated_ledger, isolated_trajectory):
    core = PHIOSCore()
    core.start(actor="Claude", event_id="E_CORE_003")
    with open(isolated_trajectory, encoding="utf-8") as f:
        rows = f.readlines()
    assert len(rows) == 1
    assert "E_CORE_003" in rows[0]


def test_phi_os_core_degrade_after_start(isolated_ledger, isolated_trajectory):
    core = PHIOSCore()
    core.start(actor="Claude", event_id="E_CORE_004")
    new_state = core.degrade(actor="ISE", event_id="E_CORE_005", reason="timeout")
    assert new_state == ISEState.DEGRADED


def test_phi_os_core_recover_after_degrade(isolated_ledger, isolated_trajectory):
    core = PHIOSCore()
    core.start(actor="Claude", event_id="E_CORE_006")
    core.degrade(actor="ISE", event_id="E_CORE_007", reason="timeout")
    new_state = core.recover(actor="Human", event_id="E_CORE_008")
    assert new_state == ISEState.ACTIVE


def test_phi_os_core_invalid_transition_raises(isolated_ledger, isolated_trajectory):
    core = PHIOSCore()
    # INITIALIZING -> DEGRADED は許可されていない
    with pytest.raises(ValueError):
        core.degrade(actor="ISE", event_id="E_CORE_009", reason="invalid")


def test_phi_os_core_full_decision_chain_verifies(isolated_ledger, isolated_trajectory):
    core = PHIOSCore()
    core.start(actor="Claude", event_id="E_CORE_010")
    core.degrade(actor="ISE", event_id="E_CORE_011", reason="timeout")
    core.recover(actor="Human", event_id="E_CORE_012")
    ok, msg = decision_ledger.verify_chain()
    assert ok is True
    assert "3 entries OK" in msg


# --- OpenAI Adapter -----------------------------------------------------

def test_openai_adapter_handshake():
    adapter = OpenAIAdapter()
    result = adapter.handshake(scope="institution_state")
    assert result["status"] == "ok"
    assert result["session_id"].startswith("session_GPT_")
    assert "CAP_STATE_READ" in result["capabilities"]


def test_openai_adapter_receive_commission_valid():
    adapter = OpenAIAdapter()
    assert adapter.receive_commission({"commission_id": "C001"}) is True


def test_openai_adapter_receive_commission_invalid():
    adapter = OpenAIAdapter()
    assert adapter.receive_commission({}) is False


def test_openai_adapter_execute_and_ack():
    adapter = OpenAIAdapter()
    commission = {"commission_id": "C002", "task": "summarize state"}
    result = adapter.execute(commission)
    assert result["commission_id"] == "C002"
    assert "[GPT]" in result["output"]

    ack = adapter.ack(result)
    assert ack["ai_id"] == "GPT"
    assert ack["status"] == "ok"
    assert ack["commission_id"] == "C002"


# --- Anthropic Adapter ---------------------------------------------------

def test_anthropic_adapter_handshake():
    adapter = AnthropicAdapter()
    result = adapter.handshake(scope="institution_state")
    assert result["status"] == "ok"
    assert result["session_id"].startswith("session_Claude_")
    assert "CAP_STATE_WRITE" in result["capabilities"]


def test_anthropic_adapter_execute_and_ack():
    adapter = AnthropicAdapter()
    commission = {"commission_id": "C003", "task": "update state"}
    result = adapter.execute(commission)
    assert result["commission_id"] == "C003"
    assert "[Claude]" in result["output"]

    ack = adapter.ack(result)
    assert ack["ai_id"] == "Claude"
    assert ack["status"] == "ok"


# --- Verification ---------------------------------------------------------

def test_verify_empty_ledger(isolated_ledger):
    result = verify()
    assert result["verified"] is True
    assert result["entry_count"] == 0


def test_verify_after_decisions(isolated_ledger):
    decision_ledger.append_decision(
        decision_type="state_transition",
        actor="Claude",
        before="initializing",
        after="active",
        reason="test",
    )
    result = verify()
    assert result["verified"] is True
    assert result["entry_count"] == 1


def test_verify_detects_tamper(isolated_ledger):
    decision_ledger.append_decision(
        decision_type="state_transition",
        actor="Claude",
        before="initializing",
        after="active",
        reason="test",
    )
    # チェーンを直接改ざんする
    with open(isolated_ledger, "a", encoding="utf-8") as f:
        f.write('{"ts": "x", "type": "incident", "actor": "x", "before": "a", '
                '"after": "b", "reason": "tamper", "prev_hash": "", "hash": "deadbeef"}\n')
    result = verify()
    assert result["verified"] is False
    assert result["entry_count"] == 2


# --- Fluid Connector across all defined transitions -----------------------

@pytest.mark.parametrize("before,after", [
    ("initializing", "active"),
    ("active", "degraded"),
    ("degraded", "active"),
    ("active", "suspended"),
    ("suspended", "active"),
    ("active", "sealed"),
])
def test_fluid_connector_all_known_transitions(before, after, isolated_trajectory):
    delta = fluid_connector.compute_delta(before, after)
    assert set(delta.keys()) == {"dx", "dy", "dz"}
    ok = fluid_connector.notify_trajectory(before, after, event_id=f"E_{before}_{after}")
    assert ok is True
