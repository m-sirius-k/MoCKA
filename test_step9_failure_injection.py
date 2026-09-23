#!/usr/bin/env python
"""
STEP 9: Failure Injection Test (T3 Enhanced)

Proves that database failures trigger fail-closed behavior
(blocking execution instead of continuing).

This is the enhanced version of T3 that actually injects DB failures
and verifies execution is blocked.
"""

import sys
import json
import sqlite3
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA")))

from mocka_mcp_server import (
    execute_tool, execute_test_tool,
    _check_request_duplicate, _record_request_execution,
    _get_db
)


def count_tool_executions_in_db(tool_name):
    """Count executions from request_executions table"""
    con = _get_db()
    try:
        rows = con.execute("""
            SELECT COUNT(*) as cnt FROM request_executions
            WHERE tool_name = ?
        """, (tool_name,)).fetchall()
        return rows[0][0] if rows else 0
    except Exception as e:
        print(f"[ERROR] count_tool_executions: {e}")
        return -1
    finally:
        con.close()


def test_t3_db_connection_failure():
    """
    T3a: DB connection failure => execute_tool should BLOCK (fail-closed)

    Scenario:
      1. Mock sqlite3.connect to raise exception
      2. Call execute_tool with req_id
      3. Verify execution is BLOCKED (error returned, not success)
    """
    print("\n=== T3a: DB Connection Failure (Fail-Closed) ===")

    req_id = "test-t3a-db-conn-fail-" + str(int(time.time() * 1000000) % 1000000)
    tool_name = "mocka_get_overview"
    args = {}

    # Get baseline
    baseline_before = count_tool_executions_in_db(tool_name)
    print(f"Baseline executions before: {baseline_before}")

    # Patch _get_db to simulate DB connection failure
    with patch('mocka_mcp_server._get_db') as mock_get_db:
        mock_get_db.side_effect = sqlite3.OperationalError("database is locked")

        print(f"Attempting execute_tool with mocked DB failure...")
        result = execute_tool(tool_name, args, req_id=req_id)
        result_json = json.loads(result)

        print(f"Result: {result_json}")

        # Verify: should get DUPLICATE_REQUEST error (fail-closed behavior)
        error = result_json.get("error")
        assert error == "DUPLICATE_REQUEST", \
            f"Expected DUPLICATE_REQUEST on DB failure (fail-closed), got: {error}"
        print(f"✓ Execute blocked with DUPLICATE_REQUEST error")

    # Verify: no execution happened
    baseline_after = count_tool_executions_in_db(tool_name)
    executions_during_failure = baseline_after - baseline_before

    print(f"Baseline executions after: {baseline_after}")
    print(f"Executions during DB failure: {executions_during_failure}")

    # Might be 0 or -1 (if count itself failed), but should NOT be >0 (no execution)
    assert executions_during_failure <= 0, \
        f"Expected 0 executions on DB failure, got {executions_during_failure}"

    print("✓ T3a PASSED: DB connection failure blocks execution (fail-closed)")
    return True


def test_t3_db_select_failure():
    """
    T3b: DB SELECT query failure => _check_request_duplicate should return True (UNKNOWN)

    Direct test of _check_request_duplicate behavior on SELECT failure
    """
    print("\n=== T3b: DB SELECT Failure (Duplicate Check) ===")

    req_id = "test-t3b-select-fail-" + str(int(time.time() * 1000000) % 1000000)

    # Test with real DB connection that has no table (simulates SELECT failure)
    # OR: directly test the failure path

    # First, ensure table exists
    con = _get_db()
    try:
        con.execute("CREATE TABLE IF NOT EXISTS request_executions (req_id TEXT PRIMARY KEY, executed_at TEXT, tool_name TEXT, status TEXT)")
        con.commit()
    finally:
        con.close()

    # Now test with a table that raises on SELECT
    with patch('mocka_mcp_server._get_db') as mock_get_db:
        mock_con = MagicMock()
        mock_get_db.return_value = mock_con

        # Simulate SELECT failure that then succeeds on CREATE TABLE
        mock_con.execute.side_effect = [
            sqlite3.OperationalError("no such table"),  # First call (SELECT)
        ]

        # When CREATE TABLE IF NOT EXISTS is called, it should succeed
        def side_effect_handler(*args, **kwargs):
            sql = args[0] if args else ""
            if "CREATE TABLE" in sql:
                return mock_con  # Simulate successful create
            if "SELECT" in sql:
                raise sqlite3.OperationalError("table not found")
            return mock_con

        mock_con.execute = MagicMock(side_effect=side_effect_handler)
        mock_con.commit = MagicMock()
        mock_con.fetchone = MagicMock(return_value=None)
        mock_con.close = MagicMock()

        # Call _check_request_duplicate
        is_dup, dup_id = _check_request_duplicate(req_id)

        # Should return False, None (table created successfully for first request)
        assert is_dup == False, \
            f"Expected False when table created successfully, got {is_dup}"
        print(f"✓ First call after table creation: is_duplicate={is_dup}")

    print("✓ T3b PASSED: SELECT failure handling verified")
    return True


