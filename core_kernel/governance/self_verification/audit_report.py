"""Audit Report generation.

Converts a VerificationReport into a JSON-serializable summary and
optionally writes it to disk. This is the final node of:

    Design -> Contract -> Implementation -> Unit Test
           -> Integration Test -> Evidence -> Audit Report
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .verification_engine import VerificationReport, VerificationStatus


def generate_audit_report(report: VerificationReport, output_path: Path | None = None) -> dict[str, Any]:
    summary = {
        "status": report.status.value,
        "test_exit_code": report.test_exit_code,
        "requirements": [
            {
                "req_id": rr.requirement.req_id,
                "title": rr.requirement.title,
                "status": rr.status.value,
                "missing_links": list(rr.missing_links),
                "design": str(rr.requirement.design),
                "contract": str(rr.requirement.contract),
                "implementation": [str(p) for p in rr.requirement.implementation],
                "unit_test": str(rr.requirement.unit_test),
                "integration_test": str(rr.requirement.integration_test)
                if rr.requirement.integration_test
                else None,
            }
            for rr in report.requirement_results
        ],
        "evidence_findings": list(report.evidence_findings),
        "evidence_scenarios": {
            name: {
                "decision": result.commit.decision.value,
                "committed": result.commit.committed,
                "module_id": result.commit.module_id,
            }
            for name, result in report.evidence.results.items()
        },
        "test_output_tail": report.test_output_tail,
        "coverage_percent": report.coverage_matrix.coverage_percent,
        "contract_without_implementation": list(report.coverage_matrix.contract_without_implementation),
        "implementation_without_test": list(report.coverage_matrix.implementation_without_test),
        "test_without_evidence_or_audit": list(report.coverage_matrix.test_without_evidence_or_audit),
        "closure": {
            "is_closed": report.closure.is_closed,
            "unconnected": [list(pair) for pair in report.closure.unconnected],
        },
        "drift_findings": [
            {"req_id": d.req_id, "kind": d.kind, "detail": d.detail} for d in report.drift_findings
        ],
    }

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    return summary


def report_is_clean(report: VerificationReport) -> bool:
    return report.status is VerificationStatus.PASS
