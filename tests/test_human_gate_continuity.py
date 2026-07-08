"""
Phase C-4: governance/human_gate_continuity.py のテスト(縮小版・DHGP)。

pending_ledger_pathは常に一時sandboxディレクトリへ差し替え、本番の
data/decisions/pending_decision_units.jsonlには一切書き込まない。

Test A: MCP offline -> defer()の結果、governance_stateが
        WAITING_FOR_HUMAN_GATEになる
Test B: MCP復旧シミュレーション -> record_mcp_recovery_observed()は
        mcp_availabilityをONLINEとして観測記録するが、governance_stateは
        WAITING_FOR_HUMAN_GATEのまま進まない(APPROVAL_REQUIRED/
        READY_TO_COMMIT等への自動遷移が発生しないことを確認)
Test C: 不正override -> attempt_state_transition()は常に拒否され、
        台帳にAPPROVED/READY_TO_COMMIT等の状態が書き込まれない
Test D: 非侵襲性確認 -> 本番のdata/decisions/pending_decision_units.jsonl・
        decision_ledger.jsonl・app.pyが無変更
"""
import hashlib
import json
import sys
import tempfile
from pathlib import Path

MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
sys.path.insert(0, str(MOCKA_ROOT / "governance"))

from human_gate_continuity import (  # noqa: E402
    HumanGateContinuity,
    HumanGateContinuityError,
)

FILES_TO_PROTECT = [
    MOCKA_ROOT / "app.py",
    MOCKA_ROOT / "data" / "decisions" / "decision_ledger.jsonl",
    MOCKA_ROOT / "data" / "decisions" / "pending_decision_units.jsonl",
]


def _sha256_of_file(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def _mock_mcp_offline():
    return "OFFLINE"


def _mock_mcp_online():
    return "ONLINE"


def test_a_mcp_offline_produces_waiting_state():
    with tempfile.TemporaryDirectory() as tmp:
        ledger_path = Path(tmp) / "pending_decision_units.jsonl"
        dhgp = HumanGateContinuity(pending_ledger_path=ledger_path)

        unit = dhgp.defer(
            change_scope=["app.py"],
            wait_reason="MCP offline during Phase C-4 test",
            mcp_check=_mock_mcp_offline,
        )

        assert unit.governance_state == "WAITING_FOR_HUMAN_GATE"
        assert unit.approval_required is True
        assert unit.human_gate_event_status == "NOT_ISSUED"
        assert unit.mcp_availability == "OFFLINE"

        entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
        assert len(entries) == 1
        entry = entries[0]
        for f in ("governance_state", "approval_required", "human_gate_event_status", "mcp_availability"):
            assert f in entry
        assert entry["governance_state"] == "WAITING_FOR_HUMAN_GATE"


def test_b_mcp_recovery_observed_does_not_advance_state():
    with tempfile.TemporaryDirectory() as tmp:
        ledger_path = Path(tmp) / "pending_decision_units.jsonl"
        dhgp = HumanGateContinuity(pending_ledger_path=ledger_path)

        unit = dhgp.defer(
            change_scope=["app.py"],
            wait_reason="MCP offline during Phase C-4 test",
            mcp_check=_mock_mcp_offline,
        )

        event = dhgp.record_mcp_recovery_observed(unit.request_id, mcp_check=_mock_mcp_online)
        assert event["mcp_availability"] == "ONLINE"
        assert event["governance_state"] == "WAITING_FOR_HUMAN_GATE"

        state = dhgp.get_state(unit.request_id)
        assert state["governance_state"] == "WAITING_FOR_HUMAN_GATE", (
            "MCP recovery must be observed without auto-advancing governance_state; "
            "reconnect/resume belongs to TODO_429, not this module"
        )
        assert state["mcp_availability"] == "ONLINE"

        for forbidden in ("APPROVAL_REQUIRED", "READY_TO_COMMIT", "APPROVED"):
            assert forbidden not in json.dumps(state), (
                f"no record should ever contain governance_state={forbidden}; "
                "this module has no code path that produces it"
            )


def test_c_illegal_override_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        ledger_path = Path(tmp) / "pending_decision_units.jsonl"
        dhgp = HumanGateContinuity(pending_ledger_path=ledger_path)

        unit = dhgp.defer(
            change_scope=["app.py"],
            wait_reason="MCP offline during Phase C-4 test",
            mcp_check=_mock_mcp_offline,
        )

        for target in ("APPROVED", "READY_TO_COMMIT", "APPROVAL_REQUIRED"):
            try:
                dhgp.attempt_state_transition(unit.request_id, target)
                raise AssertionError(f"expected HumanGateContinuityError for target={target}")
            except HumanGateContinuityError:
                pass

        state = dhgp.get_state(unit.request_id)
        assert state["governance_state"] == "WAITING_FOR_HUMAN_GATE"

        entries_raw = ledger_path.read_text(encoding="utf-8").splitlines()
        assert len(entries_raw) == 1, "rejected override attempts must not be appended to the ledger"


def test_d_real_repo_untouched():
    before = {p: _sha256_of_file(p) for p in FILES_TO_PROTECT}

    with tempfile.TemporaryDirectory() as tmp:
        ledger_path = Path(tmp) / "pending_decision_units.jsonl"
        dhgp = HumanGateContinuity(pending_ledger_path=ledger_path)
        unit = dhgp.defer(change_scope=["app.py"], wait_reason="non-invasiveness check",
                           mcp_check=_mock_mcp_offline)
        dhgp.record_mcp_recovery_observed(unit.request_id, mcp_check=_mock_mcp_online)
        try:
            dhgp.attempt_state_transition(unit.request_id, "APPROVED")
        except HumanGateContinuityError:
            pass

    after = {p: _sha256_of_file(p) for p in FILES_TO_PROTECT}
    for p in FILES_TO_PROTECT:
        assert before[p] == after[p], f"real file was modified: {p}"


if __name__ == "__main__":
    test_a_mcp_offline_produces_waiting_state()
    print("Test A (MCP offline -> WAITING_FOR_HUMAN_GATE): PASS")
    test_b_mcp_recovery_observed_does_not_advance_state()
    print("Test B (MCP recovery observed, no auto-advance): PASS")
    test_c_illegal_override_rejected()
    print("Test C (illegal override rejected): PASS")
    test_d_real_repo_untouched()
    print("Test D (real repo files untouched): PASS")
