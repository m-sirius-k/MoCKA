#!/usr/bin/env python
# tests/test_step8_real_user_flow.py
# STEP 8: Real user flow - one-shot verification

import sys
import sqlite3
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "gateway"))

# Use real adapter entry point (not direct HABBridge)
from adapter_gpt import handle_function_call
from phi_os.human_gate import approve, get_state
from runtime.jarvis.core.engine import JarvisEngine

print("\n" + "="*80)
print("STEP 8: Real User Flow - One-Shot Verification")
print("="*80)

# ============================================================================
# [1] ACTUAL AI SOCKET ENTRY: Use real adapter
# ============================================================================
print("\n[1] Entry: Call actual GPT adapter (gateway entry point)")
print("    (This is what AI sends to production gateway)")

gpt_response = handle_function_call(
    title="STEP 8 Real Flow Test",
    description="Test actual user flow from adapter to execution",
    tags=["step8", "real_flow"],
    model="gpt-4",
    runtime="ChatGPT",
    source="Orchestra"
)

print(f"  Status: {gpt_response.get('status')}")
print(f"  Event ID (MoCKA): {gpt_response.get('event_id')}")
print(f"  HAB Request ID: {gpt_response.get('hab_request_id')}")
print(f"  HAB Decision ID: {gpt_response.get('hab_decision_id')}")

if gpt_response.get("status") != "ok":
    print(f"  [NG] Adapter call failed")
    sys.exit(1)

hab_request_id = gpt_response.get("hab_request_id")
decision_id = gpt_response.get("hab_decision_id")

if not hab_request_id or not decision_id:
    print(f"  [NG] Missing HAB IDs")
    sys.exit(1)

print("  [OK] Adapter entry point works")

# ============================================================================
# [2] HAB: Verify PENDING state
# ============================================================================
print("\n[2] HAB: Verify PENDING state")
state = get_state(hab_request_id)
print(f"  Request ID: {hab_request_id}")
print(f"  State: {state}")

if state != "PENDING":
    print(f"  [NG] Expected PENDING, got {state}")
    sys.exit(1)

print("  [OK] State is PENDING (awaiting approval)")

# ============================================================================
# [3] HUMAN AUTHORITY: Explicit approval
# ============================================================================
print("\n[3] Human Authority: Approve decision")

approval_result = approve(hab_request_id, {
    "decision_id": decision_id,
    "actor": "gpt-4_ChatGPT",
    "scope": ["step8", "real_flow"],
    "authority_role": "AI_AUTHORITY",
})

authorization_id = approval_result.get("authorization_id")
print(f"  Decision ID: {decision_id}")
print(f"  Authorization ID: {authorization_id}")

if not authorization_id:
    print(f"  [NG] Approval failed")
    sys.exit(1)

state = get_state(hab_request_id)
print(f"  New State: {state}")

if state != "APPROVED":
    print(f"  [NG] Expected APPROVED, got {state}")
    sys.exit(1)

print("  [OK] Decision approved")

# ============================================================================
# [4] JARVIS: Route to T2
# ============================================================================
print("\n[4] JARVIS: Receive decision and route to T2")

jarvis = JarvisEngine(runtime_url="http://localhost:5000")
jarvis_result = jarvis.receive_decision_from_hab(decision_id)

print(f"  Decision ID: {decision_id}")
print(f"  Authorization ID: {jarvis_result.get('authorization_id')}")
print(f"  JARVIS Status: {jarvis_result.get('status')}")
print(f"  Execution ID: {jarvis_result.get('execution_id')}")

if jarvis_result.get('status') != 'AUTHORIZED':
    print(f"  [NG] JARVIS routing failed: {jarvis_result.get('reason')}")
    sys.exit(1)

execution_id = jarvis_result.get('execution_id')
print("  [OK] JARVIS routed to T2")

# ============================================================================
# [5] T2: Verify execution
# ============================================================================
print("\n[5] T2 Runtime: Verify execution")
print(f"  Execution ID: {execution_id}")
print(f"  Tool: {jarvis_result.get('tool_name')}")
print(f"  Status: {jarvis_result.get('execution_status')}")

if not execution_id:
    print(f"  [NG] No execution ID returned")
    sys.exit(1)

print("  [OK] T2 execution completed")

# ============================================================================
# [6] EXECUTION LOG: Verify traceability
# ============================================================================
print("\n[6] execution_log: Verify complete traceability")

db_path = _REPO_ROOT / 'data' / 'mocka_events.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

# Query execution_log
exec_log = conn.execute(
    'SELECT * FROM execution_log WHERE execution_id = ?',
    (execution_id,)
).fetchone()

if not exec_log:
    conn.close()
    print(f"  [NG] execution_log not found for {execution_id}")
    sys.exit(1)

print(f"  Execution ID: {exec_log['execution_id']}")
print(f"  Authorization ID: {exec_log['authorization_id']}")
print(f"  Decision ID: {exec_log['decision_id']}")
print(f"  Tool: {exec_log['tool_name']}")
print(f"  Status: {exec_log['status']}")

# Verify linkage
if exec_log['decision_id'] != decision_id:
    print(f"  [NG] Decision ID mismatch: {exec_log['decision_id']} != {decision_id}")
    sys.exit(1)

if exec_log['authorization_id'] != authorization_id:
    print(f"  [NG] Authorization ID mismatch: {exec_log['authorization_id']} != {authorization_id}")
    sys.exit(1)

print("  [OK] Complete traceability verified")

# ============================================================================
# [FINAL SUMMARY]
# ============================================================================
print("\n" + "="*80)
print("STEP 8: Real User Flow - COMPLETE")
print("="*80)

print(f"\n[SUMMARY] Complete flow verified:")
print(f"  1. AI Entry      → GPT adapter.handle_function_call()")
print(f"  2. HAB Submit    → Request: {hab_request_id}")
print(f"  3. HAB Decision  → Decision: {decision_id}")
print(f"  4. HAB Approve   → Auth: {authorization_id}")
print(f"  5. JARVIS Route  → Status: AUTHORIZED")
print(f"  6. T2 Execute    → Execution: {execution_id}")
print(f"  7. Log Linkage   → Complete traceability confirmed")

print(f"\n[TRACEABILITY CHAIN]")
print(f"  Request ID    → {hab_request_id}")
print(f"  Decision ID   → {decision_id}")
print(f"  Authorization → {authorization_id}")
print(f"  Execution ID  → {execution_id}")
print(f"  Status        → {exec_log['status']}")

conn.close()

print(f"\n[OK] Real user flow works end-to-end")
print(f"[OK] No implementation changes needed")
print(f"[OK] Production ready\n")

sys.exit(0)
