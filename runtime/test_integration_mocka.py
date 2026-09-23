"""
Test Step 9: MoCKA Side — Execution Integration

Tests T2-T3 integration from MoCKA perspective:
- hg_gateway sends request to execution-runtime-system
- Evidence state response handling
- Institutional closure gating (NI-005: A)
- Consequence preservation (NI-006)
"""
import json
from unittest.mock import patch, MagicMock
from execution_context import ExecutionContext
from hg_gateway import authorize_and_execute, _send_to_execution_runtime


# Mock execution-runtime-system responses
def mock_runtime_response_success():
    """Successful execution + verified evidence."""
    return {
        "execution_id": "exec-123",
        "status": "success",
        "result": {"data": "executed"},
        "evidence_state": "VERIFIED",
        "evidence_reference": "hash-abc123"
    }


def mock_runtime_response_evidence_failure():
    """Successful execution but evidence write failed."""
    return {
        "execution_id": "exec-124",
        "status": "success",
        "result": {"data": "executed"},
        "evidence_state": "EVIDENCE_PENDING_RETRY",
        "evidence_reference": None
    }


def mock_runtime_response_transmission_error():
    """Transmission to execution-runtime-system failed."""
    return {
        "execution_id": "UNKNOWN",
        "status": "ERROR",
        "result": "Connection refused",
        "evidence_state": "EVIDENCE_FAILED_IMMEDIATE",
        "evidence_reference": None
    }


# TEST 1: _send_to_execution_runtime with mock
def test_send_to_execution_runtime_success():
    """Test MoCKA HTTP transmission to execution-runtime-system."""
    with patch('hg_gateway.requests.post') as mock_post:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = mock_runtime_response_success()
        mock_post.return_value = mock_response

        payload = {
            "intent_id": "intent-1",
            "plan_id": "plan-1",
            "action_id": "intent-1:0",
            "step": "ANALYZE",
            "decision_record_id": "decision-1",
            "governance_decision": "PASS",
            "hg_decision": "AUTHORIZED",
            "hg_conditions": [],
            "timestamp": "2026-09-20T10:00:00Z"
        }

        result = _send_to_execution_runtime(payload)

        # Verify transmission happened
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "execute-with-metadata" in call_args[0][0]
        assert call_args[1]["json"] == payload

        # Verify response
        assert result["execution_id"] == "exec-123"
        assert result["evidence_state"] == "VERIFIED"
        print("[PASS] Test 1: HTTP transmission successful")


# TEST 2: _send_to_execution_runtime with transmission error
def test_send_to_execution_runtime_error():
    """Test MoCKA handles transmission error gracefully."""
    with patch('hg_gateway.requests.post') as mock_post:
        # Mock transmission error
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        payload = {
            "intent_id": "intent-2",
            "plan_id": "plan-2",
            "action_id": "intent-2:0",
            "step": "ANALYZE",
            "decision_record_id": "decision-2",
            "governance_decision": "PASS",
            "hg_decision": "AUTHORIZED",
            "hg_conditions": [],
            "timestamp": "2026-09-20T10:00:00Z"
        }

        result = _send_to_execution_runtime(payload)

        # Should handle error gracefully
        assert result["execution_id"] == "UNKNOWN"
        assert result["evidence_state"] == "EVIDENCE_FAILED_IMMEDIATE"
        print("[PASS] Test 2: Transmission error handled gracefully")


