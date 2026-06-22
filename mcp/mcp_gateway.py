# mcp/mcp_gateway.py
# MCP OS Layer v1 — 外部入力の唯一の入口（第2層、既存mcp/server.pyとは独立）

from .mcp_router import MCPRouterV2


class MCPGateway:
    def __init__(self):
        self.router = MCPRouterV2()

    def ingest(self, source: str, payload: dict) -> dict:
        return self.router.route(source, payload)
