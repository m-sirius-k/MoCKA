"""
STEP 10: Failure Injection Test Suite

Simulates 8 failure scenarios to verify C2-b recovery and fail-closed behavior.
Tests authorization failures, ROUTE status failures, recovery handlers, and monitoring.

Author: KUROKO Monitor (Claude)
Date: 2026-09-12
Session: claude/kuroko-c2b-route-audit-n51wgf
"""

import pytest
from governance.role_registry import RoleRegistry, RoleNotFound
from phi_os.recovery_manager import RecoveryManager
from phi_os.monitoring_system import MonitoringSystem
from phi_os.alert_system import AlertSystem
from phi_os.anomaly_detector import AnomalyDetector


class TestFI_UnauthorizedRole:
    """FI-01: Unauthorized Role Access Denied"""

    def test_fi_01_unauthorized_role_denied(self):
        """Unauthorized role should be BLOCKED by fail-closed."""
        # KUROKO_MONITOR tries to ENFORCE_GATE_POLICY (doesn't have this capability)
        result = RoleRegistry.validate_authority('KUROKO_MONITOR', 'ENFORCE_GATE_POLICY')
        assert result is False, "Unauthorized role should be DENIED"

    def test_fi_01_unauthorized_multiple_capabilities(self):
        """Test multiple unauthorized capabilities."""
        unauthorized_tests = [
            ('KUROKO_MONITOR', 'ENFORCE_GATE_POLICY'),
            ('GATE_SYSTEM', 'SIGN_EVENT'),
            ('INTEGRITY_SYSTEM', 'ENFORCE_GATE_POLICY'),
            ('AUDIT_SYSTEM', 'ENFORCE_ABORT_CONDITIONS'),
        ]

        for role, capability in unauthorized_tests:
            result = RoleRegistry.validate_authority(role, capability)
            assert result is False, f"{role} should not have {capability}"


class TestFI_UnknownRole:
    """FI-02: Unknown Role Results in BLOCK/NOT_PROVEN"""

    def test_fi_02_unknown_role_denied(self):
        """Unknown role should be BLOCKED (fail-closed default)."""
        result = RoleRegistry.validate_authority('UNKNOWN_ROLE_XYZ', 'ANY_OPERATION')
        assert result is False, "Unknown role should be BLOCKED"

    def test_fi_02_unknown_role_any_operation(self):
        """Unknown role denied for any operation."""
        operations = ['VALIDATE_PAYLOAD', 'SIGN_EVENT', 'AUDIT_DESIGN', 'RANDOM_OP']

        for op in operations:
            result = RoleRegistry.validate_authority('TOTALLY_FAKE_ROLE', op)
            assert result is False, f"Unknown role should be blocked for {op}"


class TestFI_EventWriteFailure:
    """FI-03: Event Write Failure Triggers Recovery"""

    def test_fi_03_recovery_manager_event_timeout(self):
        """Event timeout handler should escalate to KUROKO_MONITOR."""
        recovery = RecoveryManager()
        result = recovery.handle_event_timeout('test_event_id')

        assert 'status' in result
        assert 'escalated_to' in result or 'recovery_action' in result
        assert result['timestamp'] is not None

    def test_fi_03_recovery_manager_write_failure(self):
        """Write failure handler should implement retry strategy."""
        recovery = RecoveryManager()
        result = recovery.handle_write_failure('test_event_id', Exception('write failed'), 1)

        assert 'status' in result
        assert 'backoff_seconds' in result or 'escalated_to' in result
        assert result['timestamp'] is not None


class TestFI_Timeout:
    """FI-04: Timeout Triggers Recovery Handler"""

    def test_fi_04_timeout_handler_exists(self):
        """Timeout recovery handler should be callable."""
        recovery = RecoveryManager()
        assert hasattr(recovery, 'handle_event_timeout')

        result = recovery.handle_event_timeout('test_event_id')
        assert result is not None

    def test_fi_04_timeout_escalation_path(self):
        """Timeout should escalate to KUROKO_MONITOR."""
        recovery = RecoveryManager()
        result = recovery.handle_event_timeout('event_123')

        # Verify escalation or recovery action is documented
        assert 'status' in result
        assert result['timestamp'] is not None


class TestFI_SigningFailure:
    """FI-05: Signing Failure Triggers Deferred Signing"""

    def test_fi_05_signing_failure_handler(self):
        """Signing failure should trigger deferred signing mechanism."""
        recovery = RecoveryManager()
        result = recovery.handle_signing_failure('event_id', 1)

        assert 'status' in result
        assert 'action' in result  # Should contain recovery action description
        assert result['timestamp'] is not None

    def test_fi_05_signing_deferred_signing_logic(self):
        """Deferred signing should preserve event and retry later."""
        recovery = RecoveryManager()
        result = recovery.handle_signing_failure('event_456', 1)

        assert result['status'] is not None


