"""Validation Contract.

Reference: docs/governance/MODULE_VALIDATION_ENGINE_v1.md
Defines the Validation Record (Section 6) and Validation Results
enum (Section 5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

CONTRACT_VERSION = "1.0.0"

VALIDATION_SCOPE = (
    "Documentation",
    "Structure",
    "Dependencies",
    "Governance Rules",
    "Policy Results",
    "Health State",
    "Lifecycle State",
    "Certification Requirements",
)


class ValidationResult(str, Enum):
    """MODULE_VALIDATION_ENGINE_v1 Section 5."""

    VALID = "VALID"
    WARNING = "WARNING"
    INVALID = "INVALID"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class ValidationRecord:
    """MODULE_VALIDATION_ENGINE_v1 Section 6: Validation Record."""

    validation_id: str
    module_id: str
    module_version: str
    validation_timestamp: str
    result: ValidationResult
    evidence: Mapping[str, Any] = field(default_factory=dict)
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.validation_id:
            raise ValueError("ValidationRecord.validation_id is required")
        if not self.module_id:
            raise ValueError("ValidationRecord.module_id is required")
        if not self.module_version:
            raise ValueError("ValidationRecord.module_version is required")
        if not self.validation_timestamp:
            raise ValueError("ValidationRecord.validation_timestamp is required (ISO8601)")
        if not isinstance(self.result, ValidationResult):
            raise ValueError("ValidationRecord.result must be a ValidationResult")
