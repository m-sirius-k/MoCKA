"""Drift Detection.

Looks for divergence between the layers of the Trace Graph:

  - Implementation drift: a Requirement's unit test does not actually
    import the module(s) listed as its Implementation.
  - Evidence/Audit drift: the Decision recorded for an Event does not
    match the Commit outcome recorded for the same Event in the Audit
    trail (i.e. Audit silently diverged from what Decision Engine said).

Drift Detection never recomputes a Decision or rewrites a record — it
only flags mismatches between what different layers report about the
same Event/Requirement.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..evidence import EvidenceBundle
from ..requirement_map import REQUIREMENTS

_DECISION_TO_COMMIT = {
    "PASS": "COMMITTED",
    "WARNING": "COMMITTED",
    "FAIL": "BLOCKED",
}


@dataclass(frozen=True)
class DriftFinding:
    req_id: str
    kind: str
    detail: str


def _check_implementation_test_drift(root: Path) -> list[DriftFinding]:
    findings: list[DriftFinding] = []
    for req in REQUIREMENTS:
        try:
            test_source = (root / req.unit_test).read_text(encoding="utf-8")
        except OSError:
            continue  # missing-file drift is handled by Governance Closure
        for impl in req.implementation:
            # Compare at package granularity (e.g. "core_kernel.governance.audit")
            # so re-exports via package __init__ don't register as drift.
            module_path = ".".join(impl.parent.parts)
            if module_path not in test_source:
                findings.append(
                    DriftFinding(
                        req_id=req.req_id,
                        kind="implementation_not_referenced_by_test",
                        detail=f"{req.unit_test} does not reference {module_path}",
                    )
                )
    return findings


def _check_decision_audit_drift(evidence: EvidenceBundle) -> list[DriftFinding]:
    findings: list[DriftFinding] = []
    by_event: dict[str, dict[str, str]] = {}
    for record in evidence.audit_records:
        if record.engine == "DecisionEngine":
            by_event.setdefault(record.event_id, {})["decision"] = record.decision
        elif record.engine == "GovernanceRuntime":
            by_event.setdefault(record.event_id, {})["commit"] = record.decision

    for event_id, pair in by_event.items():
        decision = pair.get("decision")
        commit = pair.get("commit")
        if decision is None or commit is None:
            findings.append(
                DriftFinding(
                    req_id="REQ-AUD-001",
                    kind="incomplete_audit_trail",
                    detail=f"{event_id}: decision={decision} commit={commit}",
                )
            )
            continue

        expected_commit = _DECISION_TO_COMMIT.get(decision)
        if commit != expected_commit:
            findings.append(
                DriftFinding(
                    req_id="REQ-GOV-002",
                    kind="decision_commit_mismatch",
                    detail=f"{event_id}: decision={decision} -> expected commit={expected_commit}, got {commit}",
                )
            )
    return findings


def detect_drift(evidence: EvidenceBundle, root: Path) -> tuple[DriftFinding, ...]:
    findings: list[DriftFinding] = []
    findings.extend(_check_implementation_test_drift(root))
    findings.extend(_check_decision_audit_drift(evidence))
    return tuple(findings)
