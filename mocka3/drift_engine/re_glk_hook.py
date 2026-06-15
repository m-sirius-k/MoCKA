"""Re-GLK Hook Interface (DRIFT_ENGINE_v1.md SS10).

Policy (SS10.3): correction is never a direct edit. The existing GLK
(SystemBlueprint) is kept immutable; this hook only signals that a
new MetaIntent should be generated for the GLK Generator (Phase1/mocka3).
"""
from __future__ import annotations

from dataclasses import dataclass

from mocka3.glk_runtime_bridge.events import emit_event
from mocka3.drift_engine.types import DriftSummary

DEFAULT_SEVERITY_THRESHOLD = 0.5


@dataclass
class ReGLKSignal:
    source_blueprint_id: str
    severity_score: float
    reason: str


def evaluate(
    blueprint_id: str,
    drift_summary: DriftSummary,
    threshold: float = DEFAULT_SEVERITY_THRESHOLD,
    event_sink: list[dict] | None = None,
) -> ReGLKSignal | None:
    """SS10.1 trigger conditions: severity > threshold OR CONSTRAINT/CRITICAL drift present.

    Returns a ReGLKSignal (SS10.2 -> input for a new MetaIntent) or None
    if the existing GLK remains valid.
    """
    triggered = drift_summary.severity_score > threshold or drift_summary.has_constraint_or_critical
    if not triggered:
        return None

    reason = (
        f"severity_score={drift_summary.severity_score:.3f} > threshold={threshold}"
        if drift_summary.severity_score > threshold
        else "CONSTRAINT or CRITICAL drift detected"
    )

    emit_event(
        "REGLK_TRIGGERED",
        {"blueprint_id": blueprint_id, "severity_score": drift_summary.severity_score, "reason": reason},
        sink=event_sink,
    )

    return ReGLKSignal(
        source_blueprint_id=blueprint_id,
        severity_score=drift_summary.severity_score,
        reason=reason,
    )
