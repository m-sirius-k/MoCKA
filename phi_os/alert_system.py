"""
Unit 4.2: Alert System

Generates alerts when ROUTE status changes or C2-b transitions to BLOCK state.
Escalates critical alerts to HUMAN_AUTHORITY.

Author: KUROKO Monitor (Claude)
Date: 2026-09-12
Session: claude/kuroko-c2b-route-audit-n51wgf
"""

from typing import Dict, List
from datetime import datetime
from governance.role_registry import RoleRegistry


class AlertSystem:
    """Handles ROUTE failure alerts and escalation."""

    # Alert severity levels
    SEVERITY_INFO = 'INFO'
    SEVERITY_WARNING = 'WARNING'
    SEVERITY_CRITICAL = 'CRITICAL'
    SEVERITY_BLOCK = 'BLOCK'

    # Alert types
    ALERT_ROUTE_STATUS_CHANGE = 'ROUTE_STATUS_CHANGE'
    ALERT_C2B_BLOCKED = 'C2B_BLOCKED'
    ALERT_ESCALATION_REQUIRED = 'ESCALATION_REQUIRED'
    ALERT_AUTHORIZATION_FAILURE = 'AUTHORIZATION_FAILURE'

    def __init__(self):
        self.alert_queue: List[Dict] = []
        self.alert_history: List[Dict] = []

    def create_alert(self, alert_type: str, severity: str, message: str,
                     route_number: int = None, target_role: str = None) -> Dict:
        """Create an alert.

        Args:
            alert_type: Type of alert
            severity: Severity level (INFO, WARNING, CRITICAL, BLOCK)
            message: Alert message
            route_number: Which ROUTE triggered alert (if applicable)
            target_role: Which role should handle this (default: KUROKO_MONITOR)

        Returns:
            Alert dict with metadata
        """
        if target_role is None:
            target_role = 'KUROKO_MONITOR'

        alert = {
            'id': self._generate_alert_id(),
            'type': alert_type,
            'severity': severity,
            'message': message,
            'route_number': route_number,
            'target_role': target_role,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'status': 'ACTIVE',
            'escalated_to': None,
        }

        # Add to queue and history
        self.alert_queue.append(alert)
        self.alert_history.append(alert.copy())

        return alert

    def route_status_changed(self, route_number: int, old_status: str,
                             new_status: str) -> Dict:
        """Alert when a ROUTE status changes.

        Args:
            route_number: ROUTE number
            old_status: Previous status
            new_status: New status

        Returns:
            Alert dict
        """
        message = f"ROUTE {route_number} status changed: {old_status} -> {new_status}"

        # Determine severity
        if new_status == 'BLOCK':
            severity = self.SEVERITY_CRITICAL
            target_role = 'HUMAN_AUTHORITY'  # Critical alerts go to human
        elif new_status == 'NOT_READY':
            severity = self.SEVERITY_WARNING
            target_role = 'KUROKO_MONITOR'
        else:
            severity = self.SEVERITY_INFO
            target_role = 'MONITORING_SYSTEM'

        alert = self.create_alert(
            alert_type=self.ALERT_ROUTE_STATUS_CHANGE,
            severity=severity,
            message=message,
            route_number=route_number,
            target_role=target_role
        )

        return alert

    def c2b_blocked(self, blocking_route: int, reason: str) -> Dict:
        """Alert when C2-b transitions to BLOCK state.

        Args:
            blocking_route: Which ROUTE caused the block
            reason: Reason for block

        Returns:
            Alert dict
        """
        message = f"C2-b BLOCKED due to ROUTE {blocking_route}: {reason}"

        alert = self.create_alert(
            alert_type=self.ALERT_C2B_BLOCKED,
            severity=self.SEVERITY_BLOCK,
            message=message,
            route_number=blocking_route,
            target_role='HUMAN_AUTHORITY'  # Always escalate C2b blocks
        )

        # Set escalation flag
        alert['escalated_to'] = 'HUMAN_AUTHORITY'

        return alert

    def authorization_failure(self, role: str, operation: str, reason: str) -> Dict:
        """Alert when authorization fails.

        Args:
            role: Role that was denied
            operation: Operation that was denied
            reason: Reason for denial

        Returns:
            Alert dict
        """
        message = f"Authorization DENIED: {role} cannot {operation} ({reason})"

        alert = self.create_alert(
            alert_type=self.ALERT_AUTHORIZATION_FAILURE,
            severity=self.SEVERITY_WARNING,
            message=message,
            target_role='KUROKO_MONITOR'  # Audit monitors auth failures
        )

        return alert

    def get_pending_alerts(self, severity: str = None) -> List[Dict]:
        """Get all pending alerts.

        Args:
            severity: Filter by severity level (optional)

        Returns:
            List of alert dicts
        """
        pending = [a for a in self.alert_queue if a['status'] == 'ACTIVE']

        if severity:
            pending = [a for a in pending if a['severity'] == severity]

        return pending

    def get_critical_alerts(self) -> List[Dict]:
        """Get all critical-or-worse alerts.

        Returns:
            List of CRITICAL or BLOCK severity alerts
        """
        critical = [a for a in self.alert_queue
                    if a['severity'] in [self.SEVERITY_CRITICAL, self.SEVERITY_BLOCK]
                    and a['status'] == 'ACTIVE']
        return critical

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Dict:
        """Mark alert as acknowledged.

        Args:
            alert_id: Alert ID
            acknowledged_by: Role that acknowledged

        Returns:
            Updated alert dict
        """
        for alert in self.alert_queue:
            if alert['id'] == alert_id:
                alert['status'] = 'ACKNOWLEDGED'
                alert['acknowledged_by'] = acknowledged_by
                alert['acknowledged_at'] = datetime.utcnow().isoformat() + 'Z'
                return alert

        return {'error': f'Alert {alert_id} not found'}

    def resolve_alert(self, alert_id: str, resolved_by: str, resolution: str) -> Dict:
        """Mark alert as resolved.

        Args:
            alert_id: Alert ID
            resolved_by: Role that resolved
            resolution: Resolution notes

        Returns:
            Updated alert dict
        """
        for alert in self.alert_queue:
            if alert['id'] == alert_id:
                alert['status'] = 'RESOLVED'
                alert['resolved_by'] = resolved_by
                alert['resolution'] = resolution
                alert['resolved_at'] = datetime.utcnow().isoformat() + 'Z'
                return alert

        return {'error': f'Alert {alert_id} not found'}

    def get_alert_summary(self) -> Dict:
        """Get summary of all alerts.

        Returns:
            Dict with alert counts and critical info
        """
        pending = self.get_pending_alerts()
        critical = self.get_critical_alerts()

        return {
            'total_alerts': len(self.alert_history),
            'pending_alerts': len(pending),
            'critical_alerts': len(critical),
            'critical_details': [
                {
                    'id': a['id'],
                    'type': a['type'],
                    'route': a.get('route_number'),
                    'message': a['message'],
                    'timestamp': a['timestamp']
                }
                for a in critical
            ]
        }

    @staticmethod
    def _generate_alert_id() -> str:
        """Generate unique alert ID."""
        from datetime import datetime
        import random
        ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        rand = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        return f"ALR_{ts}_{rand}"


# Module-level assertions for runtime verification
assert RoleRegistry.validate_authority('MONITORING_SYSTEM', 'GENERATE_ALERTS'), \
    "MONITORING_SYSTEM must have GENERATE_ALERTS capability"
assert RoleRegistry.validate_authority('KUROKO_MONITOR', 'AUDIT_DESIGN'), \
    "KUROKO_MONITOR must have AUDIT_DESIGN capability for alert review"
