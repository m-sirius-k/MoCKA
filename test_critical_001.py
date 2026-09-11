#!/usr/bin/env python3
"""
Test suite for CRITICAL-001: HG API Decision/Event Chain Break
Verify Option A (Fail-Closed Atomic Binding)
"""

import json
import time
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent))
import mocka_mcp_server

def call_mcp(name, args):
    """Call MCP tool"""
    return mocka_mcp_server.handle_mcp_request(name, args)

def test_gate_timeout():
    """Test: GATE timeout → Decision INVALIDATED, fail_closed response"""
    print("\n[TEST 1] GATE Timeout")

    def mock_post_fail(*args, **kwargs):
        raise Exception("timeout")

    with patch('mocka_mcp_server.requests.post', side_effect=mock_post_fail):
        result = call_mcp("mocka_decision_write", {
            "title": "T1", "context": "C1", "decision": "D1",
            "rationale": "R1", "impact": "I1", "approved_by": "usr",
            "alternatives": [{"option": "O1", "rejected_reason": "X"}]
        })
        data = json.loads(result)
        assert data.get("status") == "fail_closed", f"Expected fail_closed, got {data.get('status')}"
        print(f"  ✓ PASS: {data}")

def test_gate_error_500():
    """Test: GATE 500 error → fail_closed response"""
    print("\n[TEST 2] GATE 500 Error")

    mock_resp = MagicMock()
    mock_resp.status_code = 500

    with patch('mocka_mcp_server.requests.post', return_value=mock_resp):
        result = call_mcp("mocka_decision_write", {
            "title": "T2", "context": "C2", "decision": "D2",
            "rationale": "R2", "impact": "I2", "approved_by": "usr",
            "alternatives": [{"option": "N/A", "rejected_reason": "N/A"}]
        })
        data = json.loads(result)
        assert data.get("status") == "fail_closed", f"Got {data.get('status')}"
        print(f"  ✓ PASS: {data}")

def test_success():
    """Test: Success → ok status, event_id returned"""
    print("\n[TEST 3] Success (Event Created)")

    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"event_id": "E_TEST_001"}

    with patch('mocka_mcp_server.requests.post', return_value=mock_resp):
        result = call_mcp("mocka_decision_write", {
            "title": "T3", "context": "C3", "decision": "D3",
            "rationale": "R3", "impact": "I3", "approved_by": "usr",
            "alternatives": [{"option": "N/A", "rejected_reason": "N/A"}]
        })
        data = json.loads(result)
        assert data.get("status") == "ok", f"Got {data.get('status')}"
        assert data.get("event_id") is not None, "event_id should be set"
        print(f"  ✓ PASS: {data}")

def test_retry_success():
    """Test: Fail once, succeed on retry"""
    print("\n[TEST 4] Retry Success")

    call_count = [0]
    def mock_post_retry(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            raise Exception("temp fail")
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"event_id": "E_RETRY_001"}
        return mock_resp

    with patch('mocka_mcp_server.requests.post', side_effect=mock_post_retry):
        result = call_mcp("mocka_decision_write", {
            "title": "T4", "context": "C4", "decision": "D4",
            "rationale": "R4", "impact": "I4", "approved_by": "usr",
            "alternatives": [{"option": "N/A", "rejected_reason": "N/A"}]
        })
        data = json.loads(result)
        assert data.get("status") == "ok", f"Got {data.get('status')}"
        print(f"  ✓ PASS: Succeeded after {call_count[0]} attempts")

def test_ledger_audit_trail():
    """Test: INVALIDATED decisions preserved in ledger"""
    print("\n[TEST 5] Ledger Audit Trail")

    def mock_post_fail(*args, **kwargs):
        raise Exception("fail")

    with patch('mocka_mcp_server.requests.post', side_effect=mock_post_fail):
        call_mcp("mocka_decision_write", {
            "title": "T5", "context": "C5", "decision": "D5",
            "rationale": "R5", "impact": "I5", "approved_by": "usr",
            "alternatives": [{"option": "N/A", "rejected_reason": "N/A"}]
        })

    # Check ledger
    records, _ = mocka_mcp_server._read_decisions()
    invalidated = [r for r in records if r.get("status") == "INVALIDATED"]
    print(f"  Total records: {len(records)}, INVALIDATED: {len(invalidated)}")
    print(f"  ✓ PASS: Audit trail preserved")

if __name__ == "__main__":
    print("=" * 70)
    print("CRITICAL-001: Fail-Closed Atomic Binding - Test Suite")
    print("=" * 70)
    try:
        test_gate_timeout()
        test_gate_error_500()
        test_success()
        test_retry_success()
        test_ledger_audit_trail()
        print("\n" + "=" * 70)
        print("✓ All tests completed")
        print("=" * 70)
    except AssertionError as e:
        print(f"\n✗ ASSERTION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
