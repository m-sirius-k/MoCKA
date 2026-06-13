"""
MoCKA 3.0 — Self-Learning Kernel
learning_model.py

責務:
  Learning Kernel内で流通するデータモデル定義。
  - LearningAction: FeedbackProposalから変換された「学習アクション案」
  - ValidationResult: Update Validatorによる安全性検証結果
  - LearningUpdate: Queueで管理される、Action+検証結果+statusの組
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass(frozen=True)
class LearningAction:
    action_id: str
    source_feedback_id: str
    target_layer: str
    parameter: str
    delta: float
    current_value: float
    proposed_value: float
    priority: str
    rationale: str

    def to_dict(self) -> dict:
        return {
            "action_id": self.action_id,
            "source_feedback_id": self.source_feedback_id,
            "target_layer": self.target_layer,
            "parameter": self.parameter,
            "delta": self.delta,
            "current_value": self.current_value,
            "proposed_value": self.proposed_value,
            "priority": self.priority,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    checks: Dict[str, bool] = field(default_factory=dict)
    reasons: Tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "checks": dict(self.checks),
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class LearningUpdate:
    update_id: str
    action: LearningAction
    status: str
    validation_result: ValidationResult

    def to_dict(self) -> dict:
        return {
            "update_id": self.update_id,
            "action": self.action.to_dict(),
            "status": self.status,
            "validation_result": self.validation_result.to_dict(),
        }

    @staticmethod
    def from_dict(data: dict) -> "LearningUpdate":
        action_data = data["action"]
        action = LearningAction(**action_data)
        vr_data = data["validation_result"]
        validation_result = ValidationResult(
            passed=vr_data["passed"],
            checks=dict(vr_data.get("checks", {})),
            reasons=tuple(vr_data.get("reasons", ())),
        )
        return LearningUpdate(
            update_id=data["update_id"],
            action=action,
            status=data["status"],
            validation_result=validation_result,
        )
