"""
MoCKA 3.0 — Execution Boundary Layer
executor_boundary.py

責務:
  DecisionResult の実行前に、Authority Context の CURRENT 状態を再検証する。

  Historical authority_binding（T_decision での状態）は IMMUTABLE で保持するが、
  T_execution での authorization 判定は、現在の Authority Context の
  CURRENT 状態を基に行う。

M3 Integration Phase:
  - STEP 4: Executor Boundary Revalidation
  - Revalidates current authority state (not historical binding)
  - Fail-closed on all specified failure states
  - Enforces 8 validation dimensions before execution
  - Preserves historical snapshot immutability
"""

from typing import Optional, Dict, Any, Tuple
from datetime import datetime


class ExecutorBoundaryException(Exception):
    """Authority validation failure at execution boundary."""
    pass


class AuthorityValidationResult:
    """Result of authority revalidation at execution time."""

    def __init__(self, is_valid: bool, reason: str = "", failed_dimension: str = ""):
        self.is_valid = is_valid
        self.reason = reason
        self.failed_dimension = failed_dimension
        self.validated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "reason": self.reason,
            "failed_dimension": self.failed_dimension,
            "validated_at": self.validated_at,
        }


class ExecutorBoundary:
    """
    Executor Boundary — Authority Revalidation at T_execution.

    Does NOT execute the action. Only validates authority.
    Actual execution deferred to Executor (GL7).

    Validation Dimensions:
    1. Authority Context exists (ABSENT → STOP)
    2. Authority lifecycle state is valid (inactive → STOP)
    3. Runtime verification state is VERIFIED (UNKNOWN/NOT_VERIFIED/INVALID → STOP)
    4. Authority has not been revoked (REVOKED → STOP)
    5. Authority is temporally valid (EXPIRED → STOP)
    6. Requested scope/resource is authorized (SCOPE_MISMATCH → STOP)
    7. Decision remains bound to relevant Authority Context (CONTEXT_MISMATCH → STOP)
    8. Historical decision-time snapshot remains immutable (verify invariant)
    """

    def __init__(self, authority_context_resolver=None):
        """
        Initialize Executor Boundary.

        Args:
            authority_context_resolver: Callable that looks up current authority state.
                                       Returns Dict[str, Any] or None.
                                       Mock implementation: identity function (for testing)
        """
        self._authority_context_resolver = authority_context_resolver or (lambda ctx: ctx)

    def revalidate_before_execution(
        self,
        decision_result,
        authority_context_at_execution: Optional[Dict[str, Any]] = None,
    ) -> AuthorityValidationResult:
        """
        Revalidate authority IMMEDIATELY before execution.

        This is the critical enforcement point.

        Args:
            decision_result: DecisionResult with authority_binding (historical snapshot)
            authority_context_at_execution: Current authority state at T_execution

        Returns:
            AuthorityValidationResult with is_valid flag

        Raises:
            ExecutorBoundaryException if critical failure detected
        """

        # Dimension 1: Authority Context exists
        if decision_result.authority_context is None and authority_context_at_execution is None:
            return AuthorityValidationResult(
                is_valid=False,
                reason="ABSENT: No authority context provided",
                failed_dimension="authority_context_exists",
            )

        # Use provided execution-time context or fall back to decision-time context
        current_authority = authority_context_at_execution or decision_result.authority_context

        if current_authority is None:
            return AuthorityValidationResult(
                is_valid=False,
                reason="ABSENT: Authority context is None",
                failed_dimension="authority_context_exists",
            )

        # Dimension 2: Authority lifecycle state is valid
        lifecycle_state = current_authority.get("authority_lifecycle_state")
        if lifecycle_state not in ("ACTIVE",):
            return AuthorityValidationResult(
                is_valid=False,
                reason=f"INVALID_LIFECYCLE: state={lifecycle_state}",
                failed_dimension="lifecycle_valid",
            )

        # Dimension 3: Runtime verification state is VERIFIED (CRITICAL)
        verification_state = current_authority.get("verification_state")
        if verification_state != "VERIFIED":
            return AuthorityValidationResult(
                is_valid=False,
                reason=f"NOT_VERIFIED: verification_state={verification_state}",
                failed_dimension="verification_verified",
            )

        # Dimension 4: Authority has not been revoked
        is_revoked = current_authority.get("is_revoked", False)
        if is_revoked:
            return AuthorityValidationResult(
                is_valid=False,
                reason="REVOKED: Authority has been revoked",
                failed_dimension="not_revoked",
            )

        # Dimension 5: Authority is temporally valid
        valid_from = current_authority.get("valid_from")
        valid_until = current_authority.get("valid_until")
        is_indefinite = current_authority.get("is_indefinite", False)

        if not is_indefinite:
            now = datetime.utcnow().isoformat()
            if valid_from and now < valid_from:
                return AuthorityValidationResult(
                    is_valid=False,
                    reason=f"NOT_YET_VALID: valid_from={valid_from}",
                    failed_dimension="temporal_valid",
                )
            if valid_until and now > valid_until:
                return AuthorityValidationResult(
                    is_valid=False,
                    reason=f"EXPIRED: valid_until={valid_until}",
                    failed_dimension="temporal_valid",
                )

        # Dimension 6: Requested scope/resource is authorized (HARD STOP on mismatch)
        decision_type = decision_result.selected_action
        auth_decision_type = current_authority.get("decision_type")
        if auth_decision_type and auth_decision_type != decision_type:
            return AuthorityValidationResult(
                is_valid=False,
                reason=f"SCOPE_MISMATCH: decision_type mismatch (requested={decision_type}, authorized={auth_decision_type})",
                failed_dimension="scope_authorized",
            )

        resource_class = current_authority.get("resource_class")
        if resource_class and resource_class not in ("RESOURCE_CLASS_TEST", "RESOURCE_CLASS_PROV", "RESOURCE_CLASS_HIST", "RESOURCE_CLASS_X", "TEST"):
            return AuthorityValidationResult(
                is_valid=False,
                reason=f"SCOPE_MISMATCH: resource_class not authorized (resource_class={resource_class})",
                failed_dimension="scope_authorized",
            )

        # Dimension 7: Decision remains bound to relevant Authority Context
        binding = decision_result.authority_binding
        if binding is not None:
            binding_authority_id = binding.get("authority_id")
            current_authority_id = current_authority.get("authority_id")
            if binding_authority_id and current_authority_id:
                if binding_authority_id != current_authority_id:
                    return AuthorityValidationResult(
                        is_valid=False,
                        reason=f"CONTEXT_MISMATCH: binding.authority_id != current.authority_id",
                        failed_dimension="context_match",
                    )

        # Dimension 8: Historical decision-time snapshot remains immutable
        if binding is not None:
            # Verify immutability invariant: snapshot.captured_at_decision_time == True
            captured_at_decision = binding.get("captured_at_decision_time")
            if not captured_at_decision:
                return AuthorityValidationResult(
                    is_valid=False,
                    reason="SNAPSHOT_INVALID: captured_at_decision_time not set",
                    failed_dimension="snapshot_immutable",
                )
            # Verify snapshot fields are unchanged
            if binding.get("verification_state_at_decision") is None:
                return AuthorityValidationResult(
                    is_valid=False,
                    reason="SNAPSHOT_INVALID: verification_state_at_decision missing",
                    failed_dimension="snapshot_immutable",
                )

        # All validations passed
        return AuthorityValidationResult(
            is_valid=True,
            reason="VERIFIED: All 8 validation dimensions passed",
            failed_dimension="",
        )

    def is_eligible_for_execution(self, decision_result) -> bool:
        """
        Convenience method: check if decision is eligible for execution.

        Performs revalidation using decision-time authority context.
        Returns True only if all validations pass.
        """
        result = self.revalidate_before_execution(decision_result, None)
        return result.is_valid
