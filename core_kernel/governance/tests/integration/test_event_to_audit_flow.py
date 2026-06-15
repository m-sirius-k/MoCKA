"""Integration tests: Event -> Pipeline -> Decision -> Runtime -> Audit.

These tests exercise the full chain end to end through public layer
boundaries only (contracts/engines/runtime/audit), matching the fixed
flow:

    Event -> Validation -> Compliance -> Policy -> Decision
           -> Runtime Execution -> Commit -> Audit Log
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from core_kernel.governance.audit import AuditLogger, AuditStore
from core_kernel.governance.contracts.validation_contract import VALIDATION_SCOPE
from core_kernel.governance.engines.decision_engine import DecisionResult
from core_kernel.governance.runtime import GovernanceEvent, GovernanceRuntime


@pytest.fixture
def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@pytest.fixture
def full_evidence() -> dict:
    return {scope: True for scope in VALIDATION_SCOPE}


@pytest.fixture
def runtime(tmp_path):
    store = AuditStore(tmp_path / "audit.jsonl")
    return GovernanceRuntime(audit_sink=AuditLogger(store)), store


def test_clean_module_flows_pass_to_committed_audit(runtime, timestamp, full_evidence):
    rt, store = runtime
    event = GovernanceEvent(
        event_id="E-INT-1",
        module_id="mod.clean",
        module_version="1.0.0",
        timestamp=timestamp,
        validation_evidence=full_evidence,
        compliance_domain_evidence={"Certification": "CERTIFIED"},
        policy_category_evidence={"Governance Policy": {"result": "PASS"}},
    )

    result = rt.execute(event)

    # Pipeline -> Decision
    assert result.pipeline.decision_record.decision is DecisionResult.PASS
    # Decision -> Runtime
    assert result.commit.committed is True
    assert result.commit.decision is DecisionResult.PASS
    # Runtime -> Audit
    records = store.query("E-INT-1")
    assert len(records) == 11  # validation + compliance + 7 policy + decision + commit
    assert records[-1].decision == "COMMITTED"


def test_broken_module_flows_fail_to_blocked_audit(runtime, timestamp, full_evidence):
    rt, store = runtime
    evidence = dict(full_evidence)
    evidence["Documentation"] = False  # critical scope missing -> INVALID -> FAIL

    event = GovernanceEvent(
        event_id="E-INT-2",
        module_id="mod.broken",
        module_version="0.1.0",
        timestamp=timestamp,
        validation_evidence=evidence,
    )

    result = rt.execute(event)

    assert result.pipeline.validation_record.result.value == "INVALID"
    assert result.pipeline.decision_record.decision is DecisionResult.FAIL
    assert result.commit.committed is False

    records = store.query("E-INT-2")
    decision_audit = next(r for r in records if r.engine == "DecisionEngine")
    commit_audit = next(r for r in records if r.engine == "GovernanceRuntime")
    assert decision_audit.decision == "FAIL"
    assert commit_audit.decision == "BLOCKED"
    assert "validation=INVALID" in decision_audit.reason


def test_two_events_remain_independently_traceable(runtime, timestamp, full_evidence):
    rt, store = runtime
    for i in range(2):
        rt.execute(
            GovernanceEvent(
                event_id=f"E-INT-MULTI-{i}",
                module_id=f"mod.{i}",
                module_version="1.0.0",
                timestamp=timestamp,
                validation_evidence=full_evidence,
            )
        )

    assert {r.event_id for r in store.all()} == {"E-INT-MULTI-0", "E-INT-MULTI-1"}
    for i in range(2):
        records = store.query(f"E-INT-MULTI-{i}")
        assert len(records) == 11
