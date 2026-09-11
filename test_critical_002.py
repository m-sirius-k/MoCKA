#!/usr/bin/env python3
"""
Test suite for CRITICAL-002: Decision-Event Binding Audit
Verify binding verification, orphan detection, and recovery
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent))
import mocka_mcp_server

def call_mcp(name, args):
    """Call MCP tool"""
    return mocka_mcp_server.execute_tool(name, args)

def test_binding_audit_complete():
    """Test: Complete binding (Decision + Event both exist)"""
    print("\n[TEST 1] Complete Binding Detection")

    # Create decision and event in test data
    test_decision = {
        "decision_id": "DC_TEST_001",
        "title": "Test Decision",
        "status": "Active",
        "approved_at": "2026-09-11T10:00:00Z",
        "maker": "test"
    }

    test_event = {
        "event_id": "E_TEST_001",
        "title": "Test Event",
        "tags": "decision_ledger,DC_TEST_001",
        "created_at": "2026-09-11T10:01:00Z"
    }

    # Mock _read_decisions and _read_events
    with patch('mocka_mcp_server._read_decisions', return_value=([test_decision], 0)), \
         patch('mocka_mcp_server._read_events', return_value=([test_event], 0)):

        result_str = mocka_mcp_server.execute_tool("mocka_binding_audit", {})
        data = json.loads(result_str)

        assert data["total_decisions"] == 1, f"Expected 1 decision, got {data['total_decisions']}"
        assert data["complete_bindings"] == 1, f"Expected 1 complete, got {data['complete_bindings']}"
        assert len(data["type1_orphans"]) == 0, f"Expected 0 Type1 orphans"
        assert len(data["type2_orphans"]) == 0, f"Expected 0 Type2 orphans"
        assert data["binding_completeness"] == 100.0
        print(f"  ✓ PASS: {data['binding_completeness']:.1f}% completeness")

def test_type1_orphan_detection():
    """Test: Type 1 Orphan (Decision without Event)"""
    print("\n[TEST 2] Type 1 Orphan Detection (Decision without Event)")

    test_decision = {
        "decision_id": "DC_TEST_002",
        "title": "Orphaned Decision",
        "status": "Active",
        "approved_at": "2026-09-11T10:00:00Z"
    }

    with patch('mocka_mcp_server._read_decisions', return_value=([test_decision], 0)), \
         patch('mocka_mcp_server._read_events', return_value=([], 0)):

        result_str = mocka_mcp_server.execute_tool("mocka_binding_audit", {})
        data = json.loads(result_str)

        assert len(data["type1_orphans"]) == 1, f"Expected 1 Type1 orphan"
        assert data["type1_orphans"][0]["decision_id"] == "DC_TEST_002"
        print(f"  ✓ PASS: Detected orphan {data['type1_orphans'][0]['decision_id']}")

def test_type2_orphan_detection():
    """Test: Type 2 Orphan (Event without Decision)"""
    print("\n[TEST 3] Type 2 Orphan Detection (Event without Decision)")

    test_event = {
        "event_id": "E_TEST_003",
        "title": "Orphaned Event",
        "tags": "decision_ledger,DC_TEST_003",
        "created_at": "2026-09-11T10:00:00Z"
    }

    with patch('mocka_mcp_server._read_decisions', return_value=([], 0)), \
         patch('mocka_mcp_server._read_events', return_value=([test_event], 0)):

        result_str = mocka_mcp_server.execute_tool("mocka_binding_audit", {})
        data = json.loads(result_str)

        assert len(data["type2_orphans"]) == 1, f"Expected 1 Type2 orphan"
        assert data["type2_orphans"][0]["decision_id"] == "DC_TEST_003"
        print(f"  ✓ PASS: Detected orphan event for decision {data['type2_orphans'][0]['decision_id']}")

def test_binding_completeness():
    """Test: Binding completeness calculation"""
    print("\n[TEST 4] Binding Completeness Calculation")

    decisions = [
        {"decision_id": "DC_A", "title": "A", "status": "Active", "approved_at": "2026-09-11T10:00:00Z"},
        {"decision_id": "DC_B", "title": "B", "status": "Active", "approved_at": "2026-09-11T10:00:00Z"},
        {"decision_id": "DC_C", "title": "C", "status": "Active", "approved_at": "2026-09-11T10:00:00Z"}
    ]

    events = [
        {"event_id": "E_A", "title": "A Event", "tags": "decision_ledger,DC_A", "created_at": "2026-09-11T10:01:00Z"},
        {"event_id": "E_B", "title": "B Event", "tags": "decision_ledger,DC_B", "created_at": "2026-09-11T10:01:00Z"}
    ]

    with patch('mocka_mcp_server._read_decisions', return_value=(decisions, 0)), \
         patch('mocka_mcp_server._read_events', return_value=(events, 0)):

        result_str = mocka_mcp_server.execute_tool("mocka_binding_audit", {})
        data = json.loads(result_str)

        assert data["total_decisions"] == 3
        assert data["complete_bindings"] == 2
        assert len(data["type1_orphans"]) == 1
        assert data["binding_completeness"] == 66.66666666666666
        print(f"  ✓ PASS: {data['binding_completeness']:.1f}% completeness (2 complete out of 3)")

if __name__ == "__main__":
    print("=" * 70)
    print("CRITICAL-002: Decision-Event Binding Audit - Test Suite")
    print("=" * 70)
    try:
        test_binding_audit_complete()
        test_type1_orphan_detection()
        test_type2_orphan_detection()
        test_binding_completeness()
        print("\n" + "=" * 70)
        print("✓ All tests completed successfully")
        print("=" * 70)
    except AssertionError as e:
        print(f"\n✗ ASSERTION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
