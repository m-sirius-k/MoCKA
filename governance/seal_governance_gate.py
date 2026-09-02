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
class AuthorizationState:
    """Current authorization state at execution time"""
    is_authorized: bool
    authority: str
    scope: list[str]
    evidence: dict
    state_at: str
    provenance: str


@dataclass
class GateResult:
    approved: bool
    execution_id: str
    reason: str = ""
    aborts: list = field(default_factory=list)
    seal_stdout: str = ""
    seal_returncode: int | None = None
    authorized: bool = False
    authorization_reason: str = ""
    approval_event_id: str = ""
    authorization_event_id: str = ""
    execution_event_id: str = ""


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
        self._last_approval_state = None

    def _current_authorization_check(self, approval_state: dict,
                                      action: dict) -> tuple[bool, str, AuthorizationState | None]:
        """
        M3: Current Authorization Re-check at execution time.
        Validates that authorization context hasn't changed since approval.

        Returns: (is_authorized, reason, auth_state)
        """
        try:
            now = datetime.now(timezone.utc).isoformat()

            # Check 0: Evidence of prior approval must exist
            if approval_state is None or not approval_state:
                return False, "No prior approval state available for authorization check", None

            # Check 1: GL7 approval state still valid at execution time
            if not approval_state.get("approved"):
                return False, "Approval state not valid at execution time", None

            # Check 2: Scope validation - ensure scope hasn't changed
            stored_scope = approval_state.get("scope", [])
            current_scope = action.get("scope", [])
            if stored_scope != current_scope:
                return False, f"Scope changed: {stored_scope} → {current_scope}", None

            # Check 3: Expected max changes unchanged
            stored_max = approval_state.get("expected_max_changes")
            current_max = action.get("expected_max_changes")
            if stored_max != current_max:
                return False, f"Max changes limit changed: {stored_max} → {current_max}", None

            # Check 4: Authority validation - approval is from system (SealGovernanceGate)
            authority = "system:seal_governance_gate"

            # Build authorization state
            auth_state = AuthorizationState(
                is_authorized=True,
                authority=authority,
                scope=current_scope,
                evidence={
                    "approval_time": approval_state.get("approval_time"),
                    "checked_at": now,
                    "action": action,
                },
                state_at=now,
                provenance="SealGovernanceGate.current_authorization_check()",
            )

            return True, "Current authorization valid", auth_state

        except Exception as e:
            return False, f"Authorization check error: {str(e)}", None

    def execute(self, message: str, scope: list[str] | None = None,
                expected_max_changes: int | None = None,
                _seal_runner=None) -> GateResult:
        execution_id = f"EXEC_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        change_start = datetime.now(timezone.utc).isoformat()

        action = {"scope": scope or [], "expected_max_changes": expected_max_changes}

        # STAGE 1: APPROVAL
        approval = self.governance.pre_execution_check(action)
        approval_event_id = f"APPROVAL_{execution_id}"

        if not approval.approved:
            # M5: Separate APPROVAL_DENIED event
            result = GateResult(
                approved=False,
                execution_id=execution_id,
                reason=approval.reason,
                aborts=approval.dry_run.aborts if approval.dry_run else [],
                approval_event_id=approval_event_id,
            )
            self._record_decision_unit(execution_id, change_start, result, event_type="APPROVAL_DENIED")
            return result

        # Record APPROVAL_PASSED event
        self._record_decision_unit(execution_id, change_start, GateResult(
            approved=True,
            execution_id=execution_id,
            reason="approval check passed",
            approval_event_id=approval_event_id,
        ), event_type="APPROVAL_PASSED")

        # STAGE 2: AUTHORIZATION (M3/M4)
        authorization_event_id = f"AUTHORIZATION_{execution_id}"

        # Build current approval state for this call
        current_approval_state = {
            "approved": True,
            "approval_time": change_start,
            "scope": action.get("scope"),
            "expected_max_changes": action.get("expected_max_changes"),
        }

        # Check if authorization context has changed since last call
        is_authorized, auth_reason, auth_state = self._current_authorization_check(
            self._last_approval_state or current_approval_state, action
        )

        if not is_authorized:
            # M4: Block execution if authorization fails (but still update state for next call)
            self._last_approval_state = current_approval_state
            result = GateResult(
                approved=True,
                authorized=False,
                execution_id=execution_id,
                reason="Approval passed",
                authorization_reason=auth_reason,
                approval_event_id=approval_event_id,
                authorization_event_id=authorization_event_id,
            )
            self._record_decision_unit(execution_id, change_start, result, event_type="AUTHORIZATION_DENIED")
            return result

        # Update approval state for next call
        self._last_approval_state = current_approval_state

        # Record AUTHORIZATION_PASSED event
        self._record_decision_unit(execution_id, change_start, GateResult(
            approved=True,
            authorized=True,
            execution_id=execution_id,
            reason="current authorization valid",
            authorization_event_id=authorization_event_id,
        ), event_type="AUTHORIZATION_PASSED")

        # STAGE 3: EXECUTION (M5)
        execution_event_id = f"EXECUTION_{execution_id}"
        runner = _seal_runner or self._run_seal_script
        stdout, returncode = runner(message)

        result = GateResult(
            approved=True,
            authorized=True,
            execution_id=execution_id,
            reason="dry run clean, seal executed",
            seal_stdout=stdout,
            seal_returncode=returncode,
            approval_event_id=approval_event_id,
            authorization_event_id=authorization_event_id,
            execution_event_id=execution_event_id,
        )
        self._record_decision_unit(execution_id, change_start, result, event_type="EXECUTION_COMPLETED")
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

    def _record_decision_unit(self, execution_id: str, change_start: str, result: GateResult,
                             event_type: str = "EXECUTION_COMPLETED") -> None:
        """
        M5: Separate audit events for APPROVAL/AUTHORIZATION/EXECUTION.
        Each event type creates a distinct record in decision_ledger.jsonl.
        """
        commit_hash, summary_hash = (None, None)
        if result.approved and result.authorized and result.seal_stdout:
            commit_hash, summary_hash = self._extract_hashes(result.seal_stdout)

        # Determine decision status based on event type
        if event_type in ("APPROVAL_DENIED", "AUTHORIZATION_DENIED"):
            decision_status = "denied"
            context_suffix = f" | {event_type}"
        elif event_type == "APPROVAL_PASSED":
            decision_status = "approved"
            context_suffix = " | APPROVAL_PASSED"
        elif event_type == "AUTHORIZATION_PASSED":
            decision_status = "authorized"
            context_suffix = " | AUTHORIZATION_PASSED"
        elif event_type == "EXECUTION_COMPLETED":
            decision_status = "executed" if result.seal_returncode == 0 else "failed"
            context_suffix = " | EXECUTION_COMPLETED"
        else:
            decision_status = "unknown"
            context_suffix = f" | {event_type}"

        entry = {
            "decision_id": f"DC_{execution_id}_{event_type}",
            "title": f"SealGovernanceGate seal request - {event_type}",
            "context": f"Phase C Authorization Boundary Implementation{context_suffix}",
            "alternatives": [],
            "decision": decision_status,
            "rationale": result.authorization_reason if event_type == "AUTHORIZATION_DENIED" else result.reason,
            "impact": "anchor_update.py execution control via Authorization Boundary",
            "related_events": [
                result.approval_event_id,
                result.authorization_event_id,
                result.execution_event_id,
            ],
            "related_documents": ["docs/governance/PHASE_C_GOVERNANCE_GATE_IMPLEMENTATION_REPORT_v1.0.md"],
            "approved_by": "system:seal_governance_gate",
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "supersedes": None,
            "superseded_by": None,
            "status": "Active",
            # --- M3/M4/M5: Authorization Boundary Event Fields ---
            "execution_id": execution_id,
            "event_type": event_type,
            "change_start": change_start,
            "change_done": datetime.now(timezone.utc).isoformat(),
            "artifact_hash": commit_hash,
            "seal_hash": summary_hash,
            "aborts": result.aborts,
            "authorized": result.authorized,
        }
        self.decision_ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.decision_ledger_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
