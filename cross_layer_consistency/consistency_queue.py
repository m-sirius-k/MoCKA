# -*- coding: utf-8 -*-
"""Consistency Queue (Phase 5 Cross-Layer Consistency Engine)

特徴:
  - 非即時適用 (enqueueのみ。applyは別途consistency_applierが行う)
  - priority ordering (cluster.impact_radius降順 -> ResolutionStrategy提案順)
  - governance check必須 (validate()でgovernance_statusを必ず確認する)

状態: pending / validated / rejected / applied / deferred
(consistency_registry.QUEUE_STATES)
"""

from dataclasses import dataclass, field
from itertools import count

from cross_layer_consistency.consistency_registry import QUEUE_STATES, SUPPRESSION_RULES

_id_counter = count(1)


@dataclass
class QueueItem:
    item_id: str
    cluster_id: str
    strategy: object   # ResolutionStrategy
    status: str = "pending"
    governance_status: str = "UNCHECKED"


class ConsistencyQueue:
    def __init__(self):
        self._items: list = []

    def enqueue(self, strategy, cluster_impact_radius: int) -> QueueItem:
        item = QueueItem(
            item_id=f"CQ_{next(_id_counter):04d}",
            cluster_id=strategy.cluster_id,
            strategy=strategy,
            status="pending",
        )
        self._items.append((cluster_impact_radius, item))
        return item

    def ordered_items(self) -> list:
        """impact_radius降順でソートしたQueueItemを返す(priority ordering)。"""
        return [item for _, item in sorted(self._items, key=lambda x: -x[0])]

    def validate(self, item: QueueItem, report_layer_snapshot) -> QueueItem:
        """governance check必須。report_truth_governanceのgovernance_fail_countを参照する。

        - SUPPRESSION_RULESに該当するstrategy_type(layer_suppression)は常にdeferred
        - report layer governance_fail_count > 0 の場合は rejected
          (governance未承認状態でのQueue進行を禁止)
        - それ以外は validated
        """
        if item.strategy.strategy_type == "layer_suppression":
            item.status = SUPPRESSION_RULES.get("LEARNING_UNBOUNDED_UPDATE", "deferred")
            item.governance_status = "SUPPRESSED"
            return item

        if report_layer_snapshot.status != "OK":
            item.status = "rejected"
            item.governance_status = "NO_EVIDENCE"
            return item

        fail_count = report_layer_snapshot.data.get("governance_fail_count", 0)
        if fail_count > 0:
            item.status = "rejected"
            item.governance_status = "FAIL"
            return item

        item.status = "validated"
        item.governance_status = "PASS"
        return item

    def all_items(self) -> list:
        return [item for _, item in self._items]

    def by_status(self, status: str) -> list:
        assert status in QUEUE_STATES
        return [item for item in self.all_items() if item.status == status]


if __name__ == "__main__":
    from cross_layer_consistency.layer_snapshot_builder import build
    from cross_layer_consistency.consistency_score_engine import compute
    from cross_layer_consistency.inconsistency_detector import detect
    from cross_layer_consistency.conflict_clusterer import cluster
    from cross_layer_consistency.resolution_strategy_engine import propose

    snap = build()
    result = compute(snap)
    incs = detect(snap, result.sub_scores)
    clusters = cluster(incs)
    strategies = propose(clusters)

    impact_by_cluster = {c.cluster_id: c.impact_radius for c in clusters}

    q = ConsistencyQueue()
    for s in strategies:
        item = q.enqueue(s, impact_by_cluster.get(s.cluster_id, 0))
        q.validate(item, snap.get("report"))

    for item in q.ordered_items():
        print(item.item_id, item.cluster_id, item.strategy.strategy_type, item.status, item.governance_status)
