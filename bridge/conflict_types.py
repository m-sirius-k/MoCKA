# bridge/conflict_types.py
# PHI-OS ↔ Personal Lexicon 衝突型定義
# 設計原則: 意味を統一しない。状態を持つ。解決はBridge経由のみ。

from __future__ import annotations
import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ─────────────────────────────────────────────────────────────
# 衝突判定結果
# ─────────────────────────────────────────────────────────────

class ConflictJudgment(str, Enum):
    MATCH         = "MATCH"          # 両系の意味が一致
    SEMANTIC_DRIFT = "SEMANTIC_DRIFT" # 意味にずれがあるが根幹は同一
    FULL_CONFLICT  = "FULL_CONFLICT"  # 意味が相互に矛盾


# ─────────────────────────────────────────────────────────────
# Bridge 内部の状態機械
# ─────────────────────────────────────────────────────────────

class ConflictState(str, Enum):
    NORMAL   = "NORMAL"    # 両系が整合
    DRIFT    = "DRIFT"     # 意味のずれが生じている（要監視）
    CONFLICT = "CONFLICT"  # 完全衝突（解決待ち）
    LOCKED   = "LOCKED"    # 手動ロック（自動操作禁止）


# ─────────────────────────────────────────────────────────────
# 衝突検出結果
# ─────────────────────────────────────────────────────────────

@dataclass
class ConflictResult:
    term: str
    judgment: ConflictJudgment
    state: ConflictState
    phi_os_meaning: Optional[str]
    personal_meaning: Optional[str]
    reason: str
    detected_at: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


# ─────────────────────────────────────────────────────────────
# Bridge レコード（registry に保存される単位）
# ─────────────────────────────────────────────────────────────

@dataclass
class BridgeRecord:
    term: str
    phi_os_meaning: Optional[str]
    personal_meaning: Optional[str]
    state: ConflictState
    last_sync: str
    conflict_reason: str

    def to_dict(self) -> dict:
        return {
            "term":             self.term,
            "phi_os_meaning":   self.phi_os_meaning,
            "personal_meaning": self.personal_meaning,
            "state":            self.state.value,
            "last_sync":        self.last_sync,
            "conflict_reason":  self.conflict_reason,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BridgeRecord":
        return cls(
            term=d["term"],
            phi_os_meaning=d.get("phi_os_meaning"),
            personal_meaning=d.get("personal_meaning"),
            state=ConflictState(d["state"]),
            last_sync=d["last_sync"],
            conflict_reason=d.get("conflict_reason", ""),
        )
