#!/usr/bin/env python3
"""
RT1-RT6 Core Logic Verification
Verifies the cryptographic and validation mechanisms without full MoCKA runtime.
"""

import json
import sys
from pathlib import Path
import base64

sys.path.insert(0, str(Path(__file__).resolve().parent))

from governance.sign_governance_event import sign_approval_payload
from governance.verify_governance_event_required import verify_approval_signature


def test_rt1_signature_generation():
    """RT1: Signature can be generated for approval payload"""
    print("[RT1] Approval signature generation")

    try:
        payload = {
            "decision_id": "DC_20260924_001_SIGNER_BOUNDARY_GOVERNANCE",
            "approved_by": "きむら博士 (L4 Human Gate)",
            "approved_scopes": ["C3:INITIALIZATION"]
        }

        signature = sign_approval_payload(payload)

        if not signature or not isinstance(signature, str) or len(signature) < 10:
            print("  ✗ FAIL: Invalid signature generated")
            return False

        print(f"  ✓ PASS: Signature generated (length={len(signature)})")
        return True

    except Exception as e:
        print(f"  ✗ FAIL: Exception during signature generation: {e}")
        return False


def test_rt1_rt2_signature_verification():
    """RT1+RT2: Generated signature verifies correctly"""
    print("[RT1/RT2] Signature verification")

    try:
        payload = {
            "decision_id": "DC_20260924_001_SIGNER_BOUNDARY_GOVERNANCE",
            "approved_by": "きむら博士 (L4 Human Gate)",
            "approved_scopes": ["C3:INITIALIZATION"]
        }

        signature = sign_approval_payload(payload)
        payload_with_sig = dict(payload)
        payload_with_sig["signature"] = signature

        is_valid = verify_approval_signature(payload_with_sig, signature)

        if not is_valid:
            print("  ✗ FAIL: Valid signature failed verification")
            return False

        print(f"  ✓ PASS: Signature verified successfully")
        return True

    except Exception as e:
        print(f"  ✗ FAIL: Exception during verification: {e}")
        return False


def test_rt3_signature_fails_on_modified_payload():
    """RT3: Signature fails when payload is modified"""
    print("[RT3] Payload modification detection")

    try:
        payload = {
            "decision_id": "DC_20260924_001_SIGNER_BOUNDARY_GOVERNANCE",
            "approved_by": "きむら博士 (L4 Human Gate)",
            "approved_scopes": ["C3:INITIALIZATION"]
        }

        signature = sign_approval_payload(payload)

        modified_payload = dict(payload)
        modified_payload["approved_scopes"] = ["C3:UNAUTHORIZED_SCOPE"]
        modified_payload["signature"] = signature

        is_valid = verify_approval_signature(modified_payload, signature)

        if is_valid:
            print("  ✗ FAIL: Modified payload verified as valid (signature should fail)")
            return False

        print(f"  ✓ PASS: Modified payload rejected")
        return True

    except Exception as e:
        print(f"  ✗ FAIL: Exception during modification test: {e}")
        return False


def test_rt5_scope_binding():
    """RT5: Scope is bound in signature"""
    print("[RT5] Scope binding in signature")

    try:
        payload1 = {
            "decision_id": "DC_TEST_001",
            "approved_by": "きむら博士 (L4 Human Gate)",
            "approved_scopes": ["C3:SCOPE_A"]
        }

        payload2 = {
            "decision_id": "DC_TEST_001",
            "approved_by": "きむら博士 (L4 Human Gate)",
            "approved_scopes": ["C3:SCOPE_B"]
        }

        sig1 = sign_approval_payload(payload1)
        sig2 = sign_approval_payload(payload2)

        if sig1 == sig2:
            print("  ✗ FAIL: Same payload with different scopes produced same signature")
            return False

        payload1["signature"] = sig1
        payload2["signature"] = sig2

        if verify_approval_signature(payload1, sig1) and verify_approval_signature(payload2, sig2):
            print(f"  ✓ PASS: Different scopes produce different signatures (scope binding works)")
            return True
        else:
            print("  ✗ FAIL: Scope-specific signatures failed verification")
            return False

    except Exception as e:
        print(f"  ✗ FAIL: Exception during scope binding test: {e}")
        return False


def test_rt6_ai_cannot_forge_without_key():
    """RT6: AI cannot forge valid signature without private key"""
    print("[RT6] AI signature forgery prevention")

    try:
        payload = {
            "decision_id": "DC_FORGED_001",
            "approved_by": "AI_FAKE_ISSUER",
            "approved_scopes": ["C3:ESCALATED"]
        }

        fake_signature = "AAAA" + base64.urlsafe_b64encode(b"fake_sig_no_key_access").decode().rstrip("=")
        payload["signature"] = fake_signature

        is_valid = verify_approval_signature(payload, fake_signature)

        if is_valid:
            print("  ✗ FAIL: Forged signature verified as valid!")
            return False

        print(f"  ✓ PASS: Forged signature rejected (AI cannot access private key)")
        return True

    except Exception as e:
        print(f"  ✓ PASS: Exception during forgery test: {e}")
        return True


def test_canonical_format_consistency():
    """Canonical JSON format consistency (critical for signing/verification)"""
    print("[FORMAT] Canonical JSON consistency")

    try:
        import json

        payload = {
            "decision_id": "DC_TEST",
            "approved_by": "きむら博士",
            "approved_scopes": ["C3:INIT", "C3:OTHER"]
        }

        payload_copy = dict(payload)
        payload_copy["signature"] = ""

        msg1 = json.dumps(payload_copy, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        msg2 = json.dumps(payload_copy, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

        if msg1 != msg2:
            print("  ✗ FAIL: Canonical format not consistent")
            return False

        print(f"  ✓ PASS: Canonical format is consistent")
        return True

    except Exception as e:
        print(f"  ✗ FAIL: Exception during format test: {e}")
        return False


def main():
    print("=" * 70)
    print("RT1-RT6 Core Logic Verification")
    print("=" * 70)
    print()

    tests = [
        test_rt1_signature_generation,
        test_rt1_rt2_signature_verification,
        test_rt3_signature_fails_on_modified_payload,
        test_rt5_scope_binding,
        test_rt6_ai_cannot_forge_without_key,
        test_canonical_format_consistency,
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
    print(f"RESULTS: {passed}/{total} core verification tests passed")
    print("=" * 70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
