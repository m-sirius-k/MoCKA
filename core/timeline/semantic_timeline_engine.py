# core/timeline/semantic_timeline_engine.py
# MoCKA v1.2.1 — Timeline Layer (単純化版)
# 責務: append_event のみ。唯一の履歴源。
# 設計原則: 書き込みのみ。上書きしない。意味を変更しない。

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class SemanticEvent:
    id: str
    timestamp: str
    term: str
    phi_value: Any
    personal_value: Any
    conflict_state: str
    phi_decision: str

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "timestamp":      self.timestamp,
            "term":           self.term,
            "phi_value":      self.phi_value,
            "personal_value": self.personal_value,
            "conflict_state": self.conflict_state,
            "phi_decision":   self.phi_decision,
        }


class SemanticTimelineEngine:
    """
    唯一の履歴源。append_event のみ提供する。
    読み出しは audit/ や cognitive/ が直接JSONLを読む。
    このクラスは書くだけ。
    """

    DEFAULT_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "logs" / "semantic_timeline.jsonl"

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self._path = storage_path or self.DEFAULT_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def append_event(
        self,
        term: str,
        phi_value: Any,
        personal_value: Any,
        conflict_state: str,
        phi_decision: str,
    ) -> SemanticEvent:
        """イベントを時系列に追記する。上書きしない。"""
        event = SemanticEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            term=term,
            phi_value=phi_value,
            personal_value=personal_value,
            conflict_state=conflict_state,
            phi_decision=phi_decision,
        )
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
        return event

    def load_all(self) -> list[SemanticEvent]:
        """audit / cognitive が読むためのインターフェース。"""
        if not self._path.exists():
            return []
        events: list[SemanticEvent] = []
        with self._path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        d = json.loads(line)
                        events.append(SemanticEvent(**d))
                    except Exception:
                        pass
        return events
