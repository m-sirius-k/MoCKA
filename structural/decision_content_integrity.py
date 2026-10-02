"""
GL10: Decision Content Integrity Engine

Verifies that decision records have not been tampered with.
Responsibilities:
  1. Compute SHA256 hash of decision payload
  2. Compare against stored content_hash
  3. Verify immutable fields are unchanged
  4. Fast-fail on hash mismatch (detects tampering)
"""

import hashlib
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class GL10Result:
    """GL10 content integrity verification result"""
    allowed: bool
    content_hash: Optional[str] = None
    stored_hash: Optional[str] = None
    failure_reason: Optional[str] = None
    failure_code: str = "GL10_OK"


class DecisionContentIntegrityEngine:
    """
    GL10 Engine: Decision Content Integrity

    Detects tampering with decision records through cryptographic hashing.
    Ensures immutable fields (decision, rationale, impact) match original hash.
    """

    # Fields that are immutable and included in content hash
    IMMUTABLE_FIELDS = {
        "decision_id",
        "title",
        "context",
        "alternatives",
        "decision",
        "rationale",
        "impact",
    }

    def verify_content_integrity(
        self,
        decision_record: Optional[Dict[str, Any]],
        stored_hash: Optional[str]
    ) -> GL10Result:
        """
        Verify that decision content has not been tampered with.

        Args:
            decision_record: Full decision record from Decision Ledger
            stored_hash: SHA256 hash stored with the decision

        Returns:
            GL10Result with allow/deny decision
        """
        # Check 1: Record must exist
        if not decision_record:
            return GL10Result(
                allowed=False,
                stored_hash=stored_hash,
                failure_reason="No decision record provided",
                failure_code="GL10_FAIL_1_MISSING_RECORD"
            )

        # Check 2: Stored hash must be provided
        if not stored_hash:
            return GL10Result(
                allowed=False,
                failure_reason="No content_hash stored with decision",
                failure_code="GL10_FAIL_2_MISSING_HASH"
            )

        # Check 3: Compute hash of immutable fields
        computed_hash = self._compute_content_hash(decision_record)

        if not computed_hash:
            return GL10Result(
                allowed=False,
                stored_hash=stored_hash,
                failure_reason="Failed to compute content hash",
                failure_code="GL10_FAIL_3_HASH_COMPUTATION_FAILED"
            )

        # Check 4: Compare computed hash with stored hash
        if computed_hash != stored_hash:
            return GL10Result(
                allowed=False,
                content_hash=computed_hash,
                stored_hash=stored_hash,
                failure_reason=f"Content hash mismatch: computed {computed_hash[:16]}... != stored {stored_hash[:16]}...",
                failure_code="GL10_FAIL_4_HASH_MISMATCH_TAMPERING_DETECTED"
            )

        # All checks passed
        return GL10Result(
            allowed=True,
            content_hash=computed_hash,
            stored_hash=stored_hash,
            failure_code="GL10_OK"
        )

    def _compute_content_hash(self, decision_record: Dict[str, Any]) -> Optional[str]:
        """
        Compute SHA256 hash of immutable decision fields.

        Args:
            decision_record: Full decision record

        Returns:
            Hex-encoded SHA256 hash or None if computation fails
        """
        try:
            # Extract immutable fields in consistent order
            immutable = {}
            for field in sorted(self.IMMUTABLE_FIELDS):
                if field in decision_record:
                    immutable[field] = decision_record[field]

            # Serialize to JSON (canonical form)
            payload = json.dumps(immutable, sort_keys=True, ensure_ascii=False)

            # Compute SHA256
            hash_obj = hashlib.sha256(payload.encode("utf-8"))
            return hash_obj.hexdigest()

        except Exception as e:
            print(f"GL10: Error computing content hash: {e}")
            return None

    def compute_decision_hash(self, decision_record: Dict[str, Any]) -> str:
        """
        Compute and return content hash for a decision record.
        Called when creating new decision records to generate stored_hash.

        Args:
            decision_record: Full decision record

        Returns:
            Hex-encoded SHA256 hash
        """
        return self._compute_content_hash(decision_record) or ""

    def get_immutable_fields(self) -> set:
        """
        Get list of fields included in content hash.

        Returns:
            Set of immutable field names
        """
        return self.IMMUTABLE_FIELDS.copy()


# Singleton instance
_gl10_engine = None


def get_gl10_engine() -> DecisionContentIntegrityEngine:
    """Get or create GL10 engine singleton"""
    global _gl10_engine
    if _gl10_engine is None:
        _gl10_engine = DecisionContentIntegrityEngine()
    return _gl10_engine
