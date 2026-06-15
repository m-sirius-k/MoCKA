"""Compliance Engine.

Reference: docs/governance/MODULE_COMPLIANCE_MODEL_v1.md

Second stage of the pipeline. Takes the ValidationRecord produced by
the Validation Engine plus domain evidence and produces a
ComplianceRecord (contracts.compliance_contract). Pure function.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..contracts.compliance_contract import (
    COMPLIANCE_DOMAINS,
    ComplianceLevel,
    ComplianceRecord,
)
from ..contracts.validation_contract import ValidationRecord, ValidationResult


def run_compliance(
    compliance_id: str,
    validation_record: ValidationRecord,
    assessment_date: str,
    domain_evidence: Mapping[str, Any],
) -> ComplianceRecord:
    """Evaluate ``domain_evidence`` against MODULE_COMPLIANCE_MODEL_v1.

    ``domain_evidence`` maps each entry in COMPLIANCE_DOMAINS to a
    PASS/WARNING/FAIL-like string. The Validation domain is taken
    directly from ``validation_record`` and overrides any caller value.
    """

    unknown = set(domain_evidence) - set(COMPLIANCE_DOMAINS)
    if unknown:
        raise ValueError(f"Unknown Compliance Domain(s): {unknown}")

    findings: dict[str, str] = {
        domain: str(domain_evidence.get(domain, "NOT_APPLICABLE"))
        for domain in COMPLIANCE_DOMAINS
    }
    findings["Validation"] = validation_record.result.value

    failing = [d for d, r in findings.items() if r in ("FAIL", "INVALID", "NON_COMPLIANT")]
    warning = [d for d, r in findings.items() if r == "WARNING"]

    if failing or validation_record.result == ValidationResult.INVALID:
        level = ComplianceLevel.NON_COMPLIANT
    elif warning:
        level = ComplianceLevel.PARTIALLY_COMPLIANT
    elif findings.get("Certification") == "CERTIFIED":
        level = ComplianceLevel.FULLY_COMPLIANT
    else:
        level = ComplianceLevel.COMPLIANT

    recommendations = tuple(
        f"Resolve {domain}: {result}" for domain, result in findings.items()
        if result in ("FAIL", "WARNING", "INVALID", "NON_COMPLIANT")
    )

    return ComplianceRecord(
        compliance_id=compliance_id,
        module_id=validation_record.module_id,
        module_version=validation_record.module_version,
        level=level,
        assessment_date=assessment_date,
        evidence={"validation_id": validation_record.validation_id, **domain_evidence},
        findings=findings,
        recommendations=recommendations,
    )
