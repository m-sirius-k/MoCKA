"""
MoCKA 3.0 — Memory Layer
memory_retriever.py

責務:
  Memory Storeに保存された記憶から、必要な記憶を検索条件に応じて
  抽出し、relevance_score付きのランキングを返す。

検索条件:
  - intent       : metadata["intent_key"] と一致するか
  - tags         : 指定タグとの重なり
  - query        : テキスト類似度(memory_index.similarity_index)
  - timestamp    : 新しいものほど高スコア(recency)
  - relevance_score: 上記を合成した0-1スコア
"""

from memory_index import MemoryIndex
from memory_model import ScoredMemory
from memory_store import MemoryStore

# relevance_score合成の重み(合計1.0)
_WEIGHTS = {
    "intent_match": 0.40,
    "tag_overlap": 0.25,
    "similarity": 0.20,
    "recency": 0.15,
}


class MemoryRetriever:
    """検索条件に応じてMemoryEntryをrelevance_score付きで抽出するRetriever。"""

    def __init__(self, store: MemoryStore = None):
        self._store = store or MemoryStore()

    def retrieve(self, intent_key: str = None, tags: tuple = (), query: str = "",
                  memory_type: str = None, top_k: int = 5) -> tuple:
        """
        検索条件に合致するMemoryEntryをrelevance_score降順で返す。

        Returns:
            tuple[ScoredMemory]
        """
        entries = self._store.all()
        if memory_type:
            entries = tuple(e for e in entries if e.memory_type == memory_type)
        if intent_key:
            entries = tuple(e for e in entries if (e.metadata or {}).get("intent_key") == intent_key)

        if not entries:
            return ()

        index = MemoryIndex(entries)
        similarity_hits = index.similar_to(query) if query else {}

        total = len(entries)
        scored = []
        for position, entry in enumerate(entries):
            intent_match = 1.0 if intent_key and (entry.metadata or {}).get("intent_key") == intent_key else 0.0

            tag_overlap = 0.0
            if tags:
                overlap = len(set(tags) & set(entry.tags))
                tag_overlap = overlap / len(tags)

            similarity = 0.0
            if query:
                hit = similarity_hits.get(entry.memory_id, 0)
                similarity = min(1.0, hit / 5.0)

            # recency: 古い=0.0、最新=1.0 (entriesはtimestamp昇順)
            recency = (position + 1) / total

            score = (
                intent_match * _WEIGHTS["intent_match"]
                + tag_overlap * _WEIGHTS["tag_overlap"]
                + similarity * _WEIGHTS["similarity"]
                + recency * _WEIGHTS["recency"]
            )

            if intent_key is None and not tags and not query:
                # 検索条件が無い場合はrecencyのみで並べる
                score = recency

            scored.append(ScoredMemory(entry=entry, relevance_score=round(min(1.0, score), 4)))

        scored.sort(key=lambda sm: sm.relevance_score, reverse=True)
        return tuple(scored[:top_k])
