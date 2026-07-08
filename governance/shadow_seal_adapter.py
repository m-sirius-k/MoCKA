"""
governance/shadow_seal_adapter.py

Phase C-3: Shadow Seal Adapter。本番sealを一切発火させずに、
scripts/ledger/anchor_update.py との契約(CLI I/O契約)・artifact互換性・
hash互換性を検証する。

anchor_update.py自体は内部でROOT(実MoCKAパス)を固定的に参照するため
sandbox化できず、実行すれば必ず本番commit・本番anchor更新が発生する
(Decision裁定によりanchor_update.py自体は変更禁止のため、この制約は解消しない)。
したがって本モジュールは、以下2種類の"実行を伴わない検証"に限定する:

1. 契約確認(verify_cli_contract): anchor_update.pyのソースを静的に読み、
   SealGovernanceGate._extract_hashes()が期待する出力形式("COMMIT: "・
   "SUMMARY_HASH: "というprefix)が現在も存在するかを確認する(実行しない)。
   将来anchor_update.pyの出力形式がCore System File Human Gate経由で
   変更された場合、このチェックがGate側のパース処理との乖離(drift)を検知する。

2. hash/artifact互換性確認(verify_hash_compatibility): anchor_update.pyが
   内部で使う既存の安全な部品(mocka_git_safe_commit・calc_summary_hash.py)は
   root/cwdでsandbox化可能なため、これらをsandbox環境で実行し、hash算出
   アルゴリズム自体とanchor_record.jsonのフィールド構成が本番と同一のロジックで
   正しく動作することを、実anchor_update.pyを呼ばずに実証する。

いずれも本番の`data/decisions/decision_ledger.jsonl`・`governance/anchor_record.json`・
`mocka-governance-kernel/anchors/anchor_record.json`・`scripts/ledger/anchor_update.py`は
一切変更しない(anchor_record.jsonの読み取りのみ行う箇所がある)。
"""
import sys
import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

_GOVERNANCE_DIR = Path(__file__).resolve().parent
_MOCKA_ROOT = _GOVERNANCE_DIR.parent

if str(_GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(_GOVERNANCE_DIR))

from mocka_git_safe_commit import mocka_git_safe_commit  # noqa: E402

SEAL_SCRIPT = _MOCKA_ROOT / "scripts" / "ledger" / "anchor_update.py"
CALC_SUMMARY_HASH_SCRIPT = _GOVERNANCE_DIR / "calc_summary_hash.py"
REAL_ANCHOR_PATHS = [
    _MOCKA_ROOT / "governance" / "anchor_record.json",
    _MOCKA_ROOT / "mocka-governance-kernel" / "anchors" / "anchor_record.json",
]

EXPECTED_STDOUT_MARKERS = ("COMMIT:", "SUMMARY_HASH:")
EXPECTED_ANCHOR_FIELDS = ("external_ref", "sealed_summary_hash", "sealed_at_utc")


@dataclass
class ContractCheckResult:
    ok: bool
    missing_markers: list = field(default_factory=list)
    details: str = ""


@dataclass
class HashCompatibilityResult:
    ok: bool
    summary_hash: str | None = None
    commit_hash: str | None = None
    detail: str = ""


def verify_cli_contract() -> ContractCheckResult:
    """
    anchor_update.pyを実行せず、ソースを静的に読んでSealGovernanceGateが
    期待する出力marker("COMMIT:"・"SUMMARY_HASH:")が現在もコード中に
    存在するかを確認する。
    """
    if not SEAL_SCRIPT.exists():
        return ContractCheckResult(ok=False, details=f"seal script not found: {SEAL_SCRIPT}")

    source = SEAL_SCRIPT.read_text(encoding="utf-8")
    missing = [m for m in EXPECTED_STDOUT_MARKERS if m not in source]
    ok = len(missing) == 0
    detail = "contract OK" if ok else f"missing markers in anchor_update.py source: {missing}"
    return ContractCheckResult(ok=ok, missing_markers=missing, details=detail)


