"""Unit tests for self_verification.traceability (Phase 6).

Verifies the Trace Graph reaches 100% Closure for the current
implementation, and that Coverage/Drift detection actually fire when
the underlying data is broken.
"""

from __future__ import annotations

from pathlib import Path

from core_kernel.governance.audit import AuditRecord
from core_kernel.governance.self_verification.evidence import EvidenceBundle, collect_evidence
from core_kernel.governance.self_verification.requirement_map import REQUIREMENTS
from core_kernel.governance.self_verification.traceability import (
    TraceLayer,
    build_coverage_matrix,
    build_trace_graph,
    check_closure,
    detect_drift,
)

ROOT = Path(__file__).resolve().parents[4]


def test_trace_graph_is_fully_closed_for_current_implementation():
    evidence = collect_evidence()
    graph = build_trace_graph(evidence, ROOT)
    closure = check_closure(graph)
    assert closure.is_closed, closure.unconnected


def test_coverage_matrix_is_100_percent_with_no_gaps():
    evidence = collect_evidence()
    graph = build_trace_graph(evidence, ROOT)
    coverage = build_coverage_matrix(graph)
    assert coverage.coverage_percent == 100.0
    assert coverage.contract_without_implementation == ()
    assert coverage.implementation_without_test == ()
    assert coverage.test_without_evidence_or_audit == ()


def test_every_requirement_appears_in_trace_graph():
    evidence = collect_evidence()
    graph = build_trace_graph(evidence, ROOT)
    assert set(graph.nodes) == {r.req_id for r in REQUIREMENTS}
    for req_id, layers in graph.nodes.items():
        assert set(layers) == set(TraceLayer)


def test_no_drift_for_current_implementation():
    evidence = collect_evidence()
    findings = detect_drift(evidence, ROOT)
    assert findings == ()


def test_decision_commit_mismatch_is_detected_as_drift():
    """If Audit's commit entry diverges from Decision Engine's verdict
    for the same event, drift detection must flag it."""
    evidence = collect_evidence()
    tampered_records = list(evidence.audit_records)

    # Find a "fail" scenario's commit record and flip it to COMMITTED.
    for i, r in enumerate(tampered_records):
        if r.event_id == "E-EVIDENCE-FAIL" and r.engine == "GovernanceRuntime":
            tampered_records[i] = AuditRecord(
                event_id=r.event_id,
                engine=r.engine,
                rule=r.rule,
                decision="COMMITTED",  # tampered: should be BLOCKED
                reason=r.reason,
                timestamp=r.timestamp,
                version=r.version,
            )
            break

    tampered = EvidenceBundle(
        results=evidence.results,
        audit_records=tuple(tampered_records),
        audit_store_path=evidence.audit_store_path,
    )

    findings = detect_drift(tampered, ROOT)
    assert any(f.kind == "decision_commit_mismatch" for f in findings)
