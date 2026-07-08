"""
Phase C-3: shadow_seal_adapter.py のテスト。

実anchor_update.pyは一度も実行しない(Decision裁定によりanchor_update.py自体は
sandbox化不可のため)。契約確認・schema確認・hash互換性確認(sandbox実行)のみを検証する。

Test A: CLI契約確認(anchor_update.pyのソースに"COMMIT:"・"SUMMARY_HASH:"が存在する)
Test B: anchor_record.jsonスキーマ互換性確認(実ファイルを読み取りのみで確認)
Test C: hash互換性確認(sandbox内でmocka_git_safe_commit・calc_summary_hash.pyを
        無変更のまま実行し、有効な64桁hexハッシュが得られる)
Test D: 非侵襲性確認(実MoCKAリポジトリのanchor_update.py・anchor_record.json・
        decision_ledger.jsonlが本テスト前後で無変更)
"""
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
sys.path.insert(0, str(MOCKA_ROOT / "governance"))

from shadow_seal_adapter import (  # noqa: E402
    verify_cli_contract,
    verify_anchor_schema_compatibility,
    verify_hash_compatibility,
    run_full_legacy_compatibility_check,
)

FILES_TO_PROTECT = [
    MOCKA_ROOT / "scripts" / "ledger" / "anchor_update.py",
    MOCKA_ROOT / "governance" / "anchor_record.json",
    MOCKA_ROOT / "mocka-governance-kernel" / "anchors" / "anchor_record.json",
    MOCKA_ROOT / "data" / "decisions" / "decision_ledger.jsonl",
]


def _sha256_of_file(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def _init_sandbox_repo(root: Path):
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "sandbox@test.local"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "SandboxTest"], cwd=root, check=True)
    (root / "governance").mkdir(parents=True, exist_ok=True)
    (root / "mocka-governance-kernel" / "anchors").mkdir(parents=True, exist_ok=True)
    stub = '{"anchor_type": "sandbox_test", "external_ref": "https://github.com/m-sirius-k/MoCKA/commit/0000000000000000000000000000000000000000", "sealed_summary_hash": "' + ("0" * 64) + '", "sealed_at_utc": "2026-01-01T00:00:00Z"}'
    (root / "governance" / "anchor_record.json").write_text(stub, encoding="utf-8")
    (root / "mocka-governance-kernel" / "anchors" / "anchor_record.json").write_text(stub, encoding="utf-8")
    (root / "README.md").write_text("sandbox\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=root, check=True)


def test_a_cli_contract():
    result = verify_cli_contract()
    assert result.ok, f"CLI contract check failed: {result.details}"


def test_b_anchor_schema_compatibility():
    result = verify_anchor_schema_compatibility()
    assert result.ok, f"anchor schema check failed: {result.details}"


def test_c_hash_compatibility_sandbox():
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        (sandbox / "change.txt").write_text("test\n", encoding="utf-8")

        result = verify_hash_compatibility(sandbox)
        assert result.ok, f"hash compatibility check failed: {result.detail}"
        assert result.summary_hash is not None and len(result.summary_hash) == 64
        assert result.commit_hash is not None


def test_d_real_repo_untouched():
    before = {p: _sha256_of_file(p) for p in FILES_TO_PROTECT}

    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        _init_sandbox_repo(sandbox)
        (sandbox / "change.txt").write_text("test\n", encoding="utf-8")
        report = run_full_legacy_compatibility_check(sandbox)
        assert report["overall_ok"], report

    after = {p: _sha256_of_file(p) for p in FILES_TO_PROTECT}
    for p in FILES_TO_PROTECT:
        assert before[p] == after[p], f"real file was modified: {p}"


if __name__ == "__main__":
    test_a_cli_contract()
    print("Test A (CLI contract): PASS")
    test_b_anchor_schema_compatibility()
    print("Test B (anchor schema compatibility): PASS")
    test_c_hash_compatibility_sandbox()
    print("Test C (hash compatibility, sandbox): PASS")
    test_d_real_repo_untouched()
    print("Test D (real repo untouched): PASS")
