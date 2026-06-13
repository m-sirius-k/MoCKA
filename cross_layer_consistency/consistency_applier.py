# -*- coding: utf-8 -*-
"""Consistency Applier (Phase 5 Cross-Layer Consistency Engine)

適用条件 (consistency_registry.APPLIER_CONDITIONS, 全て満たす必要あり):
  - governance approved        : QueueItem.status == "validated"
  - stability score threshold  : consistency_score >= 0.7
  - risk delta <= 0.05          : クラスタ内 inconsistency の diff (evidence['diff']) の
                                    最大値 <= 0.05

このモジュールは「適用可否の判定」のみを行う。実際のレイヤー状態変更は
行わない(immediate_apply_allowed=False, local_layer_fix_allowed=False)。
適用可と判定されたQueueItemは status="applied" に遷移するが、これは
「Queueにおける適用判定が完了した」ことを示すのみで、各レイヤーの実装への
書き込みは別工程(本Phaseのスコープ外)とする。
"""

from dataclasses import dataclass

from cross_layer_consistency.consistency_registry import APPLIER_CONDITIONS, OVERRIDE_POLICIES


@dataclass
class ApplyResult:
    item_id: str
    applied: bool
    reason: str


def _max_risk_delta(item) -> float:
    """strategyのcluster内inconsistencyに記録されたdiff(evidence['diff'])の最大値。
    diffが存在しないevidenceは0.0として扱う。
    """
    cluster_incs = getattr(item, "_cluster_inconsistencies", None)
    if not cluster_incs:
        return 0.0
    diffs = [inc.evidence.get("diff", 0.0) for inc in cluster_incs if "diff" in inc.evidence]
    return max(diffs) if diffs else 0.0


def apply(item, consistency_score: float, cluster_inconsistencies: list) -> ApplyResult:
    """QueueItemに対して適用判定を行い、ApplyResultを返す。
    item.status は本関数の結果に応じて更新される ("applied" / 変更なし)。
    """
    if OVERRIDE_POLICIES["immediate_apply_allowed"]:
        # この分岐には到達しない設計(常にFalse)。安全側のガード。
        return ApplyResult(item_id=item.item_id, applied=False,
                            reason="immediate_apply_allowed=False のため即時適用は常に禁止")

    if item.status != "validated":
        return ApplyResult(item_id=item.item_id, applied=False,
                            reason=f"governance未承認 (status={item.status})")

    threshold = APPLIER_CONDITIONS["stability_score_threshold"]
    if consistency_score < threshold:
        return ApplyResult(item_id=item.item_id, applied=False,
                            reason=f"consistency_score({consistency_score}) < threshold({threshold})")

    max_diff = 0.0
    for inc in cluster_inconsistencies:
        max_diff = max(max_diff, inc.evidence.get("diff", 0.0))

    max_risk_delta = APPLIER_CONDITIONS["max_risk_delta"]
    if max_diff > max_risk_delta:
        return ApplyResult(item_id=item.item_id, applied=False,
                            reason=f"risk_delta({round(max_diff,4)}) > max_risk_delta({max_risk_delta})")

    item.status = "applied"
    return ApplyResult(item_id=item.item_id, applied=True,
                        reason="governance承認済み・consistency_score基準満たす・risk_delta基準内")


if __name__ == "__main__":
    from cross_layer_consistency.layer_snapshot_builder import build
    from cross_layer_consistency.consistency_score_engine import compute
    from cross_layer_consistency.inconsistency_detector import detect
    from cross_layer_consistency.conflict_clusterer import cluster
    from cross_layer_consistency.resolution_strategy_engine import propose
    from cross_layer_consistency.consistency_queue import ConsistencyQueue

    snap = build()
    result = compute(snap)
    incs = detect(snap, result.sub_scores)
    clusters = cluster(incs)
    strategies = propose(clusters)

    incs_by_cluster = {c.cluster_id: c.inconsistencies for c in clusters}
    impact_by_cluster = {c.cluster_id: c.impact_radius for c in clusters}

    q = ConsistencyQueue()
    for s in strategies:
        item = q.enqueue(s, impact_by_cluster.get(s.cluster_id, 0))
        q.validate(item, snap.get("report"))

    for item in q.ordered_items():
        cluster_incs = incs_by_cluster.get(item.cluster_id, [])
        r = apply(item, result.total_score, cluster_incs)
        print(r)
