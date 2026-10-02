"""
GL8: Human Gate Authorization Integrity Engine

Verifies that tool execution is authorized by Human Gate decision.
Responsibilities:
  1. Extract decision_id from tool args
  2. Lookup decision in Decision Ledger
  3. Validate decision status (must be Active)
  4. Verify approved_by authority
  5. Fast-fail if any check fails
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GL8Decision:
    """Decision record from Decision Ledger"""
    decision_id: str
    title: str
    status: str  # Active, Superseded, Withdrawn
    approved_by: str
    approved_at: str
    authorized_scope: Optional[List[str]] = None
    content_hash: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


@dataclass
class GL8Result:
    """GL8 verification result"""
    allowed: bool
    decision: Optional[GL8Decision] = None
    failure_reason: Optional[str] = None
    failure_code: str = "GL8_OK"


class HumanGateAuthorizationIntegrityEngine:
    """
    GL8 Engine: Human Gate Authorization Integrity

    Fast-fail layer for decision authorization verification.
    Prevents execution of unauthorized tools before governance pipeline runs.
    """

    AUTHORIZED_APPROVERS = {
        "きむら博士",  # Primary authority
    }

    DECISION_LEDGER_PATH = Path("/home/user/MoCKA/data/decisions/decision_ledger.jsonl")

    def __init__(self):
        """Initialize GL8 engine"""
        self.decision_cache = {}

    def verify_authorization(self, tool_name: str, args: Dict[str, Any]) -> GL8Result:
        """
        Verify that tool execution is authorized by Decision Ledger.

        Args:
            tool_name: Name of MCP tool being executed
            args: Tool arguments (may contain decision_id)

        Returns:
            GL8Result with allow/deny decision
        """
        # Step 1: Extract decision_id from args
        decision_id = args.get("decision_id")

        if not decision_id:
            return GL8Result(
                allowed=False,
                failure_reason="No decision_id in tool args",
                failure_code="GL8_FAIL_1_MISSING_DECISION_ID"
            )

        # Step 2: Lookup decision in ledger
        decision = self._lookup_decision(decision_id)

        if not decision:
            return GL8Result(
                allowed=False,
                failure_reason=f"Decision {decision_id} not found in ledger",
                failure_code="GL8_FAIL_2_DECISION_NOT_FOUND"
            )

        # Step 3: Validate decision status
        if decision.status != "Active":
            return GL8Result(
                allowed=False,
                decision=decision,
                failure_reason=f"Decision status is {decision.status}, not Active",
                failure_code="GL8_FAIL_3_INACTIVE_DECISION"
            )

        # Step 4: Verify approved_by authority
        if decision.approved_by not in self.AUTHORIZED_APPROVERS:
            return GL8Result(
                allowed=False,
                decision=decision,
                failure_reason=f"Approver {decision.approved_by} not in authorized list",
                failure_code="GL8_FAIL_4_UNAUTHORIZED_APPROVER"
            )

        # All checks passed
        return GL8Result(
            allowed=True,
            decision=decision,
            failure_code="GL8_OK"
        )

    def _lookup_decision(self, decision_id: str) -> Optional[GL8Decision]:
        """
        Lookup decision record in Decision Ledger.

        Args:
            decision_id: Decision ID (DC_YYYYMMDD_NNN format)

        Returns:
            GL8Decision object or None if not found
        """
        # Check cache first
        if decision_id in self.decision_cache:
            return self.decision_cache[decision_id]

        # Read from Decision Ledger JSONL
        if not self.DECISION_LEDGER_PATH.exists():
            return None

        try:
            with open(self.DECISION_LEDGER_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    record = json.loads(line)

                    if record.get("decision_id") == decision_id:
                        decision = GL8Decision(
                            decision_id=record.get("decision_id"),
                            title=record.get("title"),
                            status=record.get("status"),
                            approved_by=record.get("approved_by"),
                            approved_at=record.get("approved_at"),
                            authorized_scope=record.get("authorized_scope"),
                            content_hash=record.get("content_hash"),
                            raw=record
                        )

                        # Cache for future lookups
                        self.decision_cache[decision_id] = decision
                        return decision

        except (IOError, json.JSONDecodeError) as e:
            print(f"GL8: Error reading Decision Ledger: {e}")
            return None

        return None

    def get_authorized_scope(self, decision: GL8Decision) -> Optional[List[str]]:
        """
        Extract authorized scope from decision record.
        Used by GL9 for scope binding verification.

        Args:
            decision: GL8Decision object from verification

        Returns:
            List of authorized scopes or None if undefined
        """
        return decision.authorized_scope if decision else None

    def get_content_hash(self, decision: GL8Decision) -> Optional[str]:
        """
        Extract content hash from decision record.
        Used by GL10 for content integrity verification.

        Args:
            decision: GL8Decision object from verification

        Returns:
            SHA256 content hash or None if undefined
        """
        return decision.content_hash if decision else None

    def clear_cache(self):
        """Clear decision cache (useful for testing)"""
        self.decision_cache.clear()


# Singleton instance
_gl8_engine = None


def get_gl8_engine() -> HumanGateAuthorizationIntegrityEngine:
    """Get or create GL8 engine singleton"""
    global _gl8_engine
    if _gl8_engine is None:
        _gl8_engine = HumanGateAuthorizationIntegrityEngine()
    return _gl8_engine
