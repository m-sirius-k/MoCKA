#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phase8_ledger.py -- Query interface for Phase 8 Decision Ledger and Event Log
Reads from data/decisions/decision_ledger.jsonl and data/decisions/decision_events.jsonl
No duplication. No parallel ledger. Direct read-back from persisted sources.
"""

import json
from pathlib import Path
from typing import Optional, Dict, List, Any


class Phase8LedgerQuery:
    """Query interface for Phase 8 Decision Ledger and Event Log"""

    def __init__(self, repo_root: Optional[Path] = None):
        if repo_root is None:
            # Auto-detect repo root
            repo_root = Path(__file__).resolve().parent.parent
        self.repo_root = repo_root
        self.ledger_path = repo_root / "data" / "decisions" / "decision_ledger.jsonl"
        self.event_path = repo_root / "data" / "decisions" / "decision_events.jsonl"
        self.hab_dispatch_path = repo_root / "data" / "hab_dispatch.jsonl"
        self.hab_execution_path = repo_root / "data" / "hab_execution.jsonl"
        self._decisions_cache = None
        self._events_cache = None
        self._dispatch_cache = None
        self._execution_cache = None
        self._task_to_decisions = None
        self._corr_to_decisions = None
        self._decision_to_events = None
        self._task_to_seals = None

    def _load_decisions(self) -> List[Dict]:
        """Load all decisions from ledger file"""
        if self._decisions_cache is not None:
            return self._decisions_cache

        if not self.ledger_path.exists():
            return []

        decisions = []
        try:
            with open(self.ledger_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        decisions.append(record)
        except Exception as e:
            print(f"[phase8_ledger] Error loading decisions: {e}")
            return []

        self._decisions_cache = decisions
        return decisions

    def _load_events(self) -> List[Dict]:
        """Load all events from event log file"""
        if self._events_cache is not None:
            return self._events_cache

        if not self.event_path.exists():
            return []

        events = []
        try:
            with open(self.event_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        events.append(record)
        except Exception as e:
            print(f"[phase8_ledger] Error loading events: {e}")
            return []

        self._events_cache = events
        return events

    def _load_dispatch_records(self) -> List[Dict]:
        """Load HAB dispatch records (contains memory seals)"""
        if self._dispatch_cache is not None:
            return self._dispatch_cache

        if not self.hab_dispatch_path.exists():
            return []

        records = []
        try:
            with open(self.hab_dispatch_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        records.append(record)
        except Exception as e:
            print(f"[phase8_ledger] Error loading dispatch records: {e}")
            return []

        self._dispatch_cache = records
        return records

    def _load_execution_records(self) -> List[Dict]:
        """Load HAB execution records (contains execution seals)"""
        if self._execution_cache is not None:
            return self._execution_cache

        if not self.hab_execution_path.exists():
            return []

        records = []
        try:
            with open(self.hab_execution_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        records.append(record)
        except Exception as e:
            print(f"[phase8_ledger] Error loading execution records: {e}")
            return []

        self._execution_cache = records
        return records

    def _build_task_index(self) -> Dict[str, List[Dict]]:
        """Build index: task_id -> [decisions]"""
        if self._task_to_decisions is not None:
            return self._task_to_decisions

        index = {}
        decisions = self._load_decisions()

        for decision in decisions:
            # Extract task_id from title or context
            title = decision.get('title', '')
            context = decision.get('context', '')

            # Look for TASK_YYYYMMDD_* pattern
            for text in [title, context]:
                if 'TASK_' in text:
                    # Simple extraction: find TASK_YYYYMMDD_xxx
                    import re
                    match = re.search(r'(TASK_\d{8}_[0-9a-f]+)', text)
                    if match:
                        task_id = match.group(1)
                        if task_id not in index:
                            index[task_id] = []
                        index[task_id].append(decision)
                        break

        self._task_to_decisions = index
        return index

    def _build_corr_index(self) -> Dict[str, List[Dict]]:
        """Build index: correlation_id -> [decisions]"""
        if self._corr_to_decisions is not None:
            return self._corr_to_decisions

        index = {}
        decisions = self._load_decisions()

        for decision in decisions:
            # Extract correlation_id from context
            context = decision.get('context', '')

            # Look for CORR_* pattern
            if 'CORR_' in context:
                import re
                match = re.search(r'(CORR_[0-9a-f]+)', context)
                if match:
                    corr_id = match.group(1)
                    if corr_id not in index:
                        index[corr_id] = []
                    index[corr_id].append(decision)

        self._corr_to_decisions = index
        return index

    def _build_decision_to_event_index(self) -> Dict[str, List[Dict]]:
        """Build index: decision_id -> [events]"""
        if self._decision_to_events is not None:
            return self._decision_to_events

        index = {}
        events = self._load_events()

        for event in events:
            decision_id = event.get('decision_id')
            if decision_id:
                if decision_id not in index:
                    index[decision_id] = []
                index[decision_id].append(event)

        self._decision_to_events = index
        return index

    def locate_by_task_id(self, task_id: str) -> Optional[Dict]:
        """Find decision by task_id. Returns first matching decision."""
        index = self._build_task_index()
        decisions = index.get(task_id, [])
        return decisions[0] if decisions else None

    def locate_by_correlation_id(self, corr_id: str) -> Optional[Dict]:
        """Find decision by correlation_id. Returns first matching decision."""
        index = self._build_corr_index()
        decisions = index.get(corr_id, [])
        return decisions[0] if decisions else None

    def locate_by_decision_id(self, decision_id: str) -> Optional[Dict]:
        """Find decision by decision_id (primary key)."""
        decisions = self._load_decisions()
        for decision in decisions:
            if decision.get('decision_id') == decision_id:
                return decision
        return None

    def locate_by_event_id(self, event_id: str) -> Optional[Dict]:
        """Find event by event_id (primary key)."""
        events = self._load_events()
        for event in events:
            if event.get('event_id') == event_id:
                return event
        return None

    def get_events_for_decision(self, decision_id: str) -> List[Dict]:
        """Get all events linked to a decision."""
        index = self._build_decision_to_event_index()
        return index.get(decision_id, [])

    def get_decisions_for_task(self, task_id: str) -> List[Dict]:
        """Get all decisions for a task (typically 4: 8-4, 8-5, 8-6, 8-7)."""
        index = self._build_task_index()
        return index.get(task_id, [])

    def get_seals_for_task(self, task_id: str) -> Dict[str, Any]:
        """Get memory seals for a task from dispatch and execution records"""
        seals = {
            "phase_8_4": None,
            "phase_8_5": None,
            "phase_8_6": None,
            "phase_8_7": None
        }

        # Check dispatch records
        dispatch = self._load_dispatch_records()
        for record in dispatch:
            if record.get('task_id') == task_id:
                # Check for old-style seals in task_data
                task_data = record.get('task_data', {})
                seal_8_4 = task_data.get('seal_hash_8_4')
                seal_8_5 = task_data.get('memory_seal')  # From 8-5
                if seal_8_4:
                    seals['phase_8_4'] = seal_8_4
                if seal_8_5:
                    seals['phase_8_5'] = seal_8_5
                # Check for new-style seal records (type="seal", phase="8-6")
                if record.get('type') == 'seal' and record.get('phase') == '8-6':
                    seal_8_6 = record.get('memory_seal')
                    if seal_8_6:
                        seals['phase_8_6'] = seal_8_6

        # Check execution records
        execution = self._load_execution_records()
        for record in execution:
            if record.get('task_id') == task_id:
                # Check for old-style seal in task_data
                task_data = record.get('task_data', {})
                seal = task_data.get('memory_seal')
                if seal:
                    seals['phase_8_7'] = seal
                # Check for new-style seal record (type="seal", phase="8-7")
                if record.get('type') == 'seal' and record.get('phase') == '8-7':
                    seal_8_7 = record.get('memory_seal')
                    if seal_8_7:
                        seals['phase_8_7'] = seal_8_7

        return seals

    def trace_execution_chain(self, task_id: str) -> Dict[str, Any]:
        """
        Trace complete execution chain for a task:
        task_id -> [decisions] -> [events] -> [seals]
        """
        decisions = self.get_decisions_for_task(task_id)
        seals = self.get_seals_for_task(task_id)

        trace = {
            "task_id": task_id,
            "status": "found" if decisions else "not_found",
            "decisions": [],
            "events": [],
            "memory_seals": seals
        }

        if not decisions:
            return trace

        # Collect decisions and their events
        for decision in decisions:
            decision_id = decision.get('decision_id')
            events = self.get_events_for_decision(decision_id)

            trace["decisions"].append({
                "decision_id": decision_id,
                "title": decision.get('title'),
                "approved_by": decision.get('approved_by'),
                "status": decision.get('status')
            })

            # Add events for this decision
            for event in events:
                trace["events"].append({
                    "event_id": event.get('event_id'),
                    "decision_id": decision_id,
                    "event_type": event.get('event_type'),
                    "status": event.get('status')
                })

        return trace

    def get_all_decisions(self, limit: int = 100) -> List[Dict]:
        """Get recent decisions (up to limit)"""
        decisions = self._load_decisions()
        return decisions[-limit:] if limit > 0 else decisions

    def get_all_events(self, limit: int = 100) -> List[Dict]:
        """Get recent events (up to limit)"""
        events = self._load_events()
        return events[-limit:] if limit > 0 else events

    def refresh_cache(self):
        """Force reload from disk"""
        self._decisions_cache = None
        self._events_cache = None
        self._task_to_decisions = None
        self._corr_to_decisions = None
        self._decision_to_events = None
