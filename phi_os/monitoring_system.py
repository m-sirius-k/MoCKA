"""
Unit 4.1: ROUTE Status Monitoring System

Real-time monitoring of all 8 ROUTE statuses and C2-b overall status.
Aggregates health metrics from route_status.py and exposes via monitoring API.

Author: KUROKO Monitor (Claude)
Date: 2026-09-12
Session: claude/kuroko-c2b-route-audit-n51wgf
"""

from phi_os.route_status import RouteStatus
from governance.role_registry import RoleRegistry
from typing import Dict, List


class MonitoringSystem:
    """ROUTE health monitoring and status aggregation system."""

    def __init__(self):
        self.route_status = RouteStatus()
        self.route_calculator = self.route_status

    def get_route_status(self, route_number: int) -> Dict:
        """Get current status for a specific ROUTE.

        Args:
            route_number: ROUTE number (1-8)

        Returns:
            Dict with route status, health metrics, timestamp
        """
        if route_number < 1 or route_number > 8:
            return {'status': 'INVALID', 'route': route_number}

        method_name = f'calculate_route_{route_number}_status'
        if not hasattr(self.route_calculator, method_name):
            return {'status': 'NOT_IMPLEMENTED', 'route': route_number}

        try:
            method = getattr(self.route_calculator, method_name)
            status = method()
            return status
        except Exception as e:
            return {
                'status': 'ERROR',
                'route': route_number,
                'error': str(e)
            }

    def get_all_routes_status(self) -> Dict[int, Dict]:
        """Get status of all 8 ROUTEs.

        Returns:
            Dict mapping route_number -> status dict
        """
        results = {}
        for route_num in range(1, 9):
            results[route_num] = self.get_route_status(route_num)
        return results

    def get_c2b_overall_status(self) -> Dict:
        """Get C2-b overall authorization framework status.

        Returns:
            Dict with overall C2-b status, aggregated from all ROUTEs
        """
        try:
            status = self.route_calculator.calculate_c2b_overall_status()
            return status
        except Exception as e:
            return {
                'c2b_status': 'ERROR',
                'error': str(e)
            }

    def is_c2b_operational(self) -> bool:
        """Check if C2-b authorization framework is operational.

        Returns:
            True if C2-b status is PASS, False otherwise
        """
        status = self.get_c2b_overall_status()
        return status.get('status') == 'PASS'

    def get_critical_routes(self) -> List[int]:
        """Identify critical ROUTEs (BLOCK or NOT_READY).

        Returns:
            List of ROUTE numbers that are blocking C2-b
        """
        all_routes = self.get_all_routes_status()
        critical = []
        for route_num, route_status in all_routes.items():
            status_value = route_status.get('status')
            if status_value in ['BLOCK', 'NOT_READY']:
                critical.append(route_num)
        return critical

    def get_authorization_roles_status(self) -> Dict:
        """Verify authorization system can reach all required roles.

        Returns:
            Dict mapping role_name -> is_accessible
        """
        required_roles = RoleRegistry.list_all_roles()
        status = {}

        for role_id in required_roles:
            try:
                role = RoleRegistry.get_role(role_id)
                status[role_id] = 'ACCESSIBLE'
            except Exception as e:
                status[role_id] = f'ERROR: {e}'

        return status

    def get_escalation_chain_status(self) -> Dict:
        """Verify escalation paths form valid DAG.

        Returns:
            Dict with is_valid and any errors found
        """
        is_valid, errors = RoleRegistry.verify_escalation_paths()
        return {
            'is_valid': is_valid,
            'errors': errors,
            'dag_structure': 'VERIFIED' if is_valid else 'INVALID'
        }

    def get_health_summary(self) -> Dict:
        """Get comprehensive health summary of C2-b system.

        Returns:
            Dict with all monitoring metrics
        """
        return {
            'c2b_overall': self.get_c2b_overall_status(),
            'critical_routes': self.get_critical_routes(),
            'is_operational': self.is_c2b_operational(),
            'roles_accessible': list(self.get_authorization_roles_status().values()).count('ACCESSIBLE'),
            'escalation_valid': self.get_escalation_chain_status()['is_valid'],
            'timestamp': self._get_timestamp()
        }

    @staticmethod
    def _get_timestamp() -> str:
        """Get current ISO timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'


# Module-level assertions for runtime verification
assert RoleRegistry.validate_authority('MONITORING_SYSTEM', 'AGGREGATE_ROUTE_STATUS'), \
    "MONITORING_SYSTEM must have AGGREGATE_ROUTE_STATUS capability"
assert RoleRegistry.validate_authority('MONITORING_SYSTEM', 'DETECT_ANOMALIES'), \
    "MONITORING_SYSTEM must have DETECT_ANOMALIES capability"
assert RoleRegistry.validate_authority('MONITORING_SYSTEM', 'GENERATE_ALERTS'), \
    "MONITORING_SYSTEM must have GENERATE_ALERTS capability"
assert RoleRegistry.validate_authority('MONITORING_SYSTEM', 'REPORT_HEALTH_METRICS'), \
    "MONITORING_SYSTEM must have REPORT_HEALTH_METRICS capability"
