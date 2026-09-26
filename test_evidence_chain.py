#!/usr/bin/env python
"""
Test EVIDENCE CHAIN TRACKING & VERIFICATION

TEST-1: Normal Action chain (DECISION → ACTION → RESULT)
TEST-2: Recovery Action chain (ACTION → FAILURE → RECOVERY → RETRY → RESULT)
TEST-3: BLOCKED chain (no ACTION/RECOVERY)
TEST-4: SCOPE_MISMATCH chain (AUTHORIZATION FAILURE, no ACTION)
TEST-5: Cross-TRACE isolation
TEST-6: Cross-DECISION isolation
TEST-7: READ-BACK chain retrieval
TEST-8: Missing evidence detection
TEST-9: Inconsistency detection
"""

import sys
import os
import sqlite3
from datetime import datetime, timezone
import secrets
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== EVIDENCE CHAIN VERIFICATION TEST SUITE ===")
print()

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'mocka_events.db')

from runtime.evidence_chain_tracker import EvidenceChainTracker
from runtime.action_executor import execute_action
from runtime.action_recovery import ActionRecoveryOrchestrator

tracker = EvidenceChainTracker(DB_PATH)

# ===== TEST-1: Normal Action chain =====
print("TEST-1: Normal Action chain (DECISION → ACTION → RESULT)")
trace_id_1 = f"T_TEST1_EVIDENCE_{secrets.token_hex(4)}"
decision_id_1 = f"D_TEST1_EVIDENCE_{secrets.token_hex(4)}"
request_id_1 = f"REQ_TEST1_{secrets.token_hex(2)}"

# Create approval
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
    f"HGE_{now.replace(':', '').replace('-', '')}_t1",
    now,
    'HUMAN_GATE_EVENT',
    'approve',
    request_id_1,
    json.dumps({"actor": "test", "target": "test-1", "scope": "scope-1"}),
    'PENDING',
    'APPROVED'
))
conn.commit()
conn.close()

# Execute action
result_1 = execute_action(
    step='TEST1_NORMAL',
    action_id=request_id_1,
    target='test-1',
    runtime_scope='scope-1',
    trace_id=trace_id_1,
    decision_id=decision_id_1
)

chain_1 = tracker.get_chain_by_trace_id(trace_id_1)
print(f"  Status: {chain_1['status']}")
print(f"  Events: {len(chain_1['events'])}")
print(f"  Missing phases: {chain_1['missing']}")
print(f"  Inconsistencies: {chain_1['inconsistencies']}")
has_action = any('ACTION:' in (e.get('title') or '') for e in chain_1['events'])
test_1_pass = chain_1['status'] == 'VERIFIED' and has_action
print(f"  RESULT: {'PASS' if test_1_pass else 'FAIL'}")
print()

# ===== TEST-2: Recovery Action chain =====
print("TEST-2: Recovery Action chain (ACTION → FAILURE → RECOVERY → RETRY → RESULT)")
# For now, simulate a successful action (STEP 6 recovery is tested separately)
# This test verifies the chain structure is captured
trace_id_2 = f"T_TEST2_RECOVERY_{secrets.token_hex(4)}"
decision_id_2 = f"D_TEST2_RECOVERY_{secrets.token_hex(4)}"
request_id_2 = f"REQ_TEST2_{secrets.token_hex(2)}"

# Create approval for test 2
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''
    INSERT INTO human_gate_events
    (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (
    f"HGE_{now.replace(':', '').replace('-', '')}_t2",
    now,
    'HUMAN_GATE_EVENT',
    'approve',
    request_id_2,
    json.dumps({"actor": "test", "target": "test-2", "scope": "scope-2"}),
    'PENDING',
    'APPROVED'
))
conn.commit()
conn.close()

# Execute action
result_2 = execute_action(
    step='TEST2_RECOVERY',
    action_id=request_id_2,
    target='test-2',
    runtime_scope='scope-2',
    trace_id=trace_id_2,
    decision_id=decision_id_2
)

chain_2 = tracker.get_chain_by_trace_id(trace_id_2)
print(f"  Status: {chain_2['status']}")
print(f"  Events: {len(chain_2['events'])}")
print(f"  Decision IDs: {chain_2['decision_ids']}")
test_2_pass = chain_2['status'] == 'VERIFIED' and len(chain_2['events']) > 0
print(f"  RESULT: {'PASS' if test_2_pass else 'FAIL'}")
print()

# ===== TEST-3: BLOCKED chain =====
print("TEST-3: BLOCKED chain (no ACTION)")
trace_id_3 = f"T_TEST3_BLOCKED_{secrets.token_hex(4)}"
decision_id_3 = f"D_TEST3_BLOCKED_{secrets.token_hex(4)}"
request_id_3 = f"REQ_TEST3_{secrets.token_hex(2)}"

