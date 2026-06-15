"""Execution Context Generation (GLK_RUNTIME_BRIDGE_v1.md SS4.2)."""
from __future__ import annotations

from mocka3.glk_runtime_bridge.types import ExecutablePlan, ExecutionContext


def build_context(plan: ExecutablePlan, input_state: dict | None = None) -> ExecutionContext:
    """Build the ExecutionContext that bounds all execution for this plan."""
    return ExecutionContext(
        context_id=f"ctx_{plan.plan_id}",
        plan_id=plan.plan_id,
        input_state=input_state or {},
        runtime_variables={},
        constraint_set=list(plan.constraint_refs),
        execution_scope=plan.source_blueprint_id,
        dependency_graph={step.step_id: step.guard for step in plan.steps},
    )
