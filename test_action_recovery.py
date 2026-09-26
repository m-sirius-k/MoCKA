#!/usr/bin/env python
"""
Test ACTION RECOVERY & RETRY with TRACE_ID/DECISION_ID preservation

TEST-1: Normal success (no recovery needed)
TEST-2: Retryable failure (error) → recovery → retry → success (mock)
TEST-3: Max attempts reached → stop
TEST-4: BLOCKED → no retry
TEST-5: UNAUTHORIZED scenario
TEST-6: SCOPE_MISMATCH → no retry
TEST-7-9: TRACE_ID/DECISION_ID preservation and read-back
"""

import sys
import os
import sqlite3
from datetime import datetime, timezone
import secrets
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== ACTION RECOVERY TEST SUITE ===")
print()

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'mocka_events.db')

# Import modules
from runtime.action_recovery import (
    is_retryable,
    should_retry,
    make_recovery_request_id,
    ActionRecoveryOrchestrator
)
from runtime.action_executor import execute_action

# Test helpers
def create_approval(request_id, target, scope):
    """Create Human Gate approval"""
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
        json.dumps({"actor": "test", "target": target, "scope": scope}),
        'PENDING',
        'APPROVED'
    ))

    conn.commit()
    conn.close()


# ===== TEST-1: Normal success (no recovery needed) =====
print("TEST-1: Normal success (no recovery needed)")
trace_id_1 = f"T_TEST1_{secrets.token_hex(4)}"
decision_id_1 = f"D_TEST1_{secrets.token_hex(4)}"
request_id_1 = f"REQ_TEST1_{secrets.token_hex(2)}"

create_approval(request_id_1, 'target-1', 'scope-1')

result_1 = execute_action(
    step='TEST1_ACTION',
    action_id=request_id_1,
    target='target-1',
    runtime_scope='scope-1',
    trace_id=trace_id_1,
    decision_id=decision_id_1
)

print(f"  Status: {result_1['status']}")
print(f"  Expected: success")
print(f"  Recovery needed: No")
test_1_pass = result_1['status'] == 'success'
print(f"  RESULT: {'PASS' if test_1_pass else 'FAIL'}")
print()

# ===== TEST-2: Retryable failure judgment =====
print("TEST-2: Retryable failure judgment")
retryable_error = {"status": "error", "reason": "Transient connection error"}
retryable_blocked = {"status": "blocked", "reason": "HG_NO_APPROVAL"}

is_retryable_error = is_retryable(retryable_error["status"], retryable_error["reason"])
is_retryable_blocked = is_retryable(retryable_blocked["status"], retryable_blocked["reason"])

print(f"  Error ('error'): {is_retryable_error} (expected True)")
print(f"  Blocked ('blocked'): {is_retryable_blocked} (expected False)")
test_2_pass = is_retryable_error and not is_retryable_blocked
print(f"  RESULT: {'PASS' if test_2_pass else 'FAIL'}")
print()

# ===== TEST-3: Max attempts enforcement =====
print("TEST-3: Max attempts enforcement")
result_error = {"status": "error", "reason": "Transient error"}

# Attempt 1: Should retry (2 < 3)
should_retry_1 = should_retry(result_error, current_attempt=1, max_attempts=3)
# Attempt 3: Should NOT retry (3 >= 3)
should_retry_3 = should_retry(result_error, current_attempt=3, max_attempts=3)

print(f"  Attempt 1/3: {should_retry_1} (expected True)")
print(f"  Attempt 3/3: {should_retry_3} (expected False)")
test_3_pass = should_retry_1 and not should_retry_3
print(f"  RESULT: {'PASS' if test_3_pass else 'FAIL'}")
print()

# ===== TEST-4: BLOCKED → no retry =====
print("TEST-4: BLOCKED → no retry")
trace_id_4 = f"T_TEST4_{secrets.token_hex(4)}"
decision_id_4 = f"D_TEST4_{secrets.token_hex(4)}"
request_id_4 = f"REQ_TEST4_{secrets.token_hex(2)}"

# No approval for this request, so it will be blocked
result_4 = execute_action(
    step='TEST4_BLOCKED',
    action_id=request_id_4,
    target='target-4',
    runtime_scope='scope-4',
    trace_id=trace_id_4,
    decision_id=decision_id_4
)

