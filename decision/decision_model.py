"""
MoCKA 3.0 — Decision Layer
decision_model.py

責務:
  Decision Layerの出力形式を統一する。

  DecisionResultは「中間意思決定の結果」であり、実行そのものは
  行わない(Decision Layerは非破壊)。最終的な実行可否は
  Governance Layer(GL1-7)に委ねるため、常に
  `required_governance_check = True` を保持する。

M3 Integration Phase:
  - authority_context: Authority Context flowing through pipeline
  - authority_binding: Immutable snapshot of authority at T_decision
  - Both optional for backward compatibility
  - Enforcement at Executor boundary (STEP 4)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


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
    """Decision Layerの統一出力形式。

    M3 Integration: Includes optional authority_context and authority_binding.
    - authority_context: Authority Context flowing through pipeline
    - authority_binding: Immutable snapshot of authority at T_decision

    Separation of concerns:
    - Code: selected_action (what the decision recommends)
    - Authorization: authority_context (who is authorized)
    - Evidence: authority_binding (proof of authorization at decision time)
    - Decision: required_governance_check (execution requires approval)
    """

    selected_action: str
    alternatives: tuple                # tuple[Alternative]
    priority_score: float              # 0.0 - 1.0
    risk_score: float                  # 0.0 - 1.0
    confidence: float                  # 0.0 - 1.0 (SemanticResultのconfidenceを継承)
    rationale: str
    required_governance_check: bool = True
    risk_factors: tuple = field(default_factory=tuple)

    # M3 Authority Integration
    authority_context: Optional[Dict[str, Any]] = None      # Authority Context instance
    authority_binding: Optional[Dict[str, Any]] = None      # Immutable snapshot at T_decision

    def to_dict(self) -> dict:
        result = {
            "selected_action": self.selected_action,
            "alternatives": [a.to_dict() for a in self.alternatives],
            "priority_score": self.priority_score,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "required_governance_check": self.required_governance_check,
            "risk_factors": list(self.risk_factors),
        }

        # Include authority fields if present
        if self.authority_context is not None:
            result["authority_context"] = self.authority_context
        if self.authority_binding is not None:
            result["authority_binding"] = self.authority_binding

        return result

    def has_authority_context(self) -> bool:
        """Check if authority context is present and verified."""
        if self.authority_context is None:
            return False
        # Check if verification state is VERIFIED
        verification_state = self.authority_context.get("verification_state")
        return verification_state == "VERIFIED"

    def get_authority_binding_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get immutable authority snapshot at decision time."""
        return self.authority_binding
