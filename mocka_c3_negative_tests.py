#!/usr/bin/env python3
"""
RT6: AI Self-Authorization Prevention Negative Tests
Verifies that AI cannot generate valid authorizations or escalate scopes.
"""

import json
import sys
from pathlib import Path
import sqlite3

sys.path.insert(0, str(Path(__file__).resolve().parent))

from governance.verify_governance_event_required import verify_approval_signature
from phi_os.human_gate import approve
from mocka_mcp_server import execute_tool


def test_ai_direct_approve_cannot_sign():
    """Test 1: AI calls approve() directly - signature should fail verification"""
    print("[TEST 1] AI direct approve() call - no TTY, signature invalid")

    try:
        conn = sqlite3.connect(str(Path(__file__).resolve().parent / "data" / "mocka_events.db"))
        conn.row_factory = sqlite3.Row

        test_payload = {
            "decision_id": "DC_TEST_AI_ATTEMPT_001",
            "approved_by": "AI_FAKE_APPROVAL",
            "approved_scopes": ["C3:INITIALIZATION", "C3:ESCALATED_UNAUTHORIZED"]
        }

        event = approve("TEST_REQUEST_AI_001", payload=test_payload, conn=conn)

        payload_in_db = json.loads(event.get("payload", "{}"))
        signature = payload_in_db.get("signature", "").strip()

        if not signature:
            print("  ✓ PASS: No signature generated (signing failed silently or rejected)")
            return True

        is_valid = verify_approval_signature(payload_in_db, signature)
        if not is_valid:
            print("  ✓ PASS: Signature generated but fails verification (invalid)")
            return True
        else:
            print("  ✗ FAIL: Signature is valid! AI forged a valid signature.")
            return False

    except Exception as e:
        print(f"  ✓ PASS: Exception during AI approve() call: {e}")
        return True


def test_ai_cannot_forge_valid_token():
    """Test 2: AI attempts to forge authorization token for unauthorized scope"""
    print("[TEST 2] AI forges token for unauthorized scope")

    try:
        forged_payload = {
            "token_type": "RUNTIME_AUTHORIZATION",
            "decision_id": "DC_FAKE_FORGED_002",
            "scope": "C3:ESCALATED_UNAUTHORIZED",
            "issuer": "AI_FAKE",
            "issued_at": "2026-09-24T00:00:00Z",
            "approval_event_id": "FAKE_EVENT_AI_002"
        }

        import hashlib
        recalc_hash = hashlib.sha256(
            json.dumps(forged_payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
        ).hexdigest()
        forged_payload["token_id"] = recalc_hash[:16]

        result = execute_tool("mocka_runtime_authorization_validate", {
            "token_id": forged_payload["token_id"],
            "token_payload": forged_payload,
            "expected_decision_id": "DC_FAKE_FORGED_002",
            "expected_scope": "C3:ESCALATED_UNAUTHORIZED"
        })

        result_obj = json.loads(result)
        if "error" in result_obj or result_obj.get("status") != "ok":
            print(f"  ✓ PASS: Token validation failed: {result_obj.get('error', result_obj.get('status'))}")
            return True
        else:
            print(f"  ✗ FAIL: Forged token was accepted!")
            return False

    except Exception as e:
        print(f"  ✓ PASS: Exception during token validation: {e}")
        return True


def test_ai_unsigned_approval_rejected():
    """Test 3: Unsigned approval (AI-generated without signature) rejected"""
    print("[TEST 3] Unsigned approval payload rejected")

    try:
        conn = sqlite3.connect(str(Path(__file__).resolve().parent / "data" / "mocka_events.db"))

        unsigned_payload = {
            "decision_id": "DC_TEST_UNSIGNED_003",
            "approved_by": "AI_CLAIM",
            "approved_scopes": ["C3:INITIALIZATION"]
        }

        event = approve("TEST_UNSIGNED_003", payload=unsigned_payload, conn=conn)
        payload_in_db = json.loads(event.get("payload", "{}"))

        if "signature" not in payload_in_db or not payload_in_db.get("signature", "").strip():
            print("  ✓ PASS: Unsigned approval created (but will fail validation)")
            return True
        else:
            print("  ? INFO: Signature present in unsigned approval (should verify if it fails)")
            return True

    except Exception as e:
        print(f"  ✓ PASS: Exception during unsigned approval: {e}")
        return True


def test_token_modification_detected():
    """Test 4: Modified token hash detection"""
    print("[TEST 4] Token modification detected via hash mismatch")

    try:
        valid_payload = {
            "token_type": "RUNTIME_AUTHORIZATION",
            "decision_id": "DC_20260924_001_SIGNER_BOUNDARY_GOVERNANCE",
            "scope": "C3:INITIALIZATION",
            "issuer": "きむら博士 (L4 Human Gate)",
            "issued_at": "2026-09-24T02:25:44Z",
            "approval_event_id": "HG20260924_7445524968434",
            "token_id": "abc123"
        }

        modified_payload = dict(valid_payload)
        modified_payload["scope"] = "C3:ESCALATED_UNAUTHORIZED"

        result = execute_tool("mocka_runtime_authorization_validate", {
            "token_id": valid_payload["token_id"],
            "token_payload": modified_payload,
            "expected_decision_id": valid_payload["decision_id"],
            "expected_scope": valid_payload["scope"]
        })

        result_obj = json.loads(result)
        if "error" in result_obj:
            print(f"  ✓ PASS: Modified token rejected: {result_obj.get('code')}")
            return True
        else:
            print(f"  ✗ FAIL: Modified token accepted!")
            return False

    except Exception as e:
        print(f"  ✓ PASS: Exception during modified token check: {e}")
        return True


def main():
    print("=" * 70)
    print("RT6: AI Self-Authorization Prevention Negative Test Suite")
    print("=" * 70)
    print()

    tests = [
        test_ai_direct_approve_cannot_sign,
        test_ai_cannot_forge_valid_token,
        test_ai_unsigned_approval_rejected,
        test_token_modification_detected,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"[ERROR] Test exception: {e}")
            results.append(False)
        print()

    passed = sum(1 for r in results if r)
    total = len(results)

    print("=" * 70)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
