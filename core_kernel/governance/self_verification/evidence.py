"""Evidence Layer.

Runs a small, fixed set of GovernanceEvents through the real
Engines/Runtime/Audit and captures the resulting PipelineResults,
CommitRecords and AuditRecords as Evidence. Self Verification compares
this Evidence against expectations derived from the design docs
(e.g. "a FAIL decision must yield committed=False and a BLOCKED audit
entry") — it never re-derives the decision itself.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ..audit import AuditLogger, AuditRecord, AuditStore
from ..contracts.validation_contract import VALIDATION_SCOPE
from ..runtime import ExecutionResult, GovernanceEvent, GovernanceRuntime


@dataclass(frozen=True)
class EvidenceBundle:
    """Evidence produced by executing the fixed scenario set."""

    results: dict[str, ExecutionResult]
    audit_records: tuple[AuditRecord, ...]
    audit_store_path: Path


def _full_evidence() -> dict[str, bool]:
    return {scope: True for scope in VALIDATION_SCOPE}


def collect_evidence(store_path: Path | None = None) -> EvidenceBundle:
    """Execute the fixed Evidence scenario set and return what Runtime
    and Audit actually produced.

    Scenarios:
      - "pass":    all VALIDATION_SCOPE present -> expect DecisionResult.PASS
      - "warning": one Policy Category WARNING -> expect DecisionResult.WARNING
      - "fail":    critical VALIDATION_SCOPE missing -> expect DecisionResult.FAIL
    """

    if store_path is None:
        store_path = Path(tempfile.mkdtemp(prefix="mocka_governance_evidence_")) / "audit.jsonl"

    store = AuditStore(store_path)
    runtime = GovernanceRuntime(audit_sink=AuditLogger(store))
    timestamp = datetime.now(timezone.utc).isoformat()

    scenarios: dict[str, GovernanceEvent] = {
        "pass": GovernanceEvent(
            event_id="E-EVIDENCE-PASS",
            module_id="mod.evidence.pass",
            module_version="1.0.0",
            timestamp=timestamp,
            validation_evidence=_full_evidence(),
        ),
        "warning": GovernanceEvent(
            event_id="E-EVIDENCE-WARNING",
            module_id="mod.evidence.warning",
            module_version="1.0.0",
            timestamp=timestamp,
            validation_evidence=_full_evidence(),
            policy_category_evidence={"Security Policy": {"result": "WARNING"}},
        ),
        "fail": GovernanceEvent(
            event_id="E-EVIDENCE-FAIL",
            module_id="mod.evidence.fail",
            module_version="1.0.0",
            timestamp=timestamp,
            validation_evidence={**_full_evidence(), "Documentation": False},
        ),
    }

    results = {name: runtime.execute(event) for name, event in scenarios.items()}

    return EvidenceBundle(
        results=results,
        audit_records=tuple(store.all()),
        audit_store_path=store_path,
    )
