import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
MoCKA 3.0 -- Authorization Pipeline
authorization_pipeline.py

GL8-GL12 authorization orchestrator.
Implements HGD-A1 Option B+A (READ_ONLY_TOOLS bypass + _authz envelope).

Class A: tools in READ_ONLY_TOOLS -> AUTHZ_BYPASS_READ_ONLY (skip GL8-GL12)
Class B: all other tools -> require _authz envelope (GL8 decision_id, GL9 scope, GL11 registry)

References: DC_20261002_HGD_A1_IMPLEMENTATION_SCOPE, DC_20261002_GL8_GL12_ARCHITECTURE
"""

from structural.governance_pipeline import READ_ONLY_TOOLS
from structural.human_gate_authorization_integrity import (
    HumanGateAuthorizationIntegrityEngine,
    GL8_OK,
)
from structural.authorization_scope_binding import (
    AuthorizationScopeBindingEngine,
    GL9_OK,
)
from structural.tool_registry_enforcement import (
    ToolRegistryEnforcementEngine,
    GL11_OK,
)

AUTHZ_BYPASS_READ_ONLY = "AUTHZ_BYPASS_READ_ONLY"
AUTHZ_OK = "AUTHZ_OK"


class AuthorizationPipeline:
    """Orchestrates GL8-GL12 authorization checks for write tool calls."""

    def __init__(self):
        self._gl8 = HumanGateAuthorizationIntegrityEngine()
        self._gl9 = AuthorizationScopeBindingEngine()
        self._gl11 = ToolRegistryEnforcementEngine()

    def execute(self, tool_name: str, args: dict) -> str:
        # Class A: READ_ONLY_TOOLS bypass (HGD-A1 Option B)
        if tool_name in READ_ONLY_TOOLS:
            return AUTHZ_BYPASS_READ_ONLY

        # Class B: WRITE tools require _authz envelope (HGD-A1 Option A)
        gl8_result = self._gl8.check(args)
        if gl8_result != GL8_OK:
            return gl8_result

        gl9_result = self._gl9.check(args)
        if gl9_result != GL9_OK:
            return gl9_result

        gl11_result = self._gl11.check(tool_name)
        if gl11_result != GL11_OK:
            return gl11_result

        return AUTHZ_OK
