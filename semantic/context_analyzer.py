"""
MoCKA 3.0 — Semantic Layer
context_analyzer.py

責務:
  現在の要求(テキスト)だけでなく、

    - 直前イベント (recent_events)
    - 会話の流れ (conversation_flow)
    - 現在フェーズ (phase)
    - Active Task (active_task)

  を入力として、意味情報を補完する。

  Context Analyzerは判断(良い/悪い、実行可否)を一切行わず、
  ContextSummary(意味情報のみ)を生成する。
"""

from semantic_result import ContextSummary

# context dictから読み取るキー(無ければ空値として扱う)
_PHASE_KEY = "phase"
_ACTIVE_TASK_KEY = "active_task"
_RECENT_EVENTS_KEY = "recent_events"
_CONVERSATION_FLOW_KEY = "conversation_flow"


class ContextAnalyzer:
    """要求の前後関係(コンテキスト)から意味情報を補完するAnalyzer。"""

    def analyze(self, context: dict = None) -> ContextSummary:
        context = context or {}

        phase = str(context.get(_PHASE_KEY, "") or "")
        active_task = str(context.get(_ACTIVE_TASK_KEY, "") or "")
        recent_events = tuple(context.get(_RECENT_EVENTS_KEY, ()) or ())
        conversation_flow = tuple(context.get(_CONVERSATION_FLOW_KEY, ()) or ())

        summary_text = self._build_summary(
            phase, active_task, recent_events, conversation_flow,
        )

        return ContextSummary(
            phase=phase,
            active_task=active_task,
            recent_events=recent_events,
            conversation_flow=conversation_flow,
            summary_text=summary_text,
        )

    @staticmethod
    def _build_summary(phase, active_task, recent_events, conversation_flow) -> str:
        parts = []
        if phase:
            parts.append(f"phase={phase}")
        if active_task:
            parts.append(f"active_task={active_task}")
        if recent_events:
            parts.append(f"recent_events={len(recent_events)}件")
        if conversation_flow:
            parts.append(f"conversation_flow={len(conversation_flow)}件")

        if not parts:
            return "コンテキスト情報なし"
        return " / ".join(parts)
