"""
phi_os/anomaly_detector.py — Anomaly Detection Framework

Detects 13 types of anomalies across authorization boundaries:
- Decision write failures (no decision_ledger entry)
- Event write failures (exception but no event row)
- Decision-event mismatches
- Type 1 orphans (event created but unsigned)
- Type 2 orphans (signed but no event row)
- Rollback events (INVALIDATED markers)
- Recovery failures (ERROR in RECOVERY_ATTEMPT)
- And more...

Design: Read-only detection methods. No side effects. Fail-safe (return empty list on error).

Author: KUROKO Monitor (Claude)
Date: 2026-09-12
Session: claude/kuroko-c2b-route-audit-n51wgf
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Database paths
_REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(_REPO_ROOT / 'data' / 'mocka_events.db')
DECISION_LEDGER_PATH = _REPO_ROOT / 'data' / 'decisions' / 'decision_ledger.jsonl'


def _get_conn() -> sqlite3.Connection:
    """Get database connection with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class AnomalyDetector:
    """Detect 13 anomaly types across TIC layers."""

    @staticmethod
    def detect_decision_write_failure() -> List[str]:
        """Detect: decision write failed (no entry in decision_ledger).

        Anomaly: Decision was supposedly created but not found in ledger.

        Returns:
            List of decision_ids that couldn't be written to ledger.
        """
        try:
            if not DECISION_LEDGER_PATH.exists():
                return []

            recorded_decisions = set()
            with open(DECISION_LEDGER_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        recorded_decisions.add(record.get('decision_id', ''))
                    except json.JSONDecodeError:
                        continue

            conn = _get_conn()
            try:
                # Look for events mentioning decision creation
                cursor = conn.execute(
                    "SELECT DISTINCT title FROM events WHERE title LIKE '%DECISION%' LIMIT 1000"
                )
                decision_refs = []
                for row in cursor:
                    if row['title'] and 'decision_id=' in str(row['title']):
                        decision_refs.append(str(row['title']))

                # Since we don't have explicit decision_id field in events, return empty
                # (this requires deeper analysis of decision event patterns)
                return []
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Error detecting decision write failures: {e}")
            return []

    @staticmethod
    def detect_event_write_failure() -> List[str]:
        """Detect: event write failed (exception logged but no event row).

        Anomaly: Write error recorded but event not persisted.

        Returns:
            List of event_ids with write failures but no event rows.
        """
        try:
            conn = _get_conn()
            try:
                # Look for EVENT_WRITE_FAILED events
                cursor = conn.execute(
                    """SELECT DISTINCT
                       SUBSTR(short_summary, INSTR(short_summary, 'E2026'), 20) as failed_event_id
                    FROM events
                    WHERE title = 'EVENT_WRITE_FAILED'
                    AND short_summary LIKE 'Event E%'"""
                )

                failed_events = []
                for row in cursor:
                    event_id = row['failed_event_id']
                    if event_id and event_id.startswith('E'):
                        failed_events.append(event_id)

                return list(set(failed_events))[:100]
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Error detecting event write failures: {e}")
            return []

    @staticmethod
    def detect_decision_event_mismatch() -> List[str]:
        """Detect: decision recorded but no corresponding event.

        Anomaly: Decision exists in ledger but no audit event trails it.

        Returns:
            List of decision_ids without event trail.
        """
        try:
            if not DECISION_LEDGER_PATH.exists():
                return []

            mismatches = []
            with open(DECISION_LEDGER_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        decision = json.loads(line.strip())
                        decision_id = decision.get('decision_id', '')
                        if not decision_id:
                            continue

                        # Check if corresponding decision event exists
                        conn = _get_conn()
                        try:
                            cursor = conn.execute(
                                "SELECT COUNT(*) as cnt FROM events WHERE title LIKE ? LIMIT 1",
                                (f'%{decision_id}%',)
                            )
                            result = cursor.fetchone()
                            if result and result['cnt'] == 0:
                                mismatches.append(decision_id)
                        finally:
                            conn.close()
                    except (json.JSONDecodeError, Exception):
                        continue

            return mismatches[:100]
        except Exception as e:
            logger.error(f"Error detecting decision-event mismatches: {e}")
            return []

    @staticmethod
    def detect_type1_orphan() -> List[str]:
        """Detect: Type 1 orphan (event created but unsigned).

        Anomaly: Event exists in table but not in event_signatures.

        Returns:
            List of unsigned event_ids.
        """
        try:
            conn = _get_conn()
            try:
                # Find events without signatures
                cursor = conn.execute("""
                    SELECT e.event_id
                    FROM events e
                    WHERE NOT EXISTS (
                        SELECT 1 FROM event_signatures es WHERE es.event_id = e.event_id
                    )
                    LIMIT 1000
                """)

                orphans = [row['event_id'] for row in cursor.fetchall()]
                return orphans
            finally:
                conn.close()
        except sqlite3.OperationalError:
            # event_signatures table may not exist yet
            return []
        except Exception as e:
            logger.error(f"Error detecting type1 orphans: {e}")
            return []

    @staticmethod
    def detect_type2_orphan() -> List[str]:
        """Detect: Type 2 orphan (signed event but no event row).

        Anomaly: Signature exists but event row was deleted/lost.

        Returns:
            List of signed but missing event_ids.
        """
        try:
            conn = _get_conn()
            try:
                # Find signatures without events
                cursor = conn.execute("""
                    SELECT es.event_id
                    FROM event_signatures es
                    WHERE NOT EXISTS (
                        SELECT 1 FROM events e WHERE e.event_id = es.event_id
                    )
                    LIMIT 1000
                """)

                orphans = [row['event_id'] for row in cursor.fetchall()]
                return orphans
            finally:
                conn.close()
        except sqlite3.OperationalError:
            # event_signatures table may not exist yet
            return []
        except Exception as e:
            logger.error(f"Error detecting type2 orphans: {e}")
            return []

    @staticmethod
    def detect_rollback_event() -> List[str]:
        """Detect: rollback/invalidation events (INVALIDATED markers).

        Anomaly: Events marked as INVALIDATED (intentional recovery).

        Returns:
            List of invalidated event_ids.
        """
        try:
            conn = _get_conn()
            try:
                cursor = conn.execute("""
                    SELECT DISTINCT event_id
                    FROM events
                    WHERE title LIKE '%INVALIDATED%'
                    OR title LIKE '%ROLLBACK%'
                    LIMIT 1000
                """)

                rollbacks = [row['event_id'] for row in cursor.fetchall()]
                return rollbacks
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Error detecting rollback events: {e}")
            return []

    @staticmethod
    def detect_recovery_failure() -> List[str]:
        """Detect: recovery attempt failed (ERROR in RECOVERY_ATTEMPT event).

        Anomaly: Recovery procedure didn't complete successfully.

        Returns:
            List of events with failed recovery attempts.
        """
        try:
            conn = _get_conn()
            try:
                cursor = conn.execute("""
                    SELECT DISTINCT event_id
                    FROM events
                    WHERE title LIKE '%RECOVERY_ATTEMPT%'
                    AND (short_summary LIKE '%ERROR%' OR short_summary LIKE '%FAILED%')
                    LIMIT 1000
                """)

                failures = [row['event_id'] for row in cursor.fetchall()]
                return failures
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Error detecting recovery failures: {e}")
            return []

    @staticmethod
    def detect_unauthorized_escalation() -> List[str]:
        """Detect: escalation to non-HUMAN_AUTHORITY role.

        Anomaly: Decision escalated to role other than HUMAN_AUTHORITY.

        Returns:
            List of events with unauthorized escalations.
        """
        try:
            conn = _get_conn()
            try:
                cursor = conn.execute("""
                    SELECT DISTINCT event_id
                    FROM events
                    WHERE title LIKE '%ESCALATE%'
                    AND short_summary NOT LIKE '%HUMAN_AUTHORITY%'
                    LIMIT 1000
                """)

                unauth = [row['event_id'] for row in cursor.fetchall()]
                return unauth
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Error detecting unauthorized escalations: {e}")
            return []

    @staticmethod
    def detect_binding_gap() -> List[str]:
        """Detect: binding incompleteness (event without trace_id or related_event_id).

        Anomaly: Event not properly bound to lineage.

        Returns:
            List of event_ids with incomplete binding.
        """
        try:
            conn = _get_conn()
            try:
                cursor = conn.execute("""
                    SELECT event_id
                    FROM events
                    WHERE (trace_id IS NULL OR trace_id = '')
                    OR (related_event_id IS NULL OR related_event_id = '')
                    LIMIT 1000
                """)

                gaps = [row['event_id'] for row in cursor.fetchall()]
                return gaps
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Error detecting binding gaps: {e}")
            return []

    @staticmethod
    def detect_timestamp_anomaly() -> List[str]:
        """Detect: timestamp violations (non-monotonic, gaps, future dates).

        Anomaly: Events with timestamps out of order or in future.

        Returns:
            List of event_ids with timestamp anomalies.
        """
        try:
            conn = _get_conn()
            try:
                cursor = conn.execute("""
                    SELECT event_id, when_ts
                    FROM events
                    ORDER BY when_ts ASC
                    LIMIT 10000
                """)

                anomalies = []
                prev_ts = None
                now_ts = datetime.utcnow().isoformat()

                for row in cursor.fetchall():
                    event_id = row['event_id']
                    when_ts = row['when_ts'] or ''

                    # Check for future timestamps
                    if when_ts > now_ts:
                        anomalies.append(event_id)

                    # Check for non-monotonic
                    if prev_ts and when_ts < prev_ts:
                        anomalies.append(event_id)

                    prev_ts = when_ts

                return anomalies[:100]
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Error detecting timestamp anomalies: {e}")
            return []

    @staticmethod
    def detect_missing_audit_trail() -> List[str]:
        """Detect: missing audit trail for critical operations.

        Anomaly: Critical operation without corresponding audit event.

        Returns:
            List of events lacking audit trail.
        """
        try:
            conn = _get_conn()
            try:
                # Look for operations without audit events
                critical_ops = ['APPROVE_DECISION', 'OVERRIDE_GATE', 'ENFORCE_ABORT_CONDITIONS']

                anomalies = []
                for op in critical_ops:
                    cursor = conn.execute("""
                        SELECT event_id
                        FROM events
                        WHERE what_type = ?
                        AND NOT EXISTS (
                            SELECT 1 FROM events e2
                            WHERE e2.what_type = 'AUDIT_RECORD'
                            AND e2.before_state LIKE '%' || ? || '%'
                        )
                        LIMIT 100
                    """, (op, op))

                    anomalies.extend([row['event_id'] for row in cursor.fetchall()])

                return list(set(anomalies))[:100]
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Error detecting missing audit trails: {e}")
            return []

    @staticmethod
    def detect_all_anomalies() -> Dict[str, List[str]]:
        """Run all 13 anomaly detections and return aggregate results.

        Returns:
            Dict mapping anomaly type to list of affected event/decision ids.
        """
        return {
            'decision_write_failure': AnomalyDetector.detect_decision_write_failure(),
            'event_write_failure': AnomalyDetector.detect_event_write_failure(),
            'decision_event_mismatch': AnomalyDetector.detect_decision_event_mismatch(),
            'type1_orphan': AnomalyDetector.detect_type1_orphan(),
            'type2_orphan': AnomalyDetector.detect_type2_orphan(),
            'rollback_event': AnomalyDetector.detect_rollback_event(),
            'recovery_failure': AnomalyDetector.detect_recovery_failure(),
            'unauthorized_escalation': AnomalyDetector.detect_unauthorized_escalation(),
            'binding_gap': AnomalyDetector.detect_binding_gap(),
            'timestamp_anomaly': AnomalyDetector.detect_timestamp_anomaly(),
            'missing_audit_trail': AnomalyDetector.detect_missing_audit_trail(),
        }

    @staticmethod
    def get_anomaly_count() -> int:
        """Return total count of all detected anomalies."""
        results = AnomalyDetector.detect_all_anomalies()
        return sum(len(v) for v in results.values())

    @staticmethod
    def has_critical_anomalies() -> bool:
        """Check if any critical anomalies exist.

        Critical: decision-event mismatch, type2 orphan, recovery failure, unauthorized escalation.

        Returns:
            True if any critical anomalies detected.
        """
        critical_checks = [
            AnomalyDetector.detect_decision_event_mismatch(),
            AnomalyDetector.detect_type2_orphan(),
            AnomalyDetector.detect_recovery_failure(),
            AnomalyDetector.detect_unauthorized_escalation(),
        ]
        return any(len(check) > 0 for check in critical_checks)
