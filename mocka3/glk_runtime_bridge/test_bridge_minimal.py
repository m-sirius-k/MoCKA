"""Tests for GLK Runtime Bridge Phase1 (flow) + Phase2 (Observation Ledger)."""
import pytest

from mocka3.glk_generator import generate_blueprint
from mocka3.meta_intent_schema import MetaIntent
from mocka3.glk_runtime_bridge import run
from mocka3.glk_runtime_bridge.bridge import BridgeError, translate_to_plan
from mocka3.glk_runtime_bridge.ledger import LedgerIntegrityError, ObservationLedger, reconstruct_trace


def make_blueprint():
    intent = MetaIntent(
        meta_intent_id="MI_20260615_010",
        target_layer_range=[0, 1, 2, 3],
        structural_goal="wire up runtime bridge",
        constraint_policy=["P1_no_unbounded_self_change"],
        evolution_pressure="human_directive",
        stability_threshold=0.05,
        generation_priority=1,
    )
    return generate_blueprint(intent, blueprint_id="BP_20260615_010")


def test_run_flows_end_to_end_and_writes_ledger():
    blueprint = make_blueprint()
    events: list[dict] = []
    ledger = ObservationLedger()

    entry = run(
        blueprint,
        plan_id="PLAN_001",
        execution_id="EXEC_001",
        ledger=ledger,
        input_state={"seed": "x"},
        event_sink=events,
    )

    assert entry.execution_id == "EXEC_001"
    assert entry.glk_id == blueprint.blueprint_id
    assert entry.input_snapshot.state == {"seed": "x"}
    assert entry.output_snapshot.state["step_layer0"] == "done"
    assert len(entry.state_transition) == 4  # layers 0-3 regenerated

    event_types = [e["event_type"] for e in events]
    assert event_types == [
        "GLK_TRANSLATED",
        "EXECUTION_STARTED",
        "EXECUTION_COMPLETED",
        "OBSERVATION_EMITTED",
    ]
    assert entry.event_ref == [e["event_id"] for e in events]


def test_unvalidated_blueprint_rejected():
    blueprint = make_blueprint()
    blueprint.validation_status = "pending"

    with pytest.raises(BridgeError):
        translate_to_plan(blueprint, plan_id="PLAN_002")


def test_ledger_is_append_only_and_immutable_per_execution():
    blueprint = make_blueprint()
    ledger = ObservationLedger()

    run(blueprint, plan_id="PLAN_003", execution_id="EXEC_DUP", ledger=ledger)

    with pytest.raises(LedgerIntegrityError):
        run(blueprint, plan_id="PLAN_003", execution_id="EXEC_DUP", ledger=ledger)


def test_trace_chain_reconstructable():
    blueprint = make_blueprint()
    events: list[dict] = []
    ledger = ObservationLedger()

    entry = run(
        blueprint,
        plan_id="PLAN_004",
        execution_id="EXEC_004",
        ledger=ledger,
        event_sink=events,
    )

    chain = reconstruct_trace(entry, events)
    assert [e["event_type"] for e in chain] == [
        "GLK_TRANSLATED",
        "EXECUTION_STARTED",
        "EXECUTION_COMPLETED",
        "OBSERVATION_EMITTED",
    ]


def test_trace_chain_broken_if_events_missing():
    blueprint = make_blueprint()
    ledger = ObservationLedger()

    entry = run(blueprint, plan_id="PLAN_005", execution_id="EXEC_005", ledger=ledger, event_sink=[])

    with pytest.raises(LedgerIntegrityError):
        reconstruct_trace(entry, events=[])
