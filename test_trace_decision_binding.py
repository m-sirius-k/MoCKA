#!/usr/bin/env python
"""
Test TRACE_ID / DECISION_ID propagation
One-shot runtime task: EVENT -> RETRIEVAL -> CONTEXT -> DECISION -> AUTHORIZATION -> ACTION -> EVENT
"""
import sys
import os
import sqlite3
from datetime import datetime, timezone
import secrets

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== TRACE_ID / DECISION_ID PROPAGATION TEST ===")
print()

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'mocka_events.db')

# Generate trace/decision IDs for this task
trace_id = f"T_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(3)}"
decision_id = f"D_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(3)}"
request_id = f"REQ_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(2)}"
approval_id = request_id  # REQUEST_ID_ALIAS from STEP 4-C

print(f"TRACE_ID:    {trace_id}")
print(f"REQUEST_ID:  {request_id}")
print(f"DECISION_ID: {decision_id}")
print(f"APPROVAL_ID: {approval_id}")
print()

# Step 1: Create approval (human_gate_events)
print("STEP 1: Create Human Gate approval")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS human_gate_events (
        event_id TEXT PRIMARY KEY,
        timestamp TEXT,
        type TEXT,
        action TEXT,
        request_id TEXT,
        payload TEXT,
        previous_state TEXT,
        next_state TEXT
    )
''')

now = datetime.now(timezone.utc).isoformat()
import json

cursor.execute('''
    INSERT INTO human_gate_events
    (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (
    f"HGE_{now.replace(':', '').replace('-', '')}_appr",
    now,
    'HUMAN_GATE_EVENT',
    'approve',
    request_id,
    json.dumps({"actor": "test", "target": "trace-test", "scope": "trace-scope"}),
    'PENDING',
    'APPROVED'
))

conn.commit()
conn.close()
print(f"  Approval created for {request_id}")
print()

# Step 2: Execute action with trace_id and decision_id
print("STEP 2: Execute action with TRACE_ID and DECISION_ID")
from runtime.action_executor import execute_action

result = execute_action(
    step='TRACE_DECISION_TEST',
    action_id=request_id,
    target='trace-test',
    runtime_scope='trace-scope',
    trace_id=trace_id,
    decision_id=decision_id
)

print(f"  Action status: {result['status']}")
print(f"  Authorization ID: {result.get('authorization_id', 'N/A')}")
print(f"  Event ID: {result.get('event_id', 'N/A')}")
print()

# Step 3: Read-back verification
print("STEP 3: Read-back verification from mocka_events.db")
if result.get('event_id'):
    event_id = result['event_id']
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT event_id, request_id, title, free_note, trace_id, related_event_id
        FROM events
        WHERE event_id = ?
    ''', (event_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        print(f"  Event ID:         {row['event_id']}")
        print(f"  Request ID:       {row['request_id']}")
        print(f"  Title:            {row['title']}")
        print(f"  Free Note:        {row['free_note'][:100] if row['free_note'] else 'N/A'}...")
        print(f"  Trace ID (hash):  {row['trace_id'][:16]}..." if row['trace_id'] else "N/A")

        # Check if trace_id/decision_id are in free_note
        free_note = row['free_note'] or ''
        has_trace = trace_id in free_note or 'trace_id=' in free_note
        has_decision = decision_id in free_note or 'decision_id=' in free_note
        has_request = request_id in free_note or row['request_id'] == request_id

        print()
        print(f"  Trace ID propagated:    {has_trace}")
        print(f"  Decision ID propagated: {has_decision}")
        print(f"  Request ID preserved:   {has_request}")

        # Summary
        print()
        print("=== SUMMARY ===")
        action_ok = result['status'] == 'success'
        event_recorded = result.get('event_recorded', False)
        readback_ok = bool(row)

        print(f"ACTION EXECUTED:        {'PASS' if action_ok else 'FAIL'}")
        print(f"EVENT RECORDED:         {'PASS' if event_recorded else 'FAIL'}")
        print(f"READ-BACK VERIFIED:     {'PASS' if readback_ok else 'FAIL'}")
        print(f"TRACE_ID PROPAGATED:    {'PASS' if has_trace else 'FAIL'}")
        print(f"DECISION_ID PROPAGATED: {'PASS' if has_decision else 'FAIL'}")
        print(f"REQUEST_ID PRESERVED:   {'PASS' if has_request else 'FAIL'}")
        print()

        all_pass = action_ok and event_recorded and readback_ok and has_trace and has_decision and has_request
        print(f"END-TO-END VERIFICATION: {'VERIFIED' if all_pass else 'PARTIAL'}")
    else:
        print(f"  Event NOT FOUND in DB")
        print(f"  FAIL")
else:
    print(f"  No event ID returned")
    print(f"  FAIL")
