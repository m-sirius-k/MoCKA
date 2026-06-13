# -*- coding: utf-8 -*-
"""Consistency Registry (Phase 5 Cross-Layer Consistency Engine)

layer priority rules / allowed correction scope / max drift thresholds /
suppression rules / override policies を一元管理する。
"""

# --- Layer Priority (Arbitration時の優先順位。数字が小さいほど優先) -----------
# Phase 4-3 の "Code Evidence > Reality Sync > Test > Report Claim" を継承し、
# 全8層に拡張する。
LAYER_PRIORITY = {
    "reality": 1,      # Code Truth (reality_sync)
    "report": 2,       # Report Truth (report_truth_governance)
    "decision": 3,
    "memory": 4,
    "self_audit": 5,
    "feedback": 6,
    "learning": 7,
    "semantic": 8,
}

# --- Consistency Score 重み (合計1.0) -----------------------------------------
SCORE_WEIGHTS = {
    "semantic_alignment": 0.20,
    "decision_stability": 0.20,
    "memory_coherence": 0.15,
    "audit_agreement": 0.15,
    "reality_alignment": 0.20,
    "report_alignment": 0.10,
}

assert abs(sum(SCORE_WEIGHTS.values()) - 1.0) < 1e-9

# --- Drift Thresholds ----------------------------------------------------------
MAX_DRIFT_THRESHOLDS = {
    "memory_vs_learning": 0.30,   # memory_coherence と learning側スコアの差の許容上限
    "reality_vs_report": 0.30,    # reality_alignment と report_alignment の差の許容上限
    "decision_vs_semantic": 0.30,
}

# --- Applier Conditions (Consistency Applier がQueueから実行可能と判定する条件) --
APPLIER_CONDITIONS = {
    "governance_status_required": "PASS",
    "stability_score_threshold": 0.7,   # consistency_score >= 0.7
    "max_risk_delta": 0.05,
}

# --- Suppression Rules ----------------------------------------------------------
# 該当する inconsistency_type は Applier に到達させず、Queue上で
# "deferred" に固定する(即時抑制対象)。
SUPPRESSION_RULES = {
    "LEARNING_UNBOUNDED_UPDATE": "deferred",   # learning無制限更新は常にdeferred
}

# --- Override Policies ----------------------------------------------------------
OVERRIDE_POLICIES = {
    "truth_override_allowed": False,     # reality_syncのtruth_stateは上書き禁止
    "report_priority_allowed": False,    # reportを優先する判定は禁止
    "local_layer_fix_allowed": False,    # 単一レイヤーのみの修正は禁止(全体整合性経由のみ)
    "immediate_apply_allowed": False,    # 即時反映禁止(Queue必須)
}

# --- Inconsistency Type -> default severity ------------------------------------
INCONSISTENCY_SEVERITY = {
    "SEMANTIC_VS_DECISION": "MEDIUM",
    "DECISION_VS_MEMORY": "MEDIUM",
    "MEMORY_VS_LEARNING_DRIFT": "HIGH",
    "REALITY_VS_REPORT_DIVERGENCE": "CRITICAL",
    "FEEDBACK_VS_LEARNING_INCONSISTENCY": "HIGH",
}

# --- Queue States ----------------------------------------------------------------
QUEUE_STATES = ("pending", "validated", "rejected", "applied", "deferred")
