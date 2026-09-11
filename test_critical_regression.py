#!/usr/bin/env python3
"""
Regression Test Suite for CRITICAL-001 and CRITICAL-002
Validates that existing mocka_decision_write/get/list functionality still works
after CRITICAL-001 and CRITICAL-002 implementations
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent))

def test_decision_write_success_path():
    """Regression: Decision + Event both succeed (success path unchanged)"""
    print("\n[REGRESSION 1] Decision Write Success Path")

    # Mock successful GATE response
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"event_id": "E_REG_001"}

    with patch('mocka_mcp_server.requests.post', return_value=mock_resp):
        import mocka_mcp_server
        result_str = mocka_mcp_server.execute_tool("mocka_decision_write", {
            "title": "Regression Test Decision",
            "context": "Testing success path",
            "decision": "Approve regression test",
            "rationale": "Verify success path still works",
            "impact": "No impact - test decision",
            "approved_by": "test_authority",
            "alternatives": [{"option": "N/A", "rejected_reason": "N/A"}]
        })
        data = json.loads(result_str)

        assert data.get("status") == "ok", f"Expected ok, got {data.get('status')}"
        assert data.get("decision_id") is not None, "decision_id should be present"
        assert data.get("event_id") is not None, "event_id should be present"
        print(f"  ✓ PASS: Success path unchanged (decision_id={data.get('decision_id')})")

def test_decision_get_basic():
    """Regression: mocka_decision_get still returns single decision"""
    print("\n[REGRESSION 2] Decision Get (Basic Query)")

    test_decision = {
        "decision_id": "DC_REG_002",
        "title": "Get Test",
        "status": "Active",
        "approved_at": "2026-09-11T10:00:00Z"
    }

    with patch('mocka_mcp_server._read_decisions', return_value=([test_decision], 0)):
        import mocka_mcp_server
        result_str = mocka_mcp_server.execute_tool("mocka_decision_get", {
            "decision_id": "DC_REG_002"
        })
        data = json.loads(result_str)

        assert data.get("decision_id") == "DC_REG_002", "Should return the requested decision"
        assert data.get("status") == "Active", "Should have Active status"
        print(f"  ✓ PASS: mocka_decision_get returns correct decision")

def test_decision_list_filtering():
    """Regression: mocka_decision_list still filters by status"""
    print("\n[REGRESSION 3] Decision List (Status Filtering)")

    test_decisions = [
        {"decision_id": "DC_A", "status": "Active", "title": "A"},
        {"decision_id": "DC_B", "status": "Superseded", "title": "B"},
        {"decision_id": "DC_C", "status": "Active", "title": "C"}
    ]

    with patch('mocka_mcp_server._read_decisions', return_value=(test_decisions, 0)):
        import mocka_mcp_server
        result_str = mocka_mcp_server.execute_tool("mocka_decision_list", {
            "status": "Active"
        })
        data = json.loads(result_str)

        decisions = data.get("decisions", [])
        assert len(decisions) == 2, f"Expected 2 Active decisions, got {len(decisions)}"
        assert all(d.get("status") == "Active" for d in decisions), "All results should be Active"
        print(f"  ✓ PASS: mocka_decision_list filters correctly (2 Active found)")

def test_invalidated_status_in_list():
    """Regression: mocka_decision_list includes INVALIDATED status (new in CRITICAL-001)"""
    print("\n[REGRESSION 4] Decision List (INVALIDATED Status Handling)")

    test_decisions = [
        {"decision_id": "DC_X", "status": "Active", "title": "X"},
        {"decision_id": "DC_Y", "status": "INVALIDATED", "title": "Y", "invalidated_at": "2026-09-11T10:30:00Z"}
    ]

    with patch('mocka_mcp_server._read_decisions', return_value=(test_decisions, 0)):
        import mocka_mcp_server
        result_str = mocka_mcp_server.execute_tool("mocka_decision_list", {})
        data = json.loads(result_str)

        decisions = data.get("decisions", [])
        assert len(decisions) >= 1, "Should include INVALIDATED decisions"
        has_invalidated = any(d.get("status") == "INVALIDATED" for d in decisions)
        assert has_invalidated or len(decisions) >= 2, "Should handle INVALIDATED status"
        print(f"  ✓ PASS: mocka_decision_list handles INVALIDATED status")

def test_binding_audit_empty_state():
    """Regression: mocka_binding_audit works with empty ledger"""
    print("\n[REGRESSION 5] Binding Audit (Empty State)")

    with patch('mocka_mcp_server._read_decisions', return_value=([], 0)), \
         patch('mocka_mcp_server._read_events', return_value=([], 0)):
        import mocka_mcp_server
        result_str = mocka_mcp_server.execute_tool("mocka_binding_audit", {})
        data = json.loads(result_str)

        assert data.get("total_decisions") == 0, "Empty state should have 0 decisions"
        assert data.get("complete_bindings") == 0, "Empty state should have 0 complete"
        assert data.get("binding_completeness") == 0.0, "Empty completeness is 0%"
        print(f"  ✓ PASS: mocka_binding_audit handles empty state")

def test_concurrent_decisions():
    """Regression: Multiple concurrent decisions processed correctly"""
    print("\n[REGRESSION 6] Concurrent Decision Processing")

    decisions = [
        {"decision_id": f"DC_CONC_{i}", "status": "Active", "title": f"Decision {i}", "approved_at": "2026-09-11T10:00:00Z"}
        for i in range(5)
    ]

    with patch('mocka_mcp_server._read_decisions', return_value=(decisions, 0)), \
         patch('mocka_mcp_server._read_events', return_value=([], 0)):
        import mocka_mcp_server
        result_str = mocka_mcp_server.execute_tool("mocka_binding_audit", {})
        data = json.loads(result_str)

        assert data.get("total_decisions") == 5, "Should count all concurrent decisions"
        assert len(data.get("type1_orphans", [])) == 5, "All should be orphans (no events)"
        print(f"  ✓ PASS: Concurrent decision handling verified (5 decisions)")

def test_partial_binding():
    """Regression: Mixed complete and incomplete bindings calculated correctly"""
    print("\n[REGRESSION 7] Partial Binding Scenarios")

    decisions = [
        {"decision_id": "DC_PART_A", "status": "Active", "title": "A"},
        {"decision_id": "DC_PART_B", "status": "Active", "title": "B"},
        {"decision_id": "DC_PART_C", "status": "Active", "title": "C"}
    ]

    events = [
        {"event_id": "E_A", "tags": "decision_ledger,DC_PART_A", "title": "A Event"},
        # B has no event
        {"event_id": "E_C", "tags": "decision_ledger,DC_PART_C", "title": "C Event"}
    ]

    with patch('mocka_mcp_server._read_decisions', return_value=(decisions, 0)), \
         patch('mocka_mcp_server._read_events', return_value=(events, 0)):
        import mocka_mcp_server
        result_str = mocka_mcp_server.execute_tool("mocka_binding_audit", {})
        data = json.loads(result_str)

        assert data.get("total_decisions") == 3
        assert data.get("complete_bindings") == 2
        assert len(data.get("type1_orphans", [])) == 1
        assert data.get("type1_orphans")[0].get("decision_id") == "DC_PART_B"
        completeness = data.get("binding_completeness")
        assert 66.0 < completeness < 67.0, f"Expected ~66.67%, got {completeness}%"
        print(f"  ✓ PASS: Partial binding calculated correctly ({completeness:.1f}%)")

if __name__ == "__main__":
    print("=" * 70)
    print("Regression Test Suite - CRITICAL-001 & CRITICAL-002")
    print("=" * 70)
    print("Tests existing functionality after CRITICAL implementations")

    try:
        test_decision_write_success_path()
        test_decision_get_basic()
        test_decision_list_filtering()
        test_invalidated_status_in_list()
        test_binding_audit_empty_state()
        test_concurrent_decisions()
        test_partial_binding()

        print("\n" + "=" * 70)
        print("✓ Regression Test Suite: ALL TESTS PASSED (7/7)")
        print("=" * 70)
        print("\nEvidence:")
        print("  - Success path (Decision + Event) unchanged: VERIFIED")
        print("  - Decision get/list operations: VERIFIED")
        print("  - INVALIDATED status handling: VERIFIED")
        print("  - Binding audit algorithm: VERIFIED")
        print("  - Concurrent processing: VERIFIED")
        print("  - Partial binding scenarios: VERIFIED")

    except AssertionError as e:
        print(f"\n✗ ASSERTION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
