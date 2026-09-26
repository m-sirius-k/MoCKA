#!/usr/bin/env python
"""STEP 9: CONCURRENCY TEST
Parallel execution of multiple TRACE/DECISION without interference"""

import sys, os, sqlite3, secrets, json
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'mocka_events.db')

from runtime.action_executor import execute_action
from runtime.evidence_chain_tracker import EvidenceChainTracker

print("=== STEP 9 CONCURRENCY TEST ===\n")

tracker = EvidenceChainTracker(DB_PATH)

def setup_approval(request_id, target, scope):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS human_gate_events (event_id TEXT PRIMARY KEY, timestamp TEXT, type TEXT, action TEXT, request_id TEXT, payload TEXT, previous_state TEXT, next_state TEXT)')
    event_id = f"HGE_{secrets.token_hex(8)}"
    cursor.execute('INSERT INTO human_gate_events (event_id, timestamp, type, action, request_id, payload, previous_state, next_state) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (event_id, datetime.now(timezone.utc).isoformat(), 'HUMAN_GATE_EVENT', 'approve', request_id, json.dumps({"actor": "test", "target": target, "scope": scope}), 'PENDING', 'APPROVED'))
    conn.commit()
    conn.close()

def execute_task(trace_id, decision_id, request_id, target, scope):
    """Execute single task (used in parallel)"""
    setup_approval(request_id, target, scope)
    result = execute_action(step=f'CONCURRENT_{trace_id}', action_id=request_id, target=target, runtime_scope=scope, trace_id=trace_id, decision_id=decision_id)
    chain = tracker.get_chain_by_trace_id(trace_id)
    return {
        'trace_id': trace_id,
        'decision_id': decision_id,
        'result_status': result.get('status'),
        'chain_status': chain['status'],
        'events_count': len(chain['events'])
    }

# ===== CASE-A: Two TRACE parallel =====
print("CASE-A: Two TRACE parallel execution")
trace_a1 = f"T_CONC_A1_{secrets.token_hex(3)}"
trace_a2 = f"T_CONC_A2_{secrets.token_hex(3)}"

with ThreadPoolExecutor(max_workers=2) as executor:
    future1 = executor.submit(execute_task, trace_a1, f"D_A1", f"REQ_A1_{secrets.token_hex(2)}", 'target-a1', 'scope-a1')
    future2 = executor.submit(execute_task, trace_a2, f"D_A2", f"REQ_A2_{secrets.token_hex(2)}", 'target-a2', 'scope-a2')
    result_a1, result_a2 = future1.result(), future2.result()

isolation_a = tracker.verify_isolation(trace_a1, trace_a2)
print(f"  TRACE-A1 status: {result_a1['result_status']}")
print(f"  TRACE-A2 status: {result_a2['result_status']}")
print(f"  Isolation: {isolation_a['status']}")
case_a = isolation_a['status'] == 'ISOLATED'
print(f"  RESULT: {'PASS' if case_a else 'FAIL'}\n")

# ===== CASE-F: Stress test (5 concurrent) =====
print("CASE-F: Stress test (5 TRACE concurrent)")
trace_ids = [f"T_STRESS_{i}_{secrets.token_hex(2)}" for i in range(5)]
tasks = []

with ThreadPoolExecutor(max_workers=5) as executor:
    for i, trace_id in enumerate(trace_ids):
        decision_id = f"D_STRESS_{i}"
        request_id = f"REQ_STRESS_{i}_{secrets.token_hex(2)}"
        task = executor.submit(execute_task, trace_id, decision_id, request_id, f'target-{i}', f'scope-{i}')
        tasks.append((trace_id, task))

    results = {trace_id: task.result() for trace_id, task in tasks}

# Check isolation between all traces
isolation_ok = True
for i, trace_a in enumerate(trace_ids):
    for j, trace_b in enumerate(trace_ids):
        if i < j:
            iso = tracker.verify_isolation(trace_a, trace_b)
            if iso['status'] != 'ISOLATED':
                isolation_ok = False
                print(f"  Contamination: {trace_a} <-> {trace_b}")

print(f"  Traces executed: {len(results)}")
print(f"  All isolated: {isolation_ok}")
case_f = isolation_ok and len(results) == 5
print(f"  RESULT: {'PASS' if case_f else 'FAIL'}\n")

# ===== CASE-G: READ-BACK all traces =====
print("CASE-G: READ-BACK verification for all traces")
readback_ok = True
for trace_id in [trace_a1, trace_a2] + trace_ids:
    chain = tracker.get_chain_by_trace_id(trace_id)
    if chain['status'] != 'VERIFIED':
        readback_ok = False
        print(f"  READ-BACK failed for {trace_id}: {chain['status']}")

print(f"  Traces read-back: {len([trace_a1, trace_a2] + trace_ids)}")
print(f"  All verified: {readback_ok}")
case_g = readback_ok
print(f"  RESULT: {'PASS' if case_g else 'FAIL'}\n")

# ===== SUMMARY =====
print("=== CONCURRENCY SUMMARY ===")
print(f"CASE-A (2 TRACE):      {'PASS' if case_a else 'FAIL'}")
print(f"CASE-F (5 TRACE):      {'PASS' if case_f else 'FAIL'}")
print(f"CASE-G (READ-BACK):    {'PASS' if case_g else 'FAIL'}")
print()

all_pass = case_a and case_f and case_g
print(f"STEP 9 CONCURRENCY: {'VERIFIED' if all_pass else 'PARTIAL'}\n")

if all_pass:
    print("Result: Existing implementation handles concurrency correctly.")
    print("No new orchestration layer needed.")
    print("Ready for PRODUCTION READINESS AUDIT.")
