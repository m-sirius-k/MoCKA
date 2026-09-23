"""
test_hab_jarvis_connector.py
HAB/JARVIS Runtime Connector - Sandbox Test
2026-09-22

テスト目的:
1. Human Gate approve() への接続確認
2. Authorization State 作成確認
3. Runtime /approve への接続試行（ベストエフォート）
4. E2E フロー実測
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hab_jarvis_runtime_connector import HABJARVISRuntimeConnector

print("=" * 80)
print("T2 HAB/JARVIS → RUNTIME CONNECTION TEST")
print("=" * 80)
print()

connector = HABJARVISRuntimeConnector()

# Test Case 1: Human Gate Approval Only
print("[TEST 1] Human Gate Approval (HG-AS-01)")
print("-" * 80)

hg_result = connector.approve_with_human_gate(
    decision_id="DC_20260922_T2_TEST",
    actor="kimura_phd",
    scope=["component_A", "component_J"],
    authority_role="HG_AUTHORITY_HOLDER_01",
    evidence_ref=["PAPER5_PHASE2_20260918"]
)

print(f"Success: {hg_result.get('success')}")
print(f"Authorization ID: {hg_result.get('authorization_id')}")
print(f"Authorization State Issued: {hg_result.get('authorization_state_issued')}")

event = hg_result.get('event') or {}
if event:
    print(f"Human Gate Event ID: {event.get('event_id')}")

if not hg_result.get('success'):
    error_msg = hg_result.get('error', 'Unknown error')
    print(f"Error: {error_msg}")
    print()
    print("[RESULT] Step 1 FAILED - Cannot proceed")
    print()
    print("[DEBUG] Full result:")
    print(json.dumps(hg_result, indent=2, default=str))
    print()
    sys.exit(1)

print("[RESULT] Step 1 PASSED ✓")
print()

# Extract authorization_id for next steps
authorization_id = hg_result.get('authorization_id')

if not authorization_id:
    print("[ERROR] No authorization_id returned from Human Gate")
    sys.exit(1)

# Test Case 2: Verify Authorization State
print("[TEST 2] Authorization State Verification")
print("-" * 80)

auth_result = connector.verify_authorization_state(authorization_id)

print(f"Exists: {auth_result.get('exists')}")
print(f"Status: {auth_result.get('status')}")
print(f"Subject: {auth_result.get('subject')}")
print(f"Scope: {auth_result.get('scope')}")
print(f"Granted By: {auth_result.get('granted_by')}")

if not auth_result.get('exists'):
    print(f"Error: {auth_result.get('error', 'Unknown')}")
    print()
    print("[RESULT] Step 2 FAILED - Authorization state not created")
    print()
    print("[CRITICAL] Gap detected:")
    print("  - Human Gate approve() succeeded")
    print("  - But authorization_state record was not created")
    print("  - Check: HG-AS-01 payload validation / issue_authorization_state() execution")
    sys.exit(1)

if auth_result.get('status') != "APPROVED":
    print(f"[ERROR] Status mismatch: {auth_result.get('status')} != APPROVED")
    sys.exit(1)

print("[RESULT] Step 2 PASSED ✓")
print()

# Test Case 3: Runtime Approval (Best Effort)
print("[TEST 3] Runtime /approve Call (Best Effort)")
print("-" * 80)

runtime_result = connector.call_runtime_approve(
    authorization_id=authorization_id,
    decision_id="DC_20260922_T2_TEST",
    human_identity="kimura_phd"
)

print(f"Success: {runtime_result.get('success')}")
print(f"Runtime Status: {runtime_result.get('runtime_status')}")
print(f"Permit Granted: {runtime_result.get('permit')}")

if not runtime_result.get('success'):
    error = runtime_result.get('error', 'Unknown error')
    print(f"Error: {error}")
    print()
    if "Connection error" in error or "not found" in error.lower():
        print("[NOTE] Runtime /approve endpoint not yet available")
        print("       This is expected; endpoint may be under development")
        print("       Proceed with Step 1+2 verification (PASSED)")
    print()
else:
    if runtime_result.get('permit'):
        print("[RESULT] Step 3 PASSED ✓")
    else:
        print("[RESULT] Step 3 BLOCKED - Runtime denied permit")

print()
print("=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print()

print("✓ STEP 1: Human Gate Approval")
print(f"  - request_id: {hg_result.get('event', {}).get('request_id')}")
print(f"  - event_id: {hg_result.get('event', {}).get('event_id')}")
print(f"  - state: {hg_result.get('event', {}).get('next_state')}")
print()

print("✓ STEP 2: Authorization State Created")
print(f"  - authorization_id: {authorization_id}")
print(f"  - status: {auth_result.get('status')}")
print(f"  - subject: {auth_result.get('subject')}")
print(f"  - scope: {auth_result.get('scope')}")
print()

if runtime_result.get('success'):
    print(f"✓ STEP 3: Runtime /approve Received")
    print(f"  - permit: {runtime_result.get('permit')}")
    print()
    if runtime_result.get('permit'):
        print("[SUCCESS] FULL E2E CONNECTION WORKING")
    else:
        print("[PARTIAL] Connection made but Runtime denied permit")
else:
    print("- STEP 3: Runtime /approve (not available yet)")
    print()
    print("[STATUS] HAB/JARVIS → Human Gate → Authorization connection VERIFIED ✓")

print()

# Database verification
print("=" * 80)
print("DATABASE VERIFICATION")
print("=" * 80)
print()

import sqlite3

db_path = str(Path(__file__).resolve().parent / 'data' / 'mocka_events.db')
try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Check human_gate_events
    hg_row = conn.execute(
        "SELECT * FROM human_gate_events WHERE request_id LIKE ? ORDER BY timestamp DESC LIMIT 1",
        (f"%DC_20260922_T2_TEST%",)
    ).fetchone()

    if hg_row:
        print("✓ human_gate_events record found")
        print(f"  - event_id: {hg_row['event_id']}")
        print(f"  - action: {hg_row['action']}")
        print(f"  - next_state: {hg_row['next_state']}")
    else:
        print("✗ human_gate_events record NOT found")

    print()

    # Check authorization_state
    auth_row = conn.execute(
        "SELECT * FROM authorization_state WHERE authorization_id = ?",
        (authorization_id,)
    ).fetchone()

    if auth_row:
        print("✓ authorization_state record found")
        print(f"  - authorization_id: {auth_row['authorization_id']}")
        print(f"  - status: {auth_row['status']}")
        print(f"  - subject: {auth_row['subject']}")
        print(f"  - immutable: {auth_row['immutable']}")
    else:
        print("✗ authorization_state record NOT found")

    conn.close()

except Exception as e:
    print(f"DB verification error: {e}")

print()
print("=" * 80)
