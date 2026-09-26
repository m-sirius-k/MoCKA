#!/usr/bin/env python
"""
STEP 8: END-TO-END INTEGRATION TEST
Verify complete pipeline: STEP 4-C → 5 → 6 → 7
Tests: CASE-A (normal), CASE-B (retry), CASE-C (blocked), CASE-D (scope), CASE-E (cross-trace)
"""

import sys, os, sqlite3
from datetime import datetime, timezone
import secrets, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== STEP 8 END-TO-END INTEGRATION TEST ===\n")

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'mocka_events.db')

from runtime.action_executor import execute_action
from runtime.action_recovery import ActionRecoveryOrchestrator
from runtime.evidence_chain_tracker import EvidenceChainTracker

tracker = EvidenceChainTracker(DB_PATH)

def setup_approval(request_id, target, scope):
    """Create HG approval"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS human_gate_events (event_id TEXT PRIMARY KEY, timestamp TEXT, type TEXT, action TEXT, request_id TEXT, payload TEXT, previous_state TEXT, next_state TEXT)')
    now = datetime.now(timezone.utc).isoformat()
    event_id = f"HGE_{secrets.token_hex(8)}"
    cursor.execute('INSERT INTO human_gate_events (event_id, timestamp, type, action, request_id, payload, previous_state, next_state) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (event_id, now, 'HUMAN_GATE_EVENT', 'approve', request_id,
         json.dumps({"actor": "test", "target": target, "scope": scope}), 'PENDING', 'APPROVED'))
    conn.commit()
    conn.close()

# ===== CASE-A: NORMAL (HG → Auth → TRACE/DECISION → ACTION → SUCCESS → EVENT → Evidence → READ-BACK) =====
print("CASE-A: NORMAL END-TO-END")
trace_a = f"T_E2E_CASEA_{secrets.token_hex(3)}"
decision_a = f"D_E2E_CASEA_{secrets.token_hex(3)}"
request_a = f"REQ_CASEA_{secrets.token_hex(2)}"

setup_approval(request_a, 'target-a', 'scope-a')
result_a = execute_action(step='E2E_CASEA', action_id=request_a, target='target-a', runtime_scope='scope-a', trace_id=trace_a, decision_id=decision_a)

chain_a = tracker.get_chain_by_trace_id(trace_a)
print(f"  Action status: {result_a['status']}")
print(f"  Chain status: {chain_a['status']}")
print(f"  Evidence: {len(chain_a['events'])} events")
print(f"  TRACE_ID: {trace_a}")
print(f"  DECISION_ID: {decision_a}")
case_a = result_a['status'] == 'success' and chain_a['status'] == 'VERIFIED'
print(f"  RESULT: {'PASS' if case_a else 'FAIL'}\n")

# ===== CASE-B: RETRY (ACTION FAILURE → RECOVERY → RETRY → SUCCESS) =====
print("CASE-B: RETRY FLOW")
trace_b = f"T_E2E_CASEB_{secrets.token_hex(3)}"
decision_b = f"D_E2E_CASEB_{secrets.token_hex(3)}"
request_b = f"REQ_CASEB_{secrets.token_hex(2)}"

setup_approval(request_b, 'target-b', 'scope-b')

class MockExecutor:
    def __init__(self):
        self.call_count = 0
    def execute(self, **kwargs):
        self.call_count += 1
        if self.call_count == 1:
            return {"status": "error", "reason": "Transient failure", "action_id": kwargs.get('action_id'), "action": "mock"}
        else:
            return {"status": "success", "reason": None, "action_id": kwargs.get('action_id'), "action": "mock", "event_id": f"E_RETRY_{secrets.token_hex(4)}"}

mock = MockExecutor()
orchestrator = ActionRecoveryOrchestrator(max_attempts=2)
result_b = orchestrator.execute_with_recovery(
    mock.execute, request_b, trace_id=trace_b, decision_id=decision_b,
    step='E2E_CASEB', target='target-b', runtime_scope='scope-b'
)

chain_b = tracker.get_chain_by_trace_id(trace_b)
print(f"  Retry attempts: {mock.call_count}")
print(f"  Final status: {result_b['status']}")
print(f"  Chain status: {chain_b['status']}")
case_b = result_b['status'] == 'success' and mock.call_count == 2
print(f"  RESULT: {'PASS' if case_b else 'FAIL'}\n")

# ===== CASE-C: BLOCKED (no ACTION/RECOVERY) =====
print("CASE-C: BLOCKED")
trace_c = f"T_E2E_CASEC_{secrets.token_hex(3)}"
decision_c = f"D_E2E_CASEC_{secrets.token_hex(3)}"
request_c = f"REQ_CASEC_{secrets.token_hex(2)}"

# No approval for case-c
result_c = execute_action(step='E2E_CASEC', action_id=request_c, target='target-c', runtime_scope='scope-c', trace_id=trace_c, decision_id=decision_c)
chain_c = tracker.get_chain_by_trace_id(trace_c)

print(f"  Action status: {result_c['status']}")
print(f"  Reason: {result_c.get('reason')}")
print(f"  Chain has events: {len(chain_c['events']) > 0}")
case_c = result_c['status'] == 'blocked' and len(chain_c['events']) > 0
print(f"  RESULT: {'PASS' if case_c else 'FAIL'}\n")

# ===== CASE-D: SCOPE_MISMATCH =====
print("CASE-D: SCOPE_MISMATCH")
trace_d = f"T_E2E_CASED_{secrets.token_hex(3)}"
decision_d = f"D_E2E_CASED_{secrets.token_hex(3)}"
request_d = f"REQ_CASED_{secrets.token_hex(2)}"

setup_approval(request_d, 'target-d', 'scope-approved')
result_d = execute_action(step='E2E_CASED', action_id=request_d, target='target-d', runtime_scope='scope-requested', trace_id=trace_d, decision_id=decision_d)

print(f"  Action status: {result_d['status']}")
print(f"  Reason: {result_d.get('reason')}")
case_d = 'SCOPE_MISMATCH' in str(result_d.get('reason', ''))
print(f"  RESULT: {'PASS' if case_d else 'FAIL'}\n")

# ===== CASE-E: CROSS-TRACE ISOLATION =====
print("CASE-E: CROSS-TRACE ISOLATION")
trace_e1 = f"T_E2E_CASEE1_{secrets.token_hex(3)}"
trace_e2 = f"T_E2E_CASEE2_{secrets.token_hex(3)}"

setup_approval(f"REQ_E2E_E1_{secrets.token_hex(2)}", 'target-e1', 'scope-e1')
setup_approval(f"REQ_E2E_E2_{secrets.token_hex(2)}", 'target-e2', 'scope-e2')

execute_action(step='E2E_CASEE1', action_id=f"REQ_E2E_E1_{secrets.token_hex(2)}", target='target-e1', runtime_scope='scope-e1', trace_id=trace_e1, decision_id=f"D_E2E_E1")
execute_action(step='E2E_CASEE2', action_id=f"REQ_E2E_E2_{secrets.token_hex(2)}", target='target-e2', runtime_scope='scope-e2', trace_id=trace_e2, decision_id=f"D_E2E_E2")

isolation = tracker.verify_isolation(trace_e1, trace_e2)
print(f"  Contamination detected: {isolation['contamination_detected']}")
print(f"  Status: {isolation['status']}")
case_e = isolation['status'] == 'ISOLATED'
print(f"  RESULT: {'PASS' if case_e else 'FAIL'}\n")

# ===== SUMMARY =====
print("=== INTEGRATION SUMMARY ===")
print(f"CASE-A (Normal):        {'PASS' if case_a else 'FAIL'}")
print(f"CASE-B (Retry):         {'PASS' if case_b else 'FAIL'}")
print(f"CASE-C (Blocked):       {'PASS' if case_c else 'FAIL'}")
print(f"CASE-D (Scope):         {'PASS' if case_d else 'FAIL'}")
print(f"CASE-E (Cross-Trace):   {'PASS' if case_e else 'FAIL'}")
print()

all_pass = case_a and case_b and case_c and case_d and case_e
print(f"STEP 8 END-TO-END: {'VERIFIED' if all_pass else 'PARTIAL'}\n")

# Evidence verification summary
print("=== EVIDENCE CHAIN VERIFICATION ===")
print(f"CASE-A evidence chain: {chain_a['status']}")
print(f"CASE-A events: {len(chain_a['events'])}")
print(f"CASE-A decisions: {chain_a['decision_ids']}")
print()
print(f"Authorization: STEP 4-C (FROZEN)")
print(f"Tracing: STEP 5 (FROZEN)")
print(f"Recovery: STEP 6 (FROZEN)")
print(f"Evidence: STEP 7 (FROZEN)")
print()
print(f"Pipeline Integration: {'VERIFIED ✓' if all_pass else 'PARTIAL'}")
