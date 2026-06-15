"""Requirement Traceability Map.

Each Requirement links Design -> Contract -> Implementation
-> Unit Test -> Integration Test for one slice of the Governance
pipeline. Paths are relative to the MoCKA repository root.

Per くろこ指示書 (Requirement Traceability): designs are not modified
here, only referenced.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_GOV = Path("core_kernel/governance")
_DOCS = Path("docs/governance")


@dataclass(frozen=True)
class Requirement:
    req_id: str
    title: str
    design: Path
    contract: Path
    implementation: tuple[Path, ...]
    unit_test: Path
    integration_test: Path | None = None
    # AuditRecord.engine values this requirement must appear under in
    # the Audit trail. Empty tuple == "any audit record is sufficient"
    # (used for the Audit requirement itself).
    audit_engines: tuple[str, ...] = ()


REQUIREMENTS: tuple[Requirement, ...] = (
    Requirement(
        req_id="REQ-VAL-001",
        title="Validation Engine",
        design=_DOCS / "MODULE_VALIDATION_ENGINE_v1.md",
        contract=_GOV / "contracts/validation_contract.py",
        implementation=(_GOV / "engines/validation_engine.py",),
        unit_test=_GOV / "tests/unit/test_validation_engine.py",
        integration_test=_GOV / "tests/integration/test_event_to_audit_flow.py",
        audit_engines=("ValidationEngine",),
    ),
    Requirement(
        req_id="REQ-CMP-001",
        title="Compliance Engine",
        design=_DOCS / "MODULE_COMPLIANCE_MODEL_v1.md",
        contract=_GOV / "contracts/compliance_contract.py",
        implementation=(_GOV / "engines/compliance_engine.py",),
        unit_test=_GOV / "tests/unit/test_compliance_engine.py",
        integration_test=_GOV / "tests/integration/test_event_to_audit_flow.py",
        audit_engines=("ComplianceEngine",),
    ),
    Requirement(
        req_id="REQ-POL-001",
        title="Policy Engine",
        design=_DOCS / "MODULE_POLICY_ENGINE_v1.md",
        contract=_GOV / "contracts/policy_contract.py",
        implementation=(_GOV / "engines/policy_engine.py",),
        unit_test=_GOV / "tests/unit/test_policy_engine.py",
        integration_test=_GOV / "tests/integration/test_event_to_audit_flow.py",
        audit_engines=("PolicyEngine",),
    ),
    Requirement(
        req_id="REQ-GOV-001",
        title="Decision Engine (central decision authority)",
        design=_DOCS / "MODULE_GOVERNANCE_RUNTIME_v1.md",
        contract=_GOV / "contracts/governance_contract.py",
        implementation=(_GOV / "engines/decision_engine.py",),
        unit_test=_GOV / "tests/unit/test_decision_engine.py",
        integration_test=_GOV / "tests/integration/test_event_to_audit_flow.py",
        audit_engines=("DecisionEngine",),
    ),
    Requirement(
        req_id="REQ-GOV-002",
        title="Governance Runtime (Event -> Pipeline -> Commit)",
        design=_DOCS / "MODULE_GOVERNANCE_RUNTIME_v1.md",
        contract=_GOV / "contracts/governance_contract.py",
        implementation=(
            _GOV / "runtime/event_pipeline.py",
            _GOV / "runtime/governance_runtime.py",
        ),
        unit_test=_GOV / "tests/unit/test_runtime.py",
        integration_test=_GOV / "tests/integration/test_event_to_audit_flow.py",
        audit_engines=("GovernanceRuntime",),
    ),
    Requirement(
        req_id="REQ-AUD-001",
        title="Audit (observation-only evidence trail)",
        design=_DOCS / "MODULE_AUDIT_PROTOCOL_v1.md",
        contract=_GOV / "audit/audit_schema.py",
        implementation=(
            _GOV / "audit/audit_logger.py",
            _GOV / "audit/audit_store.py",
        ),
        unit_test=_GOV / "tests/unit/test_audit.py",
        integration_test=_GOV / "tests/integration/test_event_to_audit_flow.py",
    ),
)
