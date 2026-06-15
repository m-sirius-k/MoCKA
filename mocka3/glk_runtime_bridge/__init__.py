"""GLK Runtime Bridge - Phase1+2 (GLK_RUNTIME_BRIDGE_v1.md).

GLK -> Execution -> Observation -> Observation Ledger (immutable trace chain).
Drift hook is Phase3 and not implemented here.
"""
from __future__ import annotations

from mocka3.system_blueprint_schema import SystemBlueprint
from mocka3.glk_runtime_bridge.bridge import translate_to_plan
from mocka3.glk_runtime_bridge.context import build_context
from mocka3.glk_runtime_bridge.executor import execute
from mocka3.glk_runtime_bridge.observation import emit_observation
from mocka3.glk_runtime_bridge.events import emit_event
from mocka3.glk_runtime_bridge.ledger import ObservationLedger
from mocka3.glk_runtime_bridge.types import ObservationLedgerEntry


def run(
    blueprint: SystemBlueprint,
    plan_id: str,
    execution_id: str,
    ledger: ObservationLedger,
    input_state: dict | None = None,
    event_sink: list[dict] | None = None,
) -> ObservationLedgerEntry:
    """SS5.1 Execution Flow: Load GLK -> Translate -> Context -> Execute -> Observe -> Ledger.

    Every emitted event's event_id is collected into event_ref, so the
    resulting ledger entry's GLK -> EXECUTION_START -> EXECUTION_END ->
    OBSERVATION_EMIT chain can be reconstructed via ledger.reconstruct_trace.
    """
    event_ref: list[str] = []

    plan = translate_to_plan(blueprint, plan_id=plan_id)
    event_ref.append(emit_event("GLK_TRANSLATED", {"plan_id": plan.plan_id}, sink=event_sink)["event_id"])

    context = build_context(plan, input_state=input_state)

    event_ref.append(emit_event("EXECUTION_STARTED", {"execution_id": execution_id}, sink=event_sink)["event_id"])
    result = execute(plan, context, execution_id=execution_id)
    event_ref.append(emit_event("EXECUTION_COMPLETED", {"execution_id": execution_id}, sink=event_sink)["event_id"])

    observation = emit_observation(context, result)
    event_ref.append(
        emit_event("OBSERVATION_EMITTED", {"execution_id": observation.execution_id}, sink=event_sink)["event_id"]
    )

    return ledger.append(glk_id=blueprint.blueprint_id, observation=observation, event_ref=event_ref)
