"""Unit tests for audit.audit_logger / audit.audit_store.

Verifies Audit only restructures forwarded records (no recomputation)
and that AuditStore is append-only and queryable per event_id.
"""

from core_kernel.governance.audit import AuditLogger, AuditRecord, AuditStore
from core_kernel.governance.engines.decision_engine import DecisionResult
from core_kernel.governance.runtime import GovernanceEvent, GovernanceRuntime


def _event(event_id, timestamp, evidence):
    return GovernanceEvent(
        event_id=event_id,
        module_id="mod.x",
        module_version="1.0.0",
        timestamp=timestamp,
        validation_evidence=evidence,
    )


def test_audit_record_requires_core_fields():
    import pytest

    with pytest.raises(ValueError):
        AuditRecord(event_id="", engine="X", rule="R", decision="PASS", reason="", timestamp="t", version="1.0.0")


def test_store_is_append_only_and_queryable(tmp_path):
    store = AuditStore(tmp_path / "audit.jsonl")
    store.append(AuditRecord("E-1", "EngineA", "ruleA", "PASS", "ok", "t1", "1.0.0"))
    store.append(AuditRecord("E-2", "EngineA", "ruleA", "FAIL", "bad", "t2", "1.0.0"))
    store.append(AuditRecord("E-1", "EngineB", "ruleB", "WARNING", "meh", "t3", "1.0.0"))

    assert len(store.all()) == 3
    e1 = store.query("E-1")
    assert len(e1) == 2
    assert {r.engine for r in e1} == {"EngineA", "EngineB"}


def test_logger_records_full_pipeline_trace(tmp_path, timestamp, full_validation_evidence):
    store = AuditStore(tmp_path / "audit.jsonl")
    runtime = GovernanceRuntime(audit_sink=AuditLogger(store))

    event = _event("E-10", timestamp, full_validation_evidence)
    result = runtime.execute(event)
    assert result.commit.decision is DecisionResult.PASS

    records = store.query("E-10")
    engines = [r.engine for r in records]
    # Validation, Compliance, 7x Policy, Decision, Commit
    assert engines.count("ValidationEngine") == 1
    assert engines.count("ComplianceEngine") == 1
    assert engines.count("PolicyEngine") == 7
    assert engines.count("DecisionEngine") == 1
    assert engines.count("GovernanceRuntime") == 1

    commit_record = next(r for r in records if r.engine == "GovernanceRuntime")
    assert commit_record.decision == "COMMITTED"


def test_logger_does_not_recompute_decision(tmp_path, timestamp, full_validation_evidence):
    """Audit must record the Decision Engine's verdict verbatim, never
    a value it derives itself."""
    store = AuditStore(tmp_path / "audit.jsonl")
    runtime = GovernanceRuntime(audit_sink=AuditLogger(store))

    evidence = dict(full_validation_evidence)
    evidence["Documentation"] = False  # -> FAIL
    event = _event("E-11", timestamp, evidence)
    result = runtime.execute(event)

    records = store.query("E-11")
    decision_record = next(r for r in records if r.engine == "DecisionEngine")
    assert decision_record.decision == result.pipeline.decision_record.decision.value == "FAIL"
