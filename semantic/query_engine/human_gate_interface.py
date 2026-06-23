# MoCKA/semantic/query_engine/human_gate_interface.py
# Phase7-B-7 - Human Gate Cognitive Interface v0 (visualization + event log)
#
# 契約: docs/contracts/phase7_b7_human_gate_interface_v1.md
#
# 重要な前提: これはUI実装ではなく、UIが従うべきデータ・状態・イベントの
# 契約のコード化である。状態は常にruling履歴からの導出値であり、直接
# 設定するメソッドは存在しない。CollisionViewは既存データを束ねるだけで
# 新たな判断・推論・要約生成は行わない。
#
# 絶対禁止（契約4章より）:
#   - 状態を直接設定するメソッドの提供
#   - CollisionView内での新たな判断・推論生成
#   - 既存HumanGateRulingStore/GovernedCollisionRecordの変更
#   - イベントの削除・上書き（append-onlyのみ）

from dataclasses import dataclass, field
from typing import Optional, Sequence

from semantic.query_engine.collision_governance import GovernedCollisionRecord
from semantic.query_engine.human_gate import (
    HumanGateRulingStore,
    RulingRecord,
    RULING_ACCEPT,
    RULING_REJECT,
    RULING_DEFER,
    RULING_SPLIT,
)

STATE_PENDING = "pending"
STATE_OBSERVED = "observed"
STATE_DECIDED = "decided"
STATE_CONFLICTED = "conflicted"

_DECIDING_TYPES = (RULING_ACCEPT, RULING_REJECT, RULING_SPLIT)


class CollisionStateTracker:
    """ruling履歴とcollision再検出有無から状態を導出するだけの読み取り層。

    状態を直接設定するメソッドは存在しない（契約1章）。
    """

    def __init__(self, ruling_store: HumanGateRulingStore):
        self._ruling_store = ruling_store

    def state_of(self, collision: GovernedCollisionRecord, re_detected: bool = False) -> str:
        history = self._ruling_store.get_rulings(collision.from_cluster, collision.to_cluster)
        if not history:
            return STATE_PENDING

        has_decision = any(record.ruling_type in _DECIDING_TYPES for record in history)
        if not has_decision:
            return STATE_OBSERVED

        return STATE_CONFLICTED if re_detected else STATE_DECIDED


@dataclass(frozen=True)
class CollisionView:
    """collisionの可視化用・読み取り専用射影(UIが表示する最小情報)。"""

    from_cluster: str
    to_cluster: str
    classification: str
    algorithmic_note: str
    relation_types: Sequence[str]
    sources: Sequence[str]
    state: str
    ruling_history: Sequence[RulingRecord] = field(default_factory=tuple)


def build_collision_view(
    collision: GovernedCollisionRecord,
    state_tracker: CollisionStateTracker,
    ruling_store: HumanGateRulingStore,
    re_detected: bool = False,
) -> CollisionView:
    """既存データを束ねるだけ。新たな判断・推論・要約生成は行わない。"""
    return CollisionView(
        from_cluster=collision.from_cluster,
        to_cluster=collision.to_cluster,
        classification=collision.classification,
        algorithmic_note=collision.algorithmic_note,
        relation_types=collision.relation_types,
        sources=collision.sources,
        state=state_tracker.state_of(collision, re_detected=re_detected),
        ruling_history=ruling_store.get_rulings(collision.from_cluster, collision.to_cluster),
    )


@dataclass(frozen=True)
class RulingEvent:
    from_cluster: str
    to_cluster: str
    ruling_type: str
    rationale: Optional[str]
    recorded_at: Optional[str]
    emitted_at: Optional[str] = None  # システム生成しない。契約3章。


class HumanGateEventLog:
    """submit_rulingの呼び出しをRulingEventとしてappend-onlyで記録する。

    既存HumanGateRulingStoreの内部実装は変更せず、外側からラップする。
    """

    def __init__(self, ruling_store: HumanGateRulingStore):
        self._ruling_store = ruling_store
        self._events: list = []

    def submit_ruling(
        self,
        collision: GovernedCollisionRecord,
        ruling_type: str,
        rationale: Optional[str] = None,
        recorded_at: Optional[str] = None,
        emitted_at: Optional[str] = None,
    ) -> RulingRecord:
        record = self._ruling_store.submit_ruling(
            collision, ruling_type, rationale=rationale, recorded_at=recorded_at
        )
        self._events.append(
            RulingEvent(
                from_cluster=record.from_cluster,
                to_cluster=record.to_cluster,
                ruling_type=record.ruling_type,
                rationale=record.rationale,
                recorded_at=record.recorded_at,
                emitted_at=emitted_at,
            )
        )
        return record

    def history(self) -> Sequence[RulingEvent]:
        return tuple(self._events)
