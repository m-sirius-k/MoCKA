"""
MoCKA 3.0 — Memory Layer
memory_index.py

責務:
  Memory Storeに保存されたMemoryEntry群から検索用インデックスを構築する。

  - intent_index      : metadata["intent_key"] -> memory_idのタプル
  - tag_index         : tag -> memory_idのタプル
  - time_index        : timestamp昇順のmemory_idタプル
  - similarity_index  : 簡易キーワード(token) -> memory_idのタプル
                        (rationale/summary_text等のテキストをトークン化)

  インデックスは検索のための構造のみを提供し、判断(relevance評価)は
  memory_retriever.pyが行う。
"""

import re
from collections import defaultdict

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[^\sA-Za-z0-9_]")


def _tokenize(text: str) -> set:
    if not text:
        return set()
    return {tok.lower() for tok in _TOKEN_PATTERN.findall(text) if len(tok) > 1}


def _entry_text(entry) -> str:
    """類似度インデックス対象のテキストをMemoryEntryから抽出する。"""
    parts = []
    content = entry.content or {}
    for key in ("rationale", "selected_action", "summary_text", "title", "description"):
        value = content.get(key)
        if isinstance(value, str):
            parts.append(value)

    metadata = entry.metadata or {}
    for key in ("intent_key", "phase", "active_task"):
        value = metadata.get(key)
        if isinstance(value, str):
            parts.append(value)

    parts.extend(entry.tags)
    return " ".join(parts)


class MemoryIndex:
    """Memory Storeのスナップショットからインデックスを構築するクラス。"""

    def __init__(self, entries: tuple):
        self._entries = entries
        self.intent_index = defaultdict(list)
        self.tag_index = defaultdict(list)
        self.time_index = []
        self.similarity_index = defaultdict(list)

        self._build()

    def _build(self) -> None:
        ordered = sorted(self._entries, key=lambda e: e.timestamp)

        for entry in ordered:
            self.time_index.append(entry.memory_id)

            intent_key = (entry.metadata or {}).get("intent_key")
            if intent_key:
                self.intent_index[intent_key].append(entry.memory_id)

            for tag in entry.tags:
                self.tag_index[tag].append(entry.memory_id)

            for token in _tokenize(_entry_text(entry)):
                self.similarity_index[token].append(entry.memory_id)

        self.intent_index = {k: tuple(v) for k, v in self.intent_index.items()}
        self.tag_index = {k: tuple(v) for k, v in self.tag_index.items()}
        self.time_index = tuple(self.time_index)
        self.similarity_index = {k: tuple(v) for k, v in self.similarity_index.items()}

    def by_intent(self, intent_key: str) -> tuple:
        return self.intent_index.get(intent_key, ())

    def by_tag(self, tag: str) -> tuple:
        return self.tag_index.get(tag, ())

    def similar_to(self, text: str) -> dict:
        """テキストをトークン化し、トークンごとにヒットしたmemory_idの出現回数を返す。"""
        counts = defaultdict(int)
        for token in _tokenize(text):
            for memory_id in self.similarity_index.get(token, ()):
                counts[memory_id] += 1
        return dict(counts)
