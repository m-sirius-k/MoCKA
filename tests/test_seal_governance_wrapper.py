"""
Phase C-1: seal_governance_wrapper.py のsandbox検証テスト。

全テストは一時ディレクトリ(tempfile.TemporaryDirectory)内で独立したgit
repositoryを作成して実行する。本番のMoCKAリポジトリ(app.py・
scripts/ledger/anchor_update.py・data/decisions/decision_ledger.jsonl・
governance/anchor_record.json等)は一切変更しない。

Test A: 正常系(GL7承認 -> sandbox commit -> sandbox anchor更新 -> ledger記録)
Test B: 異常系(GL7 Abort -> anchor未更新 -> abort記録のみ)
Test C: 非侵襲性確認(実MoCKAリポジトリのCore System Fileが無変更であることの証明)
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
sys.path.insert(0, str(MOCKA_ROOT / "governance"))

from seal_governance_wrapper import SealGovernanceWrapper  # noqa: E402

CORE_FILES_TO_PROTECT = [
    MOCKA_ROOT / "app.py",
    MOCKA_ROOT / "scripts" / "ledger" / "anchor_update.py",
]


def _sha256_of_file(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def _init_sandbox_repo(root: Path):
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "sandbox@test.local"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "SandboxTest"], cwd=root, check=True)

    (root / "governance").mkdir(parents=True, exist_ok=True)
    (root / "mocka-governance-kernel" / "anchors").mkdir(parents=True, exist_ok=True)
    anchor_stub = {
        "anchor_type": "sandbox_test",
        "external_ref": "https://github.com/m-sirius-k/MoCKA/commit/0000000000000000000000000000000000000000",
        "sealed_summary_hash": "0" * 64,
        "sealed_at_utc": "2026-01-01T00:00:00Z",
    }
    for rel in ("governance/anchor_record.json", "mocka-governance-kernel/anchors/anchor_record.json"):
        (root / rel).write_text(json.dumps(anchor_stub, ensure_ascii=False, indent=2), encoding="utf-8")

    (root / "README.md").write_text("sandbox test repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "initial sandbox commit"], cwd=root, check=True)


def test_a_normal_path_approved_and_sealed():
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)

        (sandbox / "feature.txt").write_text("test change\n", encoding="utf-8")

        wrapper = SealGovernanceWrapper(sandbox_root=sandbox)
        result = wrapper.request_seal(message="test seal request")

        assert result.approved, f"expected approval, got aborts={result.aborts} reason={result.reason}"
        assert result.commit_hash is not None
        assert result.summary_hash is not None and len(result.summary_hash) == 64

        anchor = json.loads((sandbox / "governance" / "anchor_record.json").read_text(encoding="utf-8"))
        assert anchor["sealed_summary_hash"] == result.summary_hash

        ledger_path = sandbox / "data" / "decisions" / "decision_ledger.jsonl"
        assert ledger_path.exists()
        entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
        assert len(entries) == 1
        entry = entries[0]
        for field in ("execution_id", "change_start", "change_done", "artifact_hash", "seal_hash"):
            assert field in entry, f"Decision Unit field missing: {field}"
        assert entry["artifact_hash"] == result.commit_hash
        assert entry["seal_hash"] == result.summary_hash
        assert entry["decision"] == "approved"
        # 既存decision_ledger.jsonlスキーマの必須フィールドも保持されていることを確認(後方互換)
        for field in ("decision_id", "title", "approved_by", "approved_at", "status"):
            assert field in entry, f"existing schema field missing: {field}"


def test_b_abort_path_no_seal_produced():
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)

        before_anchor = (sandbox / "governance" / "anchor_record.json").read_text(encoding="utf-8")
        commits_before = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"], cwd=sandbox, capture_output=True, text=True
        ).stdout.strip()

        (sandbox / "feature.txt").write_text("test change\n", encoding="utf-8")
        (sandbox / "extra.txt").write_text("another change\n", encoding="utf-8")

        wrapper = SealGovernanceWrapper(sandbox_root=sandbox)
        # expected_max_changes=1 だが実際は2ファイル変更 -> unexpected_file_count でAbort
        result = wrapper.request_seal(message="test seal request (should abort)", expected_max_changes=1)

        assert not result.approved
        assert "unexpected_file_count" in result.aborts
        assert result.commit_hash is None
        assert result.summary_hash is None

        after_anchor = (sandbox / "governance" / "anchor_record.json").read_text(encoding="utf-8")
        assert before_anchor == after_anchor, "anchor_record.json must not change on abort"

        commits_after = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"], cwd=sandbox, capture_output=True, text=True
        ).stdout.strip()
        assert commits_before == commits_after, "no new commit should be created on abort"

        ledger_path = sandbox / "data" / "decisions" / "decision_ledger.jsonl"
        entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
        assert len(entries) == 1
        assert entries[0]["decision"] == "aborted"
        assert entries[0]["artifact_hash"] is None
        assert entries[0]["seal_hash"] is None


def test_c_real_repo_core_files_untouched():
    before = {p: _sha256_of_file(p) for p in CORE_FILES_TO_PROTECT}

    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        (sandbox / "feature.txt").write_text("test change\n", encoding="utf-8")
        SealGovernanceWrapper(sandbox_root=sandbox).request_seal(message="non-invasiveness check")

    after = {p: _sha256_of_file(p) for p in CORE_FILES_TO_PROTECT}
    for p in CORE_FILES_TO_PROTECT:
        assert before[p] == after[p], f"Core System File was modified: {p}"


if __name__ == "__main__":
    test_a_normal_path_approved_and_sealed()
    print("Test A (normal path, approved and sealed): PASS")
    test_b_abort_path_no_seal_produced()
    print("Test B (abort path, no seal produced): PASS")
    test_c_real_repo_core_files_untouched()
    print("Test C (real repo Core System Files untouched): PASS")
