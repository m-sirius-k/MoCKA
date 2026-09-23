#!/usr/bin/env python
# tests/test_multi_ai_minimal_connection.py
# Multi-AI: Verify AI-A and AI-B use same HAB/JARVIS/T2 pipeline independently

import sys
import sqlite3
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from phi_os.human_gate import submit, approve
from governance.authorization_state_bridge import get_authorization_state
from runtime.jarvis.core.engine import JarvisEngine


def test_ai_a():
    """
    AI-A: Submit, approve, execute via JARVIS.
    Returns: (request_id, authorization_id, decision_id, execution_id)
    """
    print("\n" + "="*80)
    print("AI-A: Single execution")
    print("="*80)

    decision_id = "DECISION_AI_A_001"
    actor_id = "AI_AGENT_A"

    # HAB: Submit
    print("\n[AI-A] HAB.submit()")
    submit_result = submit({
        "decision_id": decision_id,
        "actor": actor_id,
        "scope": ["component_A"],
        "authority_role": "AI_AUTHORITY",
    })
    request_id = submit_result["request_id"]
    print(f"  request_id: {request_id}")

    # HAB: Approve
    print("[AI-A] HAB.approve()")
    approval_result = approve(request_id, {
        "decision_id": decision_id,
        "actor": actor_id,
        "scope": ["component_A"],
        "authority_role": "AI_AUTHORITY",
    })
    authorization_id = approval_result.get('authorization_id')
    print(f"  authorization_id: {authorization_id}")

    # JARVIS: Evaluate and route to T2
    print("[AI-A] JARVIS.receive_decision_from_hab()")
    jarvis = JarvisEngine(runtime_url="http://localhost:5000")
    jarvis_result = jarvis.receive_decision_from_hab(decision_id)

    if jarvis_result.get('status') != 'AUTHORIZED':
        print(f"  [NG] JARVIS denied: {jarvis_result.get('reason')}")
        return None

    execution_id = jarvis_result.get('execution_id')
    print(f"  execution_id: {execution_id}")
    print(f"  status: {jarvis_result.get('status')}")

    print("\n[OK] AI-A execution complete")
    return {
        "ai": "AI_A",
        "request_id": request_id,
        "authorization_id": authorization_id,
        "decision_id": decision_id,
        "execution_id": execution_id,
    }


def test_ai_b():
    """
    AI-B: Submit, approve, execute via JARVIS.
    Returns: (request_id, authorization_id, decision_id, execution_id)
    """
    print("\n" + "="*80)
    print("AI-B: Single execution")
    print("="*80)

    decision_id = "DECISION_AI_B_001"
    actor_id = "AI_AGENT_B"

    # HAB: Submit
    print("\n[AI-B] HAB.submit()")
    submit_result = submit({
        "decision_id": decision_id,
        "actor": actor_id,
        "scope": ["component_B"],
        "authority_role": "AI_AUTHORITY",
    })
    request_id = submit_result["request_id"]
    print(f"  request_id: {request_id}")

    # HAB: Approve
    print("[AI-B] HAB.approve()")
    approval_result = approve(request_id, {
        "decision_id": decision_id,
        "actor": actor_id,
        "scope": ["component_B"],
        "authority_role": "AI_AUTHORITY",
    })
    authorization_id = approval_result.get('authorization_id')
    print(f"  authorization_id: {authorization_id}")

    # JARVIS: Evaluate and route to T2
    print("[AI-B] JARVIS.receive_decision_from_hab()")
    jarvis = JarvisEngine(runtime_url="http://localhost:5000")
    jarvis_result = jarvis.receive_decision_from_hab(decision_id)

    if jarvis_result.get('status') != 'AUTHORIZED':
        print(f"  [NG] JARVIS denied: {jarvis_result.get('reason')}")
        return None

    execution_id = jarvis_result.get('execution_id')
    print(f"  execution_id: {execution_id}")
    print(f"  status: {jarvis_result.get('status')}")

    print("\n[OK] AI-B execution complete")
    return {
        "ai": "AI_B",
        "request_id": request_id,
        "authorization_id": authorization_id,
        "decision_id": decision_id,
        "execution_id": execution_id,
    }


