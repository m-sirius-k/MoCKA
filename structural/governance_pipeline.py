import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
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
import json
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone

from structural.grounding_engine import RepositoryGroundingEngine
from structural.working_memory import WorkingMemoryEngine
from structural.thinking_mode import ThinkingModeEngine, ThinkingMode
from structural.reasoning_governance import ReasoningGovernanceEngine
from structural.execution_governance import ExecutionGovernanceEngine

# Default Deny: 読み取り専用と確認済みのtoolのみGL7 Dry Run検査を免除する。
# このリストに含まれないtool(未知のtoolを含む)は既定でGL7 Dry Run対象=governed。
READ_ONLY_TOOLS = {
    "mocka_get_overview",
    "mocka_get_essence",
    "mocka_get_todo",
    "mocka_list_events",
    "mocka_read_event",
    "mocka_search",
    "mocka_get_incidents",
    "mocka_get_guidelines",
    "mocka_get_command_center",
    "mocka_check_utf8",
    "mocka_registry_get",
    "mocka_registry_current_state",
    "mocka_decision_get",
    "mocka_decision_list",
    "mocka_integrity_get",
    "mocka_integrity_list",
}

# 後方互換のため維持(governance_pipeline外部から書き込み系tool集合として参照される場合がある)
WRITE_TOOLS = {
    "mocka_write_event",
    "mocka_add_todo",
    "mocka_update_todo",
    "mocka_seal",
}

GROUNDING_REFRESH_SECONDS = 60


