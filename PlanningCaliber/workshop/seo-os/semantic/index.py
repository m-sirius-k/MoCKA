"""semantic/index.py — SemanticIndex: トークン→コマンド逆引きインデックス"""
from __future__ import annotations
import re
from collections import defaultdict
from command_index.db import CommandIndexDB
from command_index.registry import CommandRegistry


class SemanticIndex:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()
        self._registry = CommandRegistry(self._db)
        self._index: dict[str, set[str]] = defaultdict(set)
        self._build()

    def _build(self) -> None:
        self._index.clear()
        commands = self._registry.list_all()
        for cmd in commands:
            tokens = self._tokenize(cmd.name + " " + cmd.description)
            tokens += cmd.tags
            tokens += cmd.aliases
            for tok in tokens:
                self._index[tok].add(cmd.id)

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        # ドット記法を分割: seo.analyze → ["seo", "analyze"]
        text = text.replace(".", " ")
        tokens = re.split(r"[\s\-_/]+", text)
        return [t for t in tokens if len(t) >= 2]

    def lookup(self, token: str) -> set[str]:
        return self._index.get(token.lower(), set())

    def lookup_many(self, tokens: list[str]) -> dict[str, int]:
        """トークンリストに対して、コマンドIDとヒット数のマップを返す"""
        scores: dict[str, int] = defaultdict(int)
        for tok in tokens:
            for cmd_id in self.lookup(tok):
                scores[cmd_id] += 1
        return dict(scores)

    def rebuild(self) -> None:
        self._build()
