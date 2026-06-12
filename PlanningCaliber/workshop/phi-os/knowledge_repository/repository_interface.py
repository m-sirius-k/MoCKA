"""Knowledge Repository Interface v1

蓄積された知識（イベント・パターン）を保存・検索・進化させるための
共通インターフェース。Learning Engineから evolve() が呼ばれることを想定する。
"""
from __future__ import annotations
from abc import ABC, abstractmethod


class KnowledgeRepository(ABC):
    """全Knowledge Repository実装が満たすべきインターフェース"""

    @abstractmethod
    def store(self, event_id: str, content: dict) -> bool:
        """イベントを知識として保存する"""
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """クエリに関連する知識を検索する"""
        raise NotImplementedError

    @abstractmethod
    def evolve(self, pattern: dict) -> dict:
        """Learning Engineから呼ばれる。知識を進化させる"""
        raise NotImplementedError
