"""
MoCKA 3.0 — Self-Audit Layer
audit_model.py

責務:
  Self-Auditが扱うデータモデルを定義する。
  AuditReportは「評価結果」のみを表し、実行・修正の指示は含まない。
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Issue:
    """検出された問題点。"""

    check: str
    description: str
    severity: str

    def to_dict(self) -> dict:
        return {
            "check": self.check,
            "description": self.description,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class ImprovementSuggestion:
    """改善提案(非実行)。"""

    suggestion_id: str
    target_type: str
    target_id: str
    description: str
    related_check: str
    improvement_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "suggestion_id": self.suggestion_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "description": self.description,
            "related_check": self.related_check,
            "improvement_score": self.improvement_score,
        }


@dataclass(frozen=True)
class PrioritizedAction:
    """改善提案に優先度を付与したもの。"""

    suggestion: ImprovementSuggestion
    improvement_score: float
    rationale: str

    def to_dict(self) -> dict:
        return {
            "suggestion": self.suggestion.to_dict(),
            "improvement_score": self.improvement_score,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class AuditReport:
    """1つの対象(target_type/target_id)に対する監査結果。"""

    audit_id: str
    target_type: str
    target_id: str
    evaluation_score: float
    issue_list: tuple = field(default_factory=tuple)
    strength_list: tuple = field(default_factory=tuple)
    improvement_suggestions: tuple = field(default_factory=tuple)
    severity_level: str = "info"

    def to_dict(self) -> dict:
        return {
            "audit_id": self.audit_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "evaluation_score": self.evaluation_score,
            "issue_list": [issue.to_dict() if isinstance(issue, Issue) else issue
                           for issue in self.issue_list],
            "strength_list": list(self.strength_list),
            "improvement_suggestions": [
                s.to_dict() if isinstance(s, ImprovementSuggestion) else s
                for s in self.improvement_suggestions
            ],
            "severity_level": self.severity_level,
        }
