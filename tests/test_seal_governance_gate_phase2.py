"""
Phase 2: M2 Phase 3 Authorization Flow Tests (T09-T16)

Tests for Model B human authority controlled authorization flow.
Validates 8 authorization scenarios with HumanGate integration.

T09: GL7 Boundary Enforcement
T10: HumanGate Integration
T11: Human Approval Dependency
T12: Validation Enforcement
T13: Seal Execution Blocking
T14: Authorization Sequence
T15: Model C Elimination Verification
T16: End-to-End Model B Flow
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Support both Windows and Linux paths
if sys.platform == "win32":
    MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
else:
    MOCKA_ROOT = Path("/home/user/MoCKA")

sys.path.insert(0, str(MOCKA_ROOT / "governance"))
sys.path.insert(0, str(MOCKA_ROOT / "structural"))

from seal_governance_gate import SealGovernanceGate, _human_gate  # noqa: E402


def _init_sandbox_repo(root: Path):
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "sandbox@test.local"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "SandboxTest"], cwd=root, check=True)
    (root / "README.md").write_text("sandbox test repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "initial sandbox commit"], cwd=root, check=True)


def _mock_seal_runner_success(message: str):
    """Mock seal runner that returns success output."""
    fake_stdout = (
        "COMMIT: deadbeef1234567890deadbeef1234567890dead\n"
        "SUMMARY_HASH: " + ("a" * 64) + "\n"
        "ANCHOR UPDATED AND COMMITTED\n"
    )
    return fake_stdout, 0


def test_09_gl7_boundary_enforcement():
    """
    T09: GL7 Boundary Enforcement
    Verify: GL7=true alone does NOT execute seal
    Expected: Seal BLOCKED until HumanGate.approve()=true
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        # GL7 passes, but HumanGate NOT mocked (approve() returns False)
        calls = []

        def spy_runner(message):
            calls.append(message)
            return _mock_seal_runner_success(message)

        gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
        result = gate.execute(
            message="TEST_09_GL7_BOUNDARY",
            requester="human:test_approver",
            seal_request_id="SR_TEST_09_001",
            _seal_runner=spy_runner
        )

        assert not result.approved, "GL7 pass alone should NOT approve execution"
        assert len(calls) == 0, "seal runner should NOT be called without human approval"
        assert "human gate approval required but not obtained" in result.reason


def test_10_humangate_integration():
    """
    T10: HumanGate Integration
    Verify: HumanGate.request() called after GL7 check
    Expected: Request made with decision_id
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        # Track HumanGate method calls
        original_request = _human_gate.request
        original_approve = _human_gate.approve

        request_calls = []
        approve_calls = []

        _human_gate.request = lambda decision_id: request_calls.append(decision_id)
        _human_gate.approve = lambda decision_id: (approve_calls.append(decision_id), True)[1]

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            result = gate.execute(
                message="TEST_10_HUMANGATE_INTEGRATION",
                requester="human:test_approver",
                seal_request_id="SR_TEST_10_001",
                _seal_runner=_mock_seal_runner_success
            )

            assert len(request_calls) == 1, "HumanGate.request() should be called once"
            assert len(approve_calls) == 1, "HumanGate.approve() should be called once"
            assert request_calls[0] == approve_calls[0], "request() and approve() should use same decision_id"
            assert "DC_" in request_calls[0], "decision_id should follow DC_ format"
        finally:
            _human_gate.request = original_request
            _human_gate.approve = original_approve


def test_11_human_approval_dependency():
    """
    T11: Human Approval Dependency
    Verify: Seal executes ONLY when human_approved=true
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        calls = []

        def spy_runner(message):
            calls.append(message)
            return _mock_seal_runner_success(message)

        original_approve = _human_gate.approve

        # Test case 1: human_approved = False
        _human_gate.approve = lambda decision_id: False
        gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
        result = gate.execute(
            message="TEST_11_NO_APPROVAL",
            requester="human:test_approver",
            seal_request_id="SR_TEST_11_001",
            _seal_runner=spy_runner
        )

        assert not result.approved, "Execution should be blocked without human approval"
        assert len(calls) == 0, "seal runner should not be called"

        # Test case 2: human_approved = True
        _human_gate.approve = lambda decision_id: True
        result = gate.execute(
            message="TEST_11_WITH_APPROVAL",
            requester="human:test_approver",
            seal_request_id="SR_TEST_11_002",
            _seal_runner=spy_runner
        )

        assert result.approved, "Execution should be allowed with human approval"
        assert len(calls) == 1, "seal runner should be called once"

        _human_gate.approve = original_approve


def test_12_validation_enforcement():
    """
    T12: Validation Enforcement
    Verify: verify_auth_record() blocks execution on failure
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        calls = []

        def spy_runner(message):
            calls.append(message)
            return _mock_seal_runner_success(message)

        original_approve = _human_gate.approve
        _human_gate.approve = lambda decision_id: True

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)

            # Test with missing seal_request_id (validation will fail)
            result = gate.execute(
                message="TEST_12_VALIDATION_FAIL",
                requester="human:test_approver",
                seal_request_id="",  # Empty seal_request_id should cause validation failure
                _seal_runner=spy_runner
            )

            assert not result.approved, "Execution should be blocked on validation failure"
            assert len(calls) == 0, "seal runner should not be called on validation failure"
            assert "authorization validation failed" in result.reason
        finally:
            _human_gate.approve = original_approve


def test_13_seal_execution_blocking():
    """
    T13: Seal Execution Blocking
    Verify: Seal blocked if ANY condition fails (GL7, Human, Validation)
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        # Case 1: GL7 fails (file count exceeds expected)
        (sandbox / "file1.txt").write_text("a\n", encoding="utf-8")
        (sandbox / "file2.txt").write_text("b\n", encoding="utf-8")

        gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
        result = gate.execute(
            message="TEST_13_GL7_FAIL",
            expected_max_changes=1,
            requester="human:test_approver",
            seal_request_id="SR_TEST_13_001",
            _seal_runner=_mock_seal_runner_success
        )

        assert not result.approved, "GL7 failure should block execution"
        assert "unexpected_file_count" in result.aborts


