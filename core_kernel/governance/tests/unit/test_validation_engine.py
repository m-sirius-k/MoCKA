"""Unit tests for engines.validation_engine.

Reference: docs/governance/MODULE_VALIDATION_ENGINE_v1.md Section 5.
"""

from core_kernel.governance.contracts.validation_contract import ValidationResult
from core_kernel.governance.engines.validation_engine import run_validation


def test_all_scope_present_is_valid(timestamp, full_validation_evidence):
    record = run_validation("VAL-1", "mod.x", "1.0.0", timestamp, full_validation_evidence)
    assert record.result is ValidationResult.VALID
    assert record.notes == ""


def test_missing_non_critical_scope_is_warning(timestamp, full_validation_evidence):
    evidence = dict(full_validation_evidence)
    evidence["Health State"] = False
    record = run_validation("VAL-2", "mod.x", "1.0.0", timestamp, evidence)
    assert record.result is ValidationResult.WARNING
    assert "Health State" in record.notes


def test_missing_critical_scope_is_invalid(timestamp, full_validation_evidence):
    evidence = dict(full_validation_evidence)
    evidence["Documentation"] = False
    record = run_validation("VAL-3", "mod.x", "1.0.0", timestamp, evidence)
    assert record.result is ValidationResult.INVALID
    assert "Documentation" in record.notes


def test_record_carries_identity(timestamp, full_validation_evidence):
    record = run_validation("VAL-4", "mod.y", "2.3.0", timestamp, full_validation_evidence)
    assert record.validation_id == "VAL-4"
    assert record.module_id == "mod.y"
    assert record.module_version == "2.3.0"
    assert record.validation_timestamp == timestamp
