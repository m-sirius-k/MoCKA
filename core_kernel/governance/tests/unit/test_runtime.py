"""Unit tests for runtime.event_pipeline / runtime.governance_runtime.

Verifies Runtime never re-judges: commit follows DecisionRecord only,
and the Engine chain executes in the fixed order.
"""

import pytest

from core_kernel.governance.engines.decision_engine import DecisionResult
from core_kernel.governance.runtime import GovernanceEvent, GovernanceRuntime, run_pipeline


def _event(event_id, timestamp, evidence, domain_evidence=None, category_evidence=None):
    return GovernanceEvent(
        event_id=event_id,
        module_id="mod.x",
        module_version="1.0.0",
        timestamp=timestamp,
        validation_evidence=evidence,
        compliance_domain_evidence=domain_evidence or {},
        policy_category_evidence=category_evidence or {},
    )


def test_pipeline_produces_all_stage_records(timestamp, full_validation_evidence):
    event = _event("E-1", timestamp, full_validation_evidence)
    result = run_pipeline(event)
    assert result.validation_record.validation_id == "VAL-E-1"
    assert result.compliance_record.compliance_id == "COMP-E-1"
    assert len(result.policy_evaluations) == 7
    assert result.decision_record.decision is DecisionResult.PASS


def test_runtime_commits_on_pass_or_warning(timestamp, full_validation_evidence):
    event = _event("E-2", timestamp, full_validation_evidence, {}, {"Security Policy": {"result": "WARNING"}})
    result = GovernanceRuntime().execute(event)
    assert result.commit.decision is DecisionResult.WARNING
    assert result.commit.committed is True


def test_runtime_blocks_commit_on_fail(timestamp, full_validation_evidence):
    evidence = dict(full_validation_evidence)
    evidence["Documentation"] = False
    event = _event("E-3", timestamp, evidence)
    result = GovernanceRuntime().execute(event)
    assert result.commit.decision is DecisionResult.FAIL
    assert result.commit.committed is False


def test_event_requires_identity_fields(timestamp):
    with pytest.raises(ValueError):
        GovernanceEvent(event_id="", module_id="m", module_version="1", timestamp=timestamp)