class JarvisObservability:
    """
    Read-only observability engine. Evaluates governance decision execution outcomes.
    Does NOT hold execution authority or make governance decisions.
    """

    def __init__(self, mocka_root: Path = None):
        self.mocka_root = mocka_root or Path(__file__).resolve().parent.parent
        self.decision_ledger = self.mocka_root / "data" / "decisions" / "decision_ledger.jsonl"

    def record_tool_outcome(self, tool_name: str, allowed: bool, reason: str, result_summary: str) -> None:
        """
        Record tool execution outcome for governance observability.
        Read-only: only appends to decision_ledger, never modifies existing entries.
        """
        if not self.decision_ledger.exists():
            return

        entry = {
            "decision_id": f"JARVIS_OBS_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "title": f"JARVIS observability: {tool_name}",
            "context": "Governance execution outcome monitoring",
            "decision": "allowed" if allowed else "blocked",
            "rationale": reason,
            "tool_name": tool_name,
            "result_summary": result_summary[:200] if result_summary else "",
            "recorded_by": "system:jarvis_observability",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "Recorded",
        }

        try:
            with self.decision_ledger.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            # Fail-soft: observability failure does not block execution
            pass


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
        self.jarvis = JarvisObservability()
        self._last_grounding_at = 0.0
        self._grounding_cache = None

    def _refresh_grounding(self):
        now = time.time()
        if self._grounding_cache is None or (now - self._last_grounding_at) > GROUNDING_REFRESH_SECONDS:
            self._grounding_cache = self.grounding_engine.ground("governance_pipeline_refresh")
            self._last_grounding_at = now
        return self._grounding_cache

    def _read_decision(self, decision_id: str) -> dict or None:
        """
        Read decision record from decision_ledger.jsonl
        HG-NEW-001(A): Use Human Gate Decision Record as Canonical Authority Evidence
        """
        import json
        from pathlib import Path

        try:
            ledger_path = Path(__file__).resolve().parent.parent / "data" / "decisions" / "decision_ledger.jsonl"
            if not ledger_path.exists():
                return None

            for line in ledger_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    record = json.loads(line)
                    if record.get("decision_id") == decision_id:
                        return record
        except Exception:
            pass

        return None

    def before_tool(self, tool_name: str, args: dict, req_id: str = None, session_id: str = None) -> GovernanceDecision:
        """
        GL1~GL7をtool呼び出し直前に適用する。
        書き込み系toolはGL7 Dry Runでabort条件を検査し、abortがあればallowed=False。
        BA-04: Authority Decision validation (HG-PS-01=C, HG-SCOPE-01=C: DEFERRED → BLOCKED)
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

        # BA-04 FAIL-CLOSED GATE: Authority validation (HG Decision: PS-01=C, SCOPE-01=C DEFERRED)
        # Per HG Decisions: Present Standing and Authority Scope are DEFERRED
        # Fail-closed: DEFERRED means UNKNOWN, UNKNOWN means BLOCK
        if tool_name not in READ_ONLY_TOOLS:
            decision_id = args.get("decision_id")

            # Requirement 0: decision_id must be present
            if not decision_id:
                aborts.append("BA04_DECISION_ID_MISSING")
            else:
                decision_record = self._read_decision(decision_id)

                # Requirement 1: Decision exists
                if not decision_record:
                    aborts.append("BA04_DECISION_NOT_FOUND")

                # Requirement 2: Decision status == Active
                elif decision_record.get("status") != "Active":
                    aborts.append(f"BA04_DECISION_NOT_ACTIVE:{decision_record.get('status')}")

                else:
                    # Requirement 3: Present Standing (HG-PS-01=C DEFERRED)
                    # Per HG Decision: Present Standing Tn validation is DEFERRED
                    # Fail-closed: DEFERRED means UNKNOWN, UNKNOWN means BLOCK
                    aborts.append("BA04_PRESENT_STANDING_DEFERRED")

                    # Requirement 4: Authority Scope (HG-SCOPE-01=C DEFERRED)
                    # Per HG Decision: Authority Scope validation is DEFERRED
                    # Fail-closed: DEFERRED means UNKNOWN, UNKNOWN means BLOCK
                    aborts.append("BA04_AUTHORITY_SCOPE_DEFERRED")

        # GL7 Dry Run (only if no BA-04 aborts)
        if tool_name not in READ_ONLY_TOOLS and not aborts:
            # Default Deny: READ_ONLY_TOOLS以外(未知のtoolを含む)は全てGL7 Dry Run対象。
            # scope = 現在のリポジトリ直下全ディレクトリ。
            # 既存の未関連dirty state(バックグラウンド自動同期)をabort対象にせず、
            # GL7のnew_directory_detected/grounding_not_completed/件数異常のみを有効にする。
            scope = grounding.project_structure
            approval = self.execution.pre_execution_check({
                "scope": scope,
                "expected_new_dirs": scope,
                "expected_max_changes": 400,
            })
            aborts.extend(approval.dry_run.aborts)

        allowed = (not aborts) and checklist.ok
        if aborts:
            reason = f"GL7 abort: {aborts}"
        elif not checklist.ok:
            reason = f"GL6 pre-answer checklist failed: missing={checklist.missing}"
        else:
            reason = "ok"

        # JARVIS observability: record governance decision
        self.jarvis.record_tool_outcome(
            tool_name=tool_name,
            allowed=allowed,
            reason=reason,
            result_summary=f"GL7={len(aborts)} aborts; checklist_ok={checklist.ok}"
        )

        return GovernanceDecision(
            allowed=allowed,
            reason=reason,
            thinking_mode=mode.value,
            checklist_ok=checklist.ok,
            dry_run_aborts=aborts,
        )

    def after_tool(self, tool_name: str, args: dict, result_summary: str, allowed: bool = True, reason: str = "") -> None:
        """tool実行後、GL2/GL7へ実行結果を記録する。JARVIS observability も追加。"""
        self.wm.update(f"tool_done:{tool_name}", {"current_event": f"{tool_name} -> {result_summary[:120]}"})
        self.execution.record_execution({"tool": tool_name, "args": args}, {"summary": result_summary})
        self.jarvis.record_tool_outcome(tool_name, allowed, reason, result_summary)


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
