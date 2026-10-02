import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
MoCKA 3.0 -- Tool Registry Enforcement Engine (GL11)
tool_registry_enforcement.py

GL11: Verifies tool is registered in data/governance/tool_registry.json.
Implements HGD-B1 Option B: JSON schema file replaces hardcoded dict.

Fail-closed: TOOL_REGISTRY={} if JSON missing or malformed.
GL11_FAIL_1_UNKNOWN_TOOL when tool not in registry.
READ_ONLY_TOOLS bypass authorization_pipeline.py before reaching GL11.

References: DC_20261002_HGD_B1_IMPLEMENTATION_SCOPE
"""

import json
from pathlib import Path

GL11_OK = "GL11_OK"
GL11_FAIL_1_UNKNOWN_TOOL = "GL11_FAIL_1_UNKNOWN_TOOL"

_REGISTRY_PATH = Path(__file__).parent.parent / "data" / "governance" / "tool_registry.json"


def _load_registry() -> dict:
    try:
        return json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


TOOL_REGISTRY = _load_registry()


class ToolRegistryEnforcementEngine:
    """GL11: Tool registry membership check."""

    def check(self, tool_name: str) -> str:
        if tool_name not in TOOL_REGISTRY:
            return GL11_FAIL_1_UNKNOWN_TOOL
        return GL11_OK
