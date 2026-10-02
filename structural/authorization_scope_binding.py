"""
GL9: Authorization Scope Binding Engine

Verifies that tool execution stays within authorized scope.
Responsibilities:
  1. Extract requested_scope from tool args
  2. Extract authorized_scope from GL8 decision
  3. Verify requested_scope is subset of authorized_scope
  4. Fast-fail on scope mismatch
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class GL9Result:
    """GL9 scope verification result"""
    allowed: bool
    requested_scope: Optional[List[str]] = None
    authorized_scope: Optional[List[str]] = None
    failure_reason: Optional[str] = None
    failure_code: str = "GL9_OK"


class AuthorizationScopeBindingEngine:
    """
    GL9 Engine: Authorization Scope Binding

    Ensures tool execution is restricted to authorized scopes.
    Implements fail-closed logic: deny if scopes are undefined.
    """

    # Standard scope categories
    VALID_SCOPES = {
        "governance",       # Governance system files
        "structural",       # Structural modules
        "data",            # Data directory
        "decisions",       # Decision Ledger
        "events",          # Event ledger
        "tests",           # Test files
        "documentation",   # Doc files
        "tools",          # Tool scripts
    }

    def verify_scope_binding(
        self,
        authorized_scope: Optional[List[str]],
        args: Dict[str, Any]
    ) -> GL9Result:
        """
        Verify that requested tool scope is within authorized scope.

        Args:
            authorized_scope: List of scopes authorized by decision
            args: Tool arguments (may contain scope field)

        Returns:
            GL9Result with allow/deny decision
        """
        # Extract requested scope from args
        requested_scope = args.get("scope", [])

        # Normalize to list
        if isinstance(requested_scope, str):
            requested_scope = [requested_scope]

        # Check 1: Both scopes must be defined
        if not authorized_scope:
            return GL9Result(
                allowed=False,
                requested_scope=requested_scope,
                authorized_scope=authorized_scope,
                failure_reason="No authorized_scope defined in decision",
                failure_code="GL9_FAIL_1_UNDEFINED_AUTHORIZED_SCOPE"
            )

        if not requested_scope:
            return GL9Result(
                allowed=False,
                requested_scope=requested_scope,
                authorized_scope=authorized_scope,
                failure_reason="No scope specified in tool args",
                failure_code="GL9_FAIL_2_UNDEFINED_REQUESTED_SCOPE"
            )

        # Check 2: Verify requested_scope is subset of authorized_scope
        # Using set subset operation: requested <= authorized
        requested_set = set(requested_scope)
        authorized_set = set(authorized_scope)

        if not requested_set.issubset(authorized_set):
            # Find which scopes are out of bounds
            out_of_bounds = requested_set - authorized_set

            return GL9Result(
                allowed=False,
                requested_scope=list(requested_set),
                authorized_scope=list(authorized_set),
                failure_reason=f"Requested scope {list(out_of_bounds)} not in authorized scopes",
                failure_code="GL9_FAIL_3_SCOPE_MISMATCH"
            )

        # All checks passed
        return GL9Result(
            allowed=True,
            requested_scope=requested_scope,
            authorized_scope=authorized_scope,
            failure_code="GL9_OK"
        )

    def merge_scopes(self, *scopes: List[str]) -> List[str]:
        """
        Merge multiple scope lists into a single deduplicated list.
        Useful for combining multiple authorization decisions.

        Args:
            *scopes: Variable number of scope lists

        Returns:
            Merged and deduplicated scope list
        """
        merged = set()
        for scope_list in scopes:
            if scope_list:
                merged.update(scope_list)
        return sorted(list(merged))

    def is_valid_scope(self, scope: str) -> bool:
        """
        Check if a scope is in the valid scope registry.

        Args:
            scope: Scope string to validate

        Returns:
            True if scope is valid, False otherwise
        """
        return scope in self.VALID_SCOPES

    def validate_all_scopes(self, scopes: List[str]) -> bool:
        """
        Validate that all scopes in a list are recognized.

        Args:
            scopes: List of scopes to validate

        Returns:
            True if all scopes valid, False if any invalid
        """
        return all(self.is_valid_scope(s) for s in scopes) if scopes else False


# Singleton instance
_gl9_engine = None


def get_gl9_engine() -> AuthorizationScopeBindingEngine:
    """Get or create GL9 engine singleton"""
    global _gl9_engine
    if _gl9_engine is None:
        _gl9_engine = AuthorizationScopeBindingEngine()
    return _gl9_engine
