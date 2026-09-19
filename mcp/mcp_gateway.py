# mcp/mcp_gateway.py
# MCP OS Layer v1 — 外部入力の唯一の入口（第2層、既存mcp/server.pyとは独立）
# M3 Integration Phase: accept and validate Authority Context at gateway

from typing import Optional, Dict, Any
from .mcp_router import MCPRouterV2


class MCPGateway:
    def __init__(self):
        self.router = MCPRouterV2()

    def ingest(self, source: str, payload: dict, authority_context: Optional[Dict[str, Any]] = None) -> dict:
        """
        Ingest external MCP request with optional Authority Context.

        Authority Context may come from:
        1. Explicit authority_context parameter
        2. Extracted from payload by adapter (e.g., HTTP Authorization header)
        3. Marked as ABSENT if not provided

        Returns routing result with authority_context field present.
        """
        return self.router.route(source, payload, authority_context=authority_context)
