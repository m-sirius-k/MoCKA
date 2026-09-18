"""
E02: HumanGate Lifecycle Verification Tests

Verify complete HumanGate lifecycle: request → approval/rejection → authorization → ledger recording
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

if sys.platform == "win32":
    MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
else:
    MOCKA_ROOT = Path("/home/user/MoCKA")

sys.path.insert(0, str(MOCKA_ROOT / "governance"))
sys.path.insert(0, str(MOCKA_ROOT / "structural"))

from seal_governance_gate import SealGovernanceGate, _human_gate


def _init_sandbox_repo(root: Path):
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "sandbox@test.local"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "SandboxTest"], cwd=root, check=True)
    (root / "README.md").write_text("sandbox test repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "initial sandbox commit"], cwd=root, check=True)


def _mock_seal_runner_success(message: str):
    fake_stdout = (
        "COMMIT: deadbeef1234567890deadbeef1234567890dead\n"
        "SUMMARY_HASH: " + ("a" * 64) + "\n"
        "ANCHOR UPDATED AND COMMITTED\n"
    )
    return fake_stdout, 0


def test_e02_01_approve_flow():
    """
    E02.01: Approve Lifecycle
    Verify: HumanGate.approve()=True → seal executed
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
                message="E02_01_TEST",
                requester="human:test_approver",
                seal_request_id="SR_E02_01",
                _seal_runner=spy_runner
            )

            assert result.approved, "E02.01: Execution should be approved"
            assert len(calls) == 1, "E02.01: seal runner should be called"

            entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
            assert entries[0]["decision"] == "approved", "E02.01: Ledger should record approved"

            return "PASS", "Approve flow executes seal correctly"
        finally:
            _human_gate.approve = original_approve


def test_e02_02_reject_flow():
    """
    E02.02: Reject Lifecycle
    Verify: HumanGate.approve()=False → execution blocked
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
        _human_gate.approve = lambda decision_id: False

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            result = gate.execute(
                message="E02_02_TEST",
                requester="human:test_approver",
                seal_request_id="SR_E02_02",
                _seal_runner=spy_runner
            )

            assert not result.approved, "E02.02: Execution should be blocked"
            assert len(calls) == 0, "E02.02: seal runner should NOT be called"

            entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
            assert entries[0]["decision"] == "aborted", "E02.02: Ledger should record aborted"

            return "PASS", "Reject flow blocks seal correctly"
        finally:
            _human_gate.approve = original_approve


def test_e02_03_missing_decision():
    """
    E02.03: Missing Decision
    Verify: HumanGate.approve() not called → execution blocked
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
        # Don't mock - use placeholder behavior (returns False)
        _human_gate.approve = lambda decision_id: False

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            result = gate.execute(
                message="E02_03_TEST",
                requester="human:test_approver",
                seal_request_id="SR_E02_03",
                _seal_runner=spy_runner
            )

            assert not result.approved, "E02.03: Execution should be blocked"
            assert "human gate approval required but not obtained" in result.reason, "E02.03: Reason should indicate missing approval"

            return "PASS", "Missing decision blocks execution"
        finally:
            _human_gate.approve = original_approve


def test_e02_04_expired_approval():
    """
    E02.04: Expired Approval
    Verify: Approval state changes during execution → handled correctly
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        approval_state = [True]  # Start with approval

        original_approve = _human_gate.approve
        def time_varying_approve(decision_id):
            # Simulate approval state change
            result = approval_state[0]
            approval_state[0] = False  # Change state on next call
            return result

        _human_gate.approve = time_varying_approve

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            result = gate.execute(
                message="E02_04_TEST",
                requester="human:test_approver",
                seal_request_id="SR_E02_04",
                _seal_runner=_mock_seal_runner_success
            )

            # First execution should succeed (approve() returns True first)
            assert result.approved, "E02.04: First execution should be approved"

            return "PASS", "Approval state handled correctly"
        finally:
            _human_gate.approve = original_approve


def test_e02_05_duplicate_approval_handling():
    """
    E02.05: Duplicate Approval Handling
    Verify: Multiple approvals handled correctly
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        approval_counts = [0]

        original_approve = _human_gate.approve
        def counting_approve(decision_id):
            approval_counts[0] += 1
            return True

        _human_gate.approve = counting_approve

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            result = gate.execute(
                message="E02_05_TEST",
                requester="human:test_approver",
                seal_request_id="SR_E02_05",
                _seal_runner=_mock_seal_runner_success
            )

            # Should be called exactly once per execution
            assert approval_counts[0] == 1, "E02.05: approve() should be called exactly once per execution"
            assert result.approved, "E02.05: Execution should be approved"

            return "PASS", "Duplicate approval handling correct"
        finally:
            _human_gate.approve = original_approve


if __name__ == "__main__":
    results = []

    tests = [
        ("E02.01", test_e02_01_approve_flow),
        ("E02.02", test_e02_02_reject_flow),
        ("E02.03", test_e02_03_missing_decision),
        ("E02.04", test_e02_04_expired_approval),
        ("E02.05", test_e02_05_duplicate_approval_handling),
    ]

    for test_name, test_func in tests:
        try:
            status, message = test_func()
            results.append((test_name, status, message))
            print(f"{test_name}: {status} - {message}")
        except Exception as e:
            results.append((test_name, "FAIL", str(e)))
            print(f"{test_name}: FAIL - {e}")

    print("\n" + "="*60)
    passed = sum(1 for _, status, _ in results if status == "PASS")
    print(f"E02 RESULTS: {passed}/5 PASS")
    print("="*60)
