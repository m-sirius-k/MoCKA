"""Execution Step Sequence - stub executor (GLK_RUNTIME_BRIDGE_v1.md SS5.1 step4-5).

Phase1: "flow first, correctness later". Each step is marked executed
without performing real side effects.
"""
from __future__ import annotations

from mocka3.glk_runtime_bridge.types import ExecutablePlan, ExecutionContext, ExecutionResult


def execute(plan: ExecutablePlan, context: ExecutionContext, execution_id: str) -> ExecutionResult:
    """Run the plan's steps within the given context. Stub: records the flow only."""
    transition_log: list[str] = []
    constraint_report: dict[str, str] = {}

    state = dict(context.input_state)

    for step in plan.steps:
        transition_log.append(f"executed:{step.step_id}")
        for guard in step.guard:
            constraint_report[guard] = "satisfied"  # stub: no real check yet
        state[step.step_id] = "done"

    return ExecutionResult(
        execution_id=execution_id,
        plan_id=plan.plan_id,
        output_state=state,
        state_transition_log=transition_log,
        constraint_satisfaction_report=constraint_report,
    )
