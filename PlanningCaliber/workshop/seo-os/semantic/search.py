"""semantic/search.py — MeaningSearch: 意味検索エンジン"""
from __future__ import annotations
from dataclasses import dataclass

from command_index.db import CommandIndexDB
from command_index.registry import CommandRegistry
from command_index.metadata import CommandMetadata
from .synonym import SynonymDictionary
from .index import SemanticIndex
from .intent import IntentResolver


@dataclass
class SearchResult:
    command: CommandMetadata
    score: float
    matched_tokens: list[str]
    intent: str

    def to_dict(self) -> dict:
        return {
            "command": self.command.to_dict(),
            "score": round(self.score, 3),
            "matched_tokens": self.matched_tokens,
            "intent": self.intent,
        }


class MeaningSearch:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()
        self._registry = CommandRegistry(self._db)
        self._synonyms = SynonymDictionary(self._db)
        self._index = SemanticIndex(self._db)
        self._intent = IntentResolver()

    def search(self, query: str, limit: int = 10,
               category: str | None = None) -> list[SearchResult]:
        if not query.strip():
            return []

        intent = self._intent.resolve(query)
        intent_category = self._intent.intent_to_category(intent)

        # クエリ展開: 同義語追加
        tokens_raw = query.lower().replace(".", " ").split()
        tokens_expanded = self._synonyms.expand(tokens_raw)

        # セマンティックインデックス検索
        scores = self._index.lookup_many(tokens_expanded)

        # 直接テキスト検索のブースト
        text_results = self._registry.search(query)
        for cmd in text_results:
            scores[cmd.id] = scores.get(cmd.id, 0) + 2

        # インテントカテゴリのブースト
        if intent_category:
            cat_cmds = self._registry.list_all(category=intent_category)
            for cmd in cat_cmds:
                scores[cmd.id] = scores.get(cmd.id, 0) + 1

        # カテゴリフィルタ
        if category:
            cat_ids = {c.id for c in self._registry.list_all(category=category)}
            scores = {k: v for k, v in scores.items() if k in cat_ids}

        if not scores:
            return []

        # スコア正規化
        max_score = max(scores.values())
        results = []
        for cmd_id, raw_score in sorted(scores.items(), key=lambda x: -x[1])[:limit]:
            cmd = self._registry.get(cmd_id)
            if cmd is None:
                continue
            matched = [t for t in tokens_expanded
                       if t in cmd.name.lower() or t in cmd.description.lower()
                       or t in cmd.tags]
            results.append(SearchResult(
                command=cmd,
                score=raw_score / max_score,
                matched_tokens=matched[:5],
                intent=intent,
            ))
        return results
