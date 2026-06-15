"""GLK Translation (GLK_RUNTIME_BRIDGE_v1.md SS4.1 / SS9 step1-2).

GLK Specification Object (SystemBlueprint) -> Executable Plan Object.
"""
from __future__ import annotations

from mocka3.system_blueprint_schema import SystemBlueprint
from mocka3.glk_runtime_bridge.types import ExecutablePlan, ExecutableStep


class BridgeError(Exception):
    pass


def translate_to_plan(blueprint: SystemBlueprint, plan_id: str) -> ExecutablePlan:
    """Translate a validated SystemBlueprint into an ExecutablePlan.

    Trigger conditions (SS4.3): blueprint must already be validated.
    """
    if blueprint.validation_status != "passed":
        raise BridgeError(
            f"GLK validation not passed (status={blueprint.validation_status}); execution forbidden."
        )

    steps: list[ExecutableStep] = []
    constraint_refs: list[str] = []

    for layer_name, definition in blueprint.layer_definitions.items():
        if definition.get("status") != "regenerated":
            continue
        layer_constraints = definition.get("constraint_policy", [])
        constraint_refs.extend(layer_constraints)
        steps.append(
            ExecutableStep(
                step_id=f"step_{layer_name}",
                description=f"apply structural goal to {layer_name}: {definition.get('structural_goal', '')}",
                guard=list(layer_constraints),
            )
        )

    return ExecutablePlan(
        plan_id=plan_id,
        source_blueprint_id=blueprint.blueprint_id,
        steps=steps,
        constraint_refs=sorted(set(constraint_refs)),
    )