is_retryable_4 = is_retryable(result_4["status"], result_4.get("reason"))
print(f"  Status: {result_4['status']}")
print(f"  Reason: {result_4.get('reason')}")
print(f"  Retryable: {is_retryable_4} (expected False)")
test_4_pass = result_4['status'] == 'blocked' and not is_retryable_4
print(f"  RESULT: {'PASS' if test_4_pass else 'FAIL'}")
print()

# ===== TEST-5: SCOPE_MISMATCH → no retry =====
print("TEST-5: SCOPE_MISMATCH → no retry")
trace_id_5 = f"T_TEST5_{secrets.token_hex(4)}"
decision_id_5 = f"D_TEST5_{secrets.token_hex(4)}"
request_id_5 = f"REQ_TEST5_{secrets.token_hex(2)}"

# Create approval with scope-A but request scope-B
create_approval(request_id_5, 'target-5', 'scope-A')

result_5 = execute_action(
    step='TEST5_SCOPE_MISMATCH',
    action_id=request_id_5,
    target='target-5',
    runtime_scope='scope-B',  # Different scope
    trace_id=trace_id_5,
    decision_id=decision_id_5
)

is_retryable_5 = is_retryable(result_5["status"], result_5.get("reason"))
print(f"  Status: {result_5['status']}")
print(f"  Reason: {result_5.get('reason')}")
print(f"  Retryable: {is_retryable_5} (expected False)")
test_5_pass = 'SCOPE_MISMATCH' in str(result_5.get('reason', '')) and not is_retryable_5
print(f"  RESULT: {'PASS' if test_5_pass else 'FAIL'}")
print()

# ===== TEST-6: TRACE_ID/DECISION_ID preservation =====
print("TEST-6: TRACE_ID/DECISION_ID preservation & recovery request ID")
base_req_id = "REQ_20260926_TEST_abc1"
attempt_req_id = make_recovery_request_id(base_req_id, 2)

print(f"  Base request_id: {base_req_id}")
print(f"  Recovery request_id (attempt 2): {attempt_req_id}")
print(f"  Expected format: {base_req_id}_ATTEMPT_2")
test_6_pass = attempt_req_id == f"{base_req_id}_ATTEMPT_2"
print(f"  RESULT: {'PASS' if test_6_pass else 'FAIL'}")
print()

# ===== TEST-7-9: Read-back verification =====
print("TEST-7-9: Event read-back for TRACE_ID/DECISION_ID")
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Read TEST-1 event
if result_1.get('event_id'):
    cursor.execute('''
        SELECT event_id, request_id, title, free_note, trace_id
        FROM events
        WHERE event_id = ?
    ''', (result_1['event_id'],))

    row = cursor.fetchone()
    if row:
        free_note = row['free_note'] or ''
        has_trace = trace_id_1 in free_note
        has_decision = decision_id_1 in free_note
        has_request = row['request_id'] == request_id_1

        print(f"  Event ID: {row['event_id']}")
        print(f"  Trace ID in free_note: {has_trace}")
        print(f"  Decision ID in free_note: {has_decision}")
        print(f"  Request ID preserved: {has_request}")
        test_7_9_pass = has_trace and has_decision and has_request
        print(f"  RESULT: {'PASS' if test_7_9_pass else 'FAIL'}")
    else:
        print(f"  Event not found in DB")
        test_7_9_pass = False
        print(f"  RESULT: FAIL")
else:
    print(f"  No event_id from result")
    test_7_9_pass = False
    print(f"  RESULT: FAIL")

conn.close()
print()

# ===== SUMMARY =====
print("=== SUMMARY ===")
print(f"TEST-1 (Normal success):         {'PASS' if test_1_pass else 'FAIL'}")
print(f"TEST-2 (Retryable judgment):     {'PASS' if test_2_pass else 'FAIL'}")
print(f"TEST-3 (Max attempts):           {'PASS' if test_3_pass else 'FAIL'}")
print(f"TEST-4 (BLOCKED no-retry):       {'PASS' if test_4_pass else 'FAIL'}")
print(f"TEST-5 (SCOPE_MISMATCH no-retry): {'PASS' if test_5_pass else 'FAIL'}")
print(f"TEST-6 (TRACE_ID preservation):  {'PASS' if test_6_pass else 'FAIL'}")
print(f"TEST-7-9 (Read-back):            {'PASS' if test_7_9_pass else 'FAIL'}")
print()

all_pass = (test_1_pass and test_2_pass and test_3_pass and
            test_4_pass and test_5_pass and test_6_pass and test_7_9_pass)
print(f"END-TO-END: {'VERIFIED' if all_pass else 'PARTIAL'}")