# TEST 3: authorize_and_execute with successful evidence
def test_authorize_and_execute_evidence_verified():
    """Test hg_gateway gating when evidence is VERIFIED."""
    plan = {
        "intent_id": "intent-3",
        "plan_id": "plan-3",
        "steps": ["ANALYZE"],
        "action_ids": ["intent-3:0"]
    }

    governance_result = {
        "governance_decision": "PASS",
        "governance_reason": "Test",
        "decision_record_id": "decision-3"
    }

    # Mock execute_fn to do nothing (real execution happens in runtime)
    def execute_fn(execution_context, step, action_id):
        pass

    with patch('hg_gateway._send_to_execution_runtime') as mock_send:
        mock_send.return_value = mock_runtime_response_success()

        execution_context = authorize_and_execute(
            plan=plan,
            governance_decision=governance_result,
            governance_record_id=governance_result["decision_record_id"],
            execute_fn=execute_fn
        )

        # Verify results
        assert execution_context.evidence_state == "VERIFIED"
        assert execution_context.institutional_closure == "CLOSED"  # NI-005: A
        assert execution_context.execution_id == "exec-123"
        print(f"[PASS] Test 3: Evidence VERIFIED → Closure CLOSED (per NI-005: A)")


# TEST 4: authorize_and_execute with evidence failure (NI-006 critical)
def test_authorize_and_execute_evidence_pending_retry():
    """
    CRITICAL TEST: Execution succeeds but evidence write fails.
    Per NI-005: A, Institutional Closure must remain BLOCKED.
    Per NI-006: A, Consequence must be preserved for recovery.
    """
    plan = {
        "intent_id": "intent-4",
        "plan_id": "plan-4",
        "steps": ["ANALYZE"],
        "action_ids": ["intent-4:0"]
    }

    governance_result = {
        "governance_decision": "PASS",
        "governance_reason": "Test",
        "decision_record_id": "decision-4"
    }

    def execute_fn(execution_context, step, action_id):
        pass

    with patch('hg_gateway._send_to_execution_runtime') as mock_send:
        mock_send.return_value = mock_runtime_response_evidence_failure()

        execution_context = authorize_and_execute(
            plan=plan,
            governance_decision=governance_result,
            governance_record_id=governance_result["decision_record_id"],
            execute_fn=execute_fn
        )

        # CRITICAL VERIFICATION (NI-005: A + NI-006: A):
        # 1. Execution happened (execution_id is not UNKNOWN)
        assert execution_context.execution_id == "exec-124"

        # 2. Evidence state is PENDING_RETRY (failure)
        assert execution_context.evidence_state == "EVIDENCE_PENDING_RETRY"

        # 3. Institutional Closure is BLOCKED (per NI-005: A)
        assert execution_context.institutional_closure == "BLOCKED"

        # 4. Consequence is preserved (per NI-006: A)
        assert execution_context.execution_result is not None
        assert execution_context.execution_result.get("data") == "executed"

        print(f"[PASS] CRITICAL TEST 4: Execution success + evidence failure")
        print(f"       evidence_state={execution_context.evidence_state} → Closure BLOCKED")
        print(f"       consequence_preserved={execution_context.execution_result is not None}")


# TEST 5: Fail-closed: missing governance decision
def test_fail_closed_missing_governance():
    """Test fail-closed gate blocks execution when governance decision missing."""
    plan = {
        "intent_id": "intent-5",
        "plan_id": "plan-5",
        "steps": ["ANALYZE"],
        "action_ids": ["intent-5:0"]
    }

    governance_result = {
        "governance_decision": None,  # MISSING
        "governance_reason": "Test",
        "decision_record_id": "decision-5"
    }

    def execute_fn(execution_context, step, action_id):
        # Should never be called
        raise AssertionError("execute_fn should not be called")

    execution_context = authorize_and_execute(
        plan=plan,
        governance_decision=governance_result,
        governance_record_id=governance_result["decision_record_id"],
        execute_fn=execute_fn
    )

    # Should be blocked
    assert execution_context.execution_status == "BLOCKED"
    assert execution_context.institutional_closure == "BLOCKED"
    print(f"[PASS] Test 5: Fail-closed gate; missing governance_decision → BLOCKED")


