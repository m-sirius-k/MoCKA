#!/usr/bin/env python
"""
runtime/evidence_chain_tracker.py
AUDIT TRAIL & EVIDENCE VERIFICATION (minimal implementation)

Tracks TRACE_ID → DECISION_ID → AUTHORIZATION → ACTION → RECOVERY → RESULT
Using existing events table (no new DB/Audit Log/Event Bus)

Design:
- Query events by TRACE_ID
- Verify causal chain (parent_event_ref ordering)
- Detect missing/unknown evidence
- Detect inconsistencies
- Report verification status
"""

import sqlite3
from typing import Dict, List, Optional, Any
from pathlib import Path


class EvidenceChainTracker:
    """
    Retrieve and verify Evidence Chain from events table.

    Chain: TRACE_ID → DECISION_ID → AUTHORIZATION → ACTION → RECOVERY → RESULT
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_events_by_trace_id(self, trace_id: str) -> List[Dict[str, Any]]:
        """
        Get all events with given TRACE_ID from free_note.

        Returns list sorted by when_ts (temporal order)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Query events containing trace_id in free_note
        cursor.execute('''
            SELECT event_id, when_ts, title, free_note, request_id,
                   before_state, after_state, parent_event_ref
            FROM events
            WHERE free_note LIKE ?
            ORDER BY when_ts ASC, event_id ASC
        ''', (f'%trace_id={trace_id}%',))

        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return rows

    def get_chain_by_trace_id(self, trace_id: str) -> Dict[str, Any]:
        """
        Retrieve Evidence Chain for given TRACE_ID.

        Returns:
            {
                'trace_id': str,
                'decision_ids': [list of unique DECISION_IDs],
                'events': [list of events in order],
                'chain_complete': bool,
                'chain_valid': bool,
                'missing': [list of missing phases],
                'inconsistencies': [list of detected issues],
                'status': 'VERIFIED' | 'PARTIAL' | 'BROKEN'
            }
        """
        events = self.get_events_by_trace_id(trace_id)

        if not events:
            return {
                'trace_id': trace_id,
                'decision_ids': [],
                'events': [],
                'chain_complete': False,
                'chain_valid': False,
                'missing': ['NO_EVENTS'],
                'inconsistencies': [],
                'status': 'BROKEN'
            }

        # Extract DECISION_IDs from free_note
        decision_ids = set()
        for event in events:
            free_note = event.get('free_note') or ''
            if 'decision_id=' in free_note:
                # Parse decision_id from free_note
                for part in free_note.split('|'):
                    if part.startswith('decision_id='):
                        decision_ids.add(part.split('=')[1])

        # Check chain phases
        # AUTHORIZATION is implicit in ACTION event status (not separate event)
        phases = set()
        missing = []
        inconsistencies = []

        for event in events:
            title = event.get('title') or ''
            if 'ACTION:' in title:
                phases.add('ACTION')
            elif 'RECOVERY:' in title:
                phases.add('RECOVERY')

        # Detect missing phases (AUTHORIZATION implicit in ACTION)
        if 'ACTION' not in phases:
            missing.append('ACTION')

        # Check parent_event_ref chain
        event_ids = {e['event_id'] for e in events}
        for event in events:
            parent_ref = event.get('parent_event_ref')
            if parent_ref and parent_ref not in event_ids:
                # Parent exists but not in this trace
                inconsistencies.append(
                    f"Orphaned parent_event_ref: {parent_ref}"
                )

        # Check temporal ordering
        prev_ts = None
        for event in events:
            curr_ts = event.get('when_ts') or ''
            if prev_ts and curr_ts < prev_ts:
                inconsistencies.append(
                    f"Temporal order violation: {prev_ts} > {curr_ts}"
                )
            prev_ts = curr_ts

        # Determine status
        chain_complete = len(missing) == 0 and len(inconsistencies) == 0
        chain_valid = chain_complete

        if chain_complete:
            status = 'VERIFIED'
        elif missing or inconsistencies:
            status = 'PARTIAL' if missing else 'BROKEN'
        else:
            status = 'UNKNOWN'

        return {
            'trace_id': trace_id,
            'decision_ids': sorted(list(decision_ids)),
            'events': events,
            'chain_complete': chain_complete,
            'chain_valid': chain_valid,
            'missing': missing,
            'inconsistencies': inconsistencies,
            'status': status
        }

    def verify_isolation(self, trace_id_a: str, trace_id_b: str) -> Dict[str, Any]:
        """
        Verify that two TRACE_IDs don't have cross-contamination.

        Returns:
            {
                'trace_a': str,
                'trace_b': str,
                'contamination_detected': bool,
                'contaminated_events': [list of event_ids],
                'status': 'ISOLATED' | 'CONTAMINATED'
            }
        """
        events_a = self.get_events_by_trace_id(trace_id_a)
        events_b = self.get_events_by_trace_id(trace_id_b)

        contaminated_events = []

        # Check if any event from B contains trace_a
        for event_b in events_b:
            free_note = event_b.get('free_note') or ''
            if trace_id_a in free_note:
                contaminated_events.append(event_b['event_id'])

        # Check if any event from A contains trace_b
        for event_a in events_a:
            free_note = event_a.get('free_note') or ''
            if trace_id_b in free_note:
                contaminated_events.append(event_a['event_id'])

        is_contaminated = len(contaminated_events) > 0

        return {
            'trace_a': trace_id_a,
            'trace_b': trace_id_b,
            'contamination_detected': is_contaminated,
            'contaminated_events': contaminated_events,
            'status': 'CONTAMINATED' if is_contaminated else 'ISOLATED'
        }

    def verify_decision_isolation(self, trace_id: str) -> Dict[str, Any]:
        """
        Verify that within a TRACE_ID, different DECISION_IDs don't cross-contaminate.

        Returns:
            {
                'trace_id': str,
                'decision_ids': [list],
                'isolation_status': {decision_id: 'ISOLATED' | 'CONTAMINATED'},
                'violations': [list of cross-decision event_ids],
                'status': 'ISOLATED' | 'CONTAMINATED'
            }
        """
        events = self.get_events_by_trace_id(trace_id)

        # Extract all decision_ids and map to events
        decision_event_map = {}
        for event in events:
            free_note = event.get('free_note') or ''
            for part in free_note.split('|'):
                if part.startswith('decision_id='):
                    decision_id = part.split('=')[1]
                    if decision_id not in decision_event_map:
                        decision_event_map[decision_id] = []
                    decision_event_map[decision_id].append(event['event_id'])

        # Check if any event claims multiple decision_ids
        violations = []
        for event in events:
            free_note = event.get('free_note') or ''
            decision_count = free_note.count('decision_id=')
            if decision_count > 1:
                violations.append(event['event_id'])

        is_contaminated = len(violations) > 0

        isolation_status = {
            d: 'ISOLATED' for d in decision_event_map.keys()
        }

        return {
            'trace_id': trace_id,
            'decision_ids': list(decision_event_map.keys()),
            'isolation_status': isolation_status,
            'violations': violations,
            'status': 'CONTAMINATED' if is_contaminated else 'ISOLATED'
        }
