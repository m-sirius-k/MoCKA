import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
MoCKA 3.0 -- Human Gate Authorization Integrity Engine (GL8)
human_gate_authorization_integrity.py

GL8: Verifies _authz.decision_id is present for write tool calls.
Reads from args["_authz"]["decision_id"] (not args["decision_id"]).

Fail code: GL8_FAIL_1 when _authz envelope missing or decision_id absent.
AI self-generation of _authz authority is prohibited.

References: DC_20261002_HGD_A1_IMPLEMENTATION_SCOPE
"""

GL8_OK = "GL8_OK"
GL8_FAIL_1 = "GL8_FAIL_1_NO_DECISION_ID"


class HumanGateAuthorizationIntegrityEngine:
    """GL8: Decision ID integrity check on _authz envelope."""

    def check(self, args: dict) -> str:
        authz = args.get("_authz")
        if not isinstance(authz, dict):
            return GL8_FAIL_1
        if not authz.get("decision_id"):
            return GL8_FAIL_1
        return GL8_OK