def verify_anchor_schema_compatibility() -> ContractCheckResult:
    """
    実anchor_record.json(読み取りのみ、書き込みなし)が、anchor_update.pyの
    get_summary_hash()/main()が前提とするフィールド(external_ref/
    sealed_summary_hash/sealed_at_utc)を持っているかを確認する。
    """
    missing_overall = []
    for p in REAL_ANCHOR_PATHS:
        if not p.exists():
            missing_overall.append(f"{p}: file not found")
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        missing = [f for f in EXPECTED_ANCHOR_FIELDS if f not in data]
        if missing:
            missing_overall.append(f"{p}: missing fields {missing}")

    ok = len(missing_overall) == 0
    detail = "schema OK" if ok else "; ".join(missing_overall)
    return ContractCheckResult(ok=ok, missing_markers=missing_overall, details=detail)


def verify_hash_compatibility(sandbox_root: Path) -> HashCompatibilityResult:
    """
    anchor_update.py自体は実行せず、その内部で使われる既存部品
    (mocka_git_safe_commit・calc_summary_hash.py)をsandbox_root配下で
    無変更のまま実行し、hash算出アルゴリズムとanchor_record.jsonの
    読み書きロジックが正しく動作することを実証する。

    sandbox_rootは呼び出し側が事前にgit initしたリポジトリであること。
    """
    anchor_paths = [
        sandbox_root / "governance" / "anchor_record.json",
        sandbox_root / "mocka-governance-kernel" / "anchors" / "anchor_record.json",
    ]
    for p in anchor_paths:
        if not p.exists():
            return HashCompatibilityResult(ok=False, detail=f"sandbox anchor stub missing: {p}")

    commit_result = mocka_git_safe_commit(message="shadow adapter test commit", push=False, root=sandbox_root)
    if commit_result.get("error"):
        return HashCompatibilityResult(ok=False, detail=f"commit_error: {commit_result['error']}")

    commit_hash = commit_result.get("commit_hash")
    if not commit_hash:
        return HashCompatibilityResult(ok=False, detail="no changes to commit in sandbox (nothing to seal)")

    for p in anchor_paths:
        ar = json.loads(p.read_text(encoding="utf-8"))
        ar["external_ref"] = f"https://github.com/m-sirius-k/MoCKA/commit/{commit_hash}"
        ar["sealed_summary_hash"] = "0" * 64
        p.write_text(json.dumps(ar, ensure_ascii=False, indent=2), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(CALC_SUMMARY_HASH_SCRIPT)],
        cwd=str(sandbox_root), capture_output=True, text=True, encoding="utf-8",
    )
    summary_hash = None
    for line in proc.stdout.splitlines():
        if line.startswith("sealed_summary_hash:"):
            summary_hash = line.split(": ", 1)[1].strip()

    if not summary_hash or len(summary_hash) != 64:
        return HashCompatibilityResult(
            ok=False, commit_hash=commit_hash,
            detail=f"calc_summary_hash.py did not produce a valid 64-hex hash (stdout={proc.stdout!r})",
        )

    return HashCompatibilityResult(ok=True, summary_hash=summary_hash, commit_hash=commit_hash, detail="hash OK")


def run_full_legacy_compatibility_check(sandbox_root: Path) -> dict:
    """
    Phase C-3 Step 4/5相当の一括実行。実anchor_update.pyは一切呼ばない。
    """
    contract = verify_cli_contract()
    schema = verify_anchor_schema_compatibility()
    hash_compat = verify_hash_compatibility(sandbox_root)

    return {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "cli_contract": {"ok": contract.ok, "detail": contract.details},
        "anchor_schema": {"ok": schema.ok, "detail": schema.details},
        "hash_compatibility": {
            "ok": hash_compat.ok, "detail": hash_compat.detail,
            "summary_hash": hash_compat.summary_hash, "commit_hash": hash_compat.commit_hash,
        },
        "overall_ok": contract.ok and schema.ok and hash_compat.ok,
        "note": "real anchor_update.py was not executed; no production seal was triggered",
    }
