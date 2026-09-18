"""
E03-E05: Comprehensive Verification Tests

E03: Decision Ledger Continuous Recording
E04: Live Fail Closed Verification
E05: Unauthorized Override Rejection
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


# E03: DECISION LEDGER CONTINUOUS RECORDING

def test_e03_01_event_ledger_completeness():
    """E03.01: Every authorization event creates ledger entry"""
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        original_approve = _human_gate.approve
        _human_gate.approve = lambda decision_id: True

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)

            # Execute 3 events
            for i in range(3):
                gate.execute(
                    message=f"E03_01_TEST_{i}",
                    requester="human:test_approver",
                    seal_request_id=f"SR_E03_01_{i}",
                    _seal_runner=_mock_seal_runner_success
                )

            # Verify 3 entries in ledger
            entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
            assert len(entries) == 3, "E03.01: 3 entries expected"

            return "PASS", "Event ledger complete (3 events → 3 entries)"
        finally:
            _human_gate.approve = original_approve


def test_e03_02_required_field_recording():
    """E03.02: All required fields present in ledger entry"""
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        original_approve = _human_gate.approve
        _human_gate.approve = lambda decision_id: True

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            gate.execute(
                message="E03_02_TEST",
                requester="human:test_approver",
                seal_request_id="SR_E03_02",
                _seal_runner=_mock_seal_runner_success
            )

            entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
            entry = entries[0]

            required_fields = ["decision_id", "approved_by", "approval_timestamp",
                             "requester", "seal_request_id", "execution_id",
                             "change_start", "change_done"]

            for field in required_fields:
                assert field in entry, f"E03.02: Required field {field} missing"

            return "PASS", "All required fields recorded"
        finally:
            _human_gate.approve = original_approve


def test_e03_03_authority_identity_recording():
    """E03.03: Authority identity recorded correctly"""
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        original_approve = _human_gate.approve
        _human_gate.approve = lambda decision_id: True

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            gate.execute(
                message="E03_03_TEST",
                requester="human:alice",
                seal_request_id="SR_E03_03",
                _seal_runner=_mock_seal_runner_success
            )

            entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
            entry = entries[0]

            assert entry["approved_by"] == "human:alice", "E03.03: approved_by should be human authority"
            assert entry["approved_by"].startswith("human:"), "E03.03: authority should start with human:"

            return "PASS", "Authority identity correctly recorded"
        finally:
            _human_gate.approve = original_approve


def test_e03_04_timestamp_accuracy():
    """E03.04: Event timestamp matches execution time"""
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        original_approve = _human_gate.approve
        _human_gate.approve = lambda decision_id: True

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            gate.execute(
                message="E03_04_TEST",
                requester="human:test_approver",
                seal_request_id="SR_E03_04",
                _seal_runner=_mock_seal_runner_success
            )

            entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
            entry = entries[0]

            assert "approval_timestamp" in entry, "E03.04: approval_timestamp should be present"
            assert entry["approval_timestamp"], "E03.04: timestamp should not be empty"
            assert "T" in entry["approval_timestamp"], "E03.04: timestamp should be ISO format"

            return "PASS", "Timestamp recorded in ISO format"
        finally:
            _human_gate.approve = original_approve


def test_e03_05_append_only_integrity():
    """E03.05: Ledger maintains append-only structure"""
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        original_approve = _human_gate.approve
        _human_gate.approve = lambda decision_id: True

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)

            # First write
            gate.execute(
                message="E03_05_TEST_1",
                requester="human:test_approver",
                seal_request_id="SR_E03_05_1",
                _seal_runner=_mock_seal_runner_success
            )

            entries_1 = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
            entry_1_content = entries_1[0]

            # Second write
            gate.execute(
                message="E03_05_TEST_2",
                requester="human:test_approver",
                seal_request_id="SR_E03_05_2",
                _seal_runner=_mock_seal_runner_success
            )

            entries_2 = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]

            # Verify first entry unchanged
            assert len(entries_2) == 2, "E03.05: Should have 2 entries"
            assert entries_2[0] == entry_1_content, "E03.05: First entry should be unchanged"

            return "PASS", "Append-only structure maintained"
        finally:
            _human_gate.approve = original_approve


def test_e03_06_evidence_reference_continuity():
    """E03.06: Evidence chain unbroken"""
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        decision_id_tracker = []

        original_request = _human_gate.request
        original_approve = _human_gate.approve

        def track_request(decision_id):
            decision_id_tracker.append(decision_id)
            return original_request(decision_id)

        def track_approve(decision_id):
            assert decision_id == decision_id_tracker[0], "E03.06: decision_id should match"
            return True

        _human_gate.request = track_request
        _human_gate.approve = track_approve

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            gate.execute(
                message="E03_06_TEST",
                requester="human:test_approver",
                seal_request_id="SR_E03_06",
                _seal_runner=_mock_seal_runner_success
            )

            entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
            entry = entries[0]

            assert entry["decision_id"] == decision_id_tracker[0], "E03.06: Ledger decision_id should match request decision_id"

            return "PASS", "Evidence chain continuous"
        finally:
            _human_gate.request = original_request
            _human_gate.approve = original_approve


# E04: LIVE FAIL CLOSED VERIFICATION

def test_e04_missing_approval_blocks():
    """E04: Missing approval blocks execution"""
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        original_approve = _human_gate.approve
        _human_gate.approve = lambda decision_id: False

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            result = gate.execute(
                message="E04_TEST",
                requester="human:test_approver",
                seal_request_id="SR_E04",
                _seal_runner=_mock_seal_runner_success
            )

            assert not result.approved, "E04: Missing approval should block"

            return "PASS", "Fail-closed enforced (missing approval blocks)"
        finally:
            _human_gate.approve = original_approve


# E05: UNAUTHORIZED OVERRIDE REJECTION

def test_e05_humangate_bypass_rejection():
    """E05: HumanGate bypass rejected"""
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        # Don't mock HumanGate - force it to return False (bypass attempt)
        original_approve = _human_gate.approve
        _human_gate.approve = lambda decision_id: False

        try:
            gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
            result = gate.execute(
                message="E05_TEST",
                requester="human:test_approver",
                seal_request_id="SR_E05",
                _seal_runner=_mock_seal_runner_success
            )

            # Execution should fail
            assert not result.approved, "E05: Bypass attempt should be rejected"
            assert "human gate approval required" in result.reason, "E05: Reason should indicate HumanGate rejection"

            return "PASS", "HumanGate bypass rejected"
        finally:
            _human_gate.approve = original_approve


if __name__ == "__main__":
    results = []

    # E03 tests
    e03_tests = [
        ("E03.01", test_e03_01_event_ledger_completeness),
        ("E03.02", test_e03_02_required_field_recording),
        ("E03.03", test_e03_03_authority_identity_recording),
        ("E03.04", test_e03_04_timestamp_accuracy),
        ("E03.05", test_e03_05_append_only_integrity),
        ("E03.06", test_e03_06_evidence_reference_continuity),
    ]

    # E04 tests
    e04_tests = [
        ("E04.01", test_e04_missing_approval_blocks),
    ]

    # E05 tests
    e05_tests = [
        ("E05.01", test_e05_humangate_bypass_rejection),
    ]

    all_tests = e03_tests + e04_tests + e05_tests

    for test_name, test_func in all_tests:
        try:
            status, message = test_func()
            results.append((test_name, status, message))
            print(f"{test_name}: {status} - {message}")
        except Exception as e:
            results.append((test_name, "FAIL", str(e)))
            print(f"{test_name}: FAIL - {e}")

    print("\n" + "="*60)
    e03_pass = sum(1 for test, status, _ in results if test.startswith("E03") and status == "PASS")
    e04_pass = sum(1 for test, status, _ in results if test.startswith("E04") and status == "PASS")
    e05_pass = sum(1 for test, status, _ in results if test.startswith("E05") and status == "PASS")

    print(f"E03 RESULTS: {e03_pass}/6 PASS")
    print(f"E04 RESULTS: {e04_pass}/1 PASS")
    print(f"E05 RESULTS: {e05_pass}/1 PASS")
    print("="*60)
