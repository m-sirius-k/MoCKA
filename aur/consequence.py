"""
aur/consequence.py: Actual Consequence recording.

"Execution Success != Actual Consequence Verified" (core MoCKA principle)

Contract: docs/contracts/actual_consequence_contract_v1.md
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class ConsequenceRecord:
    consequence_id: str
    action_id: str
    assessment_id: str
    timestamp: str
    execution_success: bool
    consequence_verified: bool
    verification_method: str
    actual_changes: list
    expected_changes: list
    deviation: list
    outcome: str
    error_detail: str = ""
    verification_error: str = ""


def _generate_id() -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"CONSQ-{today}-{uuid.uuid4().hex[:8]}"


def _compute_deviation(actual: list, expected: list) -> list:
    """Return symmetric difference: changes that were unexpected or missing."""
    actual_set = set(actual)
    expected_set = set(expected)
    return list((actual_set - expected_set) | (expected_set - actual_set))


def _classify_outcome(
    execution_success: bool,
    consequence_verified: bool,
    deviation: list,
    verification_method: str,
) -> str:
    if not execution_success:
        return "FAILURE"
    if verification_method == "unverified" or not consequence_verified:
        return "UNKNOWN"
    if deviation:
        return "PARTIAL"
    return "SUCCESS"


def create_consequence(
    action_id: str,
    assessment_id: str,
    execution_success: bool,
    actual_changes: list,
    expected_changes: list,
    verification_method: str,
    error_detail: str = "",
    verification_error: str = "",
) -> ConsequenceRecord:
    """
    Create a ConsequenceRecord after an action has been executed (or attempted).

    verification_method: "git_diff" | "file_hash" | "db_query" | "api_response"
                         | "manual" | "unverified"
    """
    deviation = _compute_deviation(actual_changes, expected_changes)

    consequence_verified = (
        verification_method != "unverified"
        and not verification_error
        and execution_success
    )

    outcome = _classify_outcome(
        execution_success, consequence_verified, deviation, verification_method
    )

    return ConsequenceRecord(
        consequence_id=_generate_id(),
        action_id=action_id,
        assessment_id=assessment_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        execution_success=execution_success,
        consequence_verified=consequence_verified,
        verification_method=verification_method,
        actual_changes=list(actual_changes),
        expected_changes=list(expected_changes),
        deviation=deviation,
        outcome=outcome,
        error_detail=error_detail,
        verification_error=verification_error,
    )
