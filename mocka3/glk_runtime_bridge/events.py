"""Event Logging hook (GLK_RUNTIME_BRIDGE_v1.md SS11).

Phase2: each event gets an immutable event_id so Observation Ledger entries
can hold an event_ref chain (event <-> observation linking).
Wiring to MoCKA's mocka_write_event (the real ledger) remains future work.
"""
from __future__ import annotations

import uuid

EVENT_TYPES = (
    "GLK_TRANSLATED",
    "EXECUTION_STARTED",
    "EXECUTION_COMPLETED",
    "OBSERVATION_EMITTED",
    "DRIFT_DETECTED",
    "DRIFT_CLASSIFIED",
    "DRIFT_VECTOR_EMITTED",
    "REGLK_TRIGGERED",
    "DRIFT_REINTEGRATED",
)


def emit_event(event_type: str, payload: dict, sink: list[dict] | None = None) -> dict:
    """Append an immutable event record. If `sink` is given, append to it.

    Returns the event dict including a unique event_id.
    """
    if event_type not in EVENT_TYPES:
        raise ValueError(f"unknown event_type: {event_type}")

    event = {"event_id": f"EVT_{uuid.uuid4().hex[:12]}", "event_type": event_type, "payload": payload}
    if sink is not None:
        sink.append(event)
    return event