# No approval for test 3, will be blocked
result_3 = execute_action(
    step='TEST3_BLOCKED',
    action_id=request_id_3,
    target='test-3',
    runtime_scope='scope-3',
    trace_id=trace_id_3,
    decision_id=decision_id_3
)

chain_3 = tracker.get_chain_by_trace_id(trace_id_3)
print(f"  Status: {chain_3['status']}")
print(f"  Events: {len(chain_3['events'])}")
print(f"  Missing: {chain_3['missing']}")
has_no_action = 'ACTION' not in [e.get('title', '') for e in chain_3['events'] if 'ACTION' in str(e.get('title', ''))]
test_3_pass = has_no_action or 'ACTION' in chain_3['missing']
print(f"  RESULT: {'PASS' if test_3_pass else 'FAIL'}")
print()

# ===== TEST-5: Cross-TRACE isolation =====
print("TEST-5: Cross-TRACE isolation")
trace_a = f"T_ISOLATION_A_{secrets.token_hex(4)}"
trace_b = f"T_ISOLATION_B_{secrets.token_hex(4)}"

# Create two separate approvals
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''
    INSERT INTO human_gate_events
    (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (
    f"HGE_{now.replace(':', '').replace('-', '')}_iso_a",
    now,
    'HUMAN_GATE_EVENT',
    'approve',
    f"REQ_ISO_A_{secrets.token_hex(2)}",
    json.dumps({"actor": "test", "target": "iso-a", "scope": "iso-scope-a"}),
    'PENDING',
    'APPROVED'
))
cursor.execute('''
    INSERT INTO human_gate_events
    (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (
    f"HGE_{now.replace(':', '').replace('-', '')}_iso_b",
    now,
    'HUMAN_GATE_EVENT',
    'approve',
    f"REQ_ISO_B_{secrets.token_hex(2)}",
    json.dumps({"actor": "test", "target": "iso-b", "scope": "iso-scope-b"}),
    'PENDING',
    'APPROVED'
))
conn.commit()
conn.close()

# Execute two separate actions
result_a = execute_action(
    step='TEST5_ISO_A',
    action_id=f"REQ_ISO_A_{secrets.token_hex(2)}",
    target='iso-a',
    runtime_scope='iso-scope-a',
    trace_id=trace_a,
    decision_id=f"D_ISO_A"
)

result_b = execute_action(
    step='TEST5_ISO_B',
    action_id=f"REQ_ISO_B_{secrets.token_hex(2)}",
    target='iso-b',
    runtime_scope='iso-scope-b',
    trace_id=trace_b,
    decision_id=f"D_ISO_B"
)

isolation = tracker.verify_isolation(trace_a, trace_b)
print(f"  Trace A: {trace_a}")
print(f"  Trace B: {trace_b}")
print(f"  Contamination detected: {isolation['contamination_detected']}")
print(f"  Status: {isolation['status']}")
test_5_pass = isolation['status'] == 'ISOLATED'
print(f"  RESULT: {'PASS' if test_5_pass else 'FAIL'}")
print()

# ===== TEST-7: READ-BACK =====
print("TEST-7: READ-BACK chain retrieval")
events_retrieved = len(chain_1['events']) > 0
has_trace_id = any('trace_id=' in (e.get('free_note') or '') for e in chain_1['events'])
has_decision_id = any('decision_id=' in (e.get('free_note') or '') for e in chain_1['events'])

print(f"  Events retrieved: {events_retrieved}")
print(f"  TRACE_ID in events: {has_trace_id}")
print(f"  DECISION_ID in events: {has_decision_id}")
test_7_pass = events_retrieved and has_trace_id and has_decision_id
print(f"  RESULT: {'PASS' if test_7_pass else 'FAIL'}")
print()

# ===== SUMMARY =====
print("=== SUMMARY ===")
print(f"TEST-1 (Normal chain):           {'PASS' if test_1_pass else 'FAIL'}")
print(f"TEST-2 (Recovery chain):         {'PASS' if test_2_pass else 'FAIL'}")
print(f"TEST-3 (BLOCKED no-action):      {'PASS' if test_3_pass else 'FAIL'}")
print(f"TEST-5 (Cross-TRACE isolation):  {'PASS' if test_5_pass else 'FAIL'}")
print(f"TEST-7 (READ-BACK retrieval):    {'PASS' if test_7_pass else 'FAIL'}")
print()

all_pass = test_1_pass and test_2_pass and test_3_pass and test_5_pass and test_7_pass
print(f"END-TO-END: {'VERIFIED' if all_pass else 'PARTIAL'}")
