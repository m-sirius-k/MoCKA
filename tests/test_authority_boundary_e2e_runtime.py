#!/usr/bin/env python
"""
AUTHORITY BOUNDARY E2E RUNTIME AUDIT
Verify Human Authorization cannot be bypassed across full stack
JARVIS → HAB → Runtime → PHI-OS → Evidence Chain
"""

import sys
import subprocess
import time
import requests
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "gateway"))

from phi_os.human_gate import submit, approve, get_state
from governance.authorization_state_bridge import query_authorization_state
try:
    from hab_bridge import HABBridge
except ImportError:
    from gateway.hab_bridge import HABBridge
from runtime.jarvis.core.engine import JarvisEngine

TEST_PREFIX = f"E2E_AUTH_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
DB_PATH = str(Path(__file__).parent.parent / 'data' / 'mocka_events.db')

def start_server():
    """Start Human Gate Server for HTTP testing"""
    try:
        hg_path = Path(__file__).parent.parent / "run_human_gate_server.py"
        process = subprocess.Popen(
            [sys.executable, str(hg_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        for i in range(10):
            time.sleep(1)
            try:
                requests.get("http://127.0.0.1:5001/api/human_gate/pending", timeout=2)
                return process
            except:
                pass

        process.terminate()
        return None
    except Exception:
        return None

def stop_server(process):
    """Stop server"""
    if process:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()

def test_case_1_jarvis_without_auth():
    """
    CASE-1: JARVIS calls approve without Human Authorization
    Expected: BLOCKED, no authorization_state, no executor reach
    """
    print("\n[CASE-1] JARVIS attempts approval without Human Auth")

    request_id = f"{TEST_PREFIX}_CASE1"
    decision_id = f"DC_CASE1_{TEST_PREFIX[-8:]}"

    # Step 1: Submit (simulated)
    print("  Step 1: AI submits via HABBridge")
    bridge = HABBridge()
    bridge_result = bridge.submit_from_ai("gpt-4_ChatGPT", {
        "decision_id": None,
        "scope": ["case1", "test"],
        "authority_role": "AI_AUTHORITY",
    })

    request_id = bridge_result.get("request_id")
    decision_id = bridge_result.get("decision_id")
    state = get_state(request_id)
    assert state == "PENDING"
    print(f"    [OK] PENDING: {request_id}")

    # Step 2: JARVIS tries to approve without Human Auth
    print("  Step 2: JARVIS calls approve() without HUMAN_AUTHORITY")
    jarvis_approve_result = approve(request_id, {
        "decision_id": decision_id,
        "actor": "JARVIS_AUTOMATED",
        "scope": ["case1", "test"],
        "authority_role": "JARVIS_EXECUTOR"  # NOT HUMAN_AUTHORITY
    })

    is_issued = jarvis_approve_result.get("authorization_state_issued")
    print(f"    Auth state issued: {is_issued}")

    # Verify: no authorization_state created
    auth_records = query_authorization_state(decision_id=decision_id)
    if not auth_records and is_issued is False:
        print("    [OK] Authorization state BLOCKED (JARVIS_EXECUTOR rejected)")
        return True
    else:
        print("    [FAIL] Authorization state was issued")
        return False

def test_case_2_hab_without_auth():
    """
    CASE-2: HAB attempts direct approval without Human Authority
    Expected: BLOCKED
    """
    print("\n[CASE-2] HAB attempts approval without Human Auth")

    request_id = f"{TEST_PREFIX}_CASE2"

    # Submit
    print("  Step 1: Submit")
    submit_result = submit({
        "request_id": request_id,
        "actor": "HAB_ORCHESTRATOR",
        "scope": ["case2", "test"],
        "authority_role": "HAB_ORCHESTRATOR"
    })

    assert submit_result.get("next_state") == "PENDING"
    print("    [OK] PENDING")

    # HAB tries to approve
    print("  Step 2: HAB tries to approve with HAB_ORCHESTRATOR")
    hab_approve_result = approve(request_id, {
        "actor": "HAB_ORCHESTRATOR",
        "scope": ["case2", "test"],
        "authority_role": "HAB_ORCHESTRATOR"  # NOT HUMAN_AUTHORITY
    })

    is_issued = hab_approve_result.get("authorization_state_issued")
    print(f"    Auth state issued: {is_issued}")

    if is_issued is False:
        print("    [OK] Authorization state BLOCKED (HAB_ORCHESTRATOR rejected)")
        return True
    else:
        print("    [FAIL] Authorization state was issued")
        return False

def test_case_3_ai_socket_self_approve():
    """
    CASE-3: AI Socket attempts self-approval via internal call
    Expected: BLOCKED
    """
    print("\n[CASE-3] AI Socket attempts self-approval")

    request_id = f"{TEST_PREFIX}_CASE3"
    decision_id = f"DC_CASE3_{TEST_PREFIX[-8:]}"

    # AI submits via HABBridge
    print("  Step 1: Claude AI submits")
    bridge = HABBridge()
    bridge_result = bridge.submit_from_ai("claude-opus-5_Claude", {
        "decision_id": None,
        "scope": ["case3", "test"],
        "authority_role": "AI_AUTHORITY",
    })

    request_id = bridge_result.get("request_id")
    decision_id = bridge_result.get("decision_id")
    print(f"    [OK] PENDING: {request_id}")

    # AI tries to approve itself
    print("  Step 2: Claude tries to approve itself with AI_AUTHORITY")
    ai_approve_result = approve(request_id, {
        "decision_id": decision_id,
        "actor": "claude-opus-5_Claude",
        "scope": ["case3", "test"],
        "authority_role": "AI_AUTHORITY"  # NOT HUMAN_AUTHORITY
    })

    is_issued = ai_approve_result.get("authorization_state_issued")

    if is_issued is False:
        print("    [OK] Authorization state BLOCKED (AI_AUTHORITY rejected)")
        return True
    else:
        print("    [FAIL] Authorization state was issued")
        return False

def test_case_5_scope_mismatch():
    """
    CASE-5: Human Authorization with scope MISMATCH
    Expected: BLOCKED, no executor reach
    """
    print("\n[CASE-5] Human Auth but scope mismatch")

    request_id = f"{TEST_PREFIX}_CASE5"
    decision_id = f"DC_CASE5_{TEST_PREFIX[-8:]}"

    # Submit with scope_a
    print("  Step 1: Submit with scope=[scope_a]")
    submit_result = submit({
        "request_id": request_id,
        "decision_id": decision_id,
        "actor": "test_human",
        "scope": ["scope_a"],
        "authority_role": "HUMAN_AUTHORITY"
    })

    assert submit_result.get("next_state") == "PENDING"
    print("    [OK] PENDING")

    # Approve with scope_b (mismatch)
    print("  Step 2: Approve with scope=[scope_b] (MISMATCH)")
    approve_result = approve(request_id, {
        "decision_id": decision_id,
        "actor": "test_human",
        "scope": ["scope_b"],  # Different!
        "authority_role": "HUMAN_AUTHORITY"
    })

    is_issued = approve_result.get("authorization_state_issued")
    validation_error = approve_result.get("authorization_validation_error")

    print(f"    Auth state issued: {is_issued}")
    if validation_error:
        print(f"    Error: {validation_error}")

    if is_issued is False and "scope mismatch" in str(validation_error or "").lower():
        print("    [OK] Authorization state BLOCKED (scope mismatch)")
        return True
    else:
        print("    [FAIL] Scope mismatch not detected")
        return False

def test_case_positive_full_flow():
    """
    POSITIVE TEST: Correct Human Authorization → Full stack approval
    Expected: APPROVED, executor reaches PHI-OS, evidence recorded
    """
    print("\n[POSITIVE] Correct Human Authorization → Full Flow")

    request_id = f"{TEST_PREFIX}_POSITIVE"
    decision_id = f"DC_POSITIVE_{TEST_PREFIX[-8:]}"

    # Step 1: AI submits
    print("  Step 1: AI (GPT) submits")
    bridge = HABBridge()
    bridge_result = bridge.submit_from_ai("gpt-4_ChatGPT", {
        "decision_id": None,
        "scope": ["positive_test", "e2e"],
        "authority_role": "AI_AUTHORITY",
    })

    request_id = bridge_result.get("request_id")
    decision_id = bridge_result.get("decision_id")
    print(f"    [OK] PENDING: {request_id}")

    # Step 2: Human approves with HUMAN_AUTHORITY + matching scope
    print("  Step 2: Human approves with HUMAN_AUTHORITY + matching scope")
    human_approve_result = approve(request_id, {
        "decision_id": decision_id,
        "actor": "test_human_reviewer",
        "scope": ["positive_test", "e2e"],
        "authority_role": "HUMAN_AUTHORITY"
    })

    assert human_approve_result.get("next_state") == "APPROVED"
    authorization_id = human_approve_result.get("authorization_id")
    is_issued = human_approve_result.get("authorization_state_issued")

    print(f"    State: APPROVED")
    print(f"    Auth state issued: {is_issued}")
    print(f"    Auth ID: {authorization_id}")

    if not (is_issued and authorization_id):
        print("    [FAIL] Authorization state not created")
        return False

    # Step 3: JARVIS receives decision and routes to executor
    print("  Step 3: JARVIS receives decision from HAB")
    jarvis = JarvisEngine(runtime_url="http://localhost:5000")
    jarvis_result = jarvis.receive_decision_from_hab(decision_id)

    print(f"    JARVIS status: {jarvis_result.get('status')}")

    if jarvis_result.get('status') != 'AUTHORIZED':
        print("    [FAIL] JARVIS not authorized")
        return False

    execution_id = jarvis_result.get('execution_id')
    print(f"    Execution ID: {execution_id}")

    # Step 4: Verify trace chain
    print("  Step 4: Verify trace/decision chain")
    print(f"    Request ID: {request_id}")
    print(f"    Decision ID: {decision_id}")
    print(f"    Auth ID: {authorization_id}")
    print(f"    Execution ID: {execution_id}")

    if all([request_id, decision_id, authorization_id, execution_id]):
        print("    [OK] Full trace chain verified")
        return True
    else:
        print("    [FAIL] Trace chain incomplete")
        return False

def run_tests(server):
    """Run all E2E tests"""
    results = {}

    tests = [
        ("CASE-1: JARVIS without auth", test_case_1_jarvis_without_auth),
        ("CASE-2: HAB without auth", test_case_2_hab_without_auth),
        ("CASE-3: AI self-approve", test_case_3_ai_socket_self_approve),
        ("CASE-5: Scope mismatch", test_case_5_scope_mismatch),
        ("POSITIVE: Full flow", test_case_positive_full_flow),
    ]

    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"    [ERROR] {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    return results

if __name__ == "__main__":
    print("\n" + "="*80)
    print("AUTHORITY BOUNDARY E2E RUNTIME AUDIT")
    print("="*80)

    server = None
    try:
        server = start_server()
        if not server:
            print("[WARNING] Could not start HTTP server, continuing with internal tests")

        results = run_tests(server)

        print("\n" + "="*80)
        print("E2E RUNTIME AUDIT RESULTS")
        print("="*80)

        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            print(f"{status}: {test_name}")

        passed = sum(1 for v in results.values() if v)
        total = len(results)

        print(f"\n{passed}/{total} tests passed")

        if passed == total:
            print("\n[OK] AUTHORITY BOUNDARY E2E RUNTIME AUDIT PASSED")
            print("  ✓ JARVIS bypass BLOCKED")
            print("  ✓ HAB bypass BLOCKED")
            print("  ✓ AI self-auth BLOCKED")
            print("  ✓ Scope mismatch BLOCKED")
            print("  ✓ Full flow with Human Auth succeeds")
            sys.exit(0)
        else:
            print(f"\n[FAIL] {total - passed} tests failed")
            sys.exit(1)

    finally:
        if server:
            stop_server(server)
