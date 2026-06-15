"""Unit tests for engines.policy_engine.

Reference: docs/governance/MODULE_POLICY_ENGINE_v1.md Sections 3-5.
"""

import pytest

from core_kernel.governance.contracts.policy_contract import POLICY_CATEGORIES, PolicyResult
from core_kernel.governance.engines.policy_engine import run_policy


def test_returns_one_evaluation_per_category(timestamp):
    evaluations = run_policy("mod.x", timestamp, {})
    assert len(evaluations) == len(POLICY_CATEGORIES)
    assert {e.category for e in evaluations} == set(POLICY_CATEGORIES)


def test_absent_category_defaults_to_not_applicable(timestamp):
    evaluations = run_policy("mod.x", timestamp, {})
    assert all(e.result is PolicyResult.NOT_APPLICABLE for e in evaluations)


def test_provided_category_evidence_is_used(timestamp):
    evaluations = run_policy(
        "mod.x",
        timestamp,
        {"Governance Policy": {"result": "PASS", "policy_id": "GOV-1", "criteria": "VERSION_POLICY"}},
    )
    gov = next(e for e in evaluations if e.category == "Governance Policy")
    assert gov.result is PolicyResult.PASS
    assert gov.policy_id == "GOV-1"
    assert gov.evaluation_criteria == "VERSION_POLICY"
    assert gov.target_module == "mod.x"
    assert gov.timestamp == timestamp


def test_invalid_result_value_is_rejected(timestamp):
    with pytest.raises(ValueError):
        run_policy("mod.x", timestamp, {"Governance Policy": {"result": "MAYBE"}})
