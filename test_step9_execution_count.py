#!/usr/bin/env python
"""
STEP 9: Execution Count Verification

Proves that duplicate requests do NOT result in double execution
of underlying actions (write operations, state changes, etc).
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA")))

from mocka_mcp_server import execute_tool, _get_db
import sqlite3
import datetime


def count_tool_executions(tool_name):
    """
    Count how many times a tool has been executed by looking at
    request_executions records in the database.
    """
    con = _get_db()
    try:
        # Count entries in request_executions table
        rows = con.execute("""
            SELECT COUNT(*) as cnt FROM request_executions
            WHERE tool_name = ?
        """, (tool_name,)).fetchall()
        return rows[0][0] if rows else 0
    except Exception as e:
        print(f"Note: Could not count executions from request_executions: {e}")
        return -1
    finally:
        con.close()


def test_duplicate_does_not_re_execute():
    """
    Call the same tool with the same req_id twice.
    Verify execution count shows it only executed once.
    """
    print("\n=== Execution Count Test: Duplicate Prevention ===\n")

    tool_name = "mocka_get_overview"
    req_id = "exec-count-test-" + str(int(__import__('time').time() * 1000000) % 1000000)

    # Get baseline
    baseline_before = count_tool_executions(tool_name)
    print(f"Baseline executions of {tool_name}: {baseline_before}")

    # First call
    print(f"\nFirst call: tool={tool_name}, req_id={req_id}")
    result1 = execute_tool(tool_name, {}, req_id=req_id)
    result1_json = json.loads(result1)
    print(f"  Result: {'OK' if 'what_is_mocka' in result1_json else 'ERROR'}")

    baseline_after_first = count_tool_executions(tool_name)
    executions_after_first = baseline_after_first - baseline_before
    print(f"  Executions after first call: +{executions_after_first}")

    # Second call (duplicate)
    print(f"\nSecond call (DUPLICATE): tool={tool_name}, req_id={req_id}")
    result2 = execute_tool(tool_name, {}, req_id=req_id)
    result2_json = json.loads(result2)
    print(f"  Result: {result2_json.get('error', 'OK')}")
    print(f"  Reason: {result2_json.get('reason', 'N/A')}")

    baseline_after_second = count_tool_executions(tool_name)
    executions_after_second = baseline_after_second - baseline_after_first
    print(f"  Executions after second call: +{executions_after_second}")

    # Verification
    print("\n=== Verification ===")
    print(f"First call caused executions: {executions_after_first}")
    print(f"Second call caused executions: {executions_after_second}")

    if executions_after_second == 0:
        print("\n✓ SUCCESS: Duplicate request did NOT cause re-execution")
        return True
    else:
        print(f"\n✗ FAILED: Duplicate request caused {executions_after_second} execution(s)")
        return False


def test_different_req_ids_both_execute():
    """
    Call the same tool with different req_ids.
    Verify execution count shows both were executed.
    """
    print("\n=== Execution Count Test: Legitimate Re-execution ===\n")

    tool_name = "mocka_get_overview"
    req_id_1 = "exec-count-test-req1-" + str(int(__import__('time').time() * 1000000) % 1000000)
    req_id_2 = "exec-count-test-req2-" + str(int(__import__('time').time() * 1000000) % 1000000)

    # Get baseline
    baseline_before = count_tool_executions(tool_name)
    print(f"Baseline executions of {tool_name}: {baseline_before}")

    # First call
    print(f"\nFirst call: tool={tool_name}, req_id={req_id_1}")
    result1 = execute_tool(tool_name, {}, req_id=req_id_1)
    result1_json = json.loads(result1)
    print(f"  Result: {'OK' if 'what_is_mocka' in result1_json else 'ERROR'}")

    baseline_after_first = count_tool_executions(tool_name)
    executions_after_first = baseline_after_first - baseline_before
    print(f"  Executions after first call: +{executions_after_first}")

    # Second call (different req_id, legitimate)
    print(f"\nSecond call (DIFFERENT req_id): tool={tool_name}, req_id={req_id_2}")
    result2 = execute_tool(tool_name, {}, req_id=req_id_2)
    result2_json = json.loads(result2)
    print(f"  Result: {'OK' if 'what_is_mocka' in result2_json else 'ERROR'}")

    baseline_after_second = count_tool_executions(tool_name)
    executions_after_second = baseline_after_second - baseline_after_first
    print(f"  Executions after second call: +{executions_after_second}")

    # Verification
    print("\n=== Verification ===")
    print(f"First call caused executions: {executions_after_first}")
    print(f"Second call caused executions: {executions_after_second}")

    if executions_after_first > 0 and executions_after_second > 0:
        print("\n✓ SUCCESS: Both different req_ids resulted in execution")
        return True
    else:
        print(f"\n✗ FAILED: Expected both to execute")
        return False


def main():
    print("\n" + "="*70)
    print("STEP 9: EXECUTION COUNT VERIFICATION")
    print("Proof that duplicate requests do not cause re-execution")
    print("="*70)

    tests = [
        ("Duplicate prevention", test_duplicate_does_not_re_execute),
        ("Legitimate re-execution", test_different_req_ids_both_execute),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, "PASS" if passed else "FAIL"))
        except Exception as e:
            print(f"\n✗ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, f"ERROR: {str(e)[:50]}"))

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    for test_name, result in results:
        status_symbol = "✓" if result == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {result}")

    passed_count = sum(1 for _, r in results if r == "PASS")
    print(f"\nTotal: {passed_count}/{len(results)} passed")

    return passed_count == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
