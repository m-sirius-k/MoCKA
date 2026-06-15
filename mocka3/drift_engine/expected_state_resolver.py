"""Expected State Resolver (DRIFT_ENGINE_v1.md SS6).

GLK (ExecutablePlan) -> ExpectedState, normalized to the same schema
as ObservedState (SS6.2 constraint).
"""
from __future__ import annotations

from mocka3.glk_runtime_bridge.types import ExecutablePlan
from mocka3.drift_engine.types import ExpectedState


def resolve_expected_state(plan: ExecutablePlan) -> ExpectedState:
    expected_nodes = [step.step_id for step in plan.steps]
    expected_transitions = list(expected_nodes)  # SS6.1: Execution Path prediction = step order
    expected_outputs = {step.step_id: "done" for step in plan.steps}

    return ExpectedState(
        expected_nodes=expected_nodes,
        expected_transitions=expected_transitions,
        expected_constraints=list(plan.constraint_refs),
        expected_outputs=expected_outputs,
    )
