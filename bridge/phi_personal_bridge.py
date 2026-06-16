# bridge/phi_personal_bridge.py
# PHI-OS ↔ Personal Lexicon Bridge v1 — 共存層
#
# 設計哲学:
#   Bridge は「変換器」ではなく「共存層」。
#   片方を消さない。必ず状態を持つ。解決はBridge経由のみ。

from __future__ import annotations
import datetime
import sys
import os
from typing import Optional

# パス解決: MoCKA ルートを参照できるよう調整
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from bridge.conflict_engine import ConflictEngine
from bridge.conflict_types import BridgeRecord, ConflictState
from bridge.mapping_registry import MappingRegistry


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class PhiPersonalBridge:
    """
    PHI-OS（意味変動系）と Personal Lexicon（固定認知系）の共存レイヤ。

    外部から呼び出せる操作:
      register_mapping(term)   — 新規 term を Bridge に登録
      sync_from_phi_os(...)    — PHI-OS 側の更新を Bridge に反映
      sync_from_personal(...)  — Personal 側の更新を Bridge に反映
      get_dual_view(term)      — 両系の意味と現在状態を返す

    禁止操作:
      - Bridge 経由以外での意味上書き
      - 片方の意味を捨てる操作
      - 状態なしでの保存
    """

    def __init__(
        self,
        registry: Optional[MappingRegistry] = None,
        engine: Optional[ConflictEngine] = None,
    ):
        self.registry = registry or MappingRegistry()
        self.engine = engine or ConflictEngine()

    # ─────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────

    def register_mapping(
        self,
        term: str,
        phi_os_meaning: Optional[str] = None,
        personal_meaning: Optional[str] = None,
    ) -> BridgeRecord:
        """
        term を Bridge に登録する。
        既存レコードが LOCKED の場合は登録を拒否し、既存レコードをそのまま返す。
        """
        existing = self.registry.get(term)
        if existing and existing.state == ConflictState.LOCKED:
            return existing

        result = self.engine.detect(term, phi_os_meaning, personal_meaning)

        record = BridgeRecord(
            term=term,
            phi_os_meaning=phi_os_meaning,
            personal_meaning=personal_meaning,
            state=result.state,
            last_sync=_now(),
            conflict_reason=result.reason,
        )
        self.registry.upsert(record)
        return record

    def sync_from_phi_os(
        self,
        term: str,
        new_phi_meaning: str,
    ) -> BridgeRecord:
        """
        PHI-OS 側の意味更新を受け取り、Bridge レコードを更新する。
        Personal 意味は変更しない。状態を再判定して保存する。
        LOCKED レコードは変更しない。
        """
        existing = self.registry.get(term)

        if existing and existing.state == ConflictState.LOCKED:
            return existing

        personal_meaning = existing.personal_meaning if existing else None

        result = self.engine.detect(term, new_phi_meaning, personal_meaning)

        new_state = (
            self.engine.transition(existing, result.judgment)
            if existing
            else result.state
        )

        record = BridgeRecord(
            term=term,
            phi_os_meaning=new_phi_meaning,
            personal_meaning=personal_meaning,
            state=new_state,
            last_sync=_now(),
            conflict_reason=result.reason,
        )
        self.registry.upsert(record)
        return record

    def sync_from_personal(
        self,
        term: str,
        new_personal_meaning: str,
    ) -> BridgeRecord:
        """
        Personal 側の意味更新を受け取り、Bridge レコードを更新する。
        PHI-OS 意味は変更しない。状態を再判定して保存する。
        LOCKED レコードは変更しない。
        """
        existing = self.registry.get(term)

        if existing and existing.state == ConflictState.LOCKED:
            return existing

        phi_os_meaning = existing.phi_os_meaning if existing else None

        result = self.engine.detect(term, phi_os_meaning, new_personal_meaning)

        new_state = (
            self.engine.transition(existing, result.judgment)
            if existing
            else result.state
        )

        record = BridgeRecord(
            term=term,
            phi_os_meaning=phi_os_meaning,
            personal_meaning=new_personal_meaning,
            state=new_state,
            last_sync=_now(),
            conflict_reason=result.reason,
        )
        self.registry.upsert(record)
        return record

    def get_dual_view(self, term: str) -> dict:
        """
        term の両系ビューを返す。
        未登録の term は None として両フィールドを返す。
        """
        record = self.registry.get(term)
        if record is None:
            return {
                "term":             term,
                "phi_os_meaning":   None,
                "personal_meaning": None,
                "state":            None,
                "last_sync":        None,
                "conflict_reason":  None,
                "registered":       False,
            }
        d = record.to_dict()
        d["registered"] = True
        return d

    # ─────────────────────────────────────────────────────────
    # 管理操作
    # ─────────────────────────────────────────────────────────

    def lock(self, term: str) -> Optional[BridgeRecord]:
        """term を LOCKED 状態にする。存在しない場合は None。"""
        record = self.registry.get(term)
        if record is None:
            return None
        locked = self.engine.lock(record)
        # last_sync を更新してロック記録
        locked = BridgeRecord(
            term=locked.term,
            phi_os_meaning=locked.phi_os_meaning,
            personal_meaning=locked.personal_meaning,
            state=locked.state,
            last_sync=_now(),
            conflict_reason="手動ロック",
        )
        self.registry.upsert(locked)
        return locked

    def unlock(self, term: str) -> Optional[BridgeRecord]:
        """LOCKED を解除し、再判定した状態で保存する。存在しない場合は None。"""
        record = self.registry.get(term)
        if record is None:
            return None
        unlocked = self.engine.unlock(record)
        unlocked = BridgeRecord(
            term=unlocked.term,
            phi_os_meaning=unlocked.phi_os_meaning,
            personal_meaning=unlocked.personal_meaning,
            state=unlocked.state,
            last_sync=_now(),
            conflict_reason=unlocked.conflict_reason,
        )
        self.registry.upsert(unlocked)
        return unlocked

    def list_conflicts(self) -> list[BridgeRecord]:
        """CONFLICT 状態のレコード一覧を返す。"""
        return self.registry.list_by_state(ConflictState.CONFLICT)

    def list_drifts(self) -> list[BridgeRecord]:
        """DRIFT 状態のレコード一覧を返す。"""
        return self.registry.list_by_state(ConflictState.DRIFT)

    def close(self) -> None:
        self.registry.close()
