"""
governance/seal_governance_gate.py

Phase C-2: SealGovernanceGate。/audit/seal(MANUAL_SEAL)からGL7評価を経由して
既存seal pipeline(scripts/ledger/anchor_update.py)を呼ぶための正式なGovernance Gate。

責務:
- 実行要求受付(message)
- Governance Context生成(execution_id/change_start)
- GL7(structural/execution_governance.py)評価
- Abort判定(GL7がabortsを返した場合はanchor_update.pyを呼ばない)
- Decision Unit記録(data/decisions/decision_ledger.jsonlへ既存スキーマの追加
  フィールドとして記録)
- 承認時のみ既存 scripts/ledger/anchor_update.py をsubprocess実行

禁止(Decision裁定通り): anchor_update.py・mocka_git_safe_commit.py・
calc_summary_hash.pyの内部ロジックは一切変更・再実装しない。本ファイルは
"呼ぶか呼ばないか"を制御するのみで、seal/hash/anchor更新の実処理は
既存スクリプトにそのまま委譲する。
"""
import sys
import json
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

_GOVERNANCE_DIR = Path(__file__).resolve().parent
_MOCKA_ROOT = _GOVERNANCE_DIR.parent
_STRUCTURAL_DIR = _MOCKA_ROOT / "structural"

if str(_STRUCTURAL_DIR) not in sys.path:
    sys.path.insert(0, str(_STRUCTURAL_DIR))

from execution_governance import ExecutionGovernanceEngine  # noqa: E402

SEAL_SCRIPT = _MOCKA_ROOT / "scripts" / "ledger" / "anchor_update.py"
DECISION_LEDGER_PATH = _MOCKA_ROOT / "data" / "decisions" / "decision_ledger.jsonl"


@dataclass
class GateResult:
    approved: bool
    execution_id: str
    reason: str = ""
    aborts: list = field(default_factory=list)
    seal_stdout: str = ""
    seal_returncode: int | None = None


class SealGovernanceGate:
    """
    seal request -> GL7 validation -> (承認時のみ)既存anchor_update.pyをそのまま起動
    -> Decision Unit記録。anchor_update.py自体は無変更のまま呼び出すのみ。

    repo_root/decision_ledger_pathはテスト時にsandbox pathへ差し替え可能。
    _seal_runnerはテスト用フックで、Noneの場合は実際にanchor_update.pyを
    subprocess実行する(本番動作)。anchor_update.py自体はROOT(実MoCKAパス)を
    内部で固定的に参照しているため、テスト時は必ず_seal_runnerへモック関数を
    渡し、実anchor_update.pyの実行(実commit発生)を回避すること。
    """

    def __init__(self, repo_root: Path = _MOCKA_ROOT,
                 decision_ledger_path: Path = DECISION_LEDGER_PATH):
        self.repo_root = Path(repo_root)
        self.decision_ledger_path = Path(decision_ledger_path)
        self.governance = ExecutionGovernanceEngine(repo_root=self.repo_root)

    def execute(self, message: str, scope: list[str] | None = None,
                expected_max_changes: int | None = None,
                _seal_runner=None) -> GateResult:
        execution_id = f"EXEC_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        change_start = datetime.now(timezone.utc).isoformat()

        action = {"scope": scope or [], "expected_max_changes": expected_max_changes}
        approval = self.governance.pre_execution_check(action)

        if not approval.approved:
            result = GateResult(
                approved=False,
                execution_id=execution_id,
                reason=approval.reason,
                aborts=approval.dry_run.aborts if approval.dry_run else [],
            )
            self._record_decision_unit(execution_id, change_start, result)
            return result

        runner = _seal_runner or self._run_seal_script
        stdout, returncode = runner(message)

        result = GateResult(
            approved=True,
            execution_id=execution_id,
            reason="dry run clean, seal executed",
            seal_stdout=stdout,
            seal_returncode=returncode,
        )
        self._record_decision_unit(execution_id, change_start, result)
        return result

    def _run_seal_script(self, message: str):
        proc = subprocess.run(
            ["python", str(SEAL_SCRIPT), message],
            cwd=str(self.repo_root), capture_output=True, text=True, timeout=60,
        )
        return proc.stdout, proc.returncode

    @staticmethod
    def _extract_hashes(stdout: str):
        commit_hash = None
        summary_hash = None
        for line in stdout.splitlines():
            if line.startswith("COMMIT:"):
                commit_hash = line.split(":", 1)[1].strip()
            elif line.startswith("SUMMARY_HASH:"):
                summary_hash = line.split(":", 1)[1].strip()
        return commit_hash, summary_hash

    def _record_decision_unit(self, execution_id: str, change_start: str, result: GateResult) -> None:
        commit_hash, summary_hash = (None, None)
        if result.approved:
            commit_hash, summary_hash = self._extract_hashes(result.seal_stdout)

        entry = {
            "decision_id": f"DC_{execution_id}",
            "title": "SealGovernanceGate seal request",
            "context": "Phase C-2 Governance Gate正式配置(TODO_411/412/413 Boundary対応)",
            "alternatives": [],
            "decision": "approved" if result.approved else "aborted",
            "rationale": result.reason,
            "impact": "anchor_update.py実行有無の制御のみ、seal/hashロジック自体は無変更",
            "related_events": [],
            "related_documents": ["docs/governance/PHASE_C_GOVERNANCE_GATE_IMPLEMENTATION_REPORT_v1.0.md"],
            "approved_by": "system:seal_governance_gate",
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "supersedes": None,
            "superseded_by": None,
            "status": "Active",
            "execution_id": execution_id,
            "change_start": change_start,
            "change_done": datetime.now(timezone.utc).isoformat(),
            "artifact_hash": commit_hash,
            "seal_hash": summary_hash,
            "aborts": result.aborts,
        }
        self.decision_ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.decision_ledger_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
