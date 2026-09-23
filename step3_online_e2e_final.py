import sys
import json
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA\structural")))
sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA")))

import mocka_mcp_server

print("=" * 70)
print("STEP 3 — ONLINE E2E TEST (After Server Restart)")
print("=" * 70)
print()

# Test Case 1: Full execution with server restart
print("Case 1: mocka_add_todo with valid decision_id")
print("-" * 70)
print()

req_id = "req_online_e2e_001"
args = {
    "decision_id": "DC_20260705_001",
    "title": "ONLINE E2E TEST - Step 3",
    "description": "Testing governance_block persistence after server reload"
}

print(f"Request ID: {req_id}")
print(f"Decision ID: DC_20260705_001")
print(f"Time: {datetime.now().isoformat()}")
print()

print("Execution trace:")
print("  mocka_add_todo → execute_tool() → before_tool()")
print("  ↓")
print("  decision.allowed=False → _record_governance_block()")
print("  ↓")
print("  POST /api/gate/event with what_type='governance_block'")
print()

result_json = mocka_mcp_server.execute_tool("mocka_add_todo", args, req_id=req_id)
result = json.loads(result_json)

print("Response:")
print(json.dumps(result, indent=2, ensure_ascii=False))
print()

# Analyze result
print("Analysis:")
print("-" * 70)

if result.get("error") == "GL7_EXECUTION_BLOCKED":
    print("✓ BLOCK: Tool execution blocked")
    block_pass = True
else:
    print(f"✗ BLOCK: Unexpected response: {result}")
    block_pass = False

# Check for governance persistence message
print()
print("Note: Check server output for:")
print("  '[GOVERNANCE_BLOCK] recorded <event_id>:' (HTTP 201 success)")
print("  OR '[ERROR] GOVERNANCE_BLOCK persistence failed' (HTTP 422 or other failure)")
print()

print("=" * 70)
print("STEP 3 RESULT")
print("=" * 70)
if block_pass:
    print("✓ RUNTIME BLOCK: PASS")
    print("  Tool execution blocked as expected")
    print()
    print("Next: Check for HTTP response in server output")
    print("      (governed by server reboot status)")
else:
    print("✗ RUNTIME BLOCK: FAIL")
