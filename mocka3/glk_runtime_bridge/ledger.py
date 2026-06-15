"""Observation Ledger (GLK_RUNTIME_BRIDGE_v1.md Phase2).

An append-only, immutable record store linking GLK executions to their
ObservationRecords and the Event chain that produced them.

Entry = {execution_id, glk_id, input_snapshot, output_snapshot,
         state_transition, timestamp, event_ref}
"""
from __future__ import annotations

from mocka3.glk_runtime_bridge.types import ObservationLedgerEntry, ObservationRecord


class LedgerIntegrityError(Exception):
    pass


class ObservationLedger:
    """Append-only store. No update/delete operations are exposed."""

    def __init__(self) -> None:
        self._entries: list[ObservationLedgerEntry] = []

    def append(self, glk_id: str, observation: ObservationRecord, event_ref: list[str]) -> ObservationLedgerEntry:
        if any(e.execution_id == observation.execution_id for e in self._entries):
            raise LedgerIntegrityError(
                f"execution_id {observation.execution_id} already recorded; ledger is append-only and immutable."
            )

        entry = ObservationLedgerEntry(
            execution_id=observation.execution_id,
            glk_id=glk_id,
            input_snapshot=observation.input_snapshot,
            output_snapshot=observation.output_snapshot,
            state_transition=list(observation.state_transition_log),
            constraint_satisfaction_report=dict(observation.constraint_satisfaction_report),
            event_ref=list(event_ref),
        )
        self._entries.append(entry)
        return entry

    def get(self, execution_id: str) -> ObservationLedgerEntry | None:
        for entry in self._entries:
            if entry.execution_id == execution_id:
                return entry
        return None

    def all(self) -> list[ObservationLedgerEntry]:
        return list(self._entries)


def reconstruct_trace(entry: ObservationLedgerEntry, events: list[dict]) -> list[dict]:
    """Reconstruct the GLK -> EXECUTION_START -> EXECUTION_END -> OBSERVATION_EMIT chain
    for one execution, in event order, from the full event list.
    """
    ref_set = set(entry.event_ref)
    chain = [e for e in events if e["event_id"] in ref_set]
    if len(chain) != len(entry.event_ref):
        raise LedgerIntegrityError(
            f"trace chain broken for execution_id={entry.execution_id}: "
            f"expected {len(entry.event_ref)} events, found {len(chain)}."
        )
    return chain
