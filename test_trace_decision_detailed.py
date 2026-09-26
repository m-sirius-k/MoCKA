#!/usr/bin/env python
"""
Detailed TRACE_ID / DECISION_ID verification
- Full free_note inspection
- Cross-trace contamination check
"""
import sys
import os
import sqlite3
from datetime import datetime, timezone
import secrets
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== DETAILED TRACE_ID / DECISION_ID VERIFICATION ===")
print()

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'mocka_events.db')

# Task 1
task1_trace_id = f"T_TASK1_{secrets.token_hex(4)}"
task1_decision_id = f"D_TASK1_{secrets.token_hex(4)}"
task1_request_id = f"REQ_TASK1_{secrets.token_hex(2)}"

# Task 2 (different)
task2_trace_id = f"T_TASK2_{secrets.token_hex(4)}"
task2_decision_id = f"D_TASK2_{secrets.token_hex(4)}"
task2_request_id = f"REQ_TASK2_{secrets.token_hex(2)}"

print(f"TASK 1:")
print(f"  TRACE_ID:    {task1_trace_id}")
print(f"  REQUEST_ID:  {task1_request_id}")
print(f"  DECISION_ID: {task1_decision_id}")
print()

print(f"TASK 2:")
print(f"  TRACE_ID:    {task2_trace_id}")
print(f"  REQUEST_ID:  {task2_request_id}")
print(f"  DECISION_ID: {task2_decision_id}")
print()

# Create approvals
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

now = datetime.now(timezone.utc).isoformat()

for req_id, desc in [(task1_request_id, "TASK1"), (task2_request_id, "TASK2")]:
    cursor.execute('''
        INSERT INTO human_gate_events
        (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        f"HGE_{now.replace(':', '').replace('-', '')}_{desc}",
        now,
        'HUMAN_GATE_EVENT',
        'approve',
        req_id,
        json.dumps({"actor": "test", "target": f"task-{desc}", "scope": f"scope-{desc}"}),
        'PENDING',
        'APPROVED'
    ))

conn.commit()
conn.close()

# Execute both tasks
from runtime.action_executor import execute_action

result1 = execute_action(
    step='TASK1_ACTION',
    action_id=task1_request_id,
    target=f'task-TASK1',
    runtime_scope=f'scope-TASK1',
    trace_id=task1_trace_id,
    decision_id=task1_decision_id
)

result2 = execute_action(
    step='TASK2_ACTION',
    action_id=task2_request_id,
    target=f'task-TASK2',
    runtime_scope=f'scope-TASK2',
    trace_id=task2_trace_id,
    decision_id=task2_decision_id
)

print("=== TASK EXECUTION RESULTS ===")
print(f"TASK 1 status: {result1['status']}")
print(f"TASK 1 event_id: {result1.get('event_id')}")
print(f"TASK 2 status: {result2['status']}")
print(f"TASK 2 event_id: {result2.get('event_id')}")
print()

# Read-back and cross-check
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== DETAILED READ-BACK ===")
print()

for task_num, result, req_id, trace_id, decision_id in [
    (1, result1, task1_request_id, task1_trace_id, task1_decision_id),
    (2, result2, task2_request_id, task2_trace_id, task2_decision_id),
]:
    event_id = result.get('event_id')
    if not event_id:
        print(f"TASK {task_num}: No event_id")
        continue

    cursor.execute('''
        SELECT event_id, request_id, title, free_note, trace_id as trace_hash
        FROM events
        WHERE event_id = ?
    ''', (event_id,))

    row = cursor.fetchone()
    if not row:
        print(f"TASK {task_num}: Event NOT found")
        continue

    print(f"TASK {task_num}:")
    print(f"  Event ID:      {row['event_id']}")
    print(f"  Request ID:    {row['request_id']}")
    print(f"  Title:         {row['title']}")
    print(f"  Free Note (full):")
    print(f"    {row['free_note']}")
    print()

    # Verify trace/decision in free_note
    free_note = row['free_note'] or ''
    has_my_trace = trace_id in free_note
    has_my_decision = decision_id in free_note
    has_correct_req = row['request_id'] == req_id

    # Check for contamination from other task
    other_trace = task2_trace_id if task_num == 1 else task1_trace_id
    other_decision = task2_decision_id if task_num == 1 else task1_decision_id
    has_other_trace = other_trace in free_note
    has_other_decision = other_decision in free_note

    print(f"  Correct trace_id:        {has_my_trace}")
    print(f"  Correct decision_id:     {has_my_decision}")
    print(f"  Correct request_id:      {has_correct_req}")
    print(f"  No cross-contamination trace: {not has_other_trace}")
    print(f"  No cross-contamination decision: {not has_other_decision}")
    print()

conn.close()

print("=== CROSS-TASK CONTAMINATION CHECK ===")
cursor = sqlite3.connect(DB_PATH).cursor()
cursor.execute('''
    SELECT count(*) FROM events
    WHERE (free_note LIKE ? OR free_note LIKE ?) AND request_id = ?
''', (f"%{task1_trace_id}%", f"%{task1_decision_id}%", task2_request_id))
contamination_count = cursor.fetchone()[0]
cursor.close()

if contamination_count == 0:
    print("Cross-task contamination: NONE DETECTED")
    print("PASS")
else:
    print(f"Cross-task contamination: {contamination_count} events")
    print("FAIL")
