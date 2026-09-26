#!/usr/bin/env python
"""
Test Human Gate Approval + Action Execution
Direct DB manipulation to avoid logging module collision
"""
import sys
import os
import sqlite3
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== HUMAN GATE APPROVAL TEST (DIRECT DB) ===")
print()

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'mocka_events.db')

# Case A: Create approval record directly
print("CASE A: Create Human Gate approval in DB")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

request_id_a = 'case_a_approved_direct_001'

# Create human_gate_events table if needed
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

# Insert PENDING event
now = datetime.now(timezone.utc).isoformat()
event_id_pending = f"HGE_{now.replace(':', '').replace('-', '')}_pending"
cursor.execute('''
    INSERT INTO human_gate_events
    (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (
    event_id_pending, now, 'HUMAN_GATE_EVENT', 'submit',
    request_id_a, '{"actor": "test", "target": "TEST_CASE_A"}', None, 'PENDING'
))

# Insert APPROVED event
event_id_approved = f"HGE_{now.replace(':', '').replace('-', '')}_approved"
cursor.execute('''
    INSERT INTO human_gate_events
    (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (
    event_id_approved, now, 'HUMAN_GATE_EVENT', 'approve',
    request_id_a, '{"actor": "approver", "target": "TEST_CASE_A"}', 'PENDING', 'APPROVED'
))

conn.commit()
conn.close()

print(f"  Created approval record for {request_id_a}")
print()

# Now execute action with approval
print("CASE A: Execute action with approval")
from runtime.action_executor import execute_action

result_a = execute_action(
    step='TEST_CASE_A_WITH_APPROVAL',
    action_id=request_id_a
)

print(f"  Status: {result_a['status']}")
print(f"  Expected: success")
print(f"  PASS" if result_a['status'] == 'success' else f"  FAIL")
print()

# Case B: No approval (existing test)
print("CASE B: No approval")
result_b = execute_action(
    step='TEST_CASE_B_NO_APPROVAL',
    action_id='case_b_no_approval_direct_001'
)
print(f"  Status: {result_b['status']}")
print(f"  Expected: blocked")
print(f"  PASS" if result_b['status'] == 'blocked' else f"  FAIL")
print()

# Summary
print("=== RESULTS ===")
case_a_pass = result_a['status'] == 'success'
case_b_pass = result_b['status'] == 'blocked'
print(f"CASE A (With approval): {'PASS' if case_a_pass else 'FAIL'}")
print(f"CASE B (No approval): {'PASS' if case_b_pass else 'FAIL'}")
print()
all_pass = case_a_pass and case_b_pass
print(f"END-TO-END: {'VERIFIED' if all_pass else 'PARTIAL'}")
