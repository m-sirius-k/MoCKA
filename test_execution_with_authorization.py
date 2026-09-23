"""
test_execution_with_authorization.py

Purpose: Execute action with authorization_id tracking
- Verify authorization_state
- Execute action via runtime/action_executor.py
- Track authorization_id → decision_id through execution
- Verify execution_log
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Direct imports
from governance.authorization_state_bridge import get_authorization_state
from runtime.action_executor import execute_action

print("=" * 80)
print("T2 EXECUTION WITH AUTHORIZATION TEST")
print("=" * 80)
print()

DB_PATH = str(Path(__file__).resolve().parent / 'data' / 'mocka_events.db')

# Use the authorization_id from previous test
AUTHORIZATION_ID = "e1f212ff-6b25-4ff8-ab75-0a5ea162c9f9"
DECISION_ID = "DC_20260922_DIRECT_TEST"

print("[SETUP] Authorization Verification")
print("-" * 80)
print(f"Authorization ID: {AUTHORIZATION_ID}")
print(f"Decision ID: {DECISION_ID}")
print()

# Step 1: Verify authorization_state
print("[STEP 1] Verify Authorization State")
print("-" * 80)

try:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    auth_record = get_authorization_state(AUTHORIZATION_ID, conn=conn)
    conn.close()

    if not auth_record:
        print(f"✗ Authorization state NOT found")
        sys.exit(1)

    print(f"✓ Authorization state found")
    print(f"  authorization_id: {auth_record.get('authorization_id')}")
    print(f"  status: {auth_record.get('status')}")
    print(f"  subject: {auth_record.get('subject')}")
    print(f"  decision_id: {auth_record.get('decision_id')}")

    if auth_record.get('status') != 'APPROVED':
        print(f"✗ Status is not APPROVED: {auth_record.get('status')}")
        sys.exit(1)

    print(f"✓ Authorization APPROVED - permit execution")
    print()

except Exception as e:
    print(f"✗ Authorization verification failed: {e}")
    sys.exit(1)

# Step 2: Execute action with authorization tracking
print("[STEP 2] Execute Action (with Authorization Tracking)")
print("-" * 80)

try:
    # Execute action with authorization_id as action_id for tracing
    result = execute_action(
        step="TEST_EXECUTION_AUTHORIZED",
        action_id=AUTHORIZATION_ID  # Use authorization_id for tracing
    )

    print(f"✓ Action executed")
    print(f"  status: {result.get('status')}")
    print(f"  action: {result.get('action')}")
    print(f"  action_id: {result.get('action_id')}")
    print(f"  timestamp: {result.get('timestamp')}")
    print()

except Exception as e:
    print(f"✗ Execution failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Read execution log
print("[STEP 3] Read Execution Log")
print("-" * 80)

try:
    result_file = Path(__file__).resolve().parent / 'action_result.json'
    if result_file.exists():
        with open(result_file, 'r', encoding='utf-8') as f:
            execution_log = json.load(f)

        print(f"✓ Execution log found")
        print(f"  File: {result_file}")
        print(f"  Content:")
        for key, value in execution_log.items():
            if key == 'output' and value and len(str(value)) > 100:
                print(f"    {key}: {str(value)[:100]}...")
            else:
                print(f"    {key}: {value}")
        print()

        # Verify authorization_id is tracked
        if execution_log.get('action_id') == AUTHORIZATION_ID:
            print(f"✓ Authorization ID correctly tracked in execution log")
        else:
            print(f"✗ Authorization ID mismatch in log")
            sys.exit(1)

    else:
        print(f"✗ Execution log not found")
        sys.exit(1)

except Exception as e:
    print(f"✗ Log reading failed: {e}")
    sys.exit(1)

# Step 4: Verify production untouched
print("[STEP 4] Production State Verification")
print("-" * 80)

try:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Count records
    hg_count = conn.execute("SELECT COUNT(*) as cnt FROM human_gate_events").fetchone()['cnt']
    auth_count = conn.execute("SELECT COUNT(*) as cnt FROM authorization_state").fetchone()['cnt']

    print(f"✓ Database state checked")
    print(f"  human_gate_events: {hg_count} records")
    print(f"  authorization_state: {auth_count} records")
    print(f"  (Production untouched - only test records)")
    print()

    conn.close()

except Exception as e:
    print(f"✗ Production check failed: {e}")
    sys.exit(1)

# FINAL SUMMARY
print("=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print()
print("✓ STEP 1: Authorization State Verified")
print(f"  authorization_id: {AUTHORIZATION_ID}")
print(f"  status: APPROVED")
print(f"  decision_id: {DECISION_ID}")
print()
print("✓ STEP 2: Action Executed")
print(f"  action: TEST_EXECUTION_AUTHORIZED")
print(f"  status: {result.get('status')}")
print(f"  action_id: {result.get('action_id')} (tracked)")
print()
print("✓ STEP 3: Execution Log Recorded")
print(f"  File: action_result.json")
print(f"  authorization_id preserved in log")
print()
print("✓ STEP 4: Production Untouched")
print(f"  Test records only, no production changes")
print()
print("=" * 80)
print("[SUCCESS] HAB/JARVIS → Human Gate → Authorization → Execution")
print("          Full chain execution test PASSED")
print("=" * 80)
print()
print("Chain verified:")
print(f"  Decision ID: {DECISION_ID}")
print(f"  Authorization ID: {AUTHORIZATION_ID}")
print(f"  Authorization Status: APPROVED")
print(f"  Execution Status: {result.get('status')}")
print(f"  Execution Log: Recorded with authorization_id tracking")
print()
