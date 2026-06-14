"""
MoCKA Core Kernel — prism.models.context

責務:
  複数Eventから構築された状況スナップショットを表す不変データ構造。
  保存処理は含まない(Memoryへの永続化は呼び出し側の責務)。
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Context:
    """Prismが構築した状況コンテキスト。"""

    context_id: str
    event_ids: tuple = field(default_factory=tuple)
    time_window: tuple = field(default_factory=tuple)  # (start_iso, end_iso)
    actors: tuple = field(default_factory=tuple)        # source_module等の集合
    topics: tuple = field(default_factory=tuple)
    relationships: tuple = field(default_factory=tuple)  # CorrelationEngineの出力
    system_state: dict = field(default_factory=dict)     # Lifecycle等のRead Onlyスナップショット
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "context_id": self.context_id,
            "event_ids": list(self.event_ids),
            "time_window": list(self.time_window),
            "actors": list(self.actors),
            "topics": list(self.topics),
            "relationships": list(self.relationships),
            "system_state": dict(self.system_state),
            "metadata": dict(self.metadata),
        }
