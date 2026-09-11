"""
C2-b Role Registry: Formal role definitions for authorization boundaries.

Implements 7-role Hybrid Model (Candidate C) from HG-N05 Decision.
Single source of truth for role definitions, authority levels, and escalation paths.

Author: KUROKO Monitor (Claude)
Date: 2026-09-12
Session: claude/kuroko-c2b-route-audit-n51wgf
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum


class AuthorityLevel(Enum):
    """Authority hierarchy levels."""
    SUPREME = 0  # HUMAN_AUTHORITY only
    MAJOR = 1    # System enforcement roles
    MINOR = 2    # Monitoring and audit roles


class RoleRegistry:
    """Formal role definitions for C2-b implementation.

    Maintains single source of truth for:
    - Role authority levels
    - Capability definitions
    - Decision rights and execution rights
    - Escalation paths (must form a DAG)
    """

    # Role definitions from HG-N05 Candidate C (91/100 score)
    ROLE_DEFINITIONS: Dict[str, Dict] = {
        'HUMAN_AUTHORITY': {
            'authority_level': 'SUPREME',
            'description': 'Final authority on authorization decisions and policy',
            'capabilities': [
                'APPROVE_DECISION',
                'REJECT_DECISION',
                'OVERRIDE_GATE',
                'ESCALATE_AUTHORITY',
                'REVOKE_AUTHORIZATION',
            ],
            'escalation': None,  # No escalation point
            'decision_rights': 'SELF',
            'execution_rights': 'HUMAN_AUTHORITY',
        },
        'KUROKO_MONITOR': {
            'authority_level': 'MINOR',
            'description': 'Pre-decision audit, design work, and proposal generation',
            'capabilities': [
                'AUDIT_DESIGN',
                'COLLECT_EVIDENCE',
                'PROPOSE_CANDIDATES',
                'RECOMMEND_DECISION',
                'IMPLEMENT_PRE_DECISION_WORK',
            ],
            'escalation': 'HUMAN_AUTHORITY',
            'decision_rights': 'HUMAN_AUTHORITY',
            'execution_rights': 'KUROKO_MONITOR',
        },
        'GATE_SYSTEM': {
            'authority_level': 'MAJOR',
            'description': 'Event validation and payload enforcement',
            'capabilities': [
                'VALIDATE_PAYLOAD',
                'ENFORCE_GATE_POLICY',
                'REJECT_INVALID_EVENT',
                'CREATE_VALIDATION_RECORD',
            ],
            'escalation': 'KUROKO_MONITOR',
            'decision_rights': 'KUROKO_MONITOR',
            'execution_rights': 'GATE_SYSTEM',
        },
        'INTEGRITY_SYSTEM': {
            'authority_level': 'MAJOR',
            'description': 'Event signing, binding, verification, and tamper detection',
            'capabilities': [
                'SIGN_EVENT',
                'BIND_EVENT_LINEAGE',
                'VERIFY_HASH_CHAIN',
                'DETECT_TAMPERING',
                'DETECT_ANOMALIES',
                'CREATE_BINDING_RECORD',
            ],
            'escalation': 'GATE_SYSTEM',
            'decision_rights': 'KUROKO_MONITOR',
            'execution_rights': 'INTEGRITY_SYSTEM',
        },
        'GL7_KERNEL': {
            'authority_level': 'MAJOR',
            'description': 'Execution control and modification prevention',
            'capabilities': [
                'ENFORCE_ABORT_CONDITIONS',
                'BLOCK_UNAUTHORIZED_EXECUTION',
                'CREATE_EXECUTION_BOUNDARY',
                'VALIDATE_PRECONDITIONS',
            ],
            'escalation': 'HUMAN_AUTHORITY',
            'decision_rights': 'HUMAN_AUTHORITY',
            'execution_rights': 'GL7_KERNEL',
        },
        'AUDIT_SYSTEM': {
            'authority_level': 'MINOR',
            'description': 'Event tracing, lineage reconstruction, and history analysis',
            'capabilities': [
                'TRACE_EVENT_LINEAGE',
                'RECONSTRUCT_EXECUTION_PATH',
                'ANALYZE_EVENT_HISTORY',
                'VERIFY_BINDING_COMPLETENESS',
            ],
            'escalation': 'INTEGRITY_SYSTEM',
            'decision_rights': 'INTEGRITY_SYSTEM',
            'execution_rights': 'AUDIT_SYSTEM',
        },
        'MONITORING_SYSTEM': {
            'authority_level': 'MINOR',
            'description': 'Status aggregation, health metrics, and alert generation',
            'capabilities': [
                'AGGREGATE_ROUTE_STATUS',
                'DETECT_ANOMALIES',
                'GENERATE_ALERTS',
                'REPORT_HEALTH_METRICS',
            ],
            'escalation': 'KUROKO_MONITOR',
            'decision_rights': 'KUROKO_MONITOR',
            'execution_rights': 'MONITORING_SYSTEM',
        },
    }

    @staticmethod
    def get_role(role_id: str) -> Dict:
        """Return role definition by ID.

        Args:
            role_id: Role identifier (e.g., 'HUMAN_AUTHORITY')

        Returns:
            Role definition dict with all 8 attributes

        Raises:
            RoleNotFound: If role_id not in ROLE_DEFINITIONS
        """
        if role_id not in RoleRegistry.ROLE_DEFINITIONS:
            raise RoleNotFound(f"Role '{role_id}' not found in registry")
        return RoleRegistry.ROLE_DEFINITIONS[role_id].copy()

    @staticmethod
    def validate_authority(actor: str, operation: str) -> bool:
        """Check if actor has authority for operation.

        Args:
            actor: Role identifier (e.g., 'GATE_SYSTEM')
            operation: Operation name (e.g., 'VALIDATE_PAYLOAD')

        Returns:
            True if actor has capability for operation, False otherwise
        """
        try:
            role = RoleRegistry.get_role(actor)
            return operation in role['capabilities']
        except RoleNotFound:
            return False

    @staticmethod
    def list_roles_by_level(authority_level: str) -> List[str]:
        """List all role IDs at given authority level.

        Args:
            authority_level: Authority level ('SUPREME', 'MAJOR', 'MINOR')

        Returns:
            List of role IDs at that level
        """
        matching_roles = [
            role_id
            for role_id, role_def in RoleRegistry.ROLE_DEFINITIONS.items()
            if role_def['authority_level'] == authority_level
        ]
        return sorted(matching_roles)

    @staticmethod
    def get_escalation_path(role_id: str) -> Optional[str]:
        """Return escalation point for role.

        Args:
            role_id: Role identifier

        Returns:
            Role ID of escalation point, or None if no escalation

        Raises:
            RoleNotFound: If role_id not in registry
        """
        role = RoleRegistry.get_role(role_id)
        return role['escalation']

    @staticmethod
    def verify_escalation_paths() -> Tuple[bool, List[str]]:
        """Verify escalation paths form a DAG (no cycles).

        Returns:
            Tuple of (is_valid, list_of_errors)
            - is_valid: True if all escalation paths are acyclic
            - list_of_errors: List of error messages (empty if valid)
        """
        errors = []
        visited = set()
        path_stack = []

        def has_cycle(role_id: str) -> bool:
            if role_id in path_stack:
                cycle_start = path_stack.index(role_id)
                cycle = path_stack[cycle_start:] + [role_id]
                errors.append(f"Cyclic escalation: {' -> '.join(cycle)}")
                return True

            if role_id in visited:
                return False

            visited.add(role_id)
            path_stack.append(role_id)

            escalation_point = RoleRegistry.get_escalation_path(role_id)
            if escalation_point:
                if has_cycle(escalation_point):
                    return True

            path_stack.pop()
            return False

        for role_id in RoleRegistry.ROLE_DEFINITIONS.keys():
            if role_id not in visited:
                if has_cycle(role_id):
                    return False, errors

        # Verify HUMAN_AUTHORITY has no escalation
        if RoleRegistry.get_escalation_path('HUMAN_AUTHORITY') is not None:
            errors.append("HUMAN_AUTHORITY must have escalation=None")
            return False, errors

        return True, errors

    @staticmethod
    def get_authority_level(role_id: str) -> AuthorityLevel:
        """Return authority level enum for role.

        Args:
            role_id: Role identifier

        Returns:
            AuthorityLevel enum value

        Raises:
            RoleNotFound: If role_id not in registry
        """
        role = RoleRegistry.get_role(role_id)
        level_str = role['authority_level']
        return AuthorityLevel[level_str]

    @staticmethod
    def is_role_supreme(role_id: str) -> bool:
        """Check if role has SUPREME authority.

        Args:
            role_id: Role identifier

        Returns:
            True if role_id == 'HUMAN_AUTHORITY'
        """
        return role_id == 'HUMAN_AUTHORITY'

    @staticmethod
    def list_all_roles() -> List[str]:
        """Return sorted list of all role IDs."""
        return sorted(list(RoleRegistry.ROLE_DEFINITIONS.keys()))

    @staticmethod
    def get_decision_authority(role_id: str) -> str:
        """Return who has decision authority for a role's operations.

        Args:
            role_id: Role identifier

        Returns:
            Role ID of decision authority (often HUMAN_AUTHORITY)
        """
        role = RoleRegistry.get_role(role_id)
        return role['decision_rights']

    @staticmethod
    def get_execution_authority(role_id: str) -> str:
        """Return who can execute for this role.

        Args:
            role_id: Role identifier

        Returns:
            Role ID with execution rights (usually same as role_id)
        """
        role = RoleRegistry.get_role(role_id)
        return role['execution_rights']


class RoleNotFound(Exception):
    """Raised when role_id not found in registry."""
    pass


class CyclicEscalationError(Exception):
    """Raised when escalation paths contain cycles."""
    pass


class IncompleteRoleDefinitionError(Exception):
    """Raised when role definition missing required attributes."""
    pass


# Initialize and validate on module load
def _validate_registry_on_load():
    """Validate registry structure at import time."""
    is_valid, errors = RoleRegistry.verify_escalation_paths()
    if not is_valid:
        raise CyclicEscalationError(f"Registry validation failed: {errors}")

    # Verify all roles have required attributes
    required_attrs = [
        'authority_level',
        'description',
        'capabilities',
        'escalation',
        'decision_rights',
        'execution_rights',
    ]

    for role_id, role_def in RoleRegistry.ROLE_DEFINITIONS.items():
        missing = [attr for attr in required_attrs if attr not in role_def]
        if missing:
            raise IncompleteRoleDefinitionError(
                f"Role '{role_id}' missing attributes: {missing}"
            )

    # Verify all escalation targets exist
    for role_id, role_def in RoleRegistry.ROLE_DEFINITIONS.items():
        escalation = role_def['escalation']
        if escalation and escalation not in RoleRegistry.ROLE_DEFINITIONS:
            raise RoleNotFound(
                f"Role '{role_id}' escalates to undefined role '{escalation}'"
            )


# Run validation on import
_validate_registry_on_load()
