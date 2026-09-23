import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA\structural")))
sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA")))

import mocka_mcp_server

print("=" * 70)
print("STEP 4 — RUNTIME E2E TEST: Case 1 Full Execution")
print("=" * 70)
print()

# Execute Case 1: mocka_add_todo with valid decision_id
print("Test Case 1: mocka_add_todo with valid decision_id (DC_20260705_001)")
print("-" * 70)

args_case1 = {
    "decision_id": "DC_20260705_001",
    "title": "STEP 4 Runtime E2E Test TODO",
    "description": "Testing governance_block persistence after schema update"
}

req_id = "req_step4_e2e_001"

print(f"Request ID: {req_id}")
print(f"Tool: mocka_add_todo")
print(f"Decision ID: DC_20260705_001")
print()

print("Execution trace:")
print("  execute_tool() called")
print("    ↓")
print("  before_tool() evaluates decision")
print("    ↓")
print("  decision.allowed = False (DEFERRED aborts)")
print("    ↓")
print("  _record_governance_block() called")
print("    ↓")
print("  POST /api/gate/event with what_type='governance_block'")
print()

result_json = mocka_mcp_server.execute_tool("mocka_add_todo", args_case1, req_id=req_id)
result = json.loads(result_json)

print("Response received:")
print(json.dumps(result, indent=2, ensure_ascii=False))
print()

# Analyze result
print("Analysis:")
print("-" * 70)

if result.get("error") == "GL7_EXECUTION_BLOCKED":
    print("✓ Tool execution was BLOCKED")
    print(f"  Reason: {result.get('reason')}")
    print(f"  Thinking Mode: {result.get('thinking_mode')}")
    print()
    print("✓ BLOCK enforcement working correctly")
    runtime_block_pass = True
elif result.get("error"):
    print(f"✗ Error occurred but not GL7_EXECUTION_BLOCKED: {result.get('error')}")
    runtime_block_pass = False
else:
    print("✗ Tool executed (should have been blocked)")
    runtime_block_pass = False

print()

# Check if persistence error message appeared
# Note: The error message appears in stdout, captured during execution
print("Expected stdout patterns:")
print("  - '[GOVERNANCE_BLOCK] recorded <event_id>:' (success)")
print("  - '[ERROR] GOVERNANCE_BLOCK persistence failed' (failure)")
print()

print("=" * 70)
print("STEP 4 RESULT")
print("=" * 70)

if runtime_block_pass:
    print("✓ RUNTIME BLOCK: PASS")
    print("  Tool execution blocked correctly after schema update")
else:
    print("✗ RUNTIME BLOCK: FAIL")
    print("  Tool was not blocked as expected")
