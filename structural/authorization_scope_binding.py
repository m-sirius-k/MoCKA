import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
MoCKA 3.0 -- Authorization Scope Binding Engine (GL9)
authorization_scope_binding.py

GL9: Verifies _authz.scope is present for write tool calls.
Reads from args["_authz"]["scope"] (not args["scope"]).

Fail code: GL9_FAIL_1 when _authz envelope missing or scope absent.

References: DC_20261002_HGD_A1_IMPLEMENTATION_SCOPE
"""

GL9_OK = "GL9_OK"
GL9_FAIL_1 = "GL9_FAIL_1_NO_SCOPE"


class AuthorizationScopeBindingEngine:
    """GL9: Scope binding check on _authz envelope."""

    def check(self, args: dict) -> str:
        authz = args.get("_authz")
        if not isinstance(authz, dict):
            return GL9_FAIL_1
        if not authz.get("scope"):
            return GL9_FAIL_1
        return GL9_OK
