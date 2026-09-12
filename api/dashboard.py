"""
Unit 4.3: Monitoring Dashboard API

HTTP API endpoints for C2-b monitoring dashboard.
Provides real-time ROUTE status, alerts, and health metrics.

Author: KUROKO Monitor (Claude)
Date: 2026-09-12
Session: claude/kuroko-c2b-route-audit-n51wgf
"""

from phi_os.monitoring_system import MonitoringSystem
from phi_os.alert_system import AlertSystem
from governance.role_registry import RoleRegistry
from typing import Dict, Any


class DashboardAPI:
    """REST API interface for C2-b monitoring dashboard."""

    def __init__(self):
        self.monitoring = MonitoringSystem()
        self.alerts = AlertSystem()

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data.

        Returns:
            Dict with all dashboard metrics
        """
        return {
            'c2b_status': self.monitoring.get_c2b_overall_status(),
            'routes': self.monitoring.get_all_routes_status(),
            'alerts': self.alerts.get_alert_summary(),
            'health': self.monitoring.get_health_summary(),
            'operational': self.monitoring.is_c2b_operational()
        }

    def get_route_status(self, route_number: int) -> Dict[str, Any]:
        """Get status of specific ROUTE.

        Args:
            route_number: ROUTE number (1-8)

        Returns:
            Dict with ROUTE status
        """
        if route_number < 1 or route_number > 8:
            return {'error': 'Invalid route number', 'route': route_number}

        route_status = self.monitoring.get_route_status(route_number)

        return {
            'route': route_number,
            'status': route_status.get('status'),
            'details': route_status,
            'critical': route_status.get('status') in ['BLOCK', 'NOT_READY']
        }

    def get_c2b_status_endpoint(self) -> Dict[str, Any]:
        """HTTP endpoint: GET /api/c2b/status

        Returns:
            C2-b overall status
        """
        return self.monitoring.get_c2b_overall_status()

    def get_routes_status_endpoint(self) -> Dict[str, Any]:
        """HTTP endpoint: GET /api/routes/status

        Returns:
            All ROUTE statuses
        """
        all_routes = self.monitoring.get_all_routes_status()

        return {
            'routes': all_routes,
            'critical_routes': self.monitoring.get_critical_routes(),
            'operational': self.monitoring.is_c2b_operational()
        }

    def get_alerts_endpoint(self) -> Dict[str, Any]:
        """HTTP endpoint: GET /api/alerts

        Returns:
            All pending alerts
        """
        return {
            'pending': self.alerts.get_pending_alerts(),
            'critical': self.alerts.get_critical_alerts(),
            'summary': self.alerts.get_alert_summary()
        }

    def get_health_endpoint(self) -> Dict[str, Any]:
        """HTTP endpoint: GET /api/health

        Returns:
            System health metrics
        """
        return {
            'health': self.monitoring.get_health_summary(),
            'roles_status': self.monitoring.get_authorization_roles_status(),
            'escalation_chain': self.monitoring.get_escalation_chain_status(),
            'timestamp': self._get_timestamp()
        }

    def acknowledge_alert_endpoint(self, alert_id: str, acknowledged_by: str) -> Dict[str, Any]:
        """HTTP endpoint: POST /api/alerts/{alert_id}/acknowledge

        Args:
            alert_id: Alert ID to acknowledge
            acknowledged_by: Role acknowledging

        Returns:
            Updated alert dict
        """
        # Verify requesting role can acknowledge alerts
        if not RoleRegistry.validate_authority(acknowledged_by, 'AUDIT_DESIGN'):
            return {'error': f'{acknowledged_by} not authorized to acknowledge alerts'}

        return self.alerts.acknowledge_alert(alert_id, acknowledged_by)

    def resolve_alert_endpoint(self, alert_id: str, resolved_by: str,
                               resolution: str) -> Dict[str, Any]:
        """HTTP endpoint: POST /api/alerts/{alert_id}/resolve

        Args:
            alert_id: Alert ID to resolve
            resolved_by: Role resolving
            resolution: Resolution notes

        Returns:
            Updated alert dict
        """
        # Verify requesting role can resolve alerts (HUMAN_AUTHORITY only)
        if not RoleRegistry.validate_authority(resolved_by, 'OVERRIDE_GATE'):
            return {'error': f'{resolved_by} not authorized to resolve alerts'}

        return self.alerts.resolve_alert(alert_id, resolved_by, resolution)

    def report_route_status_change(self, route_number: int, old_status: str,
                                  new_status: str) -> Dict[str, Any]:
        """Report ROUTE status change.

        Args:
            route_number: ROUTE number
            old_status: Previous status
            new_status: New status

        Returns:
            Alert dict created
        """
        alert = self.alerts.route_status_changed(route_number, old_status, new_status)
        return {
            'alert_created': True,
            'alert_id': alert['id'],
            'severity': alert['severity'],
            'escalated_to': alert.get('escalated_to')
        }

    def report_c2b_blocked(self, blocking_route: int, reason: str) -> Dict[str, Any]:
        """Report C2-b BLOCK state.

        Args:
            blocking_route: ROUTE causing block
            reason: Reason

        Returns:
            Alert dict created
        """
        alert = self.alerts.c2b_blocked(blocking_route, reason)
        return {
            'alert_created': True,
            'alert_id': alert['id'],
            'severity': alert['severity'],
            'escalated_to': alert['escalated_to']
        }

    def get_routes_needing_attention(self) -> Dict[str, Any]:
        """Identify ROUTEs that need attention.

        Returns:
            Dict with problematic routes and recommendations
        """
        critical = self.monitoring.get_critical_routes()
        all_statuses = self.monitoring.get_all_routes_status()

        routes_needing_attention = []
        for route_num in critical:
            route_status = all_statuses.get(route_num, {})
            routes_needing_attention.append({
                'route': route_num,
                'status': route_status.get('status'),
                'issue': self._get_route_issue_description(route_num, route_status)
            })

        return {
            'routes_needing_attention': routes_needing_attention,
            'total_critical': len(critical),
            'c2b_operational': self.monitoring.is_c2b_operational()
        }

    @staticmethod
    def _get_route_issue_description(route_num: int, route_status: Dict) -> str:
        """Get human-readable description of ROUTE issue."""
        status = route_status.get('status')

        route_names = {
            1: 'Event Clock Synchronization',
            2: 'Event Write/Persistence',
            3: 'Decision Write/Binding',
            4: 'Role Authority Verification',
            5: 'Enforcement Verification',
            6: 'Audit Trail Verification',
            7: 'Recovery Manager',
            8: 'Monitoring Ready',
        }

        route_name = route_names.get(route_num, f'ROUTE {route_num}')

        if status == 'BLOCK':
            return f"{route_name}: CRITICAL - System blocked"
        elif status == 'NOT_READY':
            return f"{route_name}: NOT_READY - Component not initialized"
        elif status == 'NOT_PROVEN':
            return f"{route_name}: NOT_PROVEN - Verification pending"
        else:
            return f"{route_name}: {status}"

    @staticmethod
    def _get_timestamp() -> str:
        """Get current ISO timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'


# Module-level assertions for runtime verification
assert RoleRegistry.validate_authority('MONITORING_SYSTEM', 'REPORT_HEALTH_METRICS'), \
    "MONITORING_SYSTEM must have REPORT_HEALTH_METRICS capability"
assert RoleRegistry.validate_authority('KUROKO_MONITOR', 'AUDIT_DESIGN'), \
    "KUROKO_MONITOR must have AUDIT_DESIGN capability for alert review"
