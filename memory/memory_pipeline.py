"""
MoCKA 3.0 — Memory Layer
memory_pipeline.py

責務:
  Memory Writer / Store / Index / Retriever / Context Builder を統合する単一窓口。

  処理フロー:
    Event / Decision
       v
    Memory Writer
       v
    Memory Store
       v
    Memory Index
       v
    Retriever
       v
    Context Builder
       v
    enriched_context (-> Semantic / Decision へ)

  Memory LayerはGovernance/Semantic/Decision Layerのロジックに変更を
  加えない(出力結果を読み取り、記憶として記録・検索するのみ)。
"""

import sys
from pathlib import Path

_SEMANTIC_DIR = Path(__file__).resolve().parent.parent / "semantic"
_DECISION_DIR = Path(__file__).resolve().parent.parent / "decision"
for _p in (_SEMANTIC_DIR, _DECISION_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from decision_pipeline import DecisionPipeline  # noqa: E402
from semantic_pipeline import SemanticPipeline  # noqa: E402

from memory_context_builder import MemoryContextBuilder  # noqa: E402
from memory_model import EnrichedContext  # noqa: E402
from memory_retriever import MemoryRetriever  # noqa: E402
from memory_store import MemoryStore  # noqa: E402
from memory_writer import MemoryWriter  # noqa: E402


class MemoryPipeline:
    """Memory Layerの統一エントリポイント。"""

    def __init__(self, store: MemoryStore = None):
        self._store = store or MemoryStore()
        self._writer = MemoryWriter(self._store)
        self._retriever = MemoryRetriever(self._store)
        self._context_builder = MemoryContextBuilder(self._store, self._retriever)
        self._semantic_pipeline = SemanticPipeline()
        self._decision_pipeline = DecisionPipeline()

    def record_decision(self, semantic_result, decision_result, extra_tags: tuple = ()):
        """DecisionResultをepisodic memoryとしてMemory Storeへ記録する。"""
        return self._writer.write_decision(decision_result, semantic_result, extra_tags=extra_tags)

    def get_enriched_context(self, intent_key: str, query: str = "") -> EnrichedContext:
        """指定Intentに関する過去の記憶からEnrichedContextを構築する。"""
        return self._context_builder.build(intent_key, query=query)

    def retrieve(self, **kwargs):
        """memory_retriever.MemoryRetriever.retrieve への委譲。"""
        return self._retriever.retrieve(**kwargs)

    def process(self, text: str, context: dict = None):
        """
        text/contextからSemanticResult/DecisionResultを生成し、
        過去の記憶でcontextを補強したうえで記録する。

        Returns:
            (decision_result, enriched_context)
        """
        # 1. 一次分類(Intent推定)のためSemanticResultを生成
        preliminary = self._semantic_pipeline.process(text, context)

        # 2. 過去の記憶からEnrichedContextを構築
        enriched_context = self.get_enriched_context(preliminary.intent.key, query=text)

        # 3. 過去の記憶をcontextへ合成し、Decision Pipelineを実行
        merged_context = dict(context or {})
        for key, value in enriched_context.to_context_dict().items():
            if value:
                merged_context.setdefault(key, value)

        semantic_result = self._semantic_pipeline.process(text, merged_context)
        decision_result = self._decision_pipeline.decide_from_semantic(semantic_result)

        # 4. DecisionResultを記憶として記録
        self.record_decision(semantic_result, decision_result)

        return decision_result, enriched_context
