# phi_os/tests/test_hg_as_01_integration.py
# HG-AS-01 Integration Test: Human Gate Approve → Authorization State
# Purpose: Verify end-to-end connection of approve() → authorization_state creation
import sys
import sqlite3
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
import phi_os.human_gate as hg
from governance.authorization_state_bridge import query_authorization_state, get_authorization_state


@pytest.fixture
def conn(tmp_path):
    """Create test database with both human_gate_events and authorization_state tables."""
    db_file = str(tmp_path / 'test_hg_as_01.db')
    c = sqlite3.connect(db_file)
    c.row_factory = sqlite3.Row

    # Initialize both tables
    hg._ensure_table(c)
    from governance.authorization_state_bridge import _ensure_authorization_state_table
    _ensure_authorization_state_table(c)

    yield c
    c.close()


class TestHGAS01Integration:
    """Test approve() integration with authorization_state_bridge."""

    def test_approve_with_valid_hg_as_01_payload(self, conn):
        """CORE: Valid payload should create both human_gate_event AND authorization_state."""
        request_id = "TEST_AS01_VALID"

        # Submit creates PENDING
        hg.submit({"request_id": request_id}, conn=conn)

        # Approve with HG-AS-01 required fields
        valid_payload = {
            "actor": "kimura_phd",
            "scope": ["component_A", "component_J"],
            "authority_role": "HG_AUTHORITY_HOLDER_01",
            "decision_id": "DC_20260922_001",
            "evidence_ref": ["PAPER5_PHASE2_20260918"],
        }
        event = hg.approve(request_id, valid_payload, conn=conn)

        # Verify state transition recorded
        assert event["next_state"] == "APPROVED"
        assert hg.get_state(request_id, conn=conn) == "APPROVED"

        # Verify authorization_state was created
        assert event.get("authorization_state_issued") == True
        assert event.get("authorization_id") is not None

        # Verify authorization_state record exists
        auth_id = event["authorization_id"]
        auth_record = get_authorization_state(auth_id, conn=conn)
        assert auth_record is not None

        # Verify fields transferred correctly
        assert auth_record["subject"] == "kimura_phd"
        assert auth_record["granted_by"] == "HG_AUTHORITY_HOLDER_01"
        assert auth_record["status"] == "APPROVED"
        assert auth_record["standing"] == "UNKNOWN"  # HG-AS-01 requirement

        # Verify scope transferred as JSON
        scope = json.loads(auth_record["scope"])
        assert scope == ["component_A", "component_J"]

        # Verify traceability
        assert auth_record["hg_event_source"] == event["event_id"]
        assert auth_record["immutable"] == 1

    def test_approve_with_invalid_payload_no_actor(self, conn):
        """Invalid payload (missing actor): state transition succeeds, authorization_state NOT created."""
        request_id = "TEST_AS01_INVALID_NO_ACTOR"

        hg.submit({"request_id": request_id}, conn=conn)

        invalid_payload = {
            # Missing "actor"
            "scope": ["component_A"],
            "authority_role": "HG_AUTHORITY_HOLDER_01",
        }
        event = hg.approve(request_id, invalid_payload, conn=conn)

        # State transition still succeeds (backward compatible)
        assert event["next_state"] == "APPROVED"
        assert hg.get_state(request_id, conn=conn) == "APPROVED"

        # Authorization state NOT issued
        assert event.get("authorization_state_issued") == False
        assert event.get("authorization_validation_error") is not None
        assert "missing mandatory field: actor" in event["authorization_validation_error"]

        # Verify no authorization_state record created
        auth_records = query_authorization_state(subject="UNKNOWN", conn=conn)
        for record in auth_records:
            # Should not find any record linked to this request
            assert record["hg_event_source"] != event["event_id"]

    def test_approve_with_invalid_payload_empty_scope(self, conn):
        """Invalid payload (empty scope array): authorization_state NOT created."""
        request_id = "TEST_AS01_INVALID_EMPTY_SCOPE"

        hg.submit({"request_id": request_id}, conn=conn)

        invalid_payload = {
            "actor": "kimura_phd",
            "scope": [],  # Empty array invalid
            "authority_role": "HG_AUTHORITY_HOLDER_01",
        }
        event = hg.approve(request_id, invalid_payload, conn=conn)

        # State transition still succeeds
        assert event["next_state"] == "APPROVED"

        # Authorization state NOT issued
        assert event.get("authorization_state_issued") == False
        assert "non-empty array" in event["authorization_validation_error"]

    def test_approve_with_minimal_valid_payload(self, conn):
        """Minimal valid payload (only mandatory fields)."""
        request_id = "TEST_AS01_MINIMAL"

        hg.submit({"request_id": request_id}, conn=conn)

        minimal_payload = {
            "actor": "test_user",
            "scope": ["component_A"],
            "authority_role": "HG_AUTHORITY_HOLDER",
        }
        event = hg.approve(request_id, minimal_payload, conn=conn)

        assert event.get("authorization_state_issued") == True
        auth_id = event["authorization_id"]
        auth_record = get_authorization_state(auth_id, conn=conn)

        # Verify mandatory fields
        assert auth_record["subject"] == "test_user"
        assert auth_record["granted_by"] == "HG_AUTHORITY_HOLDER"
        assert auth_record["standing"] == "UNKNOWN"

        # Optional fields should be None/null
        assert auth_record["decision_id"] is None
        assert auth_record["expires_at"] is None
        assert auth_record["evidence"] is None

    def test_approve_without_payload_backward_compatible(self, conn):
        """approve() with no payload should still work (backward compatible)."""
        request_id = "TEST_AS01_NO_PAYLOAD"

        hg.submit({"request_id": request_id}, conn=conn)

        # Old behavior: approve without payload
        event = hg.approve(request_id, conn=conn)  # payload=None

        # State transition succeeds
        assert event["next_state"] == "APPROVED"

        # Authorization state NOT issued (no payload to validate)
        assert event.get("authorization_state_issued") == False

    def test_standing_unknown_recorded(self, conn):
        """HG-AS-01 requirement: standing field must always be UNKNOWN."""
        request_id = "TEST_AS01_STANDING"

        hg.submit({"request_id": request_id}, conn=conn)

        payload = {
            "actor": "test",
            "scope": ["A"],
            "authority_role": "HG_ROLE",
        }
        event = hg.approve(request_id, payload, conn=conn)

        auth_id = event["authorization_id"]
        auth_record = get_authorization_state(auth_id, conn=conn)

        # Verify standing is UNKNOWN per HG-AS-01
        assert auth_record["standing"] == "UNKNOWN"

    def test_append_only_constraint(self, conn):
        """Verify authorization_state append-only constraint is enforced."""
        request_id = "TEST_AS01_APPEND_ONLY"

        hg.submit({"request_id": request_id}, conn=conn)

        payload = {
            "actor": "test",
            "scope": ["A"],
            "authority_role": "HG_ROLE",
        }
        event = hg.approve(request_id, payload, conn=conn)
        auth_id = event["authorization_id"]

        # Try to update (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "UPDATE authorization_state SET standing = 'HELD' WHERE authorization_id = ?",
                (auth_id,)
            )
            conn.commit()

        # Try to delete (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "DELETE FROM authorization_state WHERE authorization_id = ?",
                (auth_id,)
            )
            conn.commit()

    def test_existing_human_gate_tests_still_pass(self, conn):
        """Regression test: existing Human Gate behavior unchanged."""
        # From test_human_gate.py:test_approve_from_pending_succeeds
        hg.submit({"request_id": "R2"}, conn=conn)
        event = hg.approve("R2", conn=conn)

        assert event["previous_state"] == "PENDING"
        assert event["next_state"] == "APPROVED"
        assert hg.get_state("R2", conn=conn) == "APPROVED"


class TestAuthorizationStateTraceability:
    """Verify traceability between human_gate_events and authorization_state."""

    def test_hg_event_source_traceback(self, conn):
        """authorization_state.hg_event_source should link back to human_gate_events.event_id."""
        request_id = "TEST_TRACE_001"

        hg.submit({"request_id": request_id}, conn=conn)

        payload = {
            "actor": "tracer",
            "scope": ["A"],
            "authority_role": "HG_ROLE",
        }
        event = hg.approve(request_id, payload, conn=conn)

        # Get the human_gate_events record
        c = conn.cursor()
        hg_event = c.execute(
            "SELECT * FROM human_gate_events WHERE request_id = ? AND action = 'approve'",
            (request_id,)
        ).fetchone()

        # Get the authorization_state record
        auth_id = event["authorization_id"]
        auth_record = get_authorization_state(auth_id, conn=conn)

        # Verify linkage
        assert auth_record["hg_event_source"] == hg_event["event_id"]
        assert auth_record["hg_event_timestamp"] == hg_event["timestamp"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
