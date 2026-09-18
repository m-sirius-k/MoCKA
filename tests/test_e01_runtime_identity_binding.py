"""
E01: Runtime Identity Binding Verification Tests

Verify that runtime identity correctly binds to human authority identity
and decision identity throughout execution.
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
    """Mock seal runner that returns success output."""
    fake_stdout = (
        "COMMIT: deadbeef1234567890deadbeef1234567890dead\n"
        "SUMMARY_HASH: " + ("a" * 64) + "\n"
        "ANCHOR UPDATED AND COMMITTED\n"
    )
    return fake_stdout, 0


def test_e01_01_valid_identity_binding_accepted():
    """
    E01.01: Requester Binding
    Verify: Runtime requester parameter → preserved in execution context
    Expected: requester="human:test_approver" passed through all execution stages
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        original_approve = _human_gate.approve
        _human_gate.approve = lambda decision_id: True

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            result = gate.execute(
                message="E01_01_TEST",
                requester="human:test_approver",
                seal_request_id="SR_E01_01",
                _seal_runner=_mock_seal_runner_success
            )

            # Verify execution succeeded
            assert result.approved, "E01.01: Execution should be approved"

            # Verify ledger records identity
            entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
            assert len(entries) == 1, "E01.01: One ledger entry expected"

            entry = entries[0]
            assert entry["requester"] == "human:test_approver", "E01.01: Requester should be preserved"
            assert entry["approved_by"] == "human:test_approver", "E01.01: approved_by should be human identity"

            return "PASS", "Valid identity binding accepted and recorded"
        finally:
            _human_gate.approve = original_approve


def test_e01_02_missing_human_authority_identity():
    """
    E01.02: Authority Identity Binding
    Verify: Missing human authority → execution blocked
    Expected: Validation rejects missing authority
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        original_approve = _human_gate.approve
        _human_gate.approve = lambda decision_id: True

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            result = gate.execute(
                message="E01_02_TEST",
                requester="",  # Empty requester should fail validation
                seal_request_id="SR_E01_02",
                _seal_runner=_mock_seal_runner_success
            )

            # Verify execution blocked
            assert not result.approved, "E01.02: Execution should be blocked"
            assert "validation failed" in result.reason.lower(), "E01.02: Validation should fail"

            return "PASS", "Missing authority identity correctly blocks execution"
        finally:
            _human_gate.approve = original_approve


def test_e01_03_invalid_authority_identity():
    """
    E01.03: Invalid Authority Identity
    Verify: System authority (not human) → execution blocked
    Expected: Validation rejects non-human authority
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        original_approve = _human_gate.approve
        _human_gate.approve = lambda decision_id: True

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            result = gate.execute(
                message="E01_03_TEST",
                requester="system:auto",  # System authority should fail
                seal_request_id="SR_E01_03",
                _seal_runner=_mock_seal_runner_success
            )

            # Verify execution blocked
            assert not result.approved, "E01.03: Execution should be blocked"
            assert "validation failed" in result.reason.lower(), "E01.03: Validation should fail"

            return "PASS", "Invalid (non-human) authority correctly blocks execution"
        finally:
            _human_gate.approve = original_approve


def test_e01_04_decision_identity_mismatch():
    """
    E01.04: Decision Identity Persistence
    Verify: decision_id remains consistent across request → approve → ledger
    Expected: Same decision_id used throughout
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        decision_ids_seen = []

        original_request = _human_gate.request
        original_approve = _human_gate.approve

        def track_request(decision_id):
            decision_ids_seen.append(("request", decision_id))
            return original_request(decision_id)

        def track_approve(decision_id):
            decision_ids_seen.append(("approve", decision_id))
            return True

        _human_gate.request = track_request
        _human_gate.approve = track_approve

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            result = gate.execute(
                message="E01_04_TEST",
                requester="human:test_approver",
                seal_request_id="SR_E01_04",
                _seal_runner=_mock_seal_runner_success
            )

            # Verify decision_ids match
            assert len(decision_ids_seen) >= 2, "E01.04: request and approve should be tracked"
            request_id = decision_ids_seen[0][1]
            approve_id = decision_ids_seen[1][1]
            assert request_id == approve_id, "E01.04: decision_id should be same for request and approve"

            # Verify ledger has same decision_id
            entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
            assert len(entries) == 1, "E01.04: One ledger entry expected"
            entry = entries[0]
            assert entry["decision_id"] == request_id, "E01.04: Ledger decision_id should match"

            return "PASS", "Decision identity consistent across all stages"
        finally:
            _human_gate.request = original_request
            _human_gate.approve = original_approve


if __name__ == "__main__":
    results = []

    try:
        status, message = test_e01_01_valid_identity_binding_accepted()
        results.append(("E01.01", status, message))
        print(f"E01.01: {status} - {message}")
    except Exception as e:
        results.append(("E01.01", "FAIL", str(e)))
        print(f"E01.01: FAIL - {e}")

    try:
        status, message = test_e01_02_missing_human_authority_identity()
        results.append(("E01.02", status, message))
        print(f"E01.02: {status} - {message}")
    except Exception as e:
        results.append(("E01.02", "FAIL", str(e)))
        print(f"E01.02: FAIL - {e}")

    try:
        status, message = test_e01_03_invalid_authority_identity()
        results.append(("E01.03", status, message))
        print(f"E01.03: {status} - {message}")
    except Exception as e:
        results.append(("E01.03", "FAIL", str(e)))
        print(f"E01.03: FAIL - {e}")

    try:
        status, message = test_e01_04_decision_identity_mismatch()
        results.append(("E01.04", status, message))
        print(f"E01.04: {status} - {message}")
    except Exception as e:
        results.append(("E01.04", "FAIL", str(e)))
        print(f"E01.04: FAIL - {e}")

    # Summary
    print("\n" + "="*60)
    passed = sum(1 for _, status, _ in results if status == "PASS")
    print(f"E01 RESULTS: {passed}/4 PASS")
    print("="*60)
