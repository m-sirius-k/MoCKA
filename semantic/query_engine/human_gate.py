# MoCKA/semantic/query_engine/human_gate.py
# Phase7-B-6 - Human Gate Ruling v0 (institutional design, not resolution)
#
# 契約: docs/contracts/phase7_b6_human_gate_ruling_v1.md
#
# 重要な前提: Human Gateは最適化装置・解決装置・正規化装置ではない。
# 「矛盾の意味的分岐点を固定する装置」である。裁定はGovernedCollisionRecord
# を書き換えるのではなく、別レイヤのRulingRecordとして追加保存される。
#
# 絶対禁止（契約5章より）:
#   - mergeを裁定タイプとして受理すること
#   - collision以外(trace/graph fragment)への直接裁定
#   - 元データ・GovernedCollisionRecordの変更・上書き
#   - RulingRecordの削除・上書き（append-onlyのみ）
#   - 裁定の自動生成・自動推論

from dataclasses import dataclass
from typing import Optional, Sequence

from semantic.query_engine.collision_governance import GovernedCollisionRecord

RULING_ACCEPT = "accept"
RULING_REJECT = "reject"
RULING_DEFER = "defer"
RULING_SPLIT = "split"

VALID_RULING_TYPES = (RULING_ACCEPT, RULING_REJECT, RULING_DEFER, RULING_SPLIT)


@dataclass(frozen=True)
class RulingRecord:
    from_cluster: str
    to_cluster: str
    ruling_type: str
    rationale: Optional[str] = None
    recorded_at: Optional[str] = None


class HumanGateRulingStore:
    """RulingRecordをappend-onlyで保持するストア。

    上書き・削除メソッドは構造的に存在しない。同一collisionに対する
    複数のRulingRecordを時系列で積み重ねることを許容する。
    """

    def __init__(self):
        self._records: list = []

    def submit_ruling(
        self,
        collision: GovernedCollisionRecord,
        ruling_type: str,
        rationale: Optional[str] = None,
        recorded_at: Optional[str] = None,
    ) -> RulingRecord:
        if ruling_type not in VALID_RULING_TYPES:
            raise ValueError(
                f"invalid ruling_type {ruling_type!r}; must be one of {VALID_RULING_TYPES} "
                f"(merge is permanently excluded, see docs/contracts/phase7_b6_human_gate_ruling_v1.md section 1)"
            )

        record = RulingRecord(
            from_cluster=collision.from_cluster,
            to_cluster=collision.to_cluster,
            ruling_type=ruling_type,
            rationale=rationale,
            recorded_at=recorded_at,
        )
        self._records.append(record)
        return record

    def get_rulings(self, from_cluster: str, to_cluster: str) -> Sequence[RulingRecord]:
        return tuple(
            record
            for record in self._records
            if record.from_cluster == from_cluster and record.to_cluster == to_cluster
        )

    def history(self) -> Sequence[RulingRecord]:
        return tuple(self._records)
