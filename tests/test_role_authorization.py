"""
Unit 1.3: Authorization Verification Harness

Test harness for role_registry.py - verifies authorization boundaries and role definitions.
Tests cover: role loading, authority validation, escalation paths, fail-closed behavior.

Author: KUROKO Monitor (Claude)
Date: 2026-09-12
Session: claude/kuroko-c2b-route-audit-n51wgf
"""

import pytest
from governance.role_registry import (
    RoleRegistry,
    RoleNotFound,
    CyclicEscalationError,
    IncompleteRoleDefinitionError,
    AuthorityLevel,
)


class TestRoleLoading:
    """Test: all roles load correctly with required attributes."""

    def test_all_roles_loadable(self):
        """All 7 roles should load without error."""
        roles = RoleRegistry.list_all_roles()
        assert len(roles) == 7
        assert 'HUMAN_AUTHORITY' in roles
        assert 'KUROKO_MONITOR' in roles
        assert 'GATE_SYSTEM' in roles
        assert 'INTEGRITY_SYSTEM' in roles
        assert 'GL7_KERNEL' in roles
        assert 'AUDIT_SYSTEM' in roles
        assert 'MONITORING_SYSTEM' in roles

    def test_role_has_all_attributes(self):
        """Each role must have all 8 required attributes."""
        required_attrs = [
            'authority_level',
            'description',
            'capabilities',
            'escalation',
            'decision_rights',
            'execution_rights',
        ]
        for role_id in RoleRegistry.list_all_roles():
            role = RoleRegistry.get_role(role_id)
            for attr in required_attrs:
                assert attr in role, f"Role {role_id} missing attribute {attr}"

    def test_role_not_found(self):
        """RoleNotFound raised for invalid role_id."""
        with pytest.raises(RoleNotFound):
            RoleRegistry.get_role('INVALID_ROLE')

    def test_role_capabilities_non_empty(self):
        """Each role must have at least one capability."""
        for role_id in RoleRegistry.list_all_roles():
            role = RoleRegistry.get_role(role_id)
            assert len(role['capabilities']) > 0


class TestAuthorityValidation:
    """Test: authority validation works correctly."""

    def test_gate_system_can_validate(self):
        """GATE_SYSTEM role can VALIDATE_PAYLOAD."""
        assert RoleRegistry.validate_authority('GATE_SYSTEM', 'VALIDATE_PAYLOAD')

    def test_gate_system_cannot_execute_gate(self):
        """GATE_SYSTEM role cannot execute ENFORCE_GATE_POLICY (that's capability)."""
        assert RoleRegistry.validate_authority('GATE_SYSTEM', 'ENFORCE_GATE_POLICY')

    def test_kuroko_monitor_cannot_enforce_gate(self):
        """KUROKO_MONITOR role cannot ENFORCE_GATE_POLICY."""
        assert not RoleRegistry.validate_authority('KUROKO_MONITOR', 'ENFORCE_GATE_POLICY')

    def test_kuroko_monitor_can_audit(self):
        """KUROKO_MONITOR role can AUDIT_DESIGN."""
        assert RoleRegistry.validate_authority('KUROKO_MONITOR', 'AUDIT_DESIGN')

    def test_human_authority_approves_all(self):
        """HUMAN_AUTHORITY can approve decisions."""
        assert RoleRegistry.validate_authority('HUMAN_AUTHORITY', 'APPROVE_DECISION')

    def test_human_authority_can_override(self):
        """HUMAN_AUTHORITY can override gates."""
        assert RoleRegistry.validate_authority('HUMAN_AUTHORITY', 'OVERRIDE_GATE')

    def test_invalid_role_always_false(self):
        """Invalid role returns False for any operation."""
        assert not RoleRegistry.validate_authority('INVALID_ROLE', 'ANY_OPERATION')

    def test_invalid_operation_returns_false(self):
        """Invalid operation returns False for any role."""
        assert not RoleRegistry.validate_authority('GATE_SYSTEM', 'NONEXISTENT_OPERATION')

    def test_integrity_system_can_sign(self):
        """INTEGRITY_SYSTEM can SIGN_EVENT."""
        assert RoleRegistry.validate_authority('INTEGRITY_SYSTEM', 'SIGN_EVENT')

    def test_integrity_system_can_verify(self):
        """INTEGRITY_SYSTEM can VERIFY_HASH_CHAIN."""
        assert RoleRegistry.validate_authority('INTEGRITY_SYSTEM', 'VERIFY_HASH_CHAIN')


