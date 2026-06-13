"""
MoCKA 3.0 — Feedback Loop
feedback_pipeline.py

責務:
  Self-Audit Layer(AuditPipeline)の結果をFeedback Engineに渡し、
  FeedbackProposal群をGovernance Validationの結果と合わせて
  FeedbackBatchとして返す単一窓口。

  処理フロー:
    AuditReport (Self-Audit Layer)
        -> Feedback Engine (Target Classifier含む)
        -> Weight Optimizer / Decision Tuner / Memory Reinforcer / Semantic Adjuster
        -> FeedbackProposal
        -> Governance Validation (読み取り専用)
        -> Approved(pending_governance_review) / Rejected(blocked)

  非破壊原則・逆流禁止:
    本Pipelineは各層を読み取り専用で利用し、いずれのファイル・
    Registry・Storeへも書き込みを行わない。Governance Validationは
    structural/GOVERNANCE_REGRESSION_SUMMARY.md の"Overall PASS"記載を
    確認するのみで、Governance Layerへの変更は行わない。
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SELF_AUDIT_DIR = _ROOT / "self_audit"
_STRUCTURAL_DIR = _ROOT / "structural"

if str(_SELF_AUDIT_DIR) not in sys.path:
    sys.path.insert(0, str(_SELF_AUDIT_DIR))

from audit_pipeline import AuditPipeline  # noqa: E402

from feedback_engine import FeedbackEngine  # noqa: E402
from feedback_model import FeedbackBatch  # noqa: E402


class FeedbackPipeline:
    """Self-Audit -> Feedback Engine -> Governance Validation を統合するPipeline。"""

    def __init__(self, audit_pipeline: AuditPipeline = None, feedback_engine: FeedbackEngine = None):
        self._audit_pipeline = audit_pipeline or AuditPipeline()
        self._feedback_engine = feedback_engine or FeedbackEngine()

    def run(self) -> FeedbackBatch:
        """
        Self-Audit Layerの全層監査を実行し、FeedbackProposal群を生成する。

        Returns:
            FeedbackBatch(proposals, governance_status)
        """
        audit_result = self._audit_pipeline.run_full_audit()

        audit_reports = []
        audit_reports.append(audit_result["semantic"])
        audit_reports.extend(audit_result["decision"])
        audit_reports.append(audit_result["memory"])
        audit_reports.append(audit_result["governance"])

        proposals = self._feedback_engine.generate_many(tuple(audit_reports))

        governance_status = self._governance_validation()
        validated_proposals = tuple(
            self._apply_governance_status(proposal, governance_status)
            for proposal in proposals
        )

        return FeedbackBatch(proposals=validated_proposals, governance_status=governance_status)

    def run_for_report(self, audit_report) -> tuple:
        """単一のAuditReportからFeedbackProposalのtupleを生成する(Governance検証なし)。"""
        return self._feedback_engine.generate(audit_report)

    # ------------------------------------------------------------------
    def _governance_validation(self) -> str:
        """
        structural/GOVERNANCE_REGRESSION_SUMMARY.md を読み取り専用で確認し、
        'Overall PASS' の記載があれば"PASS"、無ければ"FAIL"を返す。
        """
        summary_path = _STRUCTURAL_DIR / "GOVERNANCE_REGRESSION_SUMMARY.md"
        try:
            text = summary_path.read_text(encoding="utf-8")
        except OSError:
            return "UNKNOWN"

        return "PASS" if "Overall PASS" in text else "FAIL"

    @staticmethod
    def _apply_governance_status(proposal, governance_status: str):
        """
        governance_statusに応じてFeedbackProposal.statusを更新した
        新たなFeedbackProposalを返す(元のオブジェクトは変更しない)。

        PASS -> "pending_governance_review" (人間/上位プロセスによる
                レビュー待ち。自動適用はしない)
        FAIL/UNKNOWN -> "blocked" (Governance Regressionが健全でないため、
                Feedback適用検討自体を保留する)
        """
        from dataclasses import replace

        status = "pending_governance_review" if governance_status == "PASS" else "blocked"
        return replace(proposal, status=status)
