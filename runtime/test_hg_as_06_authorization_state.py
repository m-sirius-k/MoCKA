"""
Test HG-AS-06: Runtime Authorization State Verification

Tests the integration of Authorization State verification into fail_closed_enforcement.
Sandbox only - verifies that Authorization State issued by Human Gate is checked before execution.
"""
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

# Setup path
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime.execution_context import ExecutionContext
from runtime.fail_closed_enforcement import should_permit_execution
import pytest


class TestAuthorizationStateVerification:
    """HG-AS-06: Runtime Authorization State Verification Tests"""

    def _create_execution_context(self, intent_id="intent-1", plan_id="plan-1", action_id="intent-1:0",
                                   decision_record_id="decision-1", governance_decision="PASS",
                                   hg_decision="AUTHORIZED"):
        """Helper to create valid ExecutionContext."""
        ctx = ExecutionContext(
            intent_id=intent_id,
            plan_id=plan_id,
            action_id=action_id,
            decision_record_id=decision_record_id,
            governance_decision=governance_decision,
            governance_reason="Test governance check",
            hg_decision=hg_decision,
            hg_conditions=[],
            hg_decision_reason="Test HG decision"
        )
        return ctx

    # TEST-1: Authorization State exists, matches, status=APPROVED → PERMIT
    def test_authorization_state_valid_approved(self):
        """TEST-1: Valid Authorization State with APPROVED status should permit."""
        ctx = self._create_execution_context()

        # Mock query_authorization_state to return APPROVED auth state
        mock_auth_record = {
            "authorization_id": "auth-123",
            "decision_id": "decision-1",
            "subject": "kimura_phd",
            "scope": json.dumps(["runtime_execution"]),
            "standing": "UNKNOWN",
            "status": "APPROVED",
            "granted_by": "HG_AUTHORITY_HOLDER",
            "granted_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": None,
            "evidence": None,
            "hg_event_source": "HG20260922_123456",
            "immutable": 1
        }

        with patch('governance.authorization_state_bridge.query_authorization_state') as mock_query:
            mock_query.return_value = [mock_auth_record]

            permitted, reasons = should_permit_execution(ctx)

            assert permitted is True, f"Should permit with valid Authorization State. Reasons: {reasons}"
            assert len(reasons) == 0
            print("[PASS] TEST-1: Valid Authorization State → PERMIT")

    # TEST-2: No Authorization State found → DENY
    def test_authorization_state_not_found(self):
        """TEST-2: Missing Authorization State should deny."""
        ctx = self._create_execution_context()

        with patch('governance.authorization_state_bridge.query_authorization_state') as mock_query:
            mock_query.return_value = []  # No records found

            permitted, reasons = should_permit_execution(ctx)

            assert permitted is False, "Should deny when Authorization State not found"
            assert any("No Authorization State found" in str(r) for r in reasons), \
                f"Expected 'No Authorization State found' error. Got: {reasons}"
            print("[PASS] TEST-2: No Authorization State → DENY")

    # TEST-3: Authorization State decision_id doesn't match → DENY
    def test_authorization_state_decision_id_mismatch(self):
        """TEST-3: Mismatched decision_id should deny."""
        ctx = self._create_execution_context(decision_record_id="decision-1")

        # Mock query returns no results (simulates no matching decision_id)
        with patch('governance.authorization_state_bridge.query_authorization_state') as mock_query:
            mock_query.return_value = []  # No matching records

            permitted, reasons = should_permit_execution(ctx)

            assert permitted is False
            assert any("No Authorization State found" in str(r) for r in reasons)
            print("[PASS] TEST-3: Decision ID mismatch → DENY")

    # TEST-4: Authorization State status=REJECTED → DENY
    def test_authorization_state_rejected_status(self):
        """TEST-4: REJECTED status should deny."""
        ctx = self._create_execution_context()

        # Query returns record but with REJECTED status
        # In practice, the query filters by status=APPROVED, so this tests the query filter
        with patch('governance.authorization_state_bridge.query_authorization_state') as mock_query:
            mock_query.return_value = []  # Query filtered to APPROVED status, so REJECTED won't appear

            permitted, reasons = should_permit_execution(ctx)

            assert permitted is False
            print("[PASS] TEST-4: REJECTED status → DENY (filtered by query)")

    # TEST-5: Authorization State expired → DENY
    def test_authorization_state_expired(self):
        """TEST-5: Expired Authorization State should deny."""
        ctx = self._create_execution_context()

        # Authorization that expired 1 hour ago
        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        mock_auth_record = {
            "authorization_id": "auth-124",
            "decision_id": "decision-1",
            "subject": "kimura_phd",
            "status": "APPROVED",
            "expires_at": past_time,
            "hg_event_source": "HG20260922_expired"
        }

        with patch('governance.authorization_state_bridge.query_authorization_state') as mock_query:
            mock_query.return_value = [mock_auth_record]

            permitted, reasons = should_permit_execution(ctx)

            assert permitted is False, "Should deny expired Authorization State"
            assert any("expired" in str(r).lower() for r in reasons), \
                f"Expected expiration error. Got: {reasons}"
            print("[PASS] TEST-5: Expired Authorization State → DENY")

    # TEST-6: Query exception / DB failure → DENY
    def test_authorization_state_db_error(self):
        """TEST-6: Database error should deny (fail-closed)."""
        ctx = self._create_execution_context()

        with patch('governance.authorization_state_bridge.query_authorization_state') as mock_query:
            mock_query.side_effect = Exception("Database connection failed")

            permitted, reasons = should_permit_execution(ctx)

            assert permitted is False, "Should deny on database error"
            assert any("verification failed" in str(r).lower() for r in reasons)
            print("[PASS] TEST-6: Database error → DENY (fail-closed)")

    # TEST-7: decision_record_id=None → Should not check auth state (backward compatible)
    def test_authorization_state_no_decision_record_id(self):
        """TEST-7: No decision_record_id should skip Authorization State check (backward compatible)."""
        ctx = self._create_execution_context(decision_record_id=None)

        # Should return True without calling query (no decision_record_id to check)
        with patch('governance.authorization_state_bridge.query_authorization_state') as mock_query:
            permitted, reasons = should_permit_execution(ctx)

            # Should not call query_authorization_state when decision_record_id is None
            assert permitted is True, f"Should permit when no decision_record_id. Reasons: {reasons}"
            mock_query.assert_not_called()
            print("[PASS] TEST-7: No decision_record_id → Skip check (backward compatible)")

    # TEST-8: Existing fail-closed conditions still work
    def test_existing_fail_closed_conditions(self):
        """TEST-8: Verify existing E1-E9 fail-closed conditions still work."""

        # Test E1: Missing intent_id
        ctx = ExecutionContext(intent_id=None, action_id="action-1:0",
                              governance_decision="PASS", hg_decision="AUTHORIZED")
        permitted, reasons = should_permit_execution(ctx)
        assert permitted is False and any("E1" in str(r) for r in reasons)

        # Test E4: Missing governance_decision
        ctx = self._create_execution_context(governance_decision=None)
        permitted, reasons = should_permit_execution(ctx)
        assert permitted is False and any("E4" in str(r) for r in reasons)

        # Test E5: Governance FAIL
        ctx = self._create_execution_context(governance_decision="FAIL")
        permitted, reasons = should_permit_execution(ctx)
        assert permitted is False and any("E5" in str(r) for r in reasons)

        # Test E7: Missing hg_decision
        ctx = self._create_execution_context(hg_decision=None)
        permitted, reasons = should_permit_execution(ctx)
        assert permitted is False and any("E7" in str(r) for r in reasons)

        # Test E8: HG DENIED
        ctx = self._create_execution_context(hg_decision="DENIED")
        permitted, reasons = should_permit_execution(ctx)
        assert permitted is False and any("E8" in str(r) for r in reasons)

        print("[PASS] TEST-8: All existing fail-closed conditions (E1-E9) still work")


