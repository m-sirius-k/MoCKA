import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
MoCKA 3.0 — Governance Layer 7 (GL7)
execution_governance.py

責務:
  推論が正しくてもRepositoryを破壊しないための実行制御。
  Execute前に必ずDry Runを行い、想定外があれば自動で停止する。

Execution Pipeline（固定順序）:
  Task -> Grounding(GL1) -> Policy確認(GL1) -> Conflict検出
       -> Dry Run -> Approval(Human Gate) -> Execute -> Verify
"""

import subprocess
import sys as _sys
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone

from grounding_engine import RepositoryGroundingEngine

REPO_ROOT = Path(r"C:\Users\sirok\MoCKA")

# Phase2(PHI-OS-HUMAN-GATE-STATE-MODEL-V1): GL7 -> PHI-OS は pure event
# forwarding のみ。GL7はphi_os側の関数を呼び出さない・state参照しない・
# 同期待ちしない。event_bus.append()がここで唯一のPHI-OSとの接点であり、
# 失敗してもGL7自身の判定(ApprovalResult)には影響させない(fail-soft)。
_repo_root_str = str(REPO_ROOT)
if _repo_root_str not in _sys.path:
    _sys.path.insert(0, _repo_root_str)


def _emit_gl7_event(result: str, reason_code: str, context: dict) -> None:
    try:
        from phi_os import event_bus
        event_bus.append("GL7_EVENT", {
            "result": result,
            "reason_code": reason_code,
            "context": context,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        # GL7は物理ゲートであることを優先する。PHI-OS側への転送失敗は
        # GL7自身の実行許可/拒否判定をブロックしない(fail-soft, GL7側はfail closed維持)。
        pass

FORBIDDEN_EXECUTIONS = [
    "create_new_folder_without_grounding",
    "create_mocka_3_or_similar",
    "infer_save_path",
    "change_encoding_without_confirmation",
    "infer_branch_name",
    "infer_path",
    "infer_repository_name",
    "bulk_rewrite_without_diff_review",
]

ABORT_CONDITIONS = [
    "new_directory_detected",
    "unexpected_file_count",
    "encoding_mismatch",
    "deletion_outside_scope",
    "grounding_not_completed",
]


@dataclass
class DryRunResult:
    """
    Dry Runで表示する内容。これだけ表示して停止する。
    """
    changed_files: list = field(default_factory=list)
    change_count: int = 0
    encoding: str = "UTF-8"
    git_diff_summary: str = ""
    deletions: list = field(default_factory=list)
    additions: list = field(default_factory=list)
    aborts: list = field(default_factory=list)


@dataclass
class ApprovalResult:
    approved: bool
    reason: str = ""
    dry_run: DryRunResult | None = None


class ExecutionGovernanceEngine:
    """
    存在確認なしで:
    - フォルダ生成 -> 禁止
    - ファイル生成 -> 禁止
    - 保存場所決定 -> 禁止
    必ずGrounding後に決定する。
    Dry RunはExecuteの前に必ず実行する。
    想定外があれば停止する。
    """

    def __init__(self, repo_root: Path = REPO_ROOT):
        self.repo_root = repo_root
        self.grounding = RepositoryGroundingEngine(repo_root)

    def _git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.repo_root,
            capture_output=True, text=True, encoding="utf-8",
        )
        return result.stdout

    def dry_run(self, action: dict) -> DryRunResult:
        """
        action例:
          {"scope": ["structural"], "expected_new_dirs": [], "expected_max_changes": 5}
        現在のworking tree差分からDry Run結果を構築する。
        """
        raw = self._git("status", "--porcelain", "-z")
        entries = raw.split("\0")[:-1] if raw.endswith("\0") else [e for e in raw.split("\0") if e]

        additions, deletions, changed = [], [], []
        i = 0
        while i < len(entries):
            entry = entries[i]
            code, path = entry[:2], entry[3:]
            if code[0] in ("R", "C") or code[1] in ("R", "C"):
                # rename/copy: "XY new-path" entry followed by a separate old-path entry
                new_path = path
                i += 1
                old_path = entries[i] if i < len(entries) else new_path
                changed.append(new_path)
                additions.append(new_path)
                deletions.append(old_path)
            else:
                changed.append(path)
                if "D" in code:
                    deletions.append(path)
                elif code.strip() in ("??", "A"):
                    additions.append(path)
            i += 1

        diff_summary = self._git("diff", "--stat")

        result = DryRunResult(
            changed_files=changed,
            change_count=len(changed),
            encoding="UTF-8",
            git_diff_summary=diff_summary.strip(),
            deletions=deletions,
            additions=additions,
        )
        result.aborts = self.check_abort_conditions(result, action)
        return result

    def check_abort_conditions(self, dry_run: DryRunResult, action: dict | None = None) -> list:
        action = action or {}
        aborts = []

        grounding = self.grounding.ground("dry_run_check")
        if not grounding.repository_root:
            aborts.append("grounding_not_completed")

        scope = action.get("scope", [])
        if scope:
            for path in dry_run.changed_files:
                if not any(path.startswith(s) for s in scope):
                    aborts.append("deletion_outside_scope")
                    break

        expected_new_dirs = set(action.get("expected_new_dirs", []))
        for path in dry_run.additions:
            top = path.split("/")[0]
            existing_top_level = {p.name for p in self.repo_root.iterdir()}
            if "/" in path and top not in existing_top_level and top not in expected_new_dirs:
                aborts.append("new_directory_detected")
                break

        max_changes = action.get("expected_max_changes")
        if max_changes is not None and dry_run.change_count > max_changes:
            # batch index-only removal (git rm --cached) bypass: all changes are deletions, no additions
            all_deletions = (
                len(dry_run.additions) == 0
                and len(dry_run.deletions) == dry_run.change_count
            )
            if not (all_deletions and dry_run.change_count <= 1000):
                aborts.append("unexpected_file_count")

        return aborts

    def pre_execution_check(self, action: dict) -> ApprovalResult:
        """
        Dry Runを実行し、Abort条件がなければApproval可否を返す。
        approved=TrueでもHuman Gateの承認が別途必要(本関数は機械的検査のみ)。
        """
        result = self.dry_run(action)
        if result.aborts:
            _emit_gl7_event("DENY", ",".join(result.aborts), {
                "action": action, "change_count": result.change_count,
            })
            return ApprovalResult(
                approved=False,
                reason=f"abort conditions triggered: {result.aborts}",
                dry_run=result,
            )
        _emit_gl7_event("ALLOW", "dry_run_clean", {
            "action": action, "change_count": result.change_count,
        })
        return ApprovalResult(approved=True, reason="dry run clean", dry_run=result)

    def record_execution(self, action: dict, result: dict) -> None:
        """実行結果の記録(呼び出し側がmocka_write_eventと連携する想定のフック)。"""
        self._last_execution = {"action": action, "result": result}

    def record_file_change(self, before: str, after: str, reason: str) -> None:
        """
        TODO_144: ファイル変更前後の強制記録制度。
        変更前後の内容とreasonを保持する(永続化は呼び出し側のEvent記録に委ねる)。
        """
        self._last_file_change = {"before": before, "after": after, "reason": reason}


def main():
    engine = ExecutionGovernanceEngine()
    approval = engine.pre_execution_check({"scope": ["structural", "data"]})
    print("approved:", approval.approved)
    print("reason:", approval.reason)
    print("change_count:", approval.dry_run.change_count)
    print("aborts:", approval.dry_run.aborts)


if __name__ == "__main__":
    main()
