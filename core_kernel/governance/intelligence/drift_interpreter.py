"""Drift Interpreter.

Phase 6's drift_detection answers "is there a mismatch?". This module
answers "what does that mismatch mean, and what should be done about
it?" — interpretation, not detection. It never re-runs detection and
never changes a DriftFinding; it only annotates one.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..self_verification.traceability.drift_detection import DriftFinding


class DriftSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class InterpretedDrift:
    finding: DriftFinding
    severity: DriftSeverity
    meaning: str
    recommended_action: str


# kind -> (severity, meaning, recommended_action)
_INTERPRETATIONS: dict[str, tuple[DriftSeverity, str, str]] = {
    "decision_commit_mismatch": (
        DriftSeverity.CRITICAL,
        "Audit's recorded commit outcome diverges from Decision Engine's "
        "verdict for the same Event. This breaks the 'Decision is the "
        "single authority' guarantee from Phase 2/3 — either Runtime "
        "executed something other than the Decision, or Audit recorded "
        "it incorrectly.",
        "Freeze deployment of GovernanceRuntime/AuditLogger changes; "
        "diff the DecisionRecord and CommitRecord for the affected "
        "event_id and identify which side diverged.",
    ),
    "incomplete_audit_trail": (
        DriftSeverity.CRITICAL,
        "An Event reached Decision or Commit but the Audit trail is "
        "missing the corresponding entry. The 'Event -> Commit fully "
        "traceable' guarantee from Phase 4 is violated for this event.",
        "Check AuditSink wiring for dropped stages; confirm "
        "GovernanceRuntime._forward_to_audit ran for all five stages.",
    ),
    "implementation_not_referenced_by_test": (
        DriftSeverity.WARNING,
        "A Requirement's unit test does not import the package that "
        "contains its Implementation. The test may be passing without "
        "exercising the code it is supposed to cover.",
        "Confirm the unit test imports from the Implementation's "
        "package, or update requirement_map if the Implementation "
        "moved.",
    ),
}

_DEFAULT = (
    DriftSeverity.INFO,
    "Unrecognized drift kind; no interpretation rule defined.",
    "Add an entry to drift_interpreter._INTERPRETATIONS for this kind.",
)


def interpret_drift(finding: DriftFinding) -> InterpretedDrift:
    severity, meaning, action = _INTERPRETATIONS.get(finding.kind, _DEFAULT)
    return InterpretedDrift(
        finding=finding,
        severity=severity,
        meaning=meaning,
        recommended_action=action,
    )


def interpret_all(findings: tuple[DriftFinding, ...]) -> tuple[InterpretedDrift, ...]:
    return tuple(interpret_drift(f) for f in findings)
