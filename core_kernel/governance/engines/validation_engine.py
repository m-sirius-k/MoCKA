"""Validation Engine.

Reference: docs/governance/MODULE_VALIDATION_ENGINE_v1.md

First gate of the Governance pipeline. Checks the structural shape
of the incoming Event/evidence and produces a ValidationRecord
(contracts.validation_contract). Pure function: no I/O, no mutation.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..contracts.validation_contract import (
    VALIDATION_SCOPE,
    ValidationRecord,
    ValidationResult,
)

# Scope items whose absence makes the module INVALID rather than WARNING.
_CRITICAL_SCOPE = ("Documentation", "Structure", "Governance Rules")


def run_validation(
    validation_id: str,
    module_id: str,
    module_version: str,
    timestamp: str,
    evidence: Mapping[str, Any],
) -> ValidationRecord:
    """Evaluate ``evidence`` against MODULE_VALIDATION_ENGINE_v1 Section 3.

    ``evidence`` is expected to map each VALIDATION_SCOPE item to either
    a truthy "evidence present / passed" value, or a falsy value meaning
    the scope item is missing/failed. Unknown keys are ignored.
    """

    missing = [scope for scope in VALIDATION_SCOPE if not evidence.get(scope)]

    if not missing:
        result = ValidationResult.VALID
    elif any(scope in _CRITICAL_SCOPE for scope in missing):
        result = ValidationResult.INVALID
    else:
        result = ValidationResult.WARNING

    return ValidationRecord(
        validation_id=validation_id,
        module_id=module_id,
        module_version=module_version,
        validation_timestamp=timestamp,
        result=result,
        evidence=dict(evidence),
        notes=f"missing_scope={missing}" if missing else "",
    )