def test_readback(ai_a_data, ai_b_data):
    """
    READ-BACK: Verify all IDs exist in DB and are correctly linked.
    """
    print("\n" + "="*80)
    print("READ-BACK: Verify separation and linkage")
    print("="*80)

    db_path = _REPO_ROOT / 'data' / 'mocka_events.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    print("\n[AI-A READ-BACK]")
    # Query human_gate_events
    hg_row = conn.execute(
        'SELECT * FROM human_gate_events WHERE request_id = ? ORDER BY timestamp DESC LIMIT 1',
        (ai_a_data['request_id'],)
    ).fetchone()

    # Query authorization_state
    auth_row = conn.execute(
        'SELECT * FROM authorization_state WHERE authorization_id = ?',
        (ai_a_data['authorization_id'],)
    ).fetchone()

    # Query execution_log
    exec_row = conn.execute(
        'SELECT * FROM execution_log WHERE execution_id = ?',
        (ai_a_data['execution_id'],)
    ).fetchone()

    if hg_row and auth_row and exec_row:
        print(f"  request_id: {hg_row['request_id']}")
        print(f"  authorization_id: {auth_row['authorization_id']}")
        print(f"  decision_id: {auth_row['decision_id']}")
        print(f"  execution_id: {exec_row['execution_id']}")
        print(f"  scope: {auth_row['scope']}")
        assert auth_row['decision_id'] == ai_a_data['decision_id']
        assert exec_row['decision_id'] == ai_a_data['decision_id']
        print("  [OK] AI-A READ-BACK complete")
    else:
        print("  [NG] AI-A READ-BACK failed")
        return False

    print("\n[AI-B READ-BACK]")
    # Query human_gate_events
    hg_row = conn.execute(
        'SELECT * FROM human_gate_events WHERE request_id = ? ORDER BY timestamp DESC LIMIT 1',
        (ai_b_data['request_id'],)
    ).fetchone()

    # Query authorization_state
    auth_row = conn.execute(
        'SELECT * FROM authorization_state WHERE authorization_id = ?',
        (ai_b_data['authorization_id'],)
    ).fetchone()

    # Query execution_log
    exec_row = conn.execute(
        'SELECT * FROM execution_log WHERE execution_id = ?',
        (ai_b_data['execution_id'],)
    ).fetchone()

    if hg_row and auth_row and exec_row:
        print(f"  request_id: {hg_row['request_id']}")
        print(f"  authorization_id: {auth_row['authorization_id']}")
        print(f"  decision_id: {auth_row['decision_id']}")
        print(f"  execution_id: {exec_row['execution_id']}")
        print(f"  scope: {auth_row['scope']}")
        assert auth_row['decision_id'] == ai_b_data['decision_id']
        assert exec_row['decision_id'] == ai_b_data['decision_id']
        print("  [OK] AI-B READ-BACK complete")
    else:
        print("  [NG] AI-B READ-BACK failed")
        return False

    print("\n[SEPARATION VERIFICATION]")
    # Verify AI-A and AI-B are not mixed
    ai_a_auth = conn.execute(
        'SELECT * FROM authorization_state WHERE authorization_id = ?',
        (ai_a_data['authorization_id'],)
    ).fetchone()
    ai_b_auth = conn.execute(
        'SELECT * FROM authorization_state WHERE authorization_id = ?',
        (ai_b_data['authorization_id'],)
    ).fetchone()

    if ai_a_auth['decision_id'] != ai_b_auth['decision_id']:
        print(f"  AI-A decision_id: {ai_a_auth['decision_id']}")
        print(f"  AI-B decision_id: {ai_b_auth['decision_id']}")
        print("  [OK] AI-A and AI-B are separate")
    else:
        print("  [NG] AI-A and AI-B mixed!")
        return False

    if ai_a_auth['authorization_id'] != ai_b_auth['authorization_id']:
        print(f"  AI-A authorization_id: {ai_a_auth['authorization_id']}")
        print(f"  AI-B authorization_id: {ai_b_auth['authorization_id']}")
        print("  [OK] Authorizations are separate")
    else:
        print("  [NG] Authorizations mixed!")
        return False

    conn.close()
    return True


