"""
MoCKA 3.0 — Decision Layer
decision_model.py

責務:
  Decision Layerの出力形式を統一する。

  DecisionResultは「中間意思決定の結果」であり、実行そのものは
  行わない(Decision Layerは非破壊)。最終的な実行可否は
  Governance Layer(GL1-7)に委ねるため、常に
  `required_governance_check = True` を保持する。
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Alternative:
    """selected_action以外の実行候補。"""

    action: str
    priority_score: float
    risk_score: float

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "priority_score": self.priority_score,
            "risk_score": self.risk_score,
        }


@dataclass(frozen=True)
class DecisionResult:
    """Decision Layerの統一出力形式。"""

    selected_action: str
    alternatives: tuple                # tuple[Alternative]
    priority_score: float              # 0.0 - 1.0
    risk_score: float                  # 0.0 - 1.0
    confidence: float                  # 0.0 - 1.0 (SemanticResultのconfidenceを継承)
    rationale: str
    required_governance_check: bool = True
    risk_factors: tuple = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "selected_action": self.selected_action,
            "alternatives": [a.to_dict() for a in self.alternatives],
            "priority_score": self.priority_score,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "required_governance_check": self.required_governance_check,
            "risk_factors": list(self.risk_factors),
        }
