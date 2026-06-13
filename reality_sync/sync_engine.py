# -*- coding: utf-8 -*-
"""Sync Engine (Phase 4-2 Reality Sync Layer)

中核処理フロー:

    CodeStateSnapshot
       v
    ReportStateValidator
       v
    DiscrepancyDetector
       v
    TruthChecker
       v
    SyncResult
"""

from reality_sync.code_state_scanner import scan
from reality_sync.report_state_validator import validate
from reality_sync.truth_checker import determine_truth
from reality_sync.discrepancy_detector import detect
from reality_sync.sync_registry import SEVERITY_MAP
from reality_sync.sync_result_model import SyncResult


def run() -> list[SyncResult]:
    snapshot = scan()
    claims = validate()

    results: list[SyncResult] = []

    for entry in snapshot:
        actual_status, evidence = determine_truth(entry)
        discrepancy_type, reported_status, sources = detect(entry.file_path, actual_status, claims)
        severity = SEVERITY_MAP.get(discrepancy_type, "NONE")
        fix_required = actual_status == "BROKEN"

        results.append(SyncResult(
            file_path=entry.file_path,
            reported_status=reported_status,
            actual_status=actual_status,
            discrepancy_type=discrepancy_type,
            severity=severity,
            fix_required=fix_required,
            evidence=evidence,
            sources=sources,
        ))

    return results


if __name__ == "__main__":
    for r in run():
        print(r)
