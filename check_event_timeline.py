#!/usr/bin/env python3
"""
Check when existing governance_block events were recorded
to determine if they predate the staged A+B implementation
"""

import sqlite3
from datetime import datetime

db_path = 'data/mocka_events.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== GOVERNANCE_BLOCK EVENT TIMELINE ===")
print()

# Get all governance_block events with timestamps
cursor.execute('''
    SELECT event_id, when_ts, request_id, _source
    FROM events
    WHERE what_type = 'governance_block'
    ORDER BY when_ts DESC
    LIMIT 10
''')

events = cursor.fetchall()

print(f"Total governance_block events found: {len(events)}")
print()

if events:
    print("Event Timeline (most recent first):")
    print("-" * 80)
    for event_id, ts, req_id, source in events:
        req_id_status = f"request_id={req_id}" if req_id else "request_id=NULL"
        print(f"  {event_id}")
        print(f"    Timestamp: {ts}")
        print(f"    {req_id_status}")
        print(f"    _source: {source}")
        print()

# Analysis
print("=" * 80)
print("ANALYSIS")
print("=" * 80)
print()

null_count = sum(1 for _, _, req_id, _ in events if req_id is None)
non_null_count = sum(1 for _, _, req_id, _ in events if req_id is not None)

print(f"Events with request_id = NULL: {null_count}")
print(f"Events with request_id populated: {non_null_count}")
print()

if non_null_count == 0:
    print("FINDING: All governance_block events have NULL request_id")
    print()
    print("Possible causes:")
    print("  1. Events were recorded before staged A+B implementation")
    print("  2. Staged code has not been executed with actual BLOCK requests")
    print("  3. _record_governance_block() payload assembly is incomplete")
    print("  4. phi_os/event_gate.py is not persisting request_id field")
    print()

if events:
    most_recent = events[0]
    ts_str = most_recent[1]
    print(f"Most recent event: {most_recent[0]}")
    print(f"  Timestamp: {ts_str}")
    print(f"  Request_id status: {'POPULATED' if most_recent[2] else 'NULL'}")

conn.close()
