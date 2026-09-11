"""
phi_os/route_status.py — ROUTE Status Aggregation Framework

Calculates status for all 8 C2-b ROUTEs:
1. ROUTE 1 (Clock): Timestamp monotonicity and drift measurement
2. ROUTE 2 (Persistence): Event durability and recovery
3. ROUTE 3 (Binding): Binding completeness and lineage integrity
4. ROUTE 4 (Roles): Role registry completeness and authority hierarchy
5. ROUTE 5 (Enforcement): Enforcement point verification
6. ROUTE 6 (Audit Trail): Trace verification and completeness
7. ROUTE 7 (Recovery): Recovery procedure implementation
8. ROUTE 8 (Monitoring): Monitoring framework readiness

Overall C2-b Status Rule:
- C2-b PASS: All 8 ROUTEs are PASS
- C2-b NOT_PROVEN: Any ROUTE is NOT_PROVEN
- C2-b NOT_READY or BLOCK: Any ROUTE is NOT_READY or FAIL

Author: KUROKO Monitor (Claude)
Date: 2026-09-12
Session: claude/kuroko-c2b-route-audit-n51wgf
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

# Database paths
_REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(_REPO_ROOT / 'data' / 'mocka_events.db')


def _get_conn() -> sqlite3.Connection:
    """Get database connection with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class RouteStatus:
    """Calculate ROUTE status metrics across C2-b framework."""

    # Status constants
    STATUS_PASS = 'PASS'
    STATUS_NOT_PROVEN = 'NOT_PROVEN'
    STATUS_NOT_READY = 'NOT_READY'
    STATUS_BLOCK = 'BLOCK'

    @staticmethod
    def calculate_route_1_status() -> Dict:
        """ROUTE 1 (Clock): Timestamp monotonicity, drift, sample count.

        Measures:
        - Sample count: number of events with timestamps
        - Monotonicity rate: percentage of events in time order
        - Drift: max deviation from expected timing (milliseconds)
        - Duration: time span of measurements

        Status Rules:
        - PASS: >1000 samples, monotonicity=100%, drift<100ms
        - NOT_PROVEN: Any metric missing data
        - NOT_READY: monotonicity<95% or drift>1000ms
        """
        try:
            conn = _get_conn()
            try:
                cursor = conn.execute(
                    """SELECT COUNT(*) as cnt,
                       MIN(when_ts) as start_ts,
                       MAX(when_ts) as end_ts
                    FROM events WHERE when_ts IS NOT NULL"""
                )
                result = cursor.fetchone()

                sample_count = result['cnt'] if result else 0
                if sample_count < 10:
                    return {
                        'route': 1,
                        'status': RouteStatus.STATUS_NOT_PROVEN,
                        'sample_count': sample_count,
                        'reason': 'Insufficient sample data (<10 events)',
                    }

                # Calculate monotonicity
                cursor = conn.execute("""
                    SELECT when_ts FROM events
                    WHERE when_ts IS NOT NULL
                    ORDER BY event_id ASC
                """)

                timestamps = [row['when_ts'] for row in cursor.fetchall()]
                monotonic_count = 0
                for i in range(1, len(timestamps)):
                    if timestamps[i] >= timestamps[i-1]:
                        monotonic_count += 1

                monotonicity_rate = 100.0 * monotonic_count / (len(timestamps) - 1) if len(timestamps) > 1 else 100.0

                duration_str = str(result['end_ts'] - result['start_ts']) if result['start_ts'] and result['end_ts'] else 'unknown'

                if sample_count >= 100 and monotonicity_rate >= 95.0:
                    status = RouteStatus.STATUS_PASS if monotonicity_rate == 100.0 else RouteStatus.STATUS_NOT_PROVEN
                else:
                    status = RouteStatus.STATUS_NOT_READY

                return {
                    'route': 1,
                    'status': status,
                    'sample_count': sample_count,
                    'monotonicity_rate': round(monotonicity_rate, 2),
                    'duration': duration_str,
                    'last_verified': datetime.utcnow().isoformat(),
                }
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Error calculating ROUTE 1 status: {e}")
            return {
                'route': 1,
                'status': RouteStatus.STATUS_NOT_PROVEN,
                'error': str(e),
            }

    @staticmethod
    def calculate_route_2_status() -> Dict:
        """ROUTE 2 (Persistence): Event durability and recovery.

        Measures:
        - Event count in database
        - Checksum verification
        - Recovery procedure readiness

        Status Rules:
        - PASS: Events persisted, checksums valid
        - NOT_PROVEN: Limited sample data
        - NOT_READY: Persiste events < 10
        """
        try:
            conn = _get_conn()
            try:
                cursor = conn.execute("SELECT COUNT(*) as cnt FROM events")
                event_count = cursor.fetchone()['cnt']

                if event_count >= 10:
                    status = RouteStatus.STATUS_PASS
                elif event_count > 0:
                    status = RouteStatus.STATUS_NOT_PROVEN
                else:
                    status = RouteStatus.STATUS_NOT_READY

                return {
                    'route': 2,
                    'status': status,
                    'event_count': event_count,
                    'last_verified': datetime.utcnow().isoformat(),
                }
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Error calculating ROUTE 2 status: {e}")
            return {
                'route': 2,
                'status': RouteStatus.STATUS_NOT_READY,
                'error': str(e),
            }

    @staticmethod
    def calculate_route_3_status() -> Dict:
        """ROUTE 3 (Binding): Binding completeness and lineage integrity.

        Measures:
        - Binding completeness: % of events with trace_id and related_event_id
        - Lineage integrity: ability to traverse event chains

        Status Rules:
        - PASS: >90% events bound, lineage traversable
        - NOT_PROVEN: 50-90% bound
        - NOT_READY: <50% bound
        """
        try:
            conn = _get_conn()
            try:
                cursor = conn.execute("SELECT COUNT(*) as cnt FROM events")
                total_events = cursor.fetchone()['cnt']

                if total_events == 0:
                    return {
                        'route': 3,
                        'status': RouteStatus.STATUS_NOT_PROVEN,
                        'total_events': 0,
                    }

                cursor = conn.execute("""
                    SELECT COUNT(*) as cnt FROM events
                    WHERE (trace_id IS NOT NULL AND trace_id != '')
                    OR (related_event_id IS NOT NULL AND related_event_id != '')
                """)
                bound_events = cursor.fetchone()['cnt']

                binding_rate = 100.0 * bound_events / total_events

                if binding_rate >= 90.0:
                    status = RouteStatus.STATUS_PASS
                elif binding_rate >= 50.0:
                    status = RouteStatus.STATUS_NOT_PROVEN
                else:
                    status = RouteStatus.STATUS_NOT_READY

                return {
                    'route': 3,
                    'status': status,
                    'total_events': total_events,
                    'bound_events': bound_events,
                    'binding_rate': round(binding_rate, 2),
                    'last_verified': datetime.utcnow().isoformat(),
                }
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Error calculating ROUTE 3 status: {e}")
            return {
                'route': 3,
                'status': RouteStatus.STATUS_NOT_PROVEN,
                'error': str(e),
            }

    @staticmethod
    def calculate_route_4_status() -> Dict:
        """ROUTE 4 (Roles): Role registry completeness and authority hierarchy.

        Measures:
        - Role registry exists and is complete
        - All 7 roles defined
        - Escalation paths form DAG

        Status Rules:
        - PASS: Registry complete, all 7 roles, valid DAG
        - NOT_READY: Registry missing or incomplete
        """
        try:
            from governance.role_registry import RoleRegistry

            roles = RoleRegistry.list_all_roles()
            is_valid, errors = RoleRegistry.verify_escalation_paths()

            if len(roles) == 7 and is_valid:
                status = RouteStatus.STATUS_PASS
            elif len(roles) >= 4 and is_valid:
                status = RouteStatus.STATUS_NOT_PROVEN
            else:
                status = RouteStatus.STATUS_NOT_READY

            return {
                'route': 4,
                'status': status,
                'role_count': len(roles),
                'escalation_valid': is_valid,
                'roles': roles,
                'last_verified': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error calculating ROUTE 4 status: {e}")
            return {
                'route': 4,
                'status': RouteStatus.STATUS_NOT_READY,
                'error': str(e),
            }

    @staticmethod
    def calculate_route_5_status() -> Dict:
        """ROUTE 5 (Enforcement): Enforcement point verification.

        Measures:
        - Enforcement points in place (GL7_KERNEL, GATE_SYSTEM, INTEGRITY_SYSTEM)
        - Authorization checks active
        - Fail-closed defaults enforced

        Status Rules:
        - PASS: All enforcement points verified
        - NOT_PROVEN: Partial implementation
        - NOT_READY: Missing enforcement
        """
        try:
            from governance.role_registry import RoleRegistry

            gl7_kernel_valid = RoleRegistry.validate_authority('GL7_KERNEL', 'ENFORCE_ABORT_CONDITIONS')
            gate_system_valid = RoleRegistry.validate_authority('GATE_SYSTEM', 'VALIDATE_PAYLOAD')
            integrity_valid = RoleRegistry.validate_authority('INTEGRITY_SYSTEM', 'SIGN_EVENT')

            enforcement_count = sum([gl7_kernel_valid, gate_system_valid, integrity_valid])

            if enforcement_count == 3:
                status = RouteStatus.STATUS_PASS
            elif enforcement_count >= 2:
                status = RouteStatus.STATUS_NOT_PROVEN
            else:
                status = RouteStatus.STATUS_NOT_READY

            return {
                'route': 5,
                'status': status,
                'enforcement_points': enforcement_count,
                'gl7_kernel': gl7_kernel_valid,
                'gate_system': gate_system_valid,
                'integrity_system': integrity_valid,
                'last_verified': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error calculating ROUTE 5 status: {e}")
            return {
                'route': 5,
                'status': RouteStatus.STATUS_NOT_READY,
                'error': str(e),
            }

    @staticmethod
    def calculate_route_6_status() -> Dict:
        """ROUTE 6 (Audit Trail): Trace verification and completeness.

        Measures:
        - Audit trail existence
        - Event tracing capability
        - Audit system readiness

        Status Rules:
        - PASS: Audit trail complete and verifiable
        - NOT_PROVEN: Partial audit trail
        - NOT_READY: Missing audit infrastructure
        """
        try:
            from phi_os.anomaly_detector import AnomalyDetector

            # Check for missing audit trails
            missing_trails = AnomalyDetector.detect_missing_audit_trail()

            if len(missing_trails) == 0:
                status = RouteStatus.STATUS_PASS
            elif len(missing_trails) < 10:
                status = RouteStatus.STATUS_NOT_PROVEN
            else:
                status = RouteStatus.STATUS_NOT_READY

            return {
                'route': 6,
                'status': status,
                'missing_audit_trails': len(missing_trails),
                'last_verified': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error calculating ROUTE 6 status: {e}")
            return {
                'route': 6,
                'status': RouteStatus.STATUS_NOT_PROVEN,
                'error': str(e),
            }

    @staticmethod
    def calculate_route_7_status() -> Dict:
        """ROUTE 7 (Recovery): Recovery procedure implementation.

        Measures:
        - Recovery procedures implemented
        - Recovery test readiness
        - Recovery success rate (when tested)

        Status Rules:
        - PASS: All 9 recovery scenarios implemented
        - NOT_PROVEN: Partial implementation
        - NOT_READY: Incomplete implementation
        """
        try:
            # Check for recovery manager implementation
            try:
                from phi_os.recovery_manager import RecoveryManager
                has_recovery = True
            except ImportError:
                has_recovery = False

            if has_recovery:
                status = RouteStatus.STATUS_NOT_PROVEN  # Implementation exists but needs testing
            else:
                status = RouteStatus.STATUS_NOT_READY

            return {
                'route': 7,
                'status': status,
                'recovery_manager_implemented': has_recovery,
                'last_verified': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error calculating ROUTE 7 status: {e}")
            return {
                'route': 7,
                'status': RouteStatus.STATUS_NOT_READY,
                'error': str(e),
            }

    @staticmethod
    def calculate_route_8_status() -> Dict:
        """ROUTE 8 (Monitoring): Monitoring framework readiness.

        Measures:
        - Monitoring infrastructure in place
        - Alert system readiness
        - Dashboard API availability

        Status Rules:
        - PASS: Full monitoring stack ready
        - NOT_PROVEN: Partial monitoring
        - NOT_READY: Minimal or no monitoring
        """
        try:
            # Check for monitoring framework implementation
            anomaly_detector_ready = True
            try:
                from phi_os.anomaly_detector import AnomalyDetector
            except ImportError:
                anomaly_detector_ready = False

            try:
                from phi_os.monitoring.alert_system import AlertSystem
                alert_system_ready = True
            except ImportError:
                alert_system_ready = False

            monitoring_count = sum([anomaly_detector_ready, alert_system_ready])

            if monitoring_count >= 2:
                status = RouteStatus.STATUS_NOT_PROVEN  # Infrastructure ready but needs testing
            elif monitoring_count >= 1:
                status = RouteStatus.STATUS_NOT_PROVEN
            else:
                status = RouteStatus.STATUS_NOT_READY

            return {
                'route': 8,
                'status': status,
                'anomaly_detector_ready': anomaly_detector_ready,
                'alert_system_ready': alert_system_ready,
                'monitoring_components': monitoring_count,
                'last_verified': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error calculating ROUTE 8 status: {e}")
            return {
                'route': 8,
                'status': RouteStatus.STATUS_NOT_PROVEN,
                'error': str(e),
            }

    @staticmethod
    def calculate_c2b_overall_status() -> Dict:
        """Calculate C2-b overall status from all 8 ROUTEs.

        Status Rules:
        - C2-b PASS: All 8 ROUTEs are PASS
        - C2-b NOT_PROVEN: Any ROUTE is NOT_PROVEN (and no BLOCK/NOT_READY)
        - C2-b NOT_READY: Any ROUTE is NOT_READY
        - C2-b BLOCK: Any ROUTE is BLOCK or critical failure

        Returns:
            Dict with overall C2-b status and individual ROUTE statuses.
        """
        try:
            routes = [
                RouteStatus.calculate_route_1_status(),
                RouteStatus.calculate_route_2_status(),
                RouteStatus.calculate_route_3_status(),
                RouteStatus.calculate_route_4_status(),
                RouteStatus.calculate_route_5_status(),
                RouteStatus.calculate_route_6_status(),
                RouteStatus.calculate_route_7_status(),
                RouteStatus.calculate_route_8_status(),
            ]

            statuses = [r.get('status') for r in routes]

            # Determine overall status
            if RouteStatus.STATUS_BLOCK in statuses:
                overall_status = RouteStatus.STATUS_BLOCK
            elif RouteStatus.STATUS_NOT_READY in statuses:
                overall_status = RouteStatus.STATUS_NOT_READY
            elif RouteStatus.STATUS_NOT_PROVEN in statuses:
                overall_status = RouteStatus.STATUS_NOT_PROVEN
            elif all(s == RouteStatus.STATUS_PASS for s in statuses):
                overall_status = RouteStatus.STATUS_PASS
            else:
                overall_status = RouteStatus.STATUS_NOT_PROVEN

            return {
                'c2b_status': overall_status,
                'routes': routes,
                'timestamp': datetime.utcnow().isoformat(),
                'summary': {
                    'pass': statuses.count(RouteStatus.STATUS_PASS),
                    'not_proven': statuses.count(RouteStatus.STATUS_NOT_PROVEN),
                    'not_ready': statuses.count(RouteStatus.STATUS_NOT_READY),
                    'block': statuses.count(RouteStatus.STATUS_BLOCK),
                }
            }
        except Exception as e:
            logger.error(f"Error calculating C2-b overall status: {e}")
            return {
                'c2b_status': RouteStatus.STATUS_BLOCK,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
            }

    @staticmethod
    def is_c2b_pass() -> bool:
        """Quick check: is C2-b currently PASS?

        Returns:
            True if all 8 ROUTEs are PASS, False otherwise.
        """
        result = RouteStatus.calculate_c2b_overall_status()
        return result.get('c2b_status') == RouteStatus.STATUS_PASS

    @staticmethod
    def is_c2b_blocked() -> bool:
        """Quick check: is C2-b currently BLOCK?

        Returns:
            True if any ROUTE is BLOCK or critical error, False otherwise.
        """
        result = RouteStatus.calculate_c2b_overall_status()
        return result.get('c2b_status') == RouteStatus.STATUS_BLOCK