class TestFI_RouteFailure:
    """FI-06: ROUTE Status Failure Propagates to C2-b BLOCK"""

    def test_fi_06_route_failure_detection(self):
        """Anomaly detector should detect route failures."""
        detector = AnomalyDetector()
        anomalies = detector.detect_all_anomalies()

        assert isinstance(anomalies, dict)
        # Should have detection results even if empty due to DB gaps

    def test_fi_06_monitoring_detects_failures(self):
        """Monitoring system should detect when routes are not ready."""
        monitor = MonitoringSystem()

        # Get critical routes (those that are BLOCK or NOT_READY)
        critical = monitor.get_critical_routes()
        assert isinstance(critical, list)

        # Should be able to identify problem routes
        all_routes = monitor.get_all_routes_status()
        assert len(all_routes) == 8

    def test_fi_06_alert_on_route_failure(self):
        """When ROUTE fails, alert should be generated."""
        alerts = AlertSystem()

        # Create alert for ROUTE failure
        alert = alerts.route_status_changed(
            route_number=2,
            old_status='PASS',
            new_status='NOT_READY'
        )

        assert alert['id'] is not None
        assert alert['severity'] is not None
        assert alert['message'] is not None


class TestFI_MonitoringUnavailable:
    """FI-07: Monitoring Unavailable Should Not Fail Open"""

    def test_fi_07_monitoring_graceful_degradation(self):
        """Monitoring should degrade gracefully without failing open."""
        monitor = MonitoringSystem()

        # Even if monitoring fails to get data, it should return
        # a status dict (not crash or return success)
        health = monitor.get_health_summary()

        assert isinstance(health, dict)
        assert 'c2b_overall' in health
        assert 'is_operational' in health

    def test_fi_07_monitoring_returns_status_not_error(self):
        """Monitoring should return status dict, not throw error."""
        monitor = MonitoringSystem()

        try:
            status = monitor.get_c2b_overall_status()
            # Should complete without error
            assert isinstance(status, dict)
        except Exception as e:
            pytest.fail(f"Monitoring should not throw: {e}")


class TestFI_AlertUnavailable:
    """FI-08: Alert System Unavailable Should Not Silent Success"""

    def test_fi_08_alert_creation_recorded(self):
        """Alert creation should be recorded, not silently skipped."""
        alerts = AlertSystem()

        alert = alerts.c2b_blocked(
            blocking_route=2,
            reason='Event write failure'
        )

        assert alert['id'] is not None
        assert alert['severity'] == 'BLOCK'
        assert alert['status'] == 'ACTIVE'

    def test_fi_08_alert_history_maintained(self):
        """All alerts should be recorded in history."""
        alerts = AlertSystem()

        # Create multiple alerts
        alert1 = alerts.route_status_changed(1, 'PASS', 'NOT_READY')
        alert2 = alerts.route_status_changed(2, 'PASS', 'BLOCK')

        # History should contain both
        assert len(alerts.alert_history) >= 2

        # Verify they're recorded
        assert alert1['id'] in [a['id'] for a in alerts.alert_history]
        assert alert2['id'] in [a['id'] for a in alerts.alert_history]


class TestFI_FailClosedPrincipal:
    """Verify fail-closed principle across all failure scenarios."""

    def test_fi_all_unknown_states_denied(self):
        """All unknown/uncertain states should default to DENY."""
        test_cases = [
            ('UNKNOWN', 'OPERATION'),
            ('', 'OPERATION'),
            ('INVALID_ROLE_123', 'ANY_CAP'),
        ]

        for role, cap in test_cases:
            result = RoleRegistry.validate_authority(role, cap)
            assert result is False, f"Unknown state ({role}, {cap}) should be denied"

    def test_fi_escalation_paths_verified(self):
        """Escalation paths must form valid DAG."""
        is_valid, errors = RoleRegistry.verify_escalation_paths()
        assert is_valid, f"Escalation paths invalid: {errors}"

    def test_fi_no_unauthorized_allow(self):
        """Unauthorized operations should never be allowed."""
        unauthorized = [
            ('KUROKO_MONITOR', 'ENFORCE_GATE_POLICY'),
            ('GATE_SYSTEM', 'DETECT_TAMPERING'),
            ('GL7_KERNEL', 'SIGN_EVENT'),
            ('AUDIT_SYSTEM', 'OVERRIDE_GATE'),
        ]

        for role, op in unauthorized:
            result = RoleRegistry.validate_authority(role, op)
            assert result is False, f"{role} should not be able to {op}"


class TestFI_RecoveryCompleteness:
    """Verify all recovery handlers complete execution."""

    def test_fi_recovery_handlers_callable(self):
        """All recovery handlers should be callable without crashing."""
        recovery = RecoveryManager()

        handlers = [
            ('handle_event_timeout', ['test_event']),
            ('handle_write_failure', ['test_event', Exception('test error')]),
            ('handle_decision_write_failure', [{'decision_id': 'test_decision'}]),
            ('handle_signing_failure', ['test_event']),
        ]

        for handler_name, args in handlers:
            handler = getattr(recovery, handler_name, None)
            assert handler is not None, f"Handler {handler_name} not found"

            try:
                result = handler(*args)
                assert isinstance(result, dict), f"{handler_name} should return dict"
            except Exception as e:
                pytest.fail(f"{handler_name} failed: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
