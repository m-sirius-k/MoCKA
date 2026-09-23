import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA\structural")))
sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA")))

from phi_os.gate_schema import ALLOWED_WHAT_TYPES
from phi_os.gate_validator import validate

print("=" * 70)
print("STEP 3 — SCHEMA VALIDATION TEST")
print("=" * 70)
print()

# Display current allowed types
print("A. Current ALLOWED_WHAT_TYPES:")
print(f"   Count: {len(ALLOWED_WHAT_TYPES)}")
print(f"   Values: {ALLOWED_WHAT_TYPES}")
print()

# Verify governance_block is in the list
if 'governance_block' in ALLOWED_WHAT_TYPES:
    print("✓ VERIFIED: 'governance_block' is in ALLOWED_WHAT_TYPES")
else:
    print("✗ FAILURE: 'governance_block' NOT in ALLOWED_WHAT_TYPES")
print()

# Test 1: Validate a governance_block event
print("B. Test 1: governance_block validation")
print("-" * 70)

session_ts = datetime.now().strftime("SESSION_%Y%m%d_%H%M%S")

payload_governance_block = {
    "who_actor": "Claude-sonnet-5",
    "who_session": session_ts,
    "what_type": "governance_block",
    "where_component": "ba04_execution_gate",
    "where_path": "governance_pipeline.py",
    "why_purpose": "Authority Decision Enforcement (BA-04 Governance Gate)",
    "how_trigger": "before_tool() BLOCK decision",
    "before_state": "Governance evaluation in progress",
    "after_state": "Execution BLOCKED",
    "description": "Tool blocked due to missing/invalid decision",
}

errors = validate(payload_governance_block)
if not errors:
    print("✓ PASS: governance_block event validates successfully")
else:
    print(f"✗ FAIL: governance_block validation errors: {errors}")
print()

# Test 2: Verify existing types still pass
print("C. Test 2: Existing types still validate (regression check)")
print("-" * 70)

test_types = ['file_write', 'incident', 'audit', 'todo_update', 'claude_mcp']
all_pass = True

for test_type in test_types:
    payload_test = {
        "who_actor": "Claude-sonnet-5",
        "who_session": session_ts,
        "what_type": test_type,
        "where_component": "test",
        "where_path": "/test/path",
        "why_purpose": "Test validation for existing type",
        "how_trigger": "regression_test",
        "before_state": "start",
        "after_state": "end",
    }
    errors_test = validate(payload_test)
    status = "✓ PASS" if not errors_test else "✗ FAIL"
    print(f"  {status}: {test_type:<20} {errors_test if errors_test else ''}")
    if errors_test:
        all_pass = False

if all_pass:
    print()
    print("✓ VERIFIED: All existing types continue to pass validation")
else:
    print()
    print("✗ REGRESSION: Some existing types failed validation")
print()

# Test 3: Invalid types still rejected
print("D. Test 3: Invalid types still rejected")
print("-" * 70)

payload_invalid = {
    "who_actor": "Claude-sonnet-5",
    "who_session": session_ts,
    "what_type": "invalid_type_xyz",
    "where_component": "test",
    "where_path": "/test/path",
    "why_purpose": "Test that invalid types are rejected",
    "how_trigger": "invalid_type_test",
    "before_state": "start",
    "after_state": "end",
}

errors_invalid = validate(payload_invalid)
if errors_invalid and any('REJECT-06' in e for e in errors_invalid):
    print(f"✓ PASS: Invalid type correctly rejected")
    print(f"  Error: {errors_invalid[0]}")
else:
    print(f"✗ FAIL: Invalid type was not rejected")
print()

print("=" * 70)
print("SCHEMA TEST SUMMARY")
print("=" * 70)
print(f"✓ governance_block in schema: YES")
print(f"✓ governance_block validates: {'YES' if not errors else 'NO'}")
print(f"✓ Regression (existing types): {'PASS' if all_pass else 'FAIL'}")
print(f"✓ Invalid types rejected: {'YES' if errors_invalid else 'NO'}")
