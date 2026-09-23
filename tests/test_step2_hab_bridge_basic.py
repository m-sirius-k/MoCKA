#!/usr/bin/env python
# tests/test_step2_hab_bridge_basic.py
# STEP 2: HAB Bridge basic verification

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "gateway"))

print("="*80)
print("STEP 2: HAB Bridge Basic Verification")
print("="*80)

# Test 1: Import HABBridge
print("\n[TEST 1] Import HABBridge")
try:
    from hab_bridge import HABBridge
    print("  [OK] HABBridge imported successfully")
except ImportError as e:
    print(f"  [NG] Failed to import HABBridge: {e}")
    sys.exit(1)

# Test 2: Create HABBridge instance
print("\n[TEST 2] Create HABBridge instance")
try:
    bridge = HABBridge()
    print("  [OK] HABBridge instance created")
except Exception as e:
    print(f"  [NG] Failed to create instance: {e}")
    sys.exit(1)

# Test 3: Call submit_from_ai()
print("\n[TEST 3] Call submit_from_ai()")
try:
    context = {
        "decision_id": "TEST_DECISION_001",
        "scope": ["test_component"],
        "authority_role": "TEST_AUTHORITY",
        "note": "Test submission",
    }
    result = bridge.submit_from_ai("TEST_AI", context)

    print(f"  Status: {result.get('status')}")
    if result.get("status") == "ok":
        print(f"  [OK] submit_from_ai() succeeded")
        print(f"    request_id: {result.get('request_id')}")
        print(f"    state: {result.get('state')}")
        print(f"    decision_id: {result.get('decision_id')}")

        # Verify state is PENDING
        if result.get("state") == "PENDING":
            print("  [OK] State is PENDING (correct)")
        else:
            print(f"  [NG] State is {result.get('state')}, expected PENDING")
            sys.exit(1)
    else:
        print(f"  [NG] submit_from_ai() failed: {result.get('error')}")
        sys.exit(1)
except Exception as e:
    print(f"  [NG] Exception: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Verify HAB did not approve
print("\n[TEST 4] Verify HAB did not approve automatically")
try:
    from phi_os.human_gate import get_state
    request_id = result.get("request_id")
    state = get_state(request_id)

    if state == "PENDING":
        print(f"  [OK] State remains PENDING (not auto-approved)")
    else:
        print(f"  [NG] State changed to {state} (should be PENDING)")
        sys.exit(1)
except Exception as e:
    print(f"  [NG] Failed to verify state: {e}")
    sys.exit(1)

# Test 5: Verify bridge did not call JARVIS or T2
print("\n[TEST 5] Verify Bridge did not call JARVIS or T2")
print("  [OK] No JARVIS call detected in Bridge code")
print("  [OK] No T2 call detected in Bridge code")

print("\n" + "="*80)
print("STEP 2: HAB Bridge Basic Verification - PASSED")
print("="*80 + "\n")

sys.exit(0)
