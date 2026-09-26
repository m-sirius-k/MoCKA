#!/usr/bin/env python
"""
Test Human Gate Scope/Target Binding
CASE A/B/C/D validation
"""
import sys
import os
import sqlite3
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== SCOPE/TARGET BINDING TEST ===")
print()

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'mocka_events.db')

def create_approval(request_id, target, scope):
    """Create approval record in human_gate_events"""
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
        f"HGE_{now}_appr",
        now,
        'HUMAN_GATE_EVENT',
        'approve',
        request_id,
        json.dumps({"actor": "approver", "target": target, "scope": scope}),
        'PENDING',
        'APPROVED'
    ))

    conn.commit()
    conn.close()

from runtime.action_executor import execute_action

# CASE A: Valid approval + matching target + matching scope
print("CASE A: Valid approval + matching target + matching scope")
create_approval('case_a_001', 'target-A', 'scope-A')
result_a = execute_action(
    step='CASE_A_VALID',
    action_id='case_a_001',
    target='target-A',
    runtime_scope='scope-A'
)
print(f"  Status: {result_a['status']}")
print(f"  Reason: {result_a.get('reason', 'none')}")
print(f"  Expected: success")
print(f"  {'PASS' if result_a['status'] == 'success' else 'FAIL'}")
print()

# CASE B: No approval
print("CASE B: No approval")
result_b = execute_action(
    step='CASE_B_NO_APPROVAL',
    action_id='case_b_no_approval_001',
    target='target-A',
    runtime_scope='scope-A'
)
print(f"  Status: {result_b['status']}")
print(f"  Reason: {result_b.get('reason', 'none')}")
print(f"  Expected: blocked")
print(f"  {'PASS' if result_b['status'] == 'blocked' else 'FAIL'}")
print()

# CASE C: Scope mismatch
print("CASE C: Scope mismatch")
create_approval('case_c_001', 'target-A', 'scope-A')
result_c = execute_action(
    step='CASE_C_SCOPE_MISMATCH',
    action_id='case_c_001',
    target='target-A',
    runtime_scope='scope-B'  # Different scope
)
print(f"  Status: {result_c['status']}")
print(f"  Reason: {result_c.get('reason', 'none')}")
print(f"  Expected: blocked (SCOPE_MISMATCH)")
print(f"  {'PASS' if 'SCOPE_MISMATCH' in str(result_c.get('reason', '')) else 'FAIL'}")
print()

# CASE D: Target mismatch
print("CASE D: Target mismatch")
create_approval('case_d_001', 'target-A', 'scope-A')
result_d = execute_action(
    step='CASE_D_TARGET_MISMATCH',
    action_id='case_d_001',
    target='target-B',  # Different target
    runtime_scope='scope-A'
)
print(f"  Status: {result_d['status']}")
print(f"  Reason: {result_d.get('reason', 'none')}")
print(f"  Expected: blocked (TARGET_MISMATCH)")
print(f"  {'PASS' if 'TARGET_MISMATCH' in str(result_d.get('reason', '')) else 'FAIL'}")
print()

# Summary
print("=== RESULTS ===")
case_a = result_a['status'] == 'success'
case_b = result_b['status'] == 'blocked'
case_c = 'SCOPE_MISMATCH' in str(result_c.get('reason', ''))
case_d = 'TARGET_MISMATCH' in str(result_d.get('reason', ''))

print(f"CASE A (Valid):         {'PASS' if case_a else 'FAIL'}")
print(f"CASE B (No approval):   {'PASS' if case_b else 'FAIL'}")
print(f"CASE C (Scope mismatch): {'PASS' if case_c else 'FAIL'}")
print(f"CASE D (Target mismatch): {'PASS' if case_d else 'FAIL'}")
print()

all_pass = case_a and case_b and case_c and case_d
print(f"END-TO-END: {'VERIFIED' if all_pass else 'PARTIAL'}")
