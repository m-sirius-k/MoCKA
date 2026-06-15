"""GLK Runtime Bridge - shared types (GLK_RUNTIME_BRIDGE_v1.md Phase1)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExecutableStep:
    step_id: str
    description: str
    guard: list[str] = field(default_factory=list)  # constraint refs (4.1 制約条件 -> 実行ガード)


@dataclass
class ExecutablePlan:
    plan_id: str
    source_blueprint_id: str
    steps: list[ExecutableStep]
    constraint_refs: list[str]


@dataclass
class ExecutionContext:
    context_id: str
    plan_id: str
    input_state: dict
    runtime_variables: dict
    constraint_set: list[str]
    execution_scope: str
    dependency_graph: dict


@dataclass
class ExecutionResult:
    execution_id: str
    plan_id: str
    output_state: dict
    state_transition_log: list[str]
    constraint_satisfaction_report: dict


@dataclass
class InputSnapshot:
    state: dict


@dataclass
class OutputSnapshot:
    state: dict


@dataclass
class StateTransition:
    step_id: str
    description: str


@dataclass
class ObservationRecord:
    execution_id: str
    input_snapshot: InputSnapshot
    output_snapshot: OutputSnapshot
    state_transition_log: list[StateTransition]
    constraint_satisfaction_report: dict
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ObservationLedgerEntry:
    """Immutable record: GLK -> EXECUTION_START -> EXECUTION_END -> OBSERVATION_EMIT chain."""
    execution_id: str
    glk_id: str
    input_snapshot: InputSnapshot
    output_snapshot: OutputSnapshot
    state_transition: list[StateTransition]
    constraint_satisfaction_report: dict
    event_ref: list[str]
    timestamp: datetime = field(default_factory=datetime.now)
