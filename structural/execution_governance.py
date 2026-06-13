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
from dataclasses import dataclass, field
from pathlib import Path

from grounding_engine import RepositoryGroundingEngine

REPO_ROOT = Path(r"C:\Users\sirok\MoCKA")

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
        status_lines = [l for l in self._git("status", "--porcelain").splitlines() if l]

        additions, deletions, changed = [], [], []
        for line in status_lines:
            code, path = line[:2], line[3:].strip()
            changed.append(path)
            if "D" in code:
                deletions.append(path)
            elif code.strip() in ("??", "A"):
                additions.append(path)

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
            aborts.append("unexpected_file_count")

        return aborts

    def pre_execution_check(self, action: dict) -> ApprovalResult:
        """
        Dry Runを実行し、Abort条件がなければApproval可否を返す。
        approved=TrueでもHuman Gateの承認が別途必要(本関数は機械的検査のみ)。
        """
        result = self.dry_run(action)
        if result.aborts:
            return ApprovalResult(
                approved=False,
                reason=f"abort conditions triggered: {result.aborts}",
                dry_run=result,
            )
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
