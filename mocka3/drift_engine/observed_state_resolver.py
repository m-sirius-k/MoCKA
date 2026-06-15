"""Observed State Resolver (DRIFT_ENGINE_v1.md SS4.2).

ObservationLedgerEntry -> ObservedState, normalized to the same schema
as ExpectedState (SS6.2 constraint).
"""
from __future__ import annotations

from mocka3.glk_runtime_bridge.types import ObservationLedgerEntry
from mocka3.drift_engine.types import ObservedState


def resolve_observed_state(entry: ObservationLedgerEntry) -> ObservedState:
    observed_transitions = [t.step_id for t in entry.state_transition]
    observed_nodes = list(observed_transitions)
    observed_outputs = {
        node_id: value
        for node_id, value in entry.output_snapshot.state.items()
        if node_id in observed_nodes
    }

    return ObservedState(
        observed_nodes=observed_nodes,
        observed_transitions=observed_transitions,
        observed_outputs=observed_outputs,
        constraint_satisfaction_report=dict(entry.constraint_satisfaction_report),
    )