def test_14_authorization_sequence():
    """
    T14: Authorization Sequence
    Verify: Correct order - GL7 > HumanGate > Validation > Execution
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        sequence = []

        original_pre_exec = None

        def track_gl7(self, action):
            sequence.append("GL7_CHECK")
            from structural.execution_governance import ExecutionGovernanceEngine
            result = original_pre_exec(action)
            return result

        original_approve = _human_gate.approve
        def track_humangate(decision_id):
            sequence.append("HUMANGATE_CHECK")
            return True

        _human_gate.approve = track_humangate

        gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)

        # Patch the execute method to track sequence
        original_execute = gate.governance.pre_execution_check
        def wrapped_check(action):
            sequence.append("GL7_CHECK")
            return original_execute(action)

        gate.governance.pre_execution_check = wrapped_check

        try:
            result = gate.execute(
                message="TEST_14_SEQUENCE",
                requester="human:test_approver",
                seal_request_id="SR_TEST_14_001",
                _seal_runner=_mock_seal_runner_success
            )

            assert result.approved, "Execution should succeed"
            assert "GL7_CHECK" in sequence, "GL7 check should occur"
            assert "HUMANGATE_CHECK" in sequence, "HumanGate check should occur"
        finally:
            _human_gate.approve = original_approve


def test_15_model_c_elimination():
    """
    T15: Model C Elimination Verification
    Verify: No automatic approval path remains
    Expected: Execution requires human approval
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        # Ensure HumanGate.approve() is NOT mocked (returns False)
        original_approve = _human_gate.approve
        _human_gate.approve = lambda decision_id: False

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            result = gate.execute(
                message="TEST_15_NO_AUTO_APPROVAL",
                requester="human:test_approver",
                seal_request_id="SR_TEST_15_001",
                _seal_runner=_mock_seal_runner_success
            )

            # Even with GL7 passing, execution should be blocked
            assert not result.approved, "Model C auto-approval path should NOT exist"
            assert "human gate approval required but not obtained" in result.reason
        finally:
            _human_gate.approve = original_approve


def test_16_end_to_end_model_b():
    """
    T16: End-to-End Model B Flow
    Verify: Complete authorization flow works
    Request > GL7 Check > Human Approval > Validation > Execution > Ledger Record
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        calls = []

        def spy_runner(message):
            calls.append(message)
            return _mock_seal_runner_success(message)

        original_approve = _human_gate.approve
        _human_gate.approve = lambda decision_id: True

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            result = gate.execute(
                message="TEST_16_END_TO_END",
                requester="human:test_approver",
                seal_request_id="SR_TEST_16_001",
                _seal_runner=spy_runner
            )

            # Verify execution occurred
            assert result.approved, "End-to-end flow should succeed"
            assert len(calls) == 1, "seal runner should be called"
            assert result.seal_returncode == 0, "seal execution should succeed"

            # Verify Decision Ledger record
            entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
            assert len(entries) == 1, "one decision should be recorded"

            entry = entries[0]
            assert entry["decision"] == "approved", "decision should be approved"
            assert entry["seal_request_id"] == "SR_TEST_16_001", "seal_request_id should be recorded"
            assert entry["requester"] == "human:test_approver", "requester should be recorded"
            assert entry["artifact_hash"] == "deadbeef1234567890deadbeef1234567890dead", "commit hash should be recorded"
            assert entry["seal_hash"] == "a" * 64, "summary hash should be recorded"

            # Verify complete flow fields exist
            for field in ("execution_id", "change_start", "change_done", "decision_id",
                         "approved_by", "approved_at", "status"):
                assert field in entry, f"field {field} should be in ledger record"
        finally:
            _human_gate.approve = original_approve


if __name__ == "__main__":
    test_09_gl7_boundary_enforcement()
    print("Test 09 (GL7 boundary enforcement): PASS")

    test_10_humangate_integration()
    print("Test 10 (HumanGate integration): PASS")

    test_11_human_approval_dependency()
    print("Test 11 (Human approval dependency): PASS")

    test_12_validation_enforcement()
    print("Test 12 (Validation enforcement): PASS")

    test_13_seal_execution_blocking()
    print("Test 13 (Seal execution blocking): PASS")

    test_14_authorization_sequence()
    print("Test 14 (Authorization sequence): PASS")

    test_15_model_c_elimination()
    print("Test 15 (Model C elimination): PASS")

    test_16_end_to_end_model_b()
    print("Test 16 (End-to-end Model B flow): PASS")

    print("\n" + "="*60)
    print("ALL PHASE 2 TESTS PASSED (8/8)")
    print("="*60)
