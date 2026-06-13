"""
MoCKA 3.0 — Governance Pipeline
governance_pipeline.py

責務:
  GL1~GL7を実際の推論フロー(Caliber / mocka_mcp_server)へ接続する単一の窓口。
  各MCP tool呼び出しの前後で呼び出す before_tool()/after_tool() を提供する。

設計:
  - GL1(Grounding)は毎呼び出しでgit実行すると重いため、起動時+一定間隔のみ更新する。
  - GL2(Working Memory)は呼び出しごとに current_task/current_event を更新する。
  - GL3(Thinking Mode)はtool名から判定し、GL2へ明示遷移する。
  - GL6(Reasoning)はPre-Answer Checklistを取得しログ目的で保持する(ブロックはしない)。
  - GL7(Execution Governance)は書き込み系tool(WRITE_TOOLS)に限りdry run/abortを検査する。
  - GL4/GL5はここでは直接呼ばない(検索/合議が発生する箇所で個別利用する)。
"""

import time
from dataclasses import dataclass, field

from grounding_engine import RepositoryGroundingEngine
from working_memory import WorkingMemoryEngine
from thinking_mode import ThinkingModeEngine, ThinkingMode
from reasoning_governance import ReasoningGovernanceEngine
from execution_governance import ExecutionGovernanceEngine

# Repositoryへ書き込みを行う(=GL7 dry runの対象とする)tool名
WRITE_TOOLS = {
    "mocka_write_event",
    "mocka_add_todo",
    "mocka_update_todo",
    "mocka_seal",
}

GROUNDING_REFRESH_SECONDS = 60


@dataclass
class GovernanceDecision:
    allowed: bool
    reason: str
    thinking_mode: str
    checklist_ok: bool
    dry_run_aborts: list = field(default_factory=list)


class GovernancePipeline:
    """全Tool呼び出しの単一窓口。execute_tool()の先頭でbefore_tool()を呼ぶ。"""

    def __init__(self):
        self.grounding_engine = RepositoryGroundingEngine()
        self.wm = WorkingMemoryEngine()
        self.tm = ThinkingModeEngine()
        self.reasoning = ReasoningGovernanceEngine()
        self.execution = ExecutionGovernanceEngine()
        self._last_grounding_at = 0.0
        self._grounding_cache = None

    def _refresh_grounding(self):
        now = time.time()
        if self._grounding_cache is None or (now - self._last_grounding_at) > GROUNDING_REFRESH_SECONDS:
            self._grounding_cache = self.grounding_engine.ground("governance_pipeline_refresh")
            self._last_grounding_at = now
        return self._grounding_cache

    def before_tool(self, tool_name: str, args: dict) -> GovernanceDecision:
        """
        GL1~GL7をtool呼び出し直前に適用する。
        書き込み系toolはGL7 Dry Runでabort条件を検査し、abortがあればallowed=False。
        """
        grounding = self._refresh_grounding()

        mode = self.tm.detect_mode(tool_name, args)
        self.tm.set_mode(mode, event=f"tool:{tool_name}")
        self.wm.update(f"tool:{tool_name}", {
            "current_task": tool_name,
            "current_target": str(args)[:200],
            "current_branch": grounding.current_branch,
        })

        checklist = self.reasoning.enforce_pre_answer_checklist()

        aborts = []
        if tool_name in WRITE_TOOLS:
            # scope = 現在のリポジトリ直下全ディレクトリ。
            # 既存の未関連dirty state(バックグラウンド自動同期)をabort対象にせず、
            # GL7のnew_directory_detected/grounding_not_completed/件数異常のみを有効にする。
            scope = grounding.project_structure
            approval = self.execution.pre_execution_check({
                "scope": scope,
                "expected_new_dirs": scope,
                "expected_max_changes": 200,
            })
            aborts = approval.dry_run.aborts

        allowed = not aborts
        reason = "ok" if allowed else f"GL7 abort: {aborts}"
        return GovernanceDecision(
            allowed=allowed,
            reason=reason,
            thinking_mode=mode.value,
            checklist_ok=checklist.ok,
            dry_run_aborts=aborts,
        )

    def after_tool(self, tool_name: str, args: dict, result_summary: str) -> None:
        """tool実行後、GL2/GL7へ実行結果を記録する。"""
        self.wm.update(f"tool_done:{tool_name}", {"current_event": f"{tool_name} -> {result_summary[:120]}"})
        self.execution.record_execution({"tool": tool_name, "args": args}, {"summary": result_summary})


def main():
    pipeline = GovernancePipeline()
    decision = pipeline.before_tool("mocka_write_event", {"title": "test"})
    print("allowed:", decision.allowed)
    print("reason:", decision.reason)
    print("thinking_mode:", decision.thinking_mode)
    print("checklist_ok:", decision.checklist_ok)
    pipeline.after_tool("mocka_write_event", {"title": "test"}, "ok")


if __name__ == "__main__":
    main()
