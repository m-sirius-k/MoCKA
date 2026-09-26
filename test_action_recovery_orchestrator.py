#!/usr/bin/env python
"""
Test ActionRecoveryOrchestrator
Integration test: simulated retry flow with mock execute_fn
"""

import sys
import os
import secrets
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== ACTION RECOVERY ORCHESTRATOR TEST ===")
print()

from runtime.action_recovery import ActionRecoveryOrchestrator

# ===== Mock execute_fn that fails on first attempt, succeeds on second =====
class MockExecutor:
    """Mock executor that fails first time, succeeds on retry"""

    def __init__(self):
        self.call_count = 0
        self.trace_id_check = None
        self.decision_id_check = None

    def execute(
        self,
        step,
        action_id,
        target=None,
        runtime_scope=None,
        trace_id=None,
        decision_id=None,
        **kwargs
    ):
        self.call_count += 1

        # Store trace/decision from first call
        if self.call_count == 1:
            self.trace_id_check = trace_id
            self.decision_id_check = decision_id

        # Verify trace/decision don't change
        if self.call_count > 1:
            if trace_id != self.trace_id_check:
                return {
                    "status": "error",
                    "reason": f"TRACE_ID changed: {self.trace_id_check} → {trace_id}",
                    "action": step,
                    "action_id": action_id,
                    "timestamp": "N/A"
                }
            if decision_id != self.decision_id_check:
                return {
                    "status": "error",
                    "reason": f"DECISION_ID changed: {self.decision_id_check} → {decision_id}",
                    "action": step,
                    "action_id": action_id,
                    "timestamp": "N/A"
                }

        # Fail on first attempt, succeed on retry
        if self.call_count == 1:
            return {
                "status": "error",
                "reason": "Transient connection timeout (simulated)",
                "action": step,
                "action_id": action_id,
                "timestamp": "N/A"
            }
        else:
            return {
                "status": "success",
                "reason": None,
                "action": step,
                "action_id": action_id,
                "timestamp": "N/A",
                "output": f"Recovered on attempt {self.call_count}",
                "event_id": f"E_RECOVERY_{secrets.token_hex(4)}"
            }


# ===== TEST: Orchestrator retry flow =====
print("TEST: ActionRecoveryOrchestrator retries transient failure")
print()

trace_id = f"T_RECOVERY_TEST_{secrets.token_hex(4)}"
decision_id = f"D_RECOVERY_TEST_{secrets.token_hex(4)}"
action_id = f"REQ_RECOVERY_TEST_{secrets.token_hex(2)}"

mock_executor = MockExecutor()
orchestrator = ActionRecoveryOrchestrator(max_attempts=3)

print(f"Input parameters:")
print(f"  action_id:  {action_id}")
print(f"  trace_id:   {trace_id}")
print(f"  decision_id: {decision_id}")
print(f"  max_attempts: 3")
print()

result = orchestrator.execute_with_recovery(
    mock_executor.execute,
    action_id,
    trace_id=trace_id,
    decision_id=decision_id,
    step="RECOVERY_ORCHESTRATOR_TEST",
    target="recovery-test",
    runtime_scope="recovery-scope"
)

print(f"Result:")
print(f"  Status: {result['status']}")
print(f"  Output: {result.get('output')}")
print(f"  Calls made: {mock_executor.call_count}")
print()

# Verification
test_pass = (
    result['status'] == 'success' and
    mock_executor.call_count == 2 and
    mock_executor.trace_id_check == trace_id and
    mock_executor.decision_id_check == decision_id
)

print(f"Verification:")
print(f"  Success after retry: {result['status'] == 'success'}")
print(f"  Retry count (2 attempts): {mock_executor.call_count == 2}")
print(f"  TRACE_ID preserved: {mock_executor.trace_id_check == trace_id}")
print(f"  DECISION_ID preserved: {mock_executor.decision_id_check == decision_id}")
print()

print(f"RESULT: {'PASS' if test_pass else 'FAIL'}")
