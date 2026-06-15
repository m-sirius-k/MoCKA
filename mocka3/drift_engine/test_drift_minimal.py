"""Minimal tests for Drift Engine Phase3 (DRIFT_ENGINE_v1.md)."""
from mocka3.glk_generator import generate_blueprint
from mocka3.meta_intent_schema import MetaIntent
from mocka3.glk_runtime_bridge import run
from mocka3.glk_runtime_bridge.bridge import translate_to_plan
from mocka3.glk_runtime_bridge.ledger import ObservationLedger
from mocka3.drift_engine.types import DriftType
from mocka3.drift_engine.expected_state_resolver import resolve_expected_state
from mocka3.drift_engine.observed_state_resolver import resolve_observed_state
from mocka3.drift_engine.drift_engine import analyze
from mocka3.drift_engine.re_glk_hook import evaluate


def make_blueprint(target_layer_range=(0, 1, 2, 3)):
    intent = MetaIntent(
        meta_intent_id="MI_20260615_020",
        target_layer_range=list(target_layer_range),
        structural_goal="drift engine test",
        constraint_policy=["P1_no_unbounded_self_change"],
        evolution_pressure="human_directive",
        stability_threshold=0.05,
        generation_priority=1,
    )
    return generate_blueprint(intent, blueprint_id="BP_20260615_020")


def run_once(blueprint, execution_id, plan_id="PLAN_DRIFT"):
    ledger = ObservationLedger()
    events: list[dict] = []
    entry = run(blueprint, plan_id=plan_id, execution_id=execution_id, ledger=ledger, event_sink=events)
    plan = translate_to_plan(blueprint, plan_id=plan_id)
    return entry, plan, events


def test_no_drift_for_matching_execution():
    blueprint = make_blueprint()
    entry, plan, _ = run_once(blueprint, "EXEC_D001")

    expected = resolve_expected_state(plan)
    observed = resolve_observed_state(entry)

    events: list[dict] = []
    summary = analyze(expected, observed, event_sink=events)

    assert summary.drift_set == []
    assert summary.severity_score == 0.0
    assert summary.has_constraint_or_critical is False

    event_types = [e["event_type"] for e in events]
    assert "DRIFT_DETECTED" not in event_types
    assert "DRIFT_CLASSIFIED" in event_types


def test_missing_node_yields_critical_drift_and_triggers_reglk():
    blueprint = make_blueprint()
    entry, plan, _ = run_once(blueprint, "EXEC_D002")

    expected = resolve_expected_state(plan)
    observed = resolve_observed_state(entry)

    # simulate a real execution that failed to produce one expected node
    missing_node = expected.expected_nodes[0]
    observed.observed_nodes.remove(missing_node)
    observed.observed_transitions.remove(missing_node)
    observed.observed_outputs.pop(missing_node, None)

    events: list[dict] = []
    summary = analyze(expected, observed, event_sink=events)

    critical_vectors = [v for v in summary.drift_set if v.type == DriftType.CRITICAL]
    assert critical_vectors, "missing expected node should classify as CRITICAL"
    assert summary.has_constraint_or_critical is True
    assert summary.severity_score > 0.0

    signal = evaluate(blueprint.blueprint_id, summary, event_sink=events)
    assert signal is not None
    assert signal.source_blueprint_id == blueprint.blueprint_id

    event_types = [e["event_type"] for e in events]
    assert "DRIFT_DETECTED" in event_types
    assert "REGLK_TRIGGERED" in event_types


def test_constraint_violation_yields_constraint_drift():
    blueprint = make_blueprint()
    entry, plan, _ = run_once(blueprint, "EXEC_D003")

    expected = resolve_expected_state(plan)
    observed = resolve_observed_state(entry)

    # simulate a constraint that was supposed to hold but didn't
    for constraint_id in observed.constraint_satisfaction_report:
        observed.constraint_satisfaction_report[constraint_id] = "violated"

    summary = analyze(expected, observed)

    constraint_vectors = [v for v in summary.drift_set if v.type == DriftType.CONSTRAINT]
    assert constraint_vectors
    assert summary.has_constraint_or_critical is True

    signal = evaluate(blueprint.blueprint_id, summary)
    assert signal is not None
    assert "CONSTRAINT or CRITICAL" in signal.reason


def test_below_threshold_no_signal():
    blueprint = make_blueprint()
    entry, plan, _ = run_once(blueprint, "EXEC_D004")

    expected = resolve_expected_state(plan)
    observed = resolve_observed_state(entry)
    summary = analyze(expected, observed)

    signal = evaluate(blueprint.blueprint_id, summary, threshold=0.5)
    assert signal is None
