# -*- coding: utf-8 -*-
"""Inconsistency Detector (Phase 5 Cross-Layer Consistency Engine)

検出対象 (5種):
  - SEMANTIC_VS_DECISION            : semantic_alignment と decision_stability の差分
  - DECISION_VS_MEMORY               : decision_stability と memory_coherence の差分
  - MEMORY_VS_LEARNING_DRIFT          : memory_coherence と learning側状態の不整合
  - REALITY_VS_REPORT_DIVERGENCE      : reality_alignment と report_alignment の差分
  - FEEDBACK_VS_LEARNING_INCONSISTENCY: feedback提案がlearningに反映されていない

しきい値は consistency_registry.MAX_DRIFT_THRESHOLDS を使用する。
判定は UnifiedSnapshot + SubScores のみに基づき、推測を行わない。
"""

from dataclasses import dataclass, field

from cross_layer_consistency.consistency_registry import (
    MAX_DRIFT_THRESHOLDS, INCONSISTENCY_SEVERITY,
)


@dataclass
class Inconsistency:
    inconsistency_type: str
    severity: str
    description: str
    layers_involved: list = field(default_factory=list)
    evidence: dict = field(default_factory=dict)


def detect(snapshot, sub_scores) -> list:
    findings = []

    # --- SEMANTIC_VS_DECISION ---
    diff = abs(sub_scores.semantic_alignment - sub_scores.decision_stability)
    if diff > MAX_DRIFT_THRESHOLDS["decision_vs_semantic"]:
        findings.append(Inconsistency(
            inconsistency_type="SEMANTIC_VS_DECISION",
            severity=INCONSISTENCY_SEVERITY["SEMANTIC_VS_DECISION"],
            description=f"semantic_alignment({sub_scores.semantic_alignment}) と "
                        f"decision_stability({sub_scores.decision_stability}) の差分 {round(diff,4)} が "
                        f"閾値 {MAX_DRIFT_THRESHOLDS['decision_vs_semantic']} を超過",
            layers_involved=["semantic", "decision"],
            evidence={"semantic_alignment": sub_scores.semantic_alignment,
                      "decision_stability": sub_scores.decision_stability, "diff": diff},
        ))

    # --- DECISION_VS_MEMORY ---
    diff = abs(sub_scores.decision_stability - sub_scores.memory_coherence)
    if diff > MAX_DRIFT_THRESHOLDS["decision_vs_semantic"]:
        findings.append(Inconsistency(
            inconsistency_type="DECISION_VS_MEMORY",
            severity=INCONSISTENCY_SEVERITY["DECISION_VS_MEMORY"],
            description=f"decision_stability({sub_scores.decision_stability}) と "
                        f"memory_coherence({sub_scores.memory_coherence}) の差分 {round(diff,4)} が "
                        f"閾値 {MAX_DRIFT_THRESHOLDS['decision_vs_semantic']} を超過",
            layers_involved=["decision", "memory"],
            evidence={"decision_stability": sub_scores.decision_stability,
                      "memory_coherence": sub_scores.memory_coherence, "diff": diff},
        ))

    # --- MEMORY_VS_LEARNING_DRIFT ---
    learning = snapshot.get("learning")
    if learning.status == "OK":
        learning_health = 1.0 if learning.data.get("governance_status") == "PASS" else 0.0
        diff = abs(sub_scores.memory_coherence - learning_health)
        if diff > MAX_DRIFT_THRESHOLDS["memory_vs_learning"]:
            findings.append(Inconsistency(
                inconsistency_type="MEMORY_VS_LEARNING_DRIFT",
                severity=INCONSISTENCY_SEVERITY["MEMORY_VS_LEARNING_DRIFT"],
                description=f"memory_coherence({sub_scores.memory_coherence}) と "
                            f"learning健全性({learning_health}, governance_status="
                            f"{learning.data.get('governance_status')}) の差分 {round(diff,4)} が "
                            f"閾値 {MAX_DRIFT_THRESHOLDS['memory_vs_learning']} を超過",
                layers_involved=["memory", "learning"],
                evidence={"memory_coherence": sub_scores.memory_coherence,
                          "learning_governance_status": learning.data.get("governance_status"),
                          "diff": diff},
            ))
    else:
        findings.append(Inconsistency(
            inconsistency_type="MEMORY_VS_LEARNING_DRIFT",
            severity=INCONSISTENCY_SEVERITY["MEMORY_VS_LEARNING_DRIFT"],
            description="learning layer が UNAVAILABLE のため memory との整合性を確認できない",
            layers_involved=["memory", "learning"],
            evidence={"learning_evidence": learning.evidence},
        ))

    # --- REALITY_VS_REPORT_DIVERGENCE ---
    diff = abs(sub_scores.reality_alignment - sub_scores.report_alignment)
    if diff > MAX_DRIFT_THRESHOLDS["reality_vs_report"]:
        reality = snapshot.get("reality")
        report = snapshot.get("report")
        findings.append(Inconsistency(
            inconsistency_type="REALITY_VS_REPORT_DIVERGENCE",
            severity=INCONSISTENCY_SEVERITY["REALITY_VS_REPORT_DIVERGENCE"],
            description=f"reality_alignment({sub_scores.reality_alignment}) と "
                        f"report_alignment({sub_scores.report_alignment}) の差分 {round(diff,4)} が "
                        f"閾値 {MAX_DRIFT_THRESHOLDS['reality_vs_report']} を超過。"
                        f"Code Realityは概ね健全(FIXED={reality.data.get('fixed')}/{reality.data.get('total')})だが、"
                        f"Report側はConflict={report.data.get('conflict_count')}件と多い "
                        f"(Phase4-3で全件governance PASSとして調停済みではあるが、"
                        f"conflict密度自体がreport_alignmentを下げている)",
            layers_involved=["reality", "report"],
            evidence={"reality_alignment": sub_scores.reality_alignment,
                      "report_alignment": sub_scores.report_alignment, "diff": diff,
                      "broken_files": reality.data.get("broken_files"),
                      "conflict_files": report.data.get("conflict_files")},
        ))

    # --- FEEDBACK_VS_LEARNING_INCONSISTENCY ---
    feedback = snapshot.get("feedback")
    if feedback.status == "OK" and learning.status == "OK":
        proposal_count = feedback.data.get("proposal_count", 0)
        update_count = learning.data.get("update_count", 0)
        if proposal_count > 0 and update_count == 0:
            findings.append(Inconsistency(
                inconsistency_type="FEEDBACK_VS_LEARNING_INCONSISTENCY",
                severity=INCONSISTENCY_SEVERITY["FEEDBACK_VS_LEARNING_INCONSISTENCY"],
                description=f"Feedback Layerが {proposal_count} 件の改善提案を生成したが、"
                            f"Learning Layerでは {update_count} 件しかLearningActionへ変換されていない",
                layers_involved=["feedback", "learning"],
                evidence={"proposal_count": proposal_count, "update_count": update_count,
                          "target_layers": feedback.data.get("target_layers")},
            ))
    elif feedback.status != "OK" or learning.status != "OK":
        findings.append(Inconsistency(
            inconsistency_type="FEEDBACK_VS_LEARNING_INCONSISTENCY",
            severity=INCONSISTENCY_SEVERITY["FEEDBACK_VS_LEARNING_INCONSISTENCY"],
            description="feedback または learning layer が UNAVAILABLE のため整合性を確認できない",
            layers_involved=["feedback", "learning"],
            evidence={"feedback_status": feedback.status, "learning_status": learning.status},
        ))

    return findings


if __name__ == "__main__":
    from cross_layer_consistency.layer_snapshot_builder import build
    from cross_layer_consistency.consistency_score_engine import compute

    snap = build()
    result = compute(snap)
    for f in detect(snap, result.sub_scores):
        print(f)
