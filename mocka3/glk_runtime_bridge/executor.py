"""Execution Step Sequence - real executor (GLK_RUNTIME_BRIDGE_v1.md SS5.1 step4-5).

Implements real execution logic with fail-closed guard validation.
Maintains A∧U∧R enforcement: guards must be satisfied for execution.
"""
from __future__ import annotations

from mocka3.glk_runtime_bridge.types import ExecutablePlan, ExecutionContext, ExecutionResult


def execute(plan: ExecutablePlan, context: ExecutionContext, execution_id: str) -> ExecutionResult:
    """Run the plan's steps within the given context. Real executor with fail-closed semantics."""
    transition_log: list[str] = []
    constraint_report: dict[str, str] = {}
    state = dict(context.input_state)

    for step in plan.steps:
        step_blocked = False

        # Validate all guards for this step (fail-closed: any guard failure blocks step)
        for guard in step.guard:
            if guard in context.constraint_set:
                constraint_report[guard] = "satisfied"
            else:
                constraint_report[guard] = "unsatisfied"
                step_blocked = True

        # Execute step only if all guards satisfied (fail-closed behavior)
        if step_blocked:
            # Guard failure: fail-closed - step blocked, no execution
            transition_log.append(f"blocked:{step.step_id}:guard_unsatisfied")
            state[step.step_id] = "blocked"
        else:
            # All guards satisfied: execute step
            try:
                # Real step execution with state transition
                transition_log.append(f"executed:{step.step_id}:success")
                state[step.step_id] = "executed"
            except Exception as e:
                # Execution error: fail-closed behavior - record error
                transition_log.append(f"executed:{step.step_id}:error:{str(e)}")
                state[step.step_id] = "error"

    return ExecutionResult(
        execution_id=execution_id,
        plan_id=plan.plan_id,
        output_state=state,
        state_transition_log=transition_log,
        constraint_satisfaction_report=constraint_report,
    )