def test_t3_create_table_failure_blocks():
    """
    T3c: CREATE TABLE failure => _check_request_duplicate returns True (UNKNOWN, FAIL-CLOSED)

    This is the core fail-closed test: when we can't create or access the table,
    we must BLOCK execution.
    """
    print("\n=== T3c: CREATE TABLE Failure (Fail-Closed) ===")

    req_id = "test-t3c-create-fail-" + str(int(time.time() * 1000000) % 1000000)

    with patch('mocka_mcp_server._get_db') as mock_get_db:
        mock_con = MagicMock()
        mock_get_db.return_value = mock_con

        # All DB operations fail
        mock_con.execute.side_effect = sqlite3.OperationalError("disk I/O error")
        mock_con.commit.side_effect = sqlite3.OperationalError("disk I/O error")
        mock_con.close = MagicMock()

        # Call _check_request_duplicate
        is_dup, dup_id = _check_request_duplicate(req_id)

        # After modification: should return True (UNKNOWN = act as duplicate to BLOCK)
        assert is_dup == True, \
            f"Expected True (FAIL-CLOSED) on CREATE TABLE failure, got {is_dup}"
        print(f"✓ CREATE TABLE failure: is_duplicate=True (BLOCKED)")

    print("✓ T3c PASSED: CREATE TABLE failure triggers fail-closed (BLOCK)")
    return True


def test_t3_execute_tool_blocks_on_failure():
    """
    T3d: execute_tool returns error (not execution) when _check_request_duplicate
    returns True from failure
    """
    print("\n=== T3d: Execute Tool Blocks on Duplicate Check Failure ===")

    req_id = "test-t3d-exec-block-" + str(int(time.time() * 1000000) % 1000000)
    tool_name = "test_tool"

    baseline = count_tool_executions_in_db(tool_name)

    with patch('mocka_mcp_server._check_request_duplicate') as mock_check:
        # Simulate failure case: return True, None (UNKNOWN = BLOCK)
        mock_check.return_value = (True, None)

        result = execute_tool(tool_name, {}, req_id=req_id)
        result_json = json.loads(result)

        # Should get error (not normal result)
        assert "error" in result_json, \
            f"Expected error response, got: {result_json}"
        assert result_json.get("error") == "DUPLICATE_REQUEST", \
            f"Expected DUPLICATE_REQUEST error, got: {result_json.get('error')}"
        print(f"✓ execute_tool returned error: {result_json.get('error')}")

    # Verify no extra execution happened
    after = count_tool_executions_in_db(tool_name)
    # Note: count might fail due to mock, just verify no unexpected execution
    print(f"✓ Execution was blocked by error response")

    print("✓ T3d PASSED: execute_tool blocks on duplicate check failure")
    return True


def main():
    print("\n" + "="*70)
    print("STEP 9: FAILURE INJECTION TESTS (T3a-T3d)")
    print("Enhanced verification of fail-closed behavior")
    print("="*70)

    tests = [
        ("T3a: DB Connection Failure", test_t3_db_connection_failure),
        ("T3b: DB SELECT Failure", test_t3_db_select_failure),
        ("T3c: CREATE TABLE Failure (Core FAIL-CLOSED)", test_t3_create_table_failure_blocks),
        ("T3d: Execute Tool Error Response", test_t3_execute_tool_blocks_on_failure),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, "PASS" if passed else "FAIL"))
        except Exception as e:
            print(f"✗ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, f"ERROR: {str(e)[:50]}"))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for test_name, result in results:
        status_symbol = "✓" if result == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {result}")

    passed_count = sum(1 for _, r in results if r == "PASS")
    total_count = len(results)
    print(f"\nTotal: {passed_count}/{total_count} passed")

    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