# TEST 6: Fail-closed: governance FAIL
def test_fail_closed_governance_fail():
    """Test fail-closed gate blocks when governance says FAIL."""
    plan = {
        "intent_id": "intent-6",
        "plan_id": "plan-6",
        "steps": ["ANALYZE"],
        "action_ids": ["intent-6:0"]
    }

    governance_result = {
        "governance_decision": "FAIL",  # DENY
        "governance_reason": "Policy violation",
        "decision_record_id": "decision-6"
    }

    def execute_fn(execution_context, step, action_id):
        raise AssertionError("execute_fn should not be called")

    execution_context = authorize_and_execute(
        plan=plan,
        governance_decision=governance_result,
        governance_record_id=governance_result["decision_record_id"],
        execute_fn=execute_fn
    )

    # Should be blocked
    assert execution_context.execution_status == "BLOCKED"
    print(f"[PASS] Test 6: Fail-closed gate; governance_decision=FAIL → BLOCKED")


# TEST 7: Action ID propagation
def test_action_id_propagation():
    """Test action_id is propagated to execution-runtime-system."""
    plan = {
        "intent_id": "intent-7",
        "plan_id": "plan-7",
        "steps": ["ANALYZE"],
        "action_ids": ["intent-7:0"]  # Specific action_id
    }

    governance_result = {
        "governance_decision": "PASS",
        "governance_reason": "Test",
        "decision_record_id": "decision-7"
    }

    def execute_fn(execution_context, step, action_id):
        pass

    with patch('hg_gateway._send_to_execution_runtime') as mock_send:
        mock_send.return_value = mock_runtime_response_success()

        execution_context = authorize_and_execute(
            plan=plan,
            governance_decision=governance_result,
            governance_record_id=governance_result["decision_record_id"],
            execute_fn=execute_fn
        )

        # Verify action_id was included in request
        call_args = mock_send.call_args
        request_payload = call_args[0][0]
        assert request_payload["action_id"] == "intent-7:0"

        print(f"[PASS] Test 7: action_id propagation; action_id={request_payload['action_id']}")


# TEST 8: Metadata completeness
def test_metadata_completeness():
    """Test all MoCKA metadata is sent to execution-runtime-system."""
    plan = {
        "intent_id": "intent-8",
        "plan_id": "plan-8",
        "steps": ["ANALYZE"],
        "action_ids": ["intent-8:0"]
    }

    governance_result = {
        "governance_decision": "PASS",
        "governance_reason": "Test",
        "decision_record_id": "decision-8"
    }

    def execute_fn(execution_context, step, action_id):
        pass

    with patch('hg_gateway._send_to_execution_runtime') as mock_send:
        mock_send.return_value = mock_runtime_response_success()

        execution_context = authorize_and_execute(
            plan=plan,
            governance_decision=governance_result,
            governance_record_id=governance_result["decision_record_id"],
            execute_fn=execute_fn
        )

        # Verify all metadata in request
        call_args = mock_send.call_args
        request_payload = call_args[0][0]

        assert request_payload["intent_id"] == "intent-8"
        assert request_payload["plan_id"] == "plan-8"
        assert request_payload["action_id"] == "intent-8:0"
        assert request_payload["decision_record_id"] == "decision-8"
        assert request_payload["governance_decision"] == "PASS"
        assert request_payload["hg_decision"] == "AUTHORIZED"
        assert "timestamp" in request_payload

        print(f"[PASS] Test 8: Metadata completeness; all fields present")


if __name__ == "__main__":
    print("=" * 80)
    print("TEST SUITE: Step 9 Execution Integration (MoCKA Side)")
    print("=" * 80)

    test_send_to_execution_runtime_success()
    test_send_to_execution_runtime_error()
    test_authorize_and_execute_evidence_verified()
    test_authorize_and_execute_evidence_pending_retry()
    test_fail_closed_missing_governance()
    test_fail_closed_governance_fail()
    test_action_id_propagation()
    test_metadata_completeness()

    print("=" * 80)
    print("ALL TESTS PASSED")
    print("=" * 80)
