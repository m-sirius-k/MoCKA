"""AI Adapter Interface v1

全AI Adapter（OpenAI / Anthropic / Google / 将来AI）が実装すべき
共通インターフェース。

Institution Contract → Handshake Protocol → AI Adapter Layer → ISE
の構造において、このインターフェースが「差し替え可能な境界」を定義する。
"""
from __future__ import annotations
from abc import ABC, abstractmethod


class AIAdapter(ABC):
    """全AI Adapterが実装すべきインターフェース"""

    @abstractmethod
    def handshake(self, scope: str) -> dict:
        """Handshake Protocolを実行し、能力を宣言する"""
        raise NotImplementedError

    @abstractmethod
    def receive_commission(self, commission: dict) -> bool:
        """Institutionからの委任状を受け取る"""
        raise NotImplementedError

    @abstractmethod
    def execute(self, commission: dict) -> dict:
        """委任内容を実行し、結果を返す"""
        raise NotImplementedError

    @abstractmethod
    def ack(self, result: dict) -> dict:
        """実行結果をACKとして返す"""
        raise NotImplementedError
