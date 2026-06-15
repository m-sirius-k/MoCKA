"""Policy Contract.

Reference: docs/governance/MODULE_POLICY_ENGINE_v1.md
Defines the Policy Evaluation record (Section 4) and Evaluation
Results enum (Section 5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

CONTRACT_VERSION = "1.0.0"

POLICY_CATEGORIES = (
    "Governance Policy",
    "Security Policy",
    "Dependency Policy",
    "Lifecycle Policy",
    "Certification Policy",
    "Health Policy",
    "Documentation Policy",
)


class PolicyResult(str, Enum):
    """MODULE_POLICY_ENGINE_v1 Section 5."""

    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class PolicyEvaluation:
    """MODULE_POLICY_ENGINE_v1 Section 4: Policy Evaluation record."""

    policy_id: str
    category: str
    target_module: str
    evaluation_criteria: str
    result: PolicyResult
    evidence: Mapping[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("PolicyEvaluation.policy_id is required")
        if self.category not in POLICY_CATEGORIES:
            raise ValueError(f"Unknown Policy Category: {self.category!r}")
        if not self.target_module:
            raise ValueError("PolicyEvaluation.target_module is required")
        if not self.evaluation_criteria:
            raise ValueError("PolicyEvaluation.evaluation_criteria is required")
        if not isinstance(self.result, PolicyResult):
            raise ValueError("PolicyEvaluation.result must be a PolicyResult")
        if not self.timestamp:
            raise ValueError("PolicyEvaluation.timestamp is required (ISO8601)")