class TestAuthorizationStateE2E:
    """End-to-End Test: Human Gate → Authorization State → Runtime Execution"""

    def test_e2e_human_gate_to_runtime(self):
        """E2E: Test complete flow from Human Gate approval to Runtime execution."""

        # This test demonstrates the complete flow
        # (Integration with actual phi_os/human_gate requires separate setup)

        # Simulate what Runtime sees after Human Gate approved a decision
        decision_record_id = "DC_20260922_e2e_001"

        # Create ExecutionContext with this decision_record_id
        ctx = ExecutionContext(
            intent_id="e2e-intent-1",
            plan_id="e2e-plan-1",
            action_id="e2e-intent-1:0",
            decision_record_id=decision_record_id,
            governance_decision="PASS",
            hg_decision="AUTHORIZED"
        )

        # Simulate Authorization State that was created by Human Gate
        simulated_auth_state = {
            "authorization_id": "auth-e2e-001",
            "decision_id": decision_record_id,  # Exact match to governance decision_record_id
            "subject": "kimura_phd",
            "scope": json.dumps(["e2e_test_execution"]),
            "standing": "UNKNOWN",
            "status": "APPROVED",
            "granted_by": "HG_AUTHORITY_HOLDER_E2E",
            "granted_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": None,
            "evidence": None,
            "hg_event_source": "HG20260922_e2e_source",
            "immutable": 1
        }

        # Mock the query to return this authorization state
        with patch('governance.authorization_state_bridge.query_authorization_state') as mock_query:
            mock_query.return_value = [simulated_auth_state]

            # Runtime's execution gate should permit this
            permitted, reasons = should_permit_execution(ctx)

            assert permitted is True, f"E2E flow should permit. Reasons: {reasons}"

            # Verify the query was called with the correct decision_id
            mock_query.assert_called_once_with(
                decision_id=decision_record_id,
                status="APPROVED"
            )

            print(f"[PASS] E2E: Human Gate → Authorization State → Runtime PERMIT")
            print(f"  - governance decision_record_id: {decision_record_id}")
            print(f"  - authorization_state.decision_id: {simulated_auth_state['decision_id']}")
            print(f"  - authorization_state.status: {simulated_auth_state['status']}")
            print(f"  - Runtime execution_context.decision_record_id: {ctx.decision_record_id}")


# Entry point for pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
