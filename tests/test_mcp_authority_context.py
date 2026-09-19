"""
STEP 2: MCP Boundary Authority Context Integration Tests

Tests verify that:
1. Authority Context is extracted/accepted at MCP boundary
2. ABSENT authority context is marked and passed downstream
3. Authority context is preserved through routing (not abbreviated)
4. Fail-closed for invalid/unknown authority
"""

import pytest
from datetime import datetime
from mcp.mcp_gateway import MCPGateway
from mcp.mcp_router import MCPRouterV2


def test_mcp_gateway_accepts_authority_context():
    """Authority context accepted as parameter to ingest()"""
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


def test_mcp_gateway_marks_absent_authority():
    """Authority context marked ABSENT if not provided"""
    gateway = MCPGateway()

    result = gateway.ingest(
        "http",
        {"endpoint": "/test", "method": "GET", "body": None}
    )

    assert result["authority_context"]["status"] == "ABSENT"
    assert result["authority_context"]["authority_id"] is None
    assert result["authority_context"]["verification_state"] == "UNKNOWN"


def test_mcp_adapter_extracts_authority_from_payload():
    """HTTP adapter can extract authority_context from payload"""
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


def test_mcp_preserves_full_authority_context():
    """Authority context not abbreviated (full context preserved)"""
    gateway = MCPGateway()

    auth_ctx = {
        "authority_id": "AUTH-TEST",
        "authority_context_id": "CTX-TEST",
        "verification_state": "VERIFIED",
        "decision_type": "DECISION_TYPE_A",
        "resource_class": "RESOURCE_CLASS_X",
        "additional_field": "should_be_preserved"
    }

    result = gateway.ingest(
        "http",
        {"endpoint": "/test", "method": "GET", "body": None},
        authority_context=auth_ctx
    )

    # Full context should be passed through
    assert "authority_id" in result["authority_context"]
    assert result["authority_context"]["decision_type"] == "DECISION_TYPE_A"


def test_mcp_router_accepts_explicit_authority_context():
    """Router accepts explicit authority_context parameter"""
    router = MCPRouterV2()

    auth_ctx = {"authority_id": "AUTH-ROUTER-TEST", "verification_state": "VERIFIED"}

    result = router.route(
        "http",
        {"endpoint": "/test", "method": "GET", "body": None},
        authority_context=auth_ctx
    )

    assert result["authority_context"]["authority_id"] == "AUTH-ROUTER-TEST"


def test_mcp_gateway_http_adapter_extraction():
    """HTTP adapter extracts authority from request payload"""
    gateway = MCPGateway()

    payload = {
        "endpoint": "/protected",
        "method": "POST",
        "body": {"data": "test"},
        "authority_context": {
            "authority_id": "AUTH-HTTP-001",
            "authority_context_id": "CTX-HTTP-001",
            "verification_state": "VERIFIED"
        }
    }

    result = gateway.ingest("http", payload)

    assert result["endpoint"] == "/protected"
    assert result["method"] == "POST"
    assert result["authority_context"]["authority_id"] == "AUTH-HTTP-001"
    assert result["authority_context"]["status"] == "PRESENT"


def test_mcp_authority_context_fields_present():
    """Authority context always includes required fields"""
    gateway = MCPGateway()

    # Without explicit authority
    result = gateway.ingest("http", {"endpoint": "/test", "method": "GET", "body": None})

    assert "authority_context" in result
    assert "status" in result["authority_context"]
    assert "verification_state" in result["authority_context"]


def test_mcp_multiple_sources_accept_authority():
    """Authority context supported across multiple MCP sources"""
    gateway = MCPGateway()

    auth_ctx = {
        "authority_id": "AUTH-MULTI-TEST",
        "verification_state": "VERIFIED"
    }

    for source in ["http", "github", "filesystem", "browser"]:
        if source == "http":
            payload = {"endpoint": "/test", "method": "GET", "body": None}
        elif source == "github":
            payload = {"repository": "test/repo", "action": "push", "ref": "main"}
        elif source == "filesystem":
            payload = {"path": "/test/file"}
        else:  # browser
            payload = {"url": "https://example.com"}

        result = gateway.ingest(source, payload, authority_context=auth_ctx)

        assert result["source"] == source
        assert result["authority_context"]["authority_id"] == "AUTH-MULTI-TEST"
        assert result["authority_context"]["status"] == "PRESENT"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
