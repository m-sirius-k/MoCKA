"""
MoCKA 3.0 — Semantic Layer
semantic_result.py

責務:
  Semantic Layerの出力形式を統一する。

  将来のDecision Layerは、本モジュールのSemanticResultを
  そのまま入力として利用できる構造とする。

  SemanticResultは「意味情報」のみを保持し、実行可否や
  安全性の判断は含まない(Governance Layerの責務外)。
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ContextSummary:
    """Context Analyzerの出力。意味情報のみを保持し、判断は行わない。"""

    phase: str = ""
    active_task: str = ""
    recent_events: tuple = field(default_factory=tuple)
    conversation_flow: tuple = field(default_factory=tuple)
    summary_text: str = ""

    def to_dict(self) -> dict:
        return {
            "phase": self.phase,
            "active_task": self.active_task,
            "recent_events": list(self.recent_events),
            "conversation_flow": list(self.conversation_flow),
            "summary_text": self.summary_text,
        }


@dataclass(frozen=True)
class IntentCandidate:
    """SemanticResultに含まれるIntent候補の軽量表現。"""

    key: str
    label_ja: str
    label_en: str
    confidence: float

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "label_ja": self.label_ja,
            "label_en": self.label_en,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class SemanticResult:
    """Semantic Layerの統一出力形式。"""

    intent: IntentCandidate
    confidence: float
    context_summary: ContextSummary
    related_topics: tuple
    recommended_action: str
    candidates: tuple = field(default_factory=tuple)  # 全Intent候補(IntentCandidate)

    def to_dict(self) -> dict:
        return {
            "intent": self.intent.to_dict(),
            "confidence": self.confidence,
            "context_summary": self.context_summary.to_dict(),
            "related_topics": list(self.related_topics),
            "recommended_action": self.recommended_action,
            "candidates": [c.to_dict() for c in self.candidates],
        }
