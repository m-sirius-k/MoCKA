"""Drift Engine - shared types (DRIFT_ENGINE_v1.md SS5, 6, 7.3)."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DriftType(str, Enum):
    NONE = "NONE"
    MINOR = "MINOR"
    STRUCTURAL = "STRUCTURAL"
    SEMANTIC = "SEMANTIC"
    CONSTRAINT = "CONSTRAINT"
    CRITICAL = "CRITICAL"


@dataclass
class ExpectedState:
    """SS4.1 - reconstructed from the GLK (ExecutablePlan)."""
    expected_nodes: list[str]
    expected_transitions: list[str]          # ordered step_ids
    expected_constraints: list[str]
    expected_outputs: dict[str, str]          # step_id -> expected output value


@dataclass
class ObservedState:
    """SS4.2 - taken from the Observation Ledger entry."""
    observed_nodes: list[str]
    observed_transitions: list[str]
    observed_outputs: dict[str, str]
    constraint_satisfaction_report: dict[str, str]


@dataclass
class DriftVector:
    type: DriftType
    magnitude: float                          # 0.0-1.0
    source_node_id: str | None
    target_node_id: str | None
    description: str


@dataclass
class DriftSummary:
    drift_set: list[DriftVector]
    severity_score: float                     # 0.0 = match, 1.0 = total breakdown
    has_constraint_or_critical: bool = field(init=False)

    def __post_init__(self) -> None:
        self.has_constraint_or_critical = any(
            v.type in (DriftType.CONSTRAINT, DriftType.CRITICAL) for v in self.drift_set
        )
