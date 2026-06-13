"""
MoCKA 3.0 — Feedback Loop
feedback_model.py

責務:
  Feedback Loopが扱うデータモデルを定義する。
  FeedbackProposalは「提案」であり、適用・実行の指示は含まない。
  常に requires_governance_check = True を保持する。
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FeedbackProposal:
    """1件の改善提案(重み調整案/強化提案/構造改善提案など)。"""

    feedback_id: str
    source_audit_id: str
    target_layer: str               # decision / memory / semantic
    issue_reference: str            # 対象issueのcheck名
    suggested_change: dict          # 提案内容(parameter/direction/delta等)
    expected_impact: float          # 0.0 - 1.0
    confidence: float                # 0.0 - 1.0
    risk_level: str                  # SeverityLevel
    requires_governance_check: bool = True
    status: str = "proposed"         # proposed / pending_governance_review / blocked

    def to_dict(self) -> dict:
        return {
            "feedback_id": self.feedback_id,
            "source_audit_id": self.source_audit_id,
            "target_layer": self.target_layer,
            "issue_reference": self.issue_reference,
            "suggested_change": dict(self.suggested_change),
            "expected_impact": self.expected_impact,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "requires_governance_check": self.requires_governance_check,
            "status": self.status,
        }


@dataclass(frozen=True)
class FeedbackBatch:
    """1回のFeedback Pipeline実行結果。"""

    proposals: tuple = field(default_factory=tuple)
    governance_status: str = "UNKNOWN"   # PASS / FAIL / UNKNOWN

    def to_dict(self) -> dict:
        return {
            "proposals": [p.to_dict() for p in self.proposals],
            "governance_status": self.governance_status,
        }
