"""
Authorization Pipeline (GL8-GL12 Orchestrator)

Coordinates all 5 authorization engines (GL8-GL12) for fast-fail authorization.
Runs before GovernancePipeline (GL1-GL7) to enforce authorization at entry point.

Execution Order:
  1. GL8: Human Gate Authorization Integrity (decision_id verification)
  2. GL9: Authorization Scope Binding (scope matching)
  3. GL10: Decision Content Integrity (tampering detection)
  4. GL11: Tool Registry Enforcement (tool whitelist)
  5. GL12: Encoding Integrity (file format validation)

Any layer failing -> DENY (fast-fail authorization)
All layers passing -> ALLOW (proceed to GL1-GL7)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from structural.human_gate_authorization_integrity import (
    HumanGateAuthorizationIntegrityEngine,
    get_gl8_engine
)
from structural.authorization_scope_binding import (
    AuthorizationScopeBindingEngine,
    get_gl9_engine
)
from structural.decision_content_integrity import (
    DecisionContentIntegrityEngine,
    get_gl10_engine
)
from structural.tool_registry_enforcement import (
    ToolRegistryEnforcementEngine,
    get_gl11_engine
)
from structural.encoding_integrity import (
    EncodingIntegrityEngine,
    get_gl12_engine
)


@dataclass
class AuthorizationCheckpoint:
    """Record of a single authorization layer check"""
    layer: str  # "GL8", "GL9", "GL10", "GL11", "GL12"
    passed: bool
    failure_code: str
    failure_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthorizationDecision:
    """Final authorization decision from complete pipeline"""
    allowed: bool
    tool_name: str
    decision_id: Optional[str] = None
    checkpoints: List[AuthorizationCheckpoint] = field(default_factory=list)
    first_failure: Optional[AuthorizationCheckpoint] = None
    failure_code: str = "AUTHZ_OK"


class AuthorizationPipeline:
    """
    GL8-GL12 Authorization Pipeline

    Fast-fail authorization orchestrator. Runs all 5 layers sequentially,
    stopping at first failure for performance.
    """

    def __init__(self):
        """Initialize pipeline with all 5 engine singletons"""
        self.gl8 = get_gl8_engine()
        self.gl9 = get_gl9_engine()
        self.gl10 = get_gl10_engine()
        self.gl11 = get_gl11_engine()
        self.gl12 = get_gl12_engine()

    def execute(
        self,
        tool_name: str,
        args: Dict[str, Any]
    ) -> AuthorizationDecision:
        """
        Execute full authorization pipeline for tool execution.

        Args:
            tool_name: Name of MCP tool being executed
            args: Tool arguments (may contain decision_id, scope, etc)

        Returns:
            AuthorizationDecision with allow/deny and checkpoint trail
        """
        checkpoints: List[AuthorizationCheckpoint] = []
        first_failure: Optional[AuthorizationCheckpoint] = None

        # Extract decision_id for tracking
        decision_id = args.get("decision_id")

        # =====
        # GL8: Human Gate Authorization Integrity
        # =====
        gl8_result = self.gl8.verify_authorization(tool_name, args)
        gl8_checkpoint = AuthorizationCheckpoint(
            layer="GL8",
            passed=gl8_result.allowed,
            failure_code=gl8_result.failure_code,
            failure_reason=gl8_result.failure_reason,
            metadata={
                "decision_id": decision_id,
                "tool_name": tool_name
            }
        )
        checkpoints.append(gl8_checkpoint)

        if not gl8_result.allowed:
            return AuthorizationDecision(
                allowed=False,
                tool_name=tool_name,
                decision_id=decision_id,
                checkpoints=checkpoints,
                first_failure=gl8_checkpoint,
                failure_code=gl8_result.failure_code
            )

        # =====
        # GL9: Authorization Scope Binding
        # =====
        authorized_scope = self.gl8.get_authorized_scope(gl8_result.decision) if gl8_result.decision else None
        gl9_result = self.gl9.verify_scope_binding(authorized_scope, args)
        gl9_checkpoint = AuthorizationCheckpoint(
            layer="GL9",
            passed=gl9_result.allowed,
            failure_code=gl9_result.failure_code,
            failure_reason=gl9_result.failure_reason,
            metadata={
                "authorized_scope": authorized_scope,
                "requested_scope": gl9_result.requested_scope
            }
        )
        checkpoints.append(gl9_checkpoint)

        if not gl9_result.allowed:
            return AuthorizationDecision(
                allowed=False,
                tool_name=tool_name,
                decision_id=decision_id,
                checkpoints=checkpoints,
                first_failure=gl9_checkpoint,
                failure_code=gl9_result.failure_code
            )

        # =====
        # GL10: Decision Content Integrity
        # =====
        content_hash = self.gl8.get_content_hash(gl8_result.decision) if gl8_result.decision else None
        decision_record = gl8_result.decision.raw if gl8_result.decision else None
        gl10_result = self.gl10.verify_content_integrity(decision_record, content_hash)
        gl10_checkpoint = AuthorizationCheckpoint(
            layer="GL10",
            passed=gl10_result.allowed,
            failure_code=gl10_result.failure_code,
            failure_reason=gl10_result.failure_reason,
            metadata={
                "content_hash": gl10_result.content_hash[:16] if gl10_result.content_hash else None,
                "stored_hash": gl10_result.stored_hash[:16] if gl10_result.stored_hash else None
            }
        )
        checkpoints.append(gl10_checkpoint)

        if not gl10_result.allowed:
            return AuthorizationDecision(
                allowed=False,
                tool_name=tool_name,
                decision_id=decision_id,
                checkpoints=checkpoints,
                first_failure=gl10_checkpoint,
                failure_code=gl10_result.failure_code
            )

        # =====
        # GL11: Tool Registry Enforcement
        # =====
        gl11_result = self.gl11.verify_tool_registration(tool_name, args)
        gl11_checkpoint = AuthorizationCheckpoint(
            layer="GL11",
            passed=gl11_result.allowed,
            failure_code=gl11_result.failure_code,
            failure_reason=gl11_result.failure_reason,
            metadata={
                "tool_name": tool_name,
                "registered": gl11_result.tool_metadata is not None
            }
        )
        checkpoints.append(gl11_checkpoint)

        if not gl11_result.allowed:
            return AuthorizationDecision(
                allowed=False,
                tool_name=tool_name,
                decision_id=decision_id,
                checkpoints=checkpoints,
                first_failure=gl11_checkpoint,
                failure_code=gl11_result.failure_code
            )

        # =====
        # GL12: Encoding Integrity
        # =====
        # Verify Decision Ledger file encoding
        gl12_result = self.gl12.verify_file_encoding(
            "/home/user/MoCKA/data/decisions/decision_ledger.jsonl"
        )
        gl12_checkpoint = AuthorizationCheckpoint(
            layer="GL12",
            passed=gl12_result.allowed,
            failure_code=gl12_result.failure_code,
            failure_reason=gl12_result.failure_reason,
            metadata={
                "encoding": gl12_result.encoding,
                "has_bom": gl12_result.has_bom
            }
        )
        checkpoints.append(gl12_checkpoint)

        if not gl12_result.allowed:
            return AuthorizationDecision(
                allowed=False,
                tool_name=tool_name,
                decision_id=decision_id,
                checkpoints=checkpoints,
                first_failure=gl12_checkpoint,
                failure_code=gl12_result.failure_code
            )

        # =====
        # ALL LAYERS PASSED: ALLOW
        # =====
        return AuthorizationDecision(
            allowed=True,
            tool_name=tool_name,
            decision_id=decision_id,
            checkpoints=checkpoints,
            failure_code="AUTHZ_OK"
        )

    def get_audit_trail(self, decision: AuthorizationDecision) -> str:
        """
        Generate human-readable audit trail of authorization decision.

        Args:
            decision: AuthorizationDecision from pipeline execution

        Returns:
            Formatted audit trail string
        """
        lines = []
        lines.append(f"Authorization Decision: {'ALLOW' if decision.allowed else 'DENY'}")
        lines.append(f"Tool: {decision.tool_name}")
        lines.append(f"Decision ID: {decision.decision_id}")
        lines.append(f"Failure Code: {decision.failure_code}")
        lines.append("")
        lines.append("Checkpoints:")

        for checkpoint in decision.checkpoints:
            status = "PASS" if checkpoint.passed else "FAIL"
            lines.append(f"  {checkpoint.layer}: {status} ({checkpoint.failure_code})")

            if checkpoint.failure_reason:
                lines.append(f"    Reason: {checkpoint.failure_reason}")

        if decision.first_failure:
            lines.append("")
            lines.append(f"First Failure: {decision.first_failure.layer}")

        return "\n".join(lines)


# Singleton instance
_pipeline = None


def get_authorization_pipeline() -> AuthorizationPipeline:
    """Get or create AuthorizationPipeline singleton"""
    global _pipeline
    if _pipeline is None:
        _pipeline = AuthorizationPipeline()
    return _pipeline
