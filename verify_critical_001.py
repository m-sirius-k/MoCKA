#!/usr/bin/env python3
"""
CRITICAL-001 Implementation Verification
Verify that INVALIDATED status is properly added and audit trail is preserved
"""

import json
from pathlib import Path

# Add MoCKA path
import sys
sys.path.insert(0, str(Path(__file__).parent))

# ===== Manual Verification (without full server setup) =====

print("=" * 70)
print("CRITICAL-001: Implementation Verification")
print("=" * 70)

# Check 1: Verify DECISION_STATUS_ENUM includes INVALIDATED
print("\n[CHECK 1] DECISION_STATUS_ENUM")
code_path = Path("/home/user/MoCKA/mocka_mcp_server.py")
with open(code_path) as f:
    content = f.read()
    if 'DECISION_STATUS_ENUM = {"Active", "Superseded", "Withdrawn", "INVALIDATED"}' in content:
        print("  ✓ PASS: INVALIDATED status added to enum")
    else:
        print("  ✗ FAIL: INVALIDATED status not found in enum")
        sys.exit(1)

# Check 2: Verify retry logic is implemented
print("\n[CHECK 2] Retry Logic")
if "for attempt in range(max_retries)" in content and "retry_delays = [2, 4, 8]" in content:
    print("  ✓ PASS: Exponential backoff retry logic implemented")
else:
    print("  ✗ FAIL: Retry logic not found")
    sys.exit(1)

# Check 3: Verify INVALIDATED record creation on failure
print("\n[CHECK 3] INVALIDATED Record Creation")
if 'invalidated_record["status"] = "INVALIDATED"' in content and 'invalidated_record["invalidated_at"]' in content:
    print("  ✓ PASS: INVALIDATED record with timestamp implemented")
else:
    print("  ✗ FAIL: INVALIDATED record creation not found")
    sys.exit(1)

# Check 4: Verify fail_closed response
print("\n[CHECK 4] Fail-Closed Response")
if '{"status": "fail_closed", "error": "event_creation_timeout", "decision_id": None}' in content:
    print("  ✓ PASS: fail_closed response implemented")
else:
    print("  ✗ FAIL: fail_closed response not found")
    sys.exit(1)

# Check 5: Verify audit trail preservation
print("\n[CHECK 5] Audit Trail Preservation")
if '_append_decision(invalidated_record)' in content and 'invalidation_reason' in content:
    print("  ✓ PASS: Audit trail preserved (INVALIDATED appended, not deleted)")
else:
    print("  ✗ FAIL: Audit trail preservation not found")
    sys.exit(1)

# Check 6: Verify git commit
print("\n[CHECK 6] Git Commit")
import subprocess
try:
    result = subprocess.run(["git", "log", "-1", "--oneline"], cwd="/home/user/MoCKA", capture_output=True, text=True)
    if "CRITICAL-001" in result.stdout:
        print(f"  ✓ PASS: {result.stdout.strip()}")
    else:
        print(f"  ! INFO: Latest commit: {result.stdout.strip()}")
except Exception as e:
    print(f"  ! INFO: {e}")

print("\n" + "=" * 70)
print("IMPLEMENTATION VERIFICATION: COMPLETE")
print("=" * 70)
print("\nStatus:")
print("  IMPLEMENTED: ✓")
print("  TESTED: ? (requires MCP server)")
print("  FAILED: ? (requires mock GATE)")
print("  FIXED: ? (requires verification)")
print("  REGRESSION-PASSED: ? (requires full test suite)")
print("  EVIDENCE-COMPLETE: ? (pending)")
print("\nNext step: Run full test suite with mock GATE")
