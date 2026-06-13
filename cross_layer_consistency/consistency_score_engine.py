# -*- coding: utf-8 -*-
"""Consistency Score Engine (Phase 5 Cross-Layer Consistency Engine)

ConsistencyScore =
    semantic_alignment * 0.20 +
    decision_stability * 0.20 +
    memory_coherence   * 0.15 +
    audit_agreement    * 0.15 +
    reality_alignment  * 0.20 +
    report_alignment   * 0.10

各サブスコアは UnifiedSnapshot から機械的に算出する(推測値なし)。
layerがUNAVAILABLEの場合、そのサブスコアは0.0として扱う
(証拠なし=安全側に倒す。Phase4-2/4-3のNO_EVIDENCE方針を継承)。
"""

from dataclasses import dataclass

from cross_layer_consistency.consistency_registry import SCORE_WEIGHTS


@dataclass
class SubScores:
    semantic_alignment: float
    decision_stability: float
    memory_coherence: float
    audit_agreement: float
    reality_alignment: float
    report_alignment: float


@dataclass
class ConsistencyScoreResult:
    sub_scores: SubScores
    total_score: float
    breakdown: dict


def _safe(layer_snapshot, fn, default=0.0):
    if layer_snapshot.status != "OK":
        return default
    try:
        return fn(layer_snapshot.data)
    except (KeyError, ZeroDivisionError, TypeError):
        return default


def compute(snapshot) -> ConsistencyScoreResult:
    semantic = snapshot.get("semantic")
    decision = snapshot.get("decision")
    memory = snapshot.get("memory")
    self_audit = snapshot.get("self_audit")
    reality = snapshot.get("reality")
    report = snapshot.get("report")

    semantic_alignment = _safe(semantic, lambda d: d["evaluation_score"])
    decision_stability = _safe(decision, lambda d: d["avg_score"])
    memory_coherence = _safe(memory, lambda d: d["evaluation_score"])
    audit_agreement = _safe(self_audit, lambda d: d["governance_score"])
    reality_alignment = _safe(reality, lambda d: d["fixed"] / d["total"])
    report_alignment = _safe(report, lambda d: (d["total"] - d["conflict_count"]) / d["total"])

    sub_scores = SubScores(
        semantic_alignment=semantic_alignment,
        decision_stability=decision_stability,
        memory_coherence=memory_coherence,
        audit_agreement=audit_agreement,
        reality_alignment=reality_alignment,
        report_alignment=report_alignment,
    )

    breakdown = {}
    total = 0.0
    for key, weight in SCORE_WEIGHTS.items():
        value = getattr(sub_scores, key)
        contribution = value * weight
        breakdown[key] = {"value": round(value, 4), "weight": weight, "contribution": round(contribution, 4)}
        total += contribution

    return ConsistencyScoreResult(sub_scores=sub_scores, total_score=round(total, 4), breakdown=breakdown)


if __name__ == "__main__":
    from cross_layer_consistency.layer_snapshot_builder import build

    snap = build()
    result = compute(snap)
    for k, v in result.breakdown.items():
        print(f"{k:<20} value={v['value']:<8} weight={v['weight']:<6} contribution={v['contribution']}")
    print("TOTAL CONSISTENCY SCORE:", result.total_score)
