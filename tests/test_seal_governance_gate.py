"""
Phase C-2: seal_governance_gate.py のテスト。

重要な安全上の制約: scripts/ledger/anchor_update.py は自身のROOTを
"C:\\Users\\sirok\\MoCKA" に内部で固定しており、cwdやパラメータで
sandbox化できない(Decision裁定によりanchor_update.py自体は無変更のため)。
したがって、本テストではSealGovernanceGate.execute()の_seal_runnerフックへ
モック関数を渡し、実anchor_update.pyの実行(実commit・実anchor更新の発生)を
一切行わない。実行するのはGate自身のロジック(GL7評価・承認/Abort分岐・
Decision Unit記録)のみである。

repo_root(GL7のgit dry run対象)・decision_ledger_path(記録先)は
いずれも一時sandboxディレクトリへ差し替え、本番のMoCKAリポジトリ・
data/decisions/decision_ledger.jsonlには一切書き込まない。

Test A: 正常系(GL7承認 -> モックseal実行 -> Decision Unit記録、
        実anchor_update.pyは呼ばれない(モック関数呼び出しで代替確認))
Test B: 異常系(GL7 Abort -> モックseal実行は一切呼ばれない -> abort記録のみ)
Test C: 非侵襲性確認(実MoCKAリポジトリのdata/decisions/decision_ledger.jsonl・
        governance/anchor_record.json・app.py・anchor_update.pyが無変更)
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
sys.path.insert(0, str(MOCKA_ROOT / "governance"))

from seal_governance_gate import SealGovernanceGate  # noqa: E402

FILES_TO_PROTECT = [
    MOCKA_ROOT / "app.py",
    MOCKA_ROOT / "scripts" / "ledger" / "anchor_update.py",
    MOCKA_ROOT / "data" / "decisions" / "decision_ledger.jsonl",
    MOCKA_ROOT / "governance" / "anchor_record.json",
]


def _sha256_of_file(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def _init_sandbox_repo(root: Path):
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "sandbox@test.local"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "SandboxTest"], cwd=root, check=True)
    (root / "README.md").write_text("sandbox test repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "initial sandbox commit"], cwd=root, check=True)


def _mock_seal_runner_success(message: str):
    """実anchor_update.pyを呼ばず、成功時の標準出力形式のみを模した応答を返す。"""
    fake_stdout = (
        "COMMIT: deadbeef1234567890deadbeef1234567890dead\n"
        "SUMMARY_HASH: " + ("a" * 64) + "\n"
        "ANCHOR UPDATED AND COMMITTED\n"
    )
    return fake_stdout, 0


def test_a_normal_path_approved_records_decision_unit():
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        calls = []

        def spy_runner(message):
            calls.append(message)
            return _mock_seal_runner_success(message)

        gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
        result = gate.execute(message="MANUAL_SEAL_test", _seal_runner=spy_runner)

        assert result.approved, f"expected approval, got aborts={result.aborts} reason={result.reason}"
        assert len(calls) == 1, "seal runner should be called exactly once on approval"
        assert result.seal_returncode == 0

        entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
        assert len(entries) == 1
        entry = entries[0]
        assert entry["decision"] == "approved"
        assert entry["artifact_hash"] == "deadbeef1234567890deadbeef1234567890dead"
        assert entry["seal_hash"] == "a" * 64
        for field in ("execution_id", "change_start", "change_done"):
            assert field in entry
        for field in ("decision_id", "title", "approved_by", "approved_at", "status"):
            assert field in entry


def test_b_abort_path_seal_runner_never_called():
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"

        (sandbox / "file1.txt").write_text("a\n", encoding="utf-8")
        (sandbox / "file2.txt").write_text("b\n", encoding="utf-8")

        calls = []

        def spy_runner(message):
            calls.append(message)
            return _mock_seal_runner_success(message)

        gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
        result = gate.execute(message="MANUAL_SEAL_test", expected_max_changes=1, _seal_runner=spy_runner)

        assert not result.approved
        assert "unexpected_file_count" in result.aborts
        assert len(calls) == 0, "seal runner must NOT be called when GL7 aborts"

        entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
        assert len(entries) == 1
        assert entries[0]["decision"] == "aborted"
        assert entries[0]["artifact_hash"] is None
        assert entries[0]["seal_hash"] is None


def test_c_real_repo_untouched():
    before = {p: _sha256_of_file(p) for p in FILES_TO_PROTECT}

    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        ledger_path = sandbox / "decision_ledger.jsonl"
        gate = SealGovernanceGate(repo_root=sandbox, decision_ledger_path=ledger_path)
        gate.execute(message="non-invasiveness check", _seal_runner=_mock_seal_runner_success)

        (sandbox / "f.txt").write_text("x\n", encoding="utf-8")
        gate.execute(message="abort check", expected_max_changes=0, _seal_runner=_mock_seal_runner_success)

    after = {p: _sha256_of_file(p) for p in FILES_TO_PROTECT}
    for p in FILES_TO_PROTECT:
        assert before[p] == after[p], f"real file was modified: {p}"


if __name__ == "__main__":
    test_a_normal_path_approved_records_decision_unit()
    print("Test A (normal path, approved, Decision Unit recorded): PASS")
    test_b_abort_path_seal_runner_never_called()
    print("Test B (abort path, seal runner never called): PASS")
    test_c_real_repo_untouched()
    print("Test C (real repo files untouched): PASS")
