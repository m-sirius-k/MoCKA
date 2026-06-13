"""
MoCKA 3.0 — Feedback Loop
feedback_engine.py

責務:
  AuditReportを入力として、issueごとにtarget_layerを分類し、
  WeightOptimizer / DecisionTuner / MemoryReinforcer / SemanticAdjuster
  に処理を委譲してFeedbackProposalを生成する。

  非破壊原則:
    本モジュールはFeedbackProposal(提案)を生成するのみであり、
    Decision/Memory/Semantic/Governanceのいずれにも書き込みを行わない。
    Governance Layerのissue(check)はfeedback_registry.is_feedback_target()
    によりFeedback対象外として除外される(逆流禁止)。
"""

from decision_tuner import DecisionTuner
from feedback_model import FeedbackProposal
from feedback_registry import (
    TargetLayer,
    confidence_for_severity,
    get_classification,
    is_feedback_target,
    priority_for_feedback_type,
)
from memory_reinforcer import MemoryReinforcer
from semantic_adjuster import SemanticAdjuster
from weight_optimizer import WeightOptimizer


class FeedbackEngine:
    """AuditReportからFeedbackProposalのtupleを生成するEngine。"""

    def __init__(self, weight_optimizer: WeightOptimizer = None,
                 decision_tuner: DecisionTuner = None,
                 memory_reinforcer: MemoryReinforcer = None,
                 semantic_adjuster: SemanticAdjuster = None):
        self._weight_optimizer = weight_optimizer or WeightOptimizer()
        self._decision_tuner = decision_tuner or DecisionTuner()
        self._memory_reinforcer = memory_reinforcer or MemoryReinforcer()
        self._semantic_adjuster = semantic_adjuster or SemanticAdjuster()
        self._counter = 0

    def generate(self, audit_report) -> tuple:
        """
        AuditReportのissue_listからFeedbackProposalのtupleを生成する。

        Governance LayerのAuditReport(target_type="governance")、または
        分類ルールに存在しないcheckのissueはFeedback対象外として
        スキップする(逆流禁止)。
        """
        if not is_feedback_target(audit_report.target_type):
            return ()

        proposals = []
        for issue in audit_report.issue_list:
            classification = get_classification(issue.check)
            if classification is None:
                continue

            target_layer, feedback_type = classification
            suggested_change = self._build_suggested_change(target_layer, issue)

            confidence = confidence_for_severity(issue.severity)
            priority = priority_for_feedback_type(feedback_type)
            expected_impact = round(min(1.0, confidence * priority * 1.4), 4)

            self._counter += 1
            proposals.append(FeedbackProposal(
                feedback_id=f"FEEDBACK_{audit_report.audit_id}_{self._counter:03d}",
                source_audit_id=audit_report.audit_id,
                target_layer=target_layer,
                issue_reference=issue.check,
                suggested_change=suggested_change,
                expected_impact=expected_impact,
                confidence=confidence,
                risk_level=issue.severity,
                requires_governance_check=True,
                status="proposed",
            ))

        return tuple(proposals)

    def generate_many(self, audit_reports: tuple) -> tuple:
        """複数のAuditReportからFeedbackProposalのtupleをまとめて生成する。"""
        proposals = []
        for report in audit_reports:
            proposals.extend(self.generate(report))
        return tuple(proposals)

    # ------------------------------------------------------------------
    def _build_suggested_change(self, target_layer: str, issue) -> dict:
        """target_layerに応じてOptimizer/Tuner/Reinforcer/Adjusterへ委譲する。"""
        if target_layer == TargetLayer.DECISION:
            return {
                "weight_adjustment": self._weight_optimizer.decision_weight_adjustment(issue),
                "tuning": self._decision_tuner.propose(issue),
            }

        if target_layer == TargetLayer.MEMORY:
            return {
                "weight_adjustment": self._weight_optimizer.memory_weight_adjustment(issue),
                "reinforcement": self._memory_reinforcer.propose(issue),
            }

        if target_layer == TargetLayer.SEMANTIC:
            return {
                "weight_adjustment": self._weight_optimizer.semantic_threshold_adjustment(issue),
                "adjustment": self._semantic_adjuster.propose(issue),
            }

        return {}