def test_fail_closed(ai_a_data, ai_b_data):
    """
    Test Fail-Closed: Verify AI isolation.
    """
    print("\n" + "="*80)
    print("FAIL-CLOSED TESTS: Multi-AI isolation")
    print("="*80)

    jarvis = JarvisEngine(runtime_url="http://localhost:5000")
    passed = 0
    failed = 0

    # Test 1: No authorization (completely new decision_id)
    print("\n[TEST 1] No authorization for new decision_id")
    print("  Try: Nonexistent decision_id (no authorization_state)")

    result = jarvis.receive_decision_from_hab("NONEXISTENT_DECISION_MULTI_AI_001")
    if result.get('status') == 'DENIED' and result.get('execution_id') is None:
        print(f"  [OK] PASS: Correctly denied (no authorization)")
        passed += 1
    else:
        print(f"  [NG] FAIL: Should be denied")
        failed += 1

    # Test 2: Create pending authorization for AI-C (not approved)
    print("\n[TEST 2] Authorization PENDING (not approved)")
    print("  Try: decision_id without approval")

    decision_id_pending = "DECISION_AI_C_PENDING_001"
    pending_result = submit({
        "decision_id": decision_id_pending,
        "actor": "AI_AGENT_C",
        "scope": ["component_C"],
        "authority_role": "AI_AUTHORITY",
    })
    # Don't approve - leave in PENDING

    result = jarvis.receive_decision_from_hab(decision_id_pending)
    if result.get('status') == 'DENIED' and result.get('execution_id') is None:
        print(f"  [OK] PASS: Correctly denied (PENDING)")
        passed += 1
    else:
        print(f"  [NG] FAIL: Should be denied for PENDING authorization")
        failed += 1

    # Test 3: Verify AI-A and AI-B scopes are separate
    print("\n[TEST 3] Scope separation verification")
    print("  Verify: AI-A scope [component_A] != AI-B scope [component_B]")

    db_path = _REPO_ROOT / 'data' / 'mocka_events.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    ai_a_auth = conn.execute(
        'SELECT * FROM authorization_state WHERE authorization_id = ?',
        (ai_a_data['authorization_id'],)
    ).fetchone()

    ai_b_auth = conn.execute(
        'SELECT * FROM authorization_state WHERE authorization_id = ?',
        (ai_b_data['authorization_id'],)
    ).fetchone()

    conn.close()

    if ai_a_auth['scope'] != ai_b_auth['scope']:
        print(f"  AI-A scope: {ai_a_auth['scope']}")
        print(f"  AI-B scope: {ai_b_auth['scope']}")
        print(f"  [OK] PASS: Scopes are separate")
        passed += 1
    else:
        print(f"  [NG] FAIL: Scopes should be separate")
        failed += 1

    print("\n" + "="*80)
    print(f"Fail-Closed Tests: {passed} passed, {failed} failed")
    print("="*80)

    return failed == 0


if __name__ == "__main__":
    try:
        # Execute AI-A
        ai_a_data = test_ai_a()
        if not ai_a_data:
            print("\n[NG] AI-A execution failed")
            sys.exit(1)

        # Execute AI-B
        ai_b_data = test_ai_b()
        if not ai_b_data:
            print("\n[NG] AI-B execution failed")
            sys.exit(1)

        # READ-BACK verification
        if not test_readback(ai_a_data, ai_b_data):
            print("\n[NG] READ-BACK verification failed")
            sys.exit(1)

        # Fail-Closed tests
        if not test_fail_closed(ai_a_data, ai_b_data):
            print("\n[NG] Fail-Closed tests failed")
            sys.exit(1)

        print("\n" + "="*80)
        print("MULTI-AI MINIMAL CONNECTION TEST: PASSED")
        print("="*80)
        print("\n[OK] Multiple AIs successfully use same HAB/JARVIS/T2 pipeline")
        print("[OK] AI-A and AI-B execute independently")
        print("[OK] Authorizations are separate")
        print("[OK] decision_ids are separate")
        print("[OK] execution_ids are separate")
        print("[OK] Fail-Closed guarantees maintained\n")

        sys.exit(0)

    except Exception as e:
        print(f"\n[NG] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
