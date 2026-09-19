"""
STEP 2: MCP Boundary Authority Context Integration Tests (No pytest dependency)

Tests verify that:
1. Authority Context is extracted/accepted at MCP boundary
2. ABSENT authority context is marked and passed downstream
3. Authority context is preserved through routing (not abbreviated)
"""

from datetime import datetime
from mcp.mcp_gateway import MCPGateway


def test_mcp_gateway_accepts_authority_context():
    """Authority context accepted as parameter to ingest()"""
    print("TEST: MCP gateway accepts authority_context parameter...")

    gateway = MCPGateway()

    auth_ctx = {
        "authority_id": "AUTH-20260919-TEST",
        "authority_context_id": "CTX-TEST-001",
        "verification_state": "VERIFIED"
    }

    result = gateway.ingest(
        "http",
        {"endpoint": "/test", "method": "GET", "body": None},
        authority_context=auth_ctx
    )

    assert result["authority_context"]["authority_id"] == "AUTH-20260919-TEST"
    assert result["authority_context"]["status"] == "PRESENT"
    print("  ✓ PASS: Authority context accepted and marked PRESENT")


def test_mcp_gateway_marks_absent_authority():
    """Authority context marked ABSENT if not provided"""
    print("TEST: MCP gateway marks ABSENT authority when not provided...")

    gateway = MCPGateway()

    result = gateway.ingest(
        "http",
        {"endpoint": "/test", "method": "GET", "body": None}
    )

    assert result["authority_context"]["status"] == "ABSENT"
    assert result["authority_context"]["authority_id"] is None
    assert result["authority_context"]["verification_state"] == "UNKNOWN"
    print("  ✓ PASS: ABSENT authority marked with UNKNOWN verification state")


def test_mcp_adapter_extracts_authority_from_payload():
    """HTTP adapter can extract authority_context from payload"""
    print("TEST: MCP adapter extracts authority from request payload...")

    gateway = MCPGateway()

    auth_ctx = {
        "authority_id": "AUTH-20260919-PAYLOAD",
        "authority_context_id": "CTX-PAYLOAD-001",
        "verification_state": "VERIFIED"
    }

    payload = {
        "endpoint": "/test",
        "method": "GET",
        "body": None,
        "authority_context": auth_ctx  # Embedded in payload
    }

    result = gateway.ingest("http", payload)

    assert result["authority_context"]["authority_id"] == "AUTH-20260919-PAYLOAD"
    assert result["authority_context"]["status"] == "PRESENT"
    print("  ✓ PASS: Authority extracted from payload")


def test_mcp_preserves_full_authority_context():
    """Authority context not abbreviated (full context preserved)"""
    print("TEST: MCP preserves full authority context (not abbreviated)...")

    gateway = MCPGateway()

    auth_ctx = {
        "authority_id": "AUTH-TEST",
        "authority_context_id": "CTX-TEST",
        "verification_state": "VERIFIED",
        "decision_type": "DECISION_TYPE_A",
        "resource_class": "RESOURCE_CLASS_X"
    }

    result = gateway.ingest(
        "http",
        {"endpoint": "/test", "method": "GET", "body": None},
        authority_context=auth_ctx
    )

    # Full context should be passed through
    assert "authority_id" in result["authority_context"]
    assert result["authority_context"]["decision_type"] == "DECISION_TYPE_A"
    assert result["authority_context"]["resource_class"] == "RESOURCE_CLASS_X"
    print("  ✓ PASS: Full authority context preserved (not abbreviated to ID only)")


def test_mcp_authority_context_always_present():
    """Authority context field always present in result"""
    print("TEST: Authority context field always present in MCP result...")

    gateway = MCPGateway()

    result = gateway.ingest("http", {"endpoint": "/test", "method": "GET", "body": None})

    assert "authority_context" in result
    assert "status" in result["authority_context"]
    assert "verification_state" in result["authority_context"]
    print("  ✓ PASS: Authority context always present in result")


def test_mcp_fail_closed_on_unknown_verification():
    """UNKNOWN verification state marked (fail-closed principle)"""
    print("TEST: Fail-closed on UNKNOWN verification state...")

    gateway = MCPGateway()

    # No authority provided → marked UNKNOWN
    result = gateway.ingest("http", {"endpoint": "/test", "method": "GET", "body": None})

    auth_result = result["authority_context"]
    assert auth_result["verification_state"] == "UNKNOWN"
    assert auth_result["status"] == "ABSENT"
    print("  ✓ PASS: UNKNOWN state correctly marked (fail-closed)")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("STEP 2: MCP BOUNDARY AUTHORITY CONTEXT INTEGRATION TESTS")
    print("="*70 + "\n")

    tests = [
        test_mcp_gateway_accepts_authority_context,
        test_mcp_gateway_marks_absent_authority,
        test_mcp_adapter_extracts_authority_from_payload,
        test_mcp_preserves_full_authority_context,
        test_mcp_authority_context_always_present,
        test_mcp_fail_closed_on_unknown_verification,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1

    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70 + "\n")

    exit(0 if failed == 0 else 1)