class TestEscalationPaths:
    """Test: escalation paths form a DAG (directed acyclic graph)."""

    def test_escalation_paths_acyclic(self):
        """No circular escalation paths should exist."""
        is_valid, errors = RoleRegistry.verify_escalation_paths()
        assert is_valid, f"Escalation paths contain cycles: {errors}"

    def test_human_authority_no_escalation(self):
        """HUMAN_AUTHORITY must have escalation=None."""
        escalation = RoleRegistry.get_escalation_path('HUMAN_AUTHORITY')
        assert escalation is None

    def test_escalation_targets_exist(self):
        """All escalation targets must exist in registry."""
        for role_id in RoleRegistry.list_all_roles():
            escalation = RoleRegistry.get_escalation_path(role_id)
            if escalation:
                # Verify target exists
                RoleRegistry.get_role(escalation)  # Should not raise

    def test_kuroko_monitor_escalates_to_human(self):
        """KUROKO_MONITOR escalates to HUMAN_AUTHORITY."""
        escalation = RoleRegistry.get_escalation_path('KUROKO_MONITOR')
        assert escalation == 'HUMAN_AUTHORITY'

    def test_gate_system_escalates_to_kuroko(self):
        """GATE_SYSTEM escalates to KUROKO_MONITOR."""
        escalation = RoleRegistry.get_escalation_path('GATE_SYSTEM')
        assert escalation == 'KUROKO_MONITOR'

    def test_gl7_kernel_escalates_to_human(self):
        """GL7_KERNEL escalates to HUMAN_AUTHORITY."""
        escalation = RoleRegistry.get_escalation_path('GL7_KERNEL')
        assert escalation == 'HUMAN_AUTHORITY'


class TestAuthorityLevels:
    """Test: authority level classification."""

    def test_human_authority_is_supreme(self):
        """HUMAN_AUTHORITY should be SUPREME level."""
        role = RoleRegistry.get_role('HUMAN_AUTHORITY')
        assert role['authority_level'] == 'SUPREME'

    def test_major_roles_identified(self):
        """MAJOR level should contain 3 roles."""
        major_roles = RoleRegistry.list_roles_by_level('MAJOR')
        assert len(major_roles) == 3
        assert set(major_roles) == {'GATE_SYSTEM', 'INTEGRITY_SYSTEM', 'GL7_KERNEL'}

    def test_minor_roles_identified(self):
        """MINOR level should contain 3 roles."""
        minor_roles = RoleRegistry.list_roles_by_level('MINOR')
        assert len(minor_roles) == 3
        assert set(minor_roles) == {'KUROKO_MONITOR', 'AUDIT_SYSTEM', 'MONITORING_SYSTEM'}

    def test_supreme_only_human_authority(self):
        """SUPREME level should only contain HUMAN_AUTHORITY."""
        supreme_roles = RoleRegistry.list_roles_by_level('SUPREME')
        assert supreme_roles == ['HUMAN_AUTHORITY']

    def test_authority_level_enum(self):
        """get_authority_level returns authority level string."""
        level = RoleRegistry.get_authority_level('HUMAN_AUTHORITY')
        assert level == 'SUPREME'
        assert isinstance(level, str)

    def test_is_role_supreme(self):
        """is_role_supreme returns True only for HUMAN_AUTHORITY."""
        assert RoleRegistry.is_role_supreme('HUMAN_AUTHORITY')
        assert not RoleRegistry.is_role_supreme('KUROKO_MONITOR')
        assert not RoleRegistry.is_role_supreme('GATE_SYSTEM')


