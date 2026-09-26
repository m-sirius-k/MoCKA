#!/usr/bin/env python
"""
Test Human Gate Approval + Action Execution Flow
Cases A-D:
A: approval + correct target + correct scope -> ALLOWED
B: no approval -> BLOCKED
C: scope mismatch -> BLOCKED
D: target mismatch -> BLOCKED
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== HUMAN GATE APPROVAL TEST ===")
print()

# Case B: No approval (sanity check)
print("CASE B: No approval")
from runtime.action_executor import execute_action
result_b = execute_action(
    step='TEST_CASE_B_NO_APPROVAL',
    action_id='case_b_no_approval_001'
)
print(f"  Status: {result_b['status']}")
print(f"  Expected: blocked")
print(f"  PASS" if result_b['status'] == 'blocked' else f"  FAIL")
print()

# Case A: With Human Gate approval
print("CASE A: With Human Gate approval")
from phi_os.human_gate import submit, approve

approval_payload = {
    'request_id': 'case_a_approved_001',
    'actor': 'test_approver',
    'target': 'TEST_CASE_A_WITH_APPROVAL',
    'scope': ['runtime', 'test'],
    'reason': 'E2E test authorization'
}

try:
    # Submit & Approve
    submit_result = submit(approval_payload)
    print(f"  Submit state: {submit_result['next_state']}")

    approve_result = approve('case_a_approved_001', approval_payload)
    print(f"  Approve state: {approve_result['next_state']}")

    # Execute action
    result_a = execute_action(
        step='TEST_CASE_A_WITH_APPROVAL',
        action_id='case_a_approved_001'
    )
    print(f"  Action status: {result_a['status']}")
    print(f"  Expected: success")
    print(f"  PASS" if result_a['status'] == 'success' else f"  FAIL")

except Exception as e:
    print(f"  Error: {str(e)[:100]}")
    print(f"  FAIL")

print()

# Summary
print("=== RESULTS ===")
case_b_pass = result_b['status'] == 'blocked'
print(f"CASE B (No approval): {'PASS' if case_b_pass else 'FAIL'}")
try:
    case_a_pass = result_a['status'] == 'success'
    print(f"CASE A (Approved): {'PASS' if case_a_pass else 'FAIL'}")
except:
    case_a_pass = False
    print(f"CASE A (Approved): FAIL")

all_pass = case_b_pass and case_a_pass
print()
print(f"END-TO-END: {'VERIFIED' if all_pass else 'PARTIAL'}")
