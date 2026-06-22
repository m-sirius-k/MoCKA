# mcp/mcp_router.py
# MCP OS Layer v1 — 第2層ルーター。既存mcp/router.py(.parse()契約、/ingest/github稼働中)は
# 変更しない。本ルーターは既存adapterのparse()結果に正規化されたtype情報を付与する。

from .adapters.github import GitHubAdapter
from .adapters.filesystem import FileSystemAdapter
from .adapters.http import HTTPAdapter

SOURCE_TYPE_MAP = {
    "github": "github_event",
    "filesystem": "filesystem_event",
    "http": "http_event",
}


class MCPRouterV2:
    def __init__(self):
        self.adapters = {
            "github": GitHubAdapter(),
            "filesystem": FileSystemAdapter(),
            "http": HTTPAdapter(),
        }

    def route(self, source: str, payload: dict) -> dict:
        if source not in self.adapters:
            raise Exception(f"UNKNOWN MCP SOURCE: {source}")

        parsed = self.adapters[source].parse(payload)
        return {
            "type": SOURCE_TYPE_MAP[source],
            "source": source,
            **parsed,
        }
