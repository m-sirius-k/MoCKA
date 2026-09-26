#!/usr/bin/env python
"""
TEST: Authorization header classification
VERIFY: HTTP auth boundary behavior for different auth formats
"""

import sys
import subprocess
import time
import requests
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

TEST_PREFIX = f"AUTH_CLASS_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

def start_server():
    """Start Human Gate Server"""
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

def test_no_auth_header():
    """NO AUTHORIZATION: Neither Authorization nor X-Human-Authority header"""
    print("\n[CLASS-A] No Authorization Header")

    payload = {"request_id": f"{TEST_PREFIX}_NO_AUTH"}

    resp = requests.post(
        "http://127.0.0.1:5001/api/human_gate/submit",
        json=payload,
        timeout=5
    )

    print(f"  Status: {resp.status_code}")
    is_403 = resp.status_code == 403
    print(f"  Expected: 403 | Actual: {resp.status_code} | Result: {'PASS' if is_403 else 'FAIL'}")
    return is_403

def test_malformed_authorization_header():
    """MALFORMED: Authorization header present but malformed (not Bearer, no token)"""
    print("\n[CLASS-B] Malformed Authorization Header")

    payload = {"request_id": f"{TEST_PREFIX}_MALFORMED"}
    headers = {"Authorization": "Malformed"}  # Not "Bearer XXX"

    resp = requests.post(
        "http://127.0.0.1:5001/api/human_gate/submit",
        json=payload,
        headers=headers,
        timeout=5
    )

    print(f"  Status: {resp.status_code}")
    is_403 = resp.status_code == 403
    print(f"  Expected: 403 | Actual: {resp.status_code} | Result: {'PASS' if is_403 else 'FAIL'}")
    return is_403

def test_bearer_with_empty_token():
    """BEARER EMPTY: Bearer present but token empty"""
    print("\n[CLASS-C] Bearer with Empty Token")

    payload = {"request_id": f"{TEST_PREFIX}_BEARER_EMPTY"}
    headers = {"Authorization": "Bearer"}  # No token

    resp = requests.post(
        "http://127.0.0.1:5001/api/human_gate/submit",
        json=payload,
        headers=headers,
        timeout=5
    )

    print(f"  Status: {resp.status_code}")
    # "Bearer" without space is not "Bearer " (with token)
    is_403 = resp.status_code == 403
    print(f"  Expected: 403 | Actual: {resp.status_code} | Result: {'PASS' if is_403 else 'FAIL'}")
    return is_403

def test_bearer_with_token():
    """BEARER VALID: Bearer token present (token validity not checked at auth layer)"""
    print("\n[CLASS-D] Bearer with Token")

    payload = {"request_id": f"{TEST_PREFIX}_BEARER_TOKEN"}
    headers = {"Authorization": "Bearer test_token_123"}  # Token present

    resp = requests.post(
        "http://127.0.0.1:5001/api/human_gate/submit",
        json=payload,
        headers=headers,
        timeout=5
    )

    print(f"  Status: {resp.status_code}")
    # Auth layer accepts Bearer presence; may fail at validation layer (422)
    # but NOT 403 (auth failure)
    is_not_403_auth_fail = resp.status_code != 403
    print(f"  Expected: NOT 403 | Actual: {resp.status_code} | Result: {'PASS' if is_not_403_auth_fail else 'FAIL'}")
    print(f"  Note: {resp.status_code} is expected (auth passed, validation may fail)")
    return is_not_403_auth_fail

def test_x_human_authority_header():
    """X-HUMAN-AUTHORITY: Alternative auth header"""
    print("\n[CLASS-E] X-Human-Authority Header")

    payload = {"request_id": f"{TEST_PREFIX}_X_HUMAN_AUTH"}
    headers = {"X-Human-Authority": "human_admin_123"}

    resp = requests.post(
        "http://127.0.0.1:5001/api/human_gate/submit",
        json=payload,
        headers=headers,
        timeout=5
    )

    print(f"  Status: {resp.status_code}")
    # X-Human-Authority is alternative to Bearer
    is_not_403 = resp.status_code != 403
    print(f"  Expected: NOT 403 | Actual: {resp.status_code} | Result: {'PASS' if is_not_403 else 'FAIL'}")
    print(f"  Note: {resp.status_code} means auth header accepted")
    return is_not_403

def test_both_headers_present():
    """BOTH: Both Authorization and X-Human-Authority present"""
    print("\n[CLASS-F] Both Headers Present")

    payload = {"request_id": f"{TEST_PREFIX}_BOTH_HEADERS"}
    headers = {
        "Authorization": "Bearer test_token",
        "X-Human-Authority": "human_admin_123"
    }

    resp = requests.post(
        "http://127.0.0.1:5001/api/human_gate/submit",
        json=payload,
        headers=headers,
        timeout=5
    )

    print(f"  Status: {resp.status_code}")
    # Either header should satisfy auth check
    is_not_403 = resp.status_code != 403
    print(f"  Expected: NOT 403 | Actual: {resp.status_code} | Result: {'PASS' if is_not_403 else 'FAIL'}")
    return is_not_403

def run_tests():
    """Run all authorization classification tests"""
    server = None
    results = {}

    try:
        server = start_server()
        if not server:
            return {"FATAL": "Could not start server"}

        tests = [
            ("No Authorization Header", test_no_auth_header),
            ("Malformed Authorization Header", test_malformed_authorization_header),
            ("Bearer with Empty Token", test_bearer_with_empty_token),
            ("Bearer with Token", test_bearer_with_token),
            ("X-Human-Authority Header", test_x_human_authority_header),
            ("Both Headers Present", test_both_headers_present),
        ]

        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
            except Exception as e:
                print(f"  [ERROR] {e}")
                results[test_name] = False

        return results

    finally:
        if server:
            stop_server(server)

if __name__ == "__main__":
    results = run_tests()

    print("\n" + "="*70)
    print("AUTHORIZATION CLASSIFICATION TEST RESULTS")
    print("="*70)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n{passed}/{total} tests passed")
    print("\nCLASSIFICATION SUMMARY:")
    print("  403 (Auth Failed): No header, Malformed header, Bearer-empty")
    print("  NOT 403 (Auth Passed): Bearer-with-token, X-Human-Authority, Both")
    print("  Downstream validation may fail (422) but auth boundary accepts header presence")

    sys.exit(0 if passed == total else 1)
