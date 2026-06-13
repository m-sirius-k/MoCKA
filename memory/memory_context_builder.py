"""
MoCKA 3.0 — Memory Layer
memory_context_builder.py

責務:
  Memory Storeに蓄積された記憶から、Semantic/Decisionへ渡す
  補助コンテキスト(EnrichedContext)を生成する。

  - 過去同Intent履歴   : 同じintent_keyのDecision履歴
  - 成功パターン       : risk_scoreが低かった過去Decision
  - 失敗パターン       : risk_scoreが高かった過去Decision
  - related_topics     : semantic_registryのIntentDefinition.related_topicsを参照(読み取りのみ)

  Context Builderは判断(良い/悪い)を行わず、過去の記憶を整理して
  提示するのみ。Semantic Layer / Decision Layerのロジックは変更しない。
"""

import sys
from pathlib import Path

_SEMANTIC_DIR = Path(__file__).resolve().parent.parent / "semantic"
if str(_SEMANTIC_DIR) not in sys.path:
    sys.path.insert(0, str(_SEMANTIC_DIR))

from semantic_registry import get_intent  # noqa: E402

from memory_model import EnrichedContext  # noqa: E402
from memory_registry import MemoryType  # noqa: E402
from memory_retriever import MemoryRetriever  # noqa: E402
from memory_store import MemoryStore  # noqa: E402

# success/failure判定の閾値(DecisionResult.risk_score基準)
_SUCCESS_RISK_THRESHOLD = 0.4
_FAILURE_RISK_THRESHOLD = 0.6


class MemoryContextBuilder:
    """過去のDecision履歴からEnrichedContextを生成するBuilder。"""

    def __init__(self, store: MemoryStore = None, retriever: MemoryRetriever = None):
        self._store = store or MemoryStore()
        self._retriever = retriever or MemoryRetriever(self._store)

    def build(self, intent_key: str, query: str = "", top_k: int = 5) -> EnrichedContext:
        past_decisions = self._retriever.retrieve(
            intent_key=intent_key, query=query, memory_type=MemoryType.EPISODIC, top_k=top_k,
        )

        success_patterns = tuple(
            sm for sm in past_decisions
            if sm.entry.content.get("risk_score", 1.0) < _SUCCESS_RISK_THRESHOLD
        )
        failure_patterns = tuple(
            sm for sm in past_decisions
            if sm.entry.content.get("risk_score", 0.0) >= _FAILURE_RISK_THRESHOLD
        )

        related_topics = tuple(get_intent(intent_key).related_topics)

        summary_text = self._build_summary(
            intent_key, past_decisions, success_patterns, failure_patterns,
        )

        return EnrichedContext(
            intent_key=intent_key,
            past_decisions=past_decisions,
            success_patterns=success_patterns,
            failure_patterns=failure_patterns,
            related_topics=related_topics,
            summary_text=summary_text,
        )

    @staticmethod
    def _build_summary(intent_key, past_decisions, success_patterns, failure_patterns) -> str:
        if not past_decisions:
            return f"intent={intent_key}: 過去の記憶なし"
        return (
            f"intent={intent_key}: 過去Decision{len(past_decisions)}件 "
            f"(成功パターン{len(success_patterns)}件 / 失敗パターン{len(failure_patterns)}件)"
        )
