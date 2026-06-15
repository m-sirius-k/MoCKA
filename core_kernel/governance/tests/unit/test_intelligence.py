from __future__ import annotations

from core_kernel.governance.intelligence import (
    DriftSeverity,
    InterpretedDrift,
    RequirementChange,
    RequirementHistoryStore,
    generate_intelligence_report,
    interpret_drift,
)
from core_kernel.governance.intelligence.intelligence_report import (
    intelligence_report_to_dict,
)
from core_kernel.governance.self_verification import SelfVerificationEngine
from core_kernel.governance.self_verification.traceability.drift_detection import DriftFinding


def test_interpret_drift_known_kinds():
    finding = DriftFinding(req_id="REQ-VAL-001", kind="decision_commit_mismatch", detail="x")
    interpreted = interpret_drift(finding)
    assert isinstance(interpreted, InterpretedDrift)
    assert interpreted.severity is DriftSeverity.CRITICAL
    assert interpreted.finding is finding


def test_interpret_drift_unknown_kind_defaults_to_info():
    finding = DriftFinding(req_id="REQ-VAL-001", kind="something_new", detail="x")
    interpreted = interpret_drift(finding)
    assert interpreted.severity is DriftSeverity.INFO


def test_requirement_history_store_roundtrip(tmp_path):
    store = RequirementHistoryStore(tmp_path / "history.jsonl")
    change = RequirementChange(
        req_id="REQ-VAL-001",
        version="1.0.0",
        timestamp="2026-06-15T00:00:00Z",
        change_type="CREATED",
        intent="Initial validation requirement",
        description="Established REQ-VAL-001",
    )
    store.append(change)

    assert store.all() == [change]
    assert store.query("REQ-VAL-001") == [change]
    assert store.query("REQ-NONE") == []


def test_requirement_change_requires_fields():
    import pytest

    with pytest.raises(ValueError):
        RequirementChange(
            req_id="REQ-VAL-001",
            version="1.0.0",
            timestamp="2026-06-15T00:00:00Z",
            change_type="",
            intent="why",
            description="desc",
        )


def test_generate_intelligence_report_from_verification(tmp_path):
    report = SelfVerificationEngine().run()

    history = RequirementHistoryStore(tmp_path / "history.jsonl")
    history.append(
        RequirementChange(
            req_id="REQ-VAL-001",
            version="1.0.0",
            timestamp="2026-06-15T00:00:00Z",
            change_type="CREATED",
            intent="Initial validation requirement",
            description="Established REQ-VAL-001",
        )
    )

    intel = generate_intelligence_report(report, history=history)

    assert set(intel.rationales) == set(report.evidence.results)
    assert intel.requirement_history_count == 1
    assert intel.max_severity in DriftSeverity

    for name, rationale in intel.rationales.items():
        pipeline = report.evidence.results[name].pipeline
        assert rationale.event_id == pipeline.event.event_id
        assert rationale.decision == pipeline.decision_record.decision

    as_dict = intelligence_report_to_dict(intel)
    assert "rationales" in as_dict
    assert "drift" in as_dict
