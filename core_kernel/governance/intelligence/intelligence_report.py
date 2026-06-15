"""Intelligence Report.

Combines Drift Interpretation, Decision Rationale and Requirement
History into one report sitting above
self_verification.VerificationReport. Purely additive: every value
here is derived from Phase 5/6 outputs plus Evidence; nothing is
recomputed or overridden.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..self_verification.verification_engine import VerificationReport
from .decision_rationale import RationaleRecord, build_rationale
from .drift_interpreter import DriftSeverity, InterpretedDrift, interpret_all
from .requirement_history import RequirementHistoryStore

_SEVERITY_ORDER = {DriftSeverity.INFO: 0, DriftSeverity.WARNING: 1, DriftSeverity.CRITICAL: 2}


@dataclass(frozen=True)
class IntelligenceReport:
    interpreted_drift: tuple[InterpretedDrift, ...]
    max_severity: DriftSeverity
    rationales: dict[str, RationaleRecord]
    requirement_history_count: int


def generate_intelligence_report(
    verification_report: VerificationReport,
    history: RequirementHistoryStore | None = None,
) -> IntelligenceReport:
    interpreted = interpret_all(verification_report.drift_findings)
    max_severity = max(
        (i.severity for i in interpreted), key=lambda s: _SEVERITY_ORDER[s], default=DriftSeverity.INFO
    )

    rationales = {
        name: build_rationale(result.pipeline)
        for name, result in verification_report.evidence.results.items()
    }

    history_count = len(history.all()) if history is not None else 0

    return IntelligenceReport(
        interpreted_drift=interpreted,
        max_severity=max_severity,
        rationales=rationales,
        requirement_history_count=history_count,
    )


def intelligence_report_to_dict(report: IntelligenceReport) -> dict[str, Any]:
    return {
        "max_severity": report.max_severity.value,
        "drift": [
            {
                "req_id": d.finding.req_id,
                "kind": d.finding.kind,
                "detail": d.finding.detail,
                "severity": d.severity.value,
                "meaning": d.meaning,
                "recommended_action": d.recommended_action,
            }
            for d in report.interpreted_drift
        ],
        "rationales": {
            name: {
                "event_id": r.event_id,
                "module_id": r.module_id,
                "decision": r.decision.value,
                "summary": r.summary,
                "contributing_factors": list(r.contributing_factors),
            }
            for name, r in report.rationales.items()
        },
        "requirement_history_count": report.requirement_history_count,
    }


def write_intelligence_report(report: IntelligenceReport, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(intelligence_report_to_dict(report), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
