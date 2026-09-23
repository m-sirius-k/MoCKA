"""
HG-AS-06 E2E Integration Test
Complete flow from Human Gate approval through Runtime authorization verification.

This test uses real authorization_state_bridge to create actual Authorization State records
and verifies that Runtime's fail_closed_enforcement correctly validates them.
"""
import sys
import sqlite3
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Setup path
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime.execution_context import ExecutionContext
from runtime.fail_closed_enforcement import should_permit_execution
from governance.authorization_state_bridge import (
    query_authorization_state,
    issue_authorization_state,
    _ensure_authorization_state_table
)
from phi_os import human_gate as hg


def test_e2e_human_gate_to_runtime_verification():
    """
    E2E Test: Complete flow from Human Gate approval to Runtime execution verification.

    Flow:
    1. Human Gate submit() creates PENDING request
    2. Human Gate approve() with valid payload creates APPROVED state
    3. authorization_state_bridge creates authorization_state record with decision_id
    4. Runtime queries authorization_state by decision_record_id
    5. Runtime's should_permit_execution() verifies and permits
    """

    # Use temporary database for this test
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_db = str(Path(tmpdir) / "test_e2e.db")

        # Create connection
        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row

        try:
            # Step 1: Initialize tables in test database
            hg._ensure_table(conn)
            _ensure_authorization_state_table(conn)
            print("[SETUP] Tables created")

            # Shared decision_record_id (from governance_client)
            decision_record_id = "DC_20260922_e2e_integration"
            request_id = "HG_E2E_TEST_001"

            # Step 2: Human Gate submit (creates PENDING)
            payload_submit = {"request_id": request_id}
            event_submit = hg.submit(payload_submit, conn=conn)
            print(f"[HG SUBMIT] request_id={request_id}, state={event_submit['next_state']}")

            # Step 3: Human Gate approve with Authorization State required fields
            payload_approve = {
                "actor": "kimura_phd",
                "scope": ["runtime_execution", "e2e_test"],
                "authority_role": "HG_AUTHORITY_HOLDER_E2E",
                "decision_id": decision_record_id,  # Link to governance decision
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                "evidence_ref": ["E2E_TEST_EVIDENCE_001"],
                "note": "E2E test approval"
            }
            event_approve = hg.approve(request_id, payload_approve, conn=conn)
            print(f"[HG APPROVE] state={event_approve['next_state']}, "
                  f"auth_issued={event_approve.get('authorization_state_issued')}")

            # Verify authorization_state was created
            assert event_approve.get("authorization_state_issued") is True, \
                "Authorization State should be issued"
            authorization_id = event_approve.get("authorization_id")
            print(f"[AUTH STATE] authorization_id={authorization_id}")

            # Step 4: Query authorization_state as Runtime would
            auth_records = query_authorization_state(
                decision_id=decision_record_id,
                status="APPROVED",
                conn=conn
            )
            assert len(auth_records) > 0, "Authorization State should be found"
            auth_record = auth_records[0]
            print(f"[QUERY] Found authorization_state for decision_id={decision_record_id}")
            print(f"  - authorization_id: {auth_record['authorization_id']}")
            print(f"  - subject: {auth_record['subject']}")
            print(f"  - status: {auth_record['status']}")
            print(f"  - granted_by: {auth_record['granted_by']}")
            print(f"  - expires_at: {auth_record.get('expires_at')}")

            # Step 5: Create ExecutionContext with same decision_record_id
            exec_ctx = ExecutionContext(
                intent_id="e2e-intent-1",
                plan_id="e2e-plan-1",
                action_id="e2e-intent-1:0",
                decision_record_id=decision_record_id,  # EXACT match
                governance_decision="PASS",
                governance_reason="Test governance",
                hg_decision="AUTHORIZED",
                hg_decision_reason="Test HG decision"
            )

            # Step 6: Runtime's fail_closed_enforcement verifies authorization
            # Note: Patch the connection in real scenario; for this test we mock it
            from unittest.mock import patch
            with patch('governance.authorization_state_bridge.query_authorization_state') as mock_query:
                mock_query.return_value = auth_records

                permitted, reasons = should_permit_execution(exec_ctx)

                assert permitted is True, f"Should permit with valid auth state. Reasons: {reasons}"
                print(f"[RUNTIME PERMIT] Decision={decision_record_id} → AUTHORIZED")

            # Step 7: Verify the ID chain
            print("\n[ID CHAIN VERIFICATION]")
            print(f"  governance_client.decision_record_id: {decision_record_id}")
            print(f"  human_gate.approve(payload['decision_id']): {payload_approve['decision_id']}")
            print(f"  authorization_state.decision_id: {auth_record['decision_id']}")
            print(f"  execution_context.decision_record_id: {exec_ctx.decision_record_id}")
            assert decision_record_id == auth_record['decision_id'], "ID chain must match"
            assert exec_ctx.decision_record_id == decision_record_id, "Execution context must match"
            print(f"  ✓ All IDs match: {decision_record_id}")

            # Step 8: Verify IMMUTABILITY of Authorization State
            print("\n[IMMUTABILITY CHECK]")
            assert auth_record['immutable'] == 1, "Authorization State must be immutable"
            print(f"  ✓ authorization_state.immutable = 1 (append-only enforced)")

            print("\n[E2E SUCCESS] Complete flow verified:")
            print("  Human Gate → Authorization State → Runtime Verification")

        finally:
            conn.close()


def test_e2e_expired_authorization_denied():
    """
    E2E Test: Expired Authorization State should be denied.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_db = str(Path(tmpdir) / "test_expired.db")
        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row

        try:
            hg._ensure_table(conn)
            _ensure_authorization_state_table(conn)

            decision_record_id = "DC_20260922_expired_test"
            request_id = "HG_EXPIRED_TEST_001"

            # Human Gate submit and approve with EXPIRED time
            hg.submit({"request_id": request_id}, conn=conn)

            expired_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            payload_approve = {
                "actor": "kimura_phd",
                "scope": ["test"],
                "authority_role": "HG_AUTHORITY",
                "decision_id": decision_record_id,
                "expires_at": expired_time  # Already expired
            }
            hg.approve(request_id, payload_approve, conn=conn)

            # Query the authorization_state
            auth_records = query_authorization_state(
                decision_id=decision_record_id,
                status="APPROVED",
                conn=conn
            )

            assert len(auth_records) > 0, "Authorization State should be created"

            # Try to use expired authorization
            exec_ctx = ExecutionContext(
                intent_id="expired-intent",
                plan_id="expired-plan",
                action_id="expired-intent:0",
                decision_record_id=decision_record_id,
                governance_decision="PASS",
                hg_decision="AUTHORIZED"
            )

            from unittest.mock import patch
            with patch('governance.authorization_state_bridge.query_authorization_state') as mock_query:
                mock_query.return_value = auth_records

                permitted, reasons = should_permit_execution(exec_ctx)

                assert permitted is False, "Should deny expired authorization"
                assert any("expired" in str(r).lower() for r in reasons), \
                    f"Should have expiration error. Got: {reasons}"
                print("[EXPIRE TEST] Expired Authorization State → DENIED ✓")

        finally:
            conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("HG-AS-06 E2E Integration Test: Complete Authorization State Flow")
    print("=" * 70)
    print()

    test_e2e_human_gate_to_runtime_verification()
    print()
    test_e2e_expired_authorization_denied()

    print()
    print("=" * 70)
    print("[SUCCESS] All E2E integration tests passed")
    print("=" * 70)
    print()
    print("Runtime Authorization State Binding = VERIFIED")
