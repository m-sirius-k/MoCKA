# core/bridge/phi_personal_bridge.py
# MoCKA v1.2.1 — Bridge Layer (core統合版)
# 責務: PHI-OS と Personal Lexicon の共存。意味を統合しない。状態を保つ。

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ConflictInput:
    """外部からBridgeに渡すイベント単位。"""
    term: str
    phi_value: Optional[str]
    personal_value: Optional[str]
    severity: float = 0.5   # 0.0〜1.0


@dataclass
class ConflictRecord:
    """Bridgeが保持する共存状態。意味は変更しない。"""
    term: str
    phi_value: Optional[str]
    personal_value: Optional[str]
    severity: float
    state: str      # NORMAL / DRIFT / CONFLICT

    @property
    def is_conflict(self) -> bool:
        return self.state == "CONFLICT"


class PhiPersonalBridge:
    """
    PHI-OS（制度的意味）と Personal（個人的意味）の共存レイヤ。
    意味を統合しない。両系を並行保持し、状態だけを返す。
    """

    def __init__(self) -> None:
        self._registry: dict[str, ConflictRecord] = {}

    def register(self, event: ConflictInput) -> ConflictRecord:
        """
        イベントをBridgeに登録し、conflict状態を算出して返す。
        PHI-OS / CognitiveCore はこの戻り値を使う。
        """
        state = self._evaluate(event)
        record = ConflictRecord(
            term=event.term,
            phi_value=event.phi_value,
            personal_value=event.personal_value,
            severity=event.severity,
            state=state,
        )
        self._registry[event.term] = record
        return record

    def get(self, term: str) -> Optional[ConflictRecord]:
        return self._registry.get(term)

    def _evaluate(self, event: ConflictInput) -> str:
        if event.phi_value == event.personal_value:
            return "NORMAL"
        if event.severity < 0.4:
            return "DRIFT"
        return "CONFLICT"
