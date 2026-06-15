"""Compliance Contract.

Reference: docs/governance/MODULE_COMPLIANCE_MODEL_v1.md
Defines the Compliance Record (Section 6), Compliance Levels
(Section 4) and Compliance Domains (Section 3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

CONTRACT_VERSION = "1.0.0"

COMPLIANCE_DOMAINS = (
    "Governance",
    "Documentation",
    "Structure",
    "Dependencies",
    "Validation",
    "Security",
    "Lifecycle",
    "Certification",
)


class ComplianceLevel(str, Enum):
    """MODULE_COMPLIANCE_MODEL_v1 Section 4."""

    NON_COMPLIANT = "NON_COMPLIANT"
    PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT"
    COMPLIANT = "COMPLIANT"
    FULLY_COMPLIANT = "FULLY_COMPLIANT"


@dataclass(frozen=True)
class ComplianceRecord:
    """MODULE_COMPLIANCE_MODEL_v1 Section 6: Compliance Record."""

    compliance_id: str
    module_id: str
    module_version: str
    level: ComplianceLevel
    assessment_date: str
    evidence: Mapping[str, Any] = field(default_factory=dict)
    findings: Mapping[str, Any] = field(default_factory=dict)
    recommendations: Sequence[str] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.compliance_id:
            raise ValueError("ComplianceRecord.compliance_id is required")
        if not self.module_id:
            raise ValueError("ComplianceRecord.module_id is required")
        if not self.module_version:
            raise ValueError("ComplianceRecord.module_version is required")
        if not isinstance(self.level, ComplianceLevel):
            raise ValueError("ComplianceRecord.level must be a ComplianceLevel")
        if not self.assessment_date:
            raise ValueError("ComplianceRecord.assessment_date is required (ISO8601)")
        unknown = set(self.findings) - set(COMPLIANCE_DOMAINS)
        if unknown:
            raise ValueError(f"Unknown Compliance Domain(s) in findings: {unknown}")
