"""Observation Layer interface (GLK_RUNTIME_BRIDGE_v1.md SS6).

Records execution results as structured, immutable snapshots.
Observation does not evaluate.
"""
from __future__ import annotations

from mocka3.glk_runtime_bridge.types import (
    ExecutionContext,
    ExecutionResult,
    InputSnapshot,
    ObservationRecord,
    OutputSnapshot,
    StateTransition,
)


def emit_observation(context: ExecutionContext, result: ExecutionResult) -> ObservationRecord:
    transitions = [
        StateTransition(step_id=entry.split(":", 1)[1], description=entry)
        for entry in result.state_transition_log
    ]
    return ObservationRecord(
        execution_id=result.execution_id,
        input_snapshot=InputSnapshot(state=dict(context.input_state)),
        output_snapshot=OutputSnapshot(state=dict(result.output_state)),
        state_transition_log=transitions,
        constraint_satisfaction_report=dict(result.constraint_satisfaction_report),
    )
