"""
MoCKA 3.0 — Memory Layer
memory_writer.py

責務:
  Decision Layerの出力(DecisionResult)や実行結果・イベントログから
  MemoryEntryを生成し、Memory Storeへ書き込む。

  - DecisionResult        -> episodic memory (source=Decision)
  - ExecutionResult(将来) -> episodic memory (source=Governance)
  - EventLog              -> episodic memory (source=External)

  Decision Layer / Semantic Layer / Governance Layerのロジックには
  変更を加えない(出力結果を読み取るのみ)。
"""

from memory_model import MemoryEntry
from memory_registry import MemoryType, Source, get_retention_policy
from memory_store import MemoryStore


class MemoryWriter:
    """Decision/Semantic/イベントログからMemoryEntryを生成し、Storeへ書き込むWriter。"""

    def __init__(self, store: MemoryStore = None):
        self._store = store or MemoryStore()

    def write_decision(self, decision_result, semantic_result=None, extra_tags: tuple = ()) -> MemoryEntry:
        """
        DecisionResultをepisodic memoryとして記録する。

        Args:
            decision_result: decision.decision_model.DecisionResult
            semantic_result: semantic.semantic_result.SemanticResult (任意)
            extra_tags: 追加タグ
        """
        policy = get_retention_policy(MemoryType.EPISODIC)

        metadata = {
            "priority_score": decision_result.priority_score,
            "risk_score": decision_result.risk_score,
            "required_governance_check": decision_result.required_governance_check,
        }
        tags = list(policy.default_tags) + ["decision"]

        if semantic_result is not None:
            metadata["intent_key"] = semantic_result.intent.key
            metadata["confidence"] = semantic_result.confidence
            tags.append(f"intent:{semantic_result.intent.key}")

        tags.extend(extra_tags)

        entry = MemoryEntry(
            memory_id=self._store.next_memory_id(MemoryType.EPISODIC),
            memory_type=MemoryType.EPISODIC,
            timestamp=self._store.now_iso(),
            source=Source.DECISION_LAYER,
            content=decision_result.to_dict(),
            metadata=metadata,
            tags=tuple(tags),
        )
        return self._store.append(entry)

    def write_event(self, event: dict, memory_type: str = MemoryType.EPISODIC,
                     source: str = Source.EXTERNAL, tags: tuple = ()) -> MemoryEntry:
        """
        任意のイベント/実行結果をMemoryEntryとして記録する。

        Args:
            event: 記録内容(dict)。"intent_key"キーがあればintent_indexの対象となる。
            memory_type: memory_registry.MemoryType のいずれか
            source: memory_registry.Source のいずれか
            tags: 追加タグ
        """
        policy = get_retention_policy(memory_type)

        metadata = {}
        if "intent_key" in event:
            metadata["intent_key"] = event["intent_key"]

        entry = MemoryEntry(
            memory_id=self._store.next_memory_id(memory_type),
            memory_type=memory_type,
            timestamp=self._store.now_iso(),
            source=source,
            content=event,
            metadata=metadata,
            tags=tuple(policy.default_tags) + tuple(tags),
        )
        return self._store.append(entry)

    def write_semantic_concept(self, key: str, definition: dict, tags: tuple = ()) -> MemoryEntry:
        """概念・定義・Registry情報などをsemantic memoryとして記録する(意味記憶)。"""
        policy = get_retention_policy(MemoryType.SEMANTIC)

        entry = MemoryEntry(
            memory_id=self._store.next_memory_id(MemoryType.SEMANTIC),
            memory_type=MemoryType.SEMANTIC,
            timestamp=self._store.now_iso(),
            source=Source.SEMANTIC_LAYER,
            content={"key": key, **definition},
            metadata={"concept_key": key},
            tags=tuple(policy.default_tags) + tuple(tags),
        )
        return self._store.append(entry)
