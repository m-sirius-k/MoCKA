"""
Authority Enforcement Boundaries
Implements Q2: Both MCP Boundary and Decision Executor MUST enforce authority validation

Decision Ledger: DC_20260919_008
Authorization: Q2 CONFIRM
  * MCP boundary validates authority before accepting decisions
  * Decision Executor validates authority before executing decisions
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

from .authority_model import AuthorityObject, AuthorityRegistry, get_registry
from .revocation_engine import RevocationEngine


class EnforcementBoundary(str, Enum):
    """Which boundary is enforcing"""
    MCP = "MCP"
    DECISION_EXECUTOR = "DECISION_EXECUTOR"


@dataclass
class AuthorityValidationResult:
    """Result of authority validation at enforcement boundary"""
    valid: bool
    boundary: EnforcementBoundary
    authority_id: Optional[str]
    decision_id: Optional[str]
    reason: Optional[str] = None
    authority_state: Optional[str] = None
    enforcement_timestamp: Optional[str] = None


class AuthorityEnforcer:
    """
    Enforces authority validation at MCP and Decision Executor boundaries

    Q2: Both boundaries MUST validate authority
    """

    def __init__(self, registry: Optional[AuthorityRegistry] = None,
                 revocation_engine: Optional[RevocationEngine] = None):
        self.registry = registry or get_registry()
        self.revocation_engine = revocation_engine or RevocationEngine(self.registry)

    def validate_at_mcp_boundary(self, authority_id: str, decision_id: str,
                                decision_type: str, resource_class: str) -> AuthorityValidationResult:
        """
        MCP Boundary Validation (Q2)

        Before MCP accepts a decision for processing, it must validate:
        1. Authority exists
        2. Authority is active
        3. Authority scope matches decision scope
        4. Authority has not been revoked
        """
        authority = self.registry.get(authority_id)

        if not authority:
            return AuthorityValidationResult(
                valid=False,
                boundary=EnforcementBoundary.MCP,
                authority_id=authority_id,
                decision_id=decision_id,
                reason="Authority not found in registry"
            )

        # Check if authority is currently active
        if not authority.is_active:
            return AuthorityValidationResult(
                valid=False,
                boundary=EnforcementBoundary.MCP,
                authority_id=authority_id,
                decision_id=decision_id,
                reason=f"Authority not active (state: {authority.state})",
                authority_state=authority.state.value
            )

        # Check if authority scope matches decision scope
        if authority.decision_type != decision_type:
            return AuthorityValidationResult(
                valid=False,
                boundary=EnforcementBoundary.MCP,
                authority_id=authority_id,
                decision_id=decision_id,
                reason=(
                    f"Authority decision_type '{authority.decision_type}' "
                    f"does not match decision '{decision_type}'"
                )
            )

        if authority.resource_class != resource_class:
            return AuthorityValidationResult(
                valid=False,
                boundary=EnforcementBoundary.MCP,
                authority_id=authority_id,
                decision_id=decision_id,
                reason=(
                    f"Authority resource_class '{authority.resource_class}' "
                    f"does not match decision '{resource_class}'"
                )
            )

        # Authority is valid at MCP boundary
        return AuthorityValidationResult(
            valid=True,
            boundary=EnforcementBoundary.MCP,
            authority_id=authority_id,
            decision_id=decision_id,
            authority_state=authority.state.value
        )

    def validate_at_executor_boundary(self, authority_id: str, decision_id: str,
                                     decision_type: str, resource_class: str) -> AuthorityValidationResult:
        """
        Decision Executor Boundary Validation (Q2)

        Before Executor executes a decision, it must validate:
        1. Authority exists and is active (re-check; may have changed since MCP)
        2. Authority scope matches decision scope
        3. Authority has not been revoked since MCP validation

        This is a defensive second check (authority could have been revoked
        between MCP acceptance and execution).
        """
        authority = self.registry.get(authority_id)

        if not authority:
            return AuthorityValidationResult(
                valid=False,
                boundary=EnforcementBoundary.DECISION_EXECUTOR,
                authority_id=authority_id,
                decision_id=decision_id,
                reason="Authority not found in registry"
            )

        # Check if authority is currently active
        if not authority.is_active:
            return AuthorityValidationResult(
                valid=False,
                boundary=EnforcementBoundary.DECISION_EXECUTOR,
                authority_id=authority_id,
                decision_id=decision_id,
                reason=(
                    f"Authority no longer active for execution "
                    f"(state: {authority.state})"
                ),
                authority_state=authority.state.value
            )

        # Check if authority scope still matches
        if authority.decision_type != decision_type:
            return AuthorityValidationResult(
                valid=False,
                boundary=EnforcementBoundary.DECISION_EXECUTOR,
                authority_id=authority_id,
                decision_id=decision_id,
                reason="Authority decision_type mismatch at execution"
            )

        if authority.resource_class != resource_class:
            return AuthorityValidationResult(
                valid=False,
                boundary=EnforcementBoundary.DECISION_EXECUTOR,
                authority_id=authority_id,
                decision_id=decision_id,
                reason="Authority resource_class mismatch at execution"
            )

        # Authority is valid at Executor boundary
        return AuthorityValidationResult(
            valid=True,
            boundary=EnforcementBoundary.DECISION_EXECUTOR,
            authority_id=authority_id,
            decision_id=decision_id,
            authority_state=authority.state.value
        )

    def validate_decision_execution(self, decision_dict: Dict[str, Any]) -> AuthorityValidationResult:
        """
        End-to-end validation: MCP → Executor pipeline

        Simulates the full validation flow:
        1. MCP receives decision with authority_id
        2. MCP validates at boundary
        3. Decision Executor receives the decision
        4. Executor validates at its boundary
        5. Executor executes only if both validations pass

        Returns the combined result (Executor validation is final)
        """
        authority_id = decision_dict.get("authority_id")
        decision_id = decision_dict.get("decision_id")
        decision_type = decision_dict.get("decision_type")
        resource_class = decision_dict.get("resource_class")

        if not all([authority_id, decision_id, decision_type, resource_class]):
            return AuthorityValidationResult(
                valid=False,
                boundary=EnforcementBoundary.DECISION_EXECUTOR,
                authority_id=authority_id,
                decision_id=decision_id,
                reason="Missing required decision fields"
            )

        # Step 1: MCP validation
        mcp_result = self.validate_at_mcp_boundary(
            authority_id, decision_id, decision_type, resource_class
        )

        if not mcp_result.valid:
            return mcp_result  # Fail fast at MCP

        # Step 2: Executor validation (defensive re-check)
        executor_result = self.validate_at_executor_boundary(
            authority_id, decision_id, decision_type, resource_class
        )

        return executor_result


def validate_authority_exists(authority_id: str) -> tuple[bool, Optional[str]]:
    """Check if authority exists (helper)"""
    registry = get_registry()
    authority = registry.get(authority_id)

    if not authority:
        return False, f"Authority {authority_id} not found"

    return True, None


def validate_authority_is_active(authority_id: str) -> tuple[bool, Optional[str]]:
    """Check if authority is currently active (helper)"""
    registry = get_registry()
    authority = registry.get(authority_id)

    if not authority:
        return False, f"Authority {authority_id} not found"

    if not authority.is_active:
        return False, f"Authority {authority_id} not active (state: {authority.state})"

    return True, None


def validate_authority_scope(authority_id: str, decision_type: str,
                            resource_class: str) -> tuple[bool, Optional[str]]:
    """Check if authority scope matches decision scope (helper)"""
    registry = get_registry()
    authority = registry.get(authority_id)

    if not authority:
        return False, f"Authority {authority_id} not found"

    if authority.decision_type != decision_type:
        return False, (
            f"Authority decision_type '{authority.decision_type}' "
            f"does not match '{decision_type}'"
        )

    if authority.resource_class != resource_class:
        return False, (
            f"Authority resource_class '{authority.resource_class}' "
            f"does not match '{resource_class}'"
        )

    return True, None
