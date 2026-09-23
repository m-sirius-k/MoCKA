"""
Decision Ledger Runtime Authorization Check
Minimal helper for querying runtime authorization decisions.
"""
import json
from pathlib import Path

DECISION_LEDGER_PATH = Path(__file__).parent.parent / "data" / "decisions" / "decision_ledger.jsonl"


def check_runtime_authorization(runtime_scope: str) -> dict:
    """
    Query decision_ledger.jsonl for RUNTIME_AUTHORIZATION decisions.

    Args:
        runtime_scope: "SEAL" | "MCP_WRITE" | "AUTO_APPROVAL"

    Returns:
        {
            "authorized": bool,
            "decision_id": str | None,
            "reason": str,
            "approved_by": str | None
        }
    """
    if not DECISION_LEDGER_PATH.exists():
        return {
            "authorized": False,
            "decision_id": None,
            "reason": "decision_ledger.jsonl not found",
            "approved_by": None
        }

    try:
        with open(DECISION_LEDGER_PATH, "r", encoding="utf-8") as f:
            entries = [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        return {
            "authorized": False,
            "decision_id": None,
            "reason": f"error reading decision_ledger: {e}",
            "approved_by": None
        }

    for entry in reversed(entries):
        if (entry.get("decision_purpose") == "RUNTIME_AUTHORIZATION" and
            entry.get("runtime_scope") == runtime_scope and
            entry.get("decision") == "approved" and
            entry.get("status") == "Active"):

            approved_by = entry.get("approved_by")
            return {
                "authorized": True,
                "decision_id": entry.get("decision_id"),
                "reason": "authorized",
                "approved_by": approved_by
            }

    return {
        "authorized": False,
        "decision_id": None,
        "reason": f"no active RUNTIME_AUTHORIZATION found for scope={runtime_scope}",
        "approved_by": None
    }
