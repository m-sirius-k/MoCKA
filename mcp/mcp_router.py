# mcp/mcp_router.py
# MCP OS Layer v1 — 第2層ルーター。既存mcp/router.py(.parse()契約、/ingest/github稼働中)は
# 変更しない。本ルーターは既存adapterのparse()結果に正規化されたtype情報を付与する。
# M3 Integration Phase: extract and validate Authority Context at MCP boundary

from typing import Optional, Dict, Any
from .adapters.github import GitHubAdapter
from .adapters.filesystem import FileSystemAdapter
from .adapters.http import HTTPAdapter
from .adapters.browser import BrowserAdapter
from datetime import datetime

SOURCE_TYPE_MAP = {
    "github": "github_event",
    "filesystem": "filesystem_event",
    "http": "http_event",
    "browser": "browser_event",
}


class MCPRouterV2:
    def __init__(self):
        self.adapters = {
            "github": GitHubAdapter(),
            "filesystem": FileSystemAdapter(),
            "http": HTTPAdapter(),
            "browser": BrowserAdapter(),
        }

    def route(self, source: str, payload: dict, authority_context: Optional[Dict[str, Any]] = None) -> dict:
        """
        Route MCP request through adapter, with optional Authority Context.

        If authority_context not provided, attempt to extract from payload via adapter.
        If still absent, create ABSENT marker (fail-closed).
        """
        if source not in self.adapters:
            raise Exception(f"UNKNOWN MCP SOURCE: {source}")

        adapter = self.adapters[source]
        parsed = adapter.parse(payload)

        # Try to extract authority context from payload (via adapter)
        if authority_context is None:
            authority_context = adapter.extract_authority_context(payload)

        # If still None, create ABSENT marker (fail-closed)
        if authority_context is None:
            authority_context = {
                "status": "ABSENT",
                "authority_id": None,
                "verification_state": "UNKNOWN"
            }
        else:
            # Mark as PRESENT
            if "status" not in authority_context:
                authority_context["status"] = "PRESENT"

        return {
            "type": SOURCE_TYPE_MAP[source],
            "source": source,
            "authority_context": authority_context,
            **parsed,
        }
