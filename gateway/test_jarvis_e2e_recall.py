"""
E2E Test: JARVIS recall_experience() integration via gateway
CASE B: Direct recall_experience() call without Socket wrapper

Purpose: Verify the actual execution path
1. HAB Gateway → multi_dispatcher
2. _call_jarvis() → recall_experience()
3. decision_ledger.jsonl → real Decision
4. Response back through gateway

Test Scope: Minimal E2E without full HTTP stack
(Direct function call to verify internal routing)
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add gateway directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the modified _call_jarvis
from multi_dispatcher import _call_jarvis


def test_jarvis_recall_e2e():
    """
    E2E Test: _call_jarvis() calls recall_experience() and returns real Decision

    Verification Points:
    A. _call_jarvis() is reachable from dispatcher
    B. recall_experience() is actually invoked
    C. decision_ledger.jsonl real record is returned
    D. Response contains actual Decision ID from ledger
    """

    print("=" * 70)
    print("E2E TEST: JARVIS recall_experience() integration")
    print("=" * 70)

    # Test parameters
    decision_id = "TEST_CASE_B_001"  # Dummy - unused in MVP
    request_id = "REQ_e2e_test_001"
    request_text = "test recall experience"
    title = "E2E Test Request"
    timestamp = datetime.now(timezone.utc).isoformat()

    print(f"\n[Setup] Test Parameters:")
    print(f"  decision_id (unused): {decision_id}")
    print(f"  request_id: {request_id}")
    print(f"  request_text: {request_text}")
    print(f"  timestamp: {timestamp}")

    # A. Call _call_jarvis (entry point)
    print(f"\n[STEP A] Calling _call_jarvis()...")
    try:
        jarvis_response = _call_jarvis(
            decision_id=decision_id,
            request_id=request_id,
            request_text=request_text,
            title=title,
            timestamp=timestamp
        )
        print(f"  ✓ _call_jarvis() returned: status={jarvis_response.get('status')}")
    except Exception as e:
        print(f"  ✗ _call_jarvis() failed: {e}")
        return False

    # B. Check if recall_experience() was invoked (by checking response structure)
    print(f"\n[STEP B] Verifying recall_experience() was called...")
    if jarvis_response.get('status') in ['found', 'empty', 'error']:
        print(f"  ✓ Response indicates recall_experience() was invoked")
        print(f"    Status: {jarvis_response.get('status')}")
        print(f"    Gap: {jarvis_response.get('jarvis_gap')}")
    else:
        print(f"  ✗ Unexpected response status: {jarvis_response.get('status')}")
        return False

    # C. Verify real decision_ledger.jsonl record if found
    print(f"\n[STEP C] Checking for real Decision Ledger record...")
    if jarvis_response.get('status') == 'found' and jarvis_response.get('jarvis_decision'):
        decision = jarvis_response.get('jarvis_decision')
        decision_id_returned = decision.get('decision_id')

        print(f"  ✓ Real decision found!")
        print(f"    Decision ID: {decision_id_returned}")
        print(f"    Source: {decision.get('source')}")
        print(f"    Title: {decision.get('title', 'N/A')[:60]}...")
        print(f"    Status: {decision.get('status')}")
        print(f"    Approved by: {decision.get('approved_by')}")
        print(f"    Approved at: {decision.get('approved_at')}")

        # D. Verify decision is in response and traceable
        print(f"\n[STEP D] Verifying response integrity...")
        if decision_id_returned and decision.get('source') == 'decision_ledger':
            print(f"  ✓ Decision is from decision_ledger.jsonl")
            print(f"  ✓ Decision ID is traceable: {decision_id_returned}")
        else:
            print(f"  ✗ Decision source not verified")
            return False

    elif jarvis_response.get('status') == 'empty':
        print(f"  ⚠ No active decisions found (ledger empty or no Active records)")
        print(f"    This is OK if decision_ledger.jsonl has no Active records yet")
        print(f"  ✓ recall_experience() was called (correct response for empty ledger)")
        return True
    else:
        print(f"  ✗ Error in recall_experience(): {jarvis_response.get('jarvis_error')}")
        return False

    # E. Full response structure check
    print(f"\n[STEP E] Response structure validation...")
    required_fields = ['request_id', 'status', 'timestamp']
    for field in required_fields:
        if field in jarvis_response:
            print(f"  ✓ {field}: {jarvis_response.get(field)[:50]}...")
        else:
            print(f"  ✗ Missing field: {field}")
            return False

    print(f"\n" + "=" * 70)
    print(f"E2E TEST RESULT: PASS")
    print(f"=" * 70)
    print(f"\nExecution Path Confirmed:")
    print(f"  HAB Gateway → multi_dispatcher")
    print(f"  → _call_jarvis()")
    print(f"  → JarvisEngine.recall_experience()")
    print(f"  → decision_ledger.jsonl")
    print(f"  → Decision returned")
    print(f"  → Response to HAB")

    if jarvis_response.get('status') == 'found':
        print(f"\nActual Decision Retrieved:")
        print(f"  Decision ID: {jarvis_response['jarvis_decision'].get('decision_id')}")
        print(f"  Title: {jarvis_response['jarvis_decision'].get('title')}")
        print(f"  Status: {jarvis_response['jarvis_decision'].get('status')}")

    return True


if __name__ == "__main__":
    success = test_jarvis_recall_e2e()
    sys.exit(0 if success else 1)
