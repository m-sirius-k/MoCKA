"""
MoCKA 3.0 — Memory Layer
memory_model.py

責務:
  Memory Layerの統一データ形式を定義する。

  - MemoryEntry      : Memory Storeに保存される最小単位
  - ScoredMemory     : Retrieverが返す「記憶 + relevance_score」
  - EnrichedContext  : Context BuilderがSemantic/Decisionへ渡す補助コンテキスト
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MemoryEntry:
    """Memory Storeに保存される最小単位。"""

    memory_id: str
    memory_type: str       # memory_registry.MemoryType のいずれか
    timestamp: str         # ISO8601 (UTC)
    source: str            # memory_registry.Source のいずれか
    content: dict          # 記憶の本体(例: DecisionResult.to_dict())
    metadata: dict = field(default_factory=dict)
    tags: tuple = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type,
            "timestamp": self.timestamp,
            "source": self.source,
            "content": self.content,
            "metadata": dict(self.metadata),
            "tags": list(self.tags),
        }

    @staticmethod
    def from_dict(data: dict) -> "MemoryEntry":
        return MemoryEntry(
            memory_id=data["memory_id"],
            memory_type=data["memory_type"],
            timestamp=data["timestamp"],
            source=data["source"],
            content=data.get("content", {}),
            metadata=data.get("metadata", {}),
            tags=tuple(data.get("tags", ())),
        )


@dataclass(frozen=True)
class ScoredMemory:
    """Retrieverが返す「記憶 + relevance_score」。"""

    entry: MemoryEntry
    relevance_score: float  # 0.0 - 1.0

    def to_dict(self) -> dict:
        return {
            "entry": self.entry.to_dict(),
            "relevance_score": self.relevance_score,
        }


@dataclass(frozen=True)
class EnrichedContext:
    """Context BuilderがSemantic/Decisionへ渡す補助コンテキスト。"""

    intent_key: str
    past_decisions: tuple              # tuple[ScoredMemory] (同Intentの過去Decision)
    success_patterns: tuple            # tuple[ScoredMemory] (risk_scoreが低かった過去Decision)
    failure_patterns: tuple            # tuple[ScoredMemory] (risk_scoreが高かった過去Decision)
    related_topics: tuple              # tuple[str]
    summary_text: str

    def to_dict(self) -> dict:
        return {
            "intent_key": self.intent_key,
            "past_decisions": [m.to_dict() for m in self.past_decisions],
            "success_patterns": [m.to_dict() for m in self.success_patterns],
            "failure_patterns": [m.to_dict() for m in self.failure_patterns],
            "related_topics": list(self.related_topics),
            "summary_text": self.summary_text,
        }

    def to_context_dict(self) -> dict:
        """
        Semantic Layer (ContextAnalyzer) が読み取れる形式に変換する。
        ContextAnalyzerはdictのうち phase/active_task/recent_events/
        conversation_flow キーを参照するため、recent_eventsに
        past_decisionsのmemory_idを格納する。
        """
        return {
            "recent_events": tuple(m.entry.memory_id for m in self.past_decisions),
            "conversation_flow": (self.summary_text,) if self.summary_text else (),
        }
