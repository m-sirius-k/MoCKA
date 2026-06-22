from dataclasses import dataclass

@dataclass(frozen=True)
class MCPConfig:
    service_name: str = "mocka-mcp"
    version: str = "0.1"
    debug: bool = True
