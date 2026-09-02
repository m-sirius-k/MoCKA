"""
governance/seal_governance_wrapper.py

Phase C-1(AUTO_SEAL Boundary Audit継続): Governance Wrapper Layerの
非侵襲実装検証。app.py・scripts/ledger/anchor_update.pyへの接続・変更は
一切行わない(Core System File直接変更禁止のため)。本番のPrimaryデータ
(data/decisions/decision_ledger.jsonl、governance/anchor_record.json、
mocka-governance-kernel/anchors/anchor_record.json)も一切変更しない。

本モジュールは呼び出し側が指定するsandbox_root配下でのみ動作する。
GL7(structural/execution_governance.py)のDry Run/Abort判定と、既存の
mocka_git_safe_commit()(root引数でsandbox化)・calc_summary_hash.py
(cwd引数でsandbox化)を実アルゴリズムのまま再利用し、Decision Unit形式
(execution_id/change_start/change_done/artifact_hash/seal_hash)の記録を
既存decision_ledger.jsonlスキーマへの追加フィールドとしてsandbox ledgerへ
追記する。
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

for _p in (str(_GOVERNANCE_DIR), str(_STRUCTURAL_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from mocka_git_safe_commit import mocka_git_safe_commit  # noqa: E402
from execution_governance import ExecutionGovernanceEngine  # noqa: E402

CALC_SUMMARY_HASH_SCRIPT = _GOVERNANCE_DIR / "calc_summary_hash.py"


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
class SealRequestResult:
    approved: bool
    execution_id: str
    reason: str = ""
    aborts: list = field(default_factory=list)
    commit_hash: str | None = None
    summary_hash: str | None = None
    ledger_entry: dict | None = None
    authorized: bool = False
    authorization_reason: str = ""
    approval_event_id: str = ""
    authorization_event_id: str = ""
    execution_event_id: str = ""


class SealGovernanceWrapper:
    """
    seal request -> GL7 validation(Gate B) -> mocka_git_safe_commit(Gate A)
    -> sandbox anchor_record更新 -> Decision Unit記録(ledger拡張)

    sandbox_root配下でのみ動作する。sandbox_root自体がgit repositoryで
    あることを前提とする(呼び出し側が事前にgit initしておくこと)。
    """

    def __init__(self, sandbox_root: Path, action_scope: list[str] | None = None):
        self.sandbox_root = Path(sandbox_root)
        self.action_scope = action_scope or []
        self.governance = ExecutionGovernanceEngine(repo_root=self.sandbox_root)
        self._last_approval_state = None

    def _sandbox_anchor_paths(self) -> list[Path]:
        return [
            self.sandbox_root / "governance" / "anchor_record.json",
            self.sandbox_root / "mocka-governance-kernel" / "anchors" / "anchor_record.json",
        ]

    def _sandbox_ledger_path(self) -> Path:
        return self.sandbox_root / "data" / "decisions" / "decision_ledger.jsonl"

    def _current_authorization_check(self, approval_state: dict,
                                      action: dict) -> tuple[bool, str, AuthorizationState | None]:
        """
        M3: Current Authorization Re-check at execution time.
        Validates that authorization context hasn't changed since approval.

        Returns: (is_authorized, reason, auth_state)
        """
        try:
            now = datetime.now(timezone.utc).isoformat()

            if approval_state is None or not approval_state:
                return False, "No prior approval state available for authorization check", None

            if not approval_state.get("approved"):
                return False, "Approval state not valid at execution time", None

            stored_scope = approval_state.get("scope", [])
            current_scope = action.get("scope", [])
            if stored_scope != current_scope:
                return False, f"Scope changed: {stored_scope} → {current_scope}", None

            stored_max = approval_state.get("expected_max_changes")
            current_max = action.get("expected_max_changes")
            if stored_max != current_max:
                return False, f"Max changes limit changed: {stored_max} → {current_max}", None

            authority = "system:seal_governance_wrapper(sandbox)"

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
                provenance="SealGovernanceWrapper.current_authorization_check()",
            )

            return True, "Current authorization valid", auth_state

        except Exception as e:
            return False, f"Authorization check error: {str(e)}", None

    def request_seal(self, message: str, expected_max_changes: int | None = None) -> SealRequestResult:
        execution_id = f"EXEC_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        change_start = datetime.now(timezone.utc).isoformat()

        action = {"scope": self.action_scope, "expected_max_changes": expected_max_changes}

        # STAGE 1: APPROVAL
        approval = self.governance.pre_execution_check(action)
        approval_event_id = f"APPROVAL_{execution_id}"

        if not approval.approved:
            result = SealRequestResult(
                approved=False,
                execution_id=execution_id,
                reason=approval.reason,
                aborts=approval.dry_run.aborts if approval.dry_run else [],
                approval_event_id=approval_event_id,
            )
            self._record_decision_unit(execution_id, change_start, result, event_type="APPROVAL_DENIED")
            return result

        self._record_decision_unit(execution_id, change_start, SealRequestResult(
            approved=True,
            execution_id=execution_id,
            reason="approval check passed",
            approval_event_id=approval_event_id,
        ), event_type="APPROVAL_PASSED")

        # STAGE 2: AUTHORIZATION (M3/M4)
        authorization_event_id = f"AUTHORIZATION_{execution_id}"

        current_approval_state = {
            "approved": True,
            "approval_time": change_start,
            "scope": action.get("scope"),
            "expected_max_changes": action.get("expected_max_changes"),
        }

        is_authorized, auth_reason, auth_state = self._current_authorization_check(
            self._last_approval_state or current_approval_state, action
        )

        if not is_authorized:
            self._last_approval_state = current_approval_state
            result = SealRequestResult(
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

        self._last_approval_state = current_approval_state

        self._record_decision_unit(execution_id, change_start, SealRequestResult(
            approved=True,
            authorized=True,
            execution_id=execution_id,
            reason="current authorization valid",
            authorization_event_id=authorization_event_id,
        ), event_type="AUTHORIZATION_PASSED")

        # STAGE 3: EXECUTION (M5)
        execution_event_id = f"EXECUTION_{execution_id}"
        commit_result = mocka_git_safe_commit(message=message, push=False, root=self.sandbox_root)
        if commit_result.get("error"):
            result = SealRequestResult(
                approved=True,
                authorized=True,
                execution_id=execution_id,
                reason=f"commit_error: {commit_result['error']}",
                approval_event_id=approval_event_id,
                authorization_event_id=authorization_event_id,
                execution_event_id=execution_event_id,
            )
            self._record_decision_unit(execution_id, change_start, result, event_type="EXECUTION_FAILED")
            return result

        commit_hash = commit_result.get("commit_hash")
        summary_hash = self._update_sandbox_anchor(commit_hash)

        result = SealRequestResult(
            approved=True,
            authorized=True,
            execution_id=execution_id,
            reason="dry run clean, seal completed",
            commit_hash=commit_hash,
            summary_hash=summary_hash,
            approval_event_id=approval_event_id,
            authorization_event_id=authorization_event_id,
            execution_event_id=execution_event_id,
        )
        self._record_decision_unit(execution_id, change_start, result, event_type="EXECUTION_COMPLETED")
        return result

    def _update_sandbox_anchor(self, commit_hash: str | None) -> str | None:
        anchor_paths = self._sandbox_anchor_paths()
        if not all(p.exists() for p in anchor_paths):
            return None

        for p in anchor_paths:
            ar = json.loads(p.read_text(encoding="utf-8"))
            ar["external_ref"] = f"https://github.com/m-sirius-k/MoCKA/commit/{commit_hash}"
            ar["sealed_summary_hash"] = "0" * 64
            p.write_text(json.dumps(ar, ensure_ascii=False, indent=2), encoding="utf-8")

        # calc_summary_hash.py はcwd相対でmocka-governance-kernel/anchors/anchor_record.jsonを
        # 参照するため、cwd=sandbox_rootで実行することでsandbox化する(スクリプト自体は無変更)。
        proc = subprocess.run(
            [sys.executable, str(CALC_SUMMARY_HASH_SCRIPT)],
            cwd=str(self.sandbox_root), capture_output=True, text=True, encoding="utf-8",
        )
        summary_hash = None
        for line in proc.stdout.splitlines():
            if line.startswith("sealed_summary_hash:"):
                summary_hash = line.split(": ", 1)[1].strip()
        if not summary_hash:
            return None

        for p in anchor_paths:
            ar = json.loads(p.read_text(encoding="utf-8"))
            ar["sealed_summary_hash"] = summary_hash
            ar["sealed_at_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            p.write_text(json.dumps(ar, ensure_ascii=False, indent=2), encoding="utf-8")

        short = commit_hash[:7] if commit_hash else "unknown"
        mocka_git_safe_commit(message=f"anchor: re-seal after {short}", push=False, root=self.sandbox_root)
        return summary_hash

    def _record_decision_unit(self, execution_id: str, change_start: str, result: SealRequestResult,
                             event_type: str = "EXECUTION_COMPLETED") -> None:
        """
        M5: Separate audit events for APPROVAL/AUTHORIZATION/EXECUTION.
        Each event type creates a distinct record in decision_ledger.jsonl.
        """
        ledger_path = self._sandbox_ledger_path()
        ledger_path.parent.mkdir(parents=True, exist_ok=True)

        if event_type in ("APPROVAL_DENIED", "AUTHORIZATION_DENIED"):
            decision_status = "denied"
            context_suffix = f" | {event_type}"
        elif event_type == "APPROVAL_PASSED":
            decision_status = "approved"
            context_suffix = " | APPROVAL_PASSED"
        elif event_type == "AUTHORIZATION_PASSED":
            decision_status = "authorized"
            context_suffix = " | AUTHORIZATION_PASSED"
        elif event_type in ("EXECUTION_COMPLETED", "EXECUTION_FAILED"):
            decision_status = "executed" if event_type == "EXECUTION_COMPLETED" else "failed"
            context_suffix = f" | {event_type}"
        else:
            decision_status = "unknown"
            context_suffix = f" | {event_type}"

        entry = {
            "decision_id": f"DC_{execution_id}_{event_type}",
            "title": f"Governance Wrapper seal request - {event_type}",
            "context": f"Phase C Authorization Boundary Implementation(sandbox){context_suffix}",
            "alternatives": [],
            "decision": decision_status,
            "rationale": result.authorization_reason if event_type == "AUTHORIZATION_DENIED" else result.reason,
            "impact": "sandbox限定、本番artifactへの影響なし | Authorization Boundary検証",
            "related_events": [
                result.approval_event_id,
                result.authorization_event_id,
                result.execution_event_id,
            ],
            "related_documents": [],
            "approved_by": "system:seal_governance_wrapper(sandbox)",
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "supersedes": None,
            "superseded_by": None,
            "status": "Active",
            # --- Decision Unit拡張フィールド(既存スキーマへの追加のみ) ---
            "execution_id": execution_id,
            "event_type": event_type,
            "change_start": change_start,
            "change_done": datetime.now(timezone.utc).isoformat(),
            "artifact_hash": result.commit_hash,
            "seal_hash": result.summary_hash,
            "aborts": result.aborts,
            "authorized": result.authorized,
        }
        with ledger_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        result.ledger_entry = entry