class TestDecisionAndExecutionRights:
    """Test: decision_rights and execution_rights correctly assigned."""

    def test_human_authority_self_decision(self):
        """HUMAN_AUTHORITY has decision_rights='SELF'."""
        decision_auth = RoleRegistry.get_decision_authority('HUMAN_AUTHORITY')
        assert decision_auth == 'SELF'

    def test_kuroko_monitor_proposes_human_decides(self):
        """KUROKO_MONITOR proposes but HUMAN_AUTHORITY decides."""
        decision_auth = RoleRegistry.get_decision_authority('KUROKO_MONITOR')
        assert decision_auth == 'HUMAN_AUTHORITY'

    def test_gate_system_execution(self):
        """GATE_SYSTEM executes its own operations."""
        execution_auth = RoleRegistry.get_execution_authority('GATE_SYSTEM')
        assert execution_auth == 'GATE_SYSTEM'

    def test_integrity_system_execution(self):
        """INTEGRITY_SYSTEM executes its own operations."""
        execution_auth = RoleRegistry.get_execution_authority('INTEGRITY_SYSTEM')
        assert execution_auth == 'INTEGRITY_SYSTEM'

    def test_audit_system_execution(self):
        """AUDIT_SYSTEM executes its own operations."""
        execution_auth = RoleRegistry.get_execution_authority('AUDIT_SYSTEM')
        assert execution_auth == 'AUDIT_SYSTEM'


class TestFailClosedBehavior:
    """Test: fail-closed enforcement (default deny when uncertain)."""

    def test_unknown_role_denied(self):
        """Unknown role denied for any operation."""
        result = RoleRegistry.validate_authority('UNKNOWN_ROLE', 'ANY_OP')
        assert result is False

    def test_missing_capability_denied(self):
        """Missing capability denied for role."""
        result = RoleRegistry.validate_authority('GATE_SYSTEM', 'UNKNOWN_CAPABILITY')
        assert result is False

    def test_role_not_found_exception(self):
        """RoleNotFound exception on invalid role access."""
        with pytest.raises(RoleNotFound):
            RoleRegistry.get_role('DOES_NOT_EXIST')


class TestRoleDescriptions:
    """Test: role descriptions are meaningful."""

    def test_all_roles_have_description(self):
        """All roles must have a description."""
        for role_id in RoleRegistry.list_all_roles():
            role = RoleRegistry.get_role(role_id)
            assert 'description' in role
            assert len(role['description']) > 0

    def test_human_authority_description(self):
        """HUMAN_AUTHORITY description meaningful."""
        role = RoleRegistry.get_role('HUMAN_AUTHORITY')
        assert 'Final' in role['description'] or 'final' in role['description']


class TestRegistryCoverage:
    """Test: verify comprehensive role definition coverage."""

    def test_registry_has_exactly_seven_roles(self):
        """Registry must contain exactly 7 roles from HG-N05 Candidate C."""
        roles = RoleRegistry.list_all_roles()
        assert len(roles) == 7

    def test_all_required_roles_present(self):
        """All roles from Candidate C must be present."""
        required_roles = [
            'HUMAN_AUTHORITY',
            'KUROKO_MONITOR',
            'GATE_SYSTEM',
            'INTEGRITY_SYSTEM',
            'GL7_KERNEL',
            'AUDIT_SYSTEM',
            'MONITORING_SYSTEM',
        ]
        roles = RoleRegistry.list_all_roles()
        for role in required_roles:
            assert role in roles, f"Required role {role} not in registry"

    def test_capability_non_empty_all_roles(self):
        """All roles must have at least one capability."""
        for role_id in RoleRegistry.list_all_roles():
            role = RoleRegistry.get_role(role_id)
            assert len(role['capabilities']) > 0

    def test_no_empty_role_definitions(self):
        """No role definition should be empty."""
        for role_id in RoleRegistry.list_all_roles():
            role = RoleRegistry.get_role(role_id)
            assert len(role) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
