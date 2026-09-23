#!/usr/bin/env python3
"""
TARGET-1 Remediated Decision ID Generation
Sandbox implementation with fail-closed daily limit enforcement
"""

import sqlite3
import datetime
from pathlib import Path

# SANDBOX DB (completely isolated)
SANDBOX_DB_PATH = Path(r"C:\Users\sirok\MoCKA\sandbox\mocka_events_sandbox.db")

# PRODUCTION DB (for verification only, READ-ONLY)
PRODUCTION_DB_PATH = Path(r"C:\Users\sirok\MoCKA\data\mocka_events.db")

class LimitExceededException(Exception):
    """Raised when daily decision ID limit (NNN=001-999) is exceeded"""
    pass

class SandboxConnectionError(Exception):
    """Raised when sandbox DB cannot be accessed"""
    pass

def _verify_sandbox_isolation():
    """Fail-closed verification: Sandbox path must not match production"""
    if str(SANDBOX_DB_PATH) == str(PRODUCTION_DB_PATH):
        raise SandboxConnectionError(
            f"ISOLATION VIOLATION: Sandbox and production paths are identical!\n"
            f"Sandbox: {SANDBOX_DB_PATH}\n"
            f"Production: {PRODUCTION_DB_PATH}"
        )

def _get_sandbox_db():
    """Get connection to sandbox DB only (never production)"""
    _verify_sandbox_isolation()

    if not SANDBOX_DB_PATH.exists():
        raise SandboxConnectionError(
            f"Sandbox DB not found: {SANDBOX_DB_PATH}\n"
            "Please run init_sandbox_db.py first"
        )

    con = sqlite3.connect(str(SANDBOX_DB_PATH), timeout=30.0)
    con.row_factory = sqlite3.Row
    return con

def next_decision_id_remediated():
    """
    REMEDIATED: Fail-closed daily limit enforcement

    DC_YYYYMMDD_NNN format where NNN must be in range 001-999

    When counter reaches 999:
    - Next request to increment → would reach 1000
    - Triggers limit exceeded check
    - ROLLBACK transaction
    - Raises LimitExceededException
    - Counter remains at 999
    - No invalid ID generated
    - No ledger write

    Guarantees:
    * Schema compatible: DC_YYYYMMDD_NNN (exactly 3 digits)
    * Thread-safe: ACID transaction
    * Process-safe: SQLite exclusive lock
    * Fail-closed: exception on limit exceed
    * No silent overflow: no 4-digit IDs
    * Restart-safe: counter persisted in DB
    """
    today = datetime.date.today().strftime("%Y%m%d")
    con = _get_sandbox_db()

    try:
        con.execute("BEGIN IMMEDIATE")

        # Initialize counter for today if not exists
        con.execute(
            "INSERT OR IGNORE INTO decision_id_counters (date, counter) VALUES (?, 0)",
            (today,)
        )

        # Atomic increment
        con.execute(
            "UPDATE decision_id_counters SET counter = counter + 1 WHERE date = ?",
            (today,)
        )

        # Read new counter value
        row = con.execute(
            "SELECT counter FROM decision_id_counters WHERE date = ?",
            (today,)
        ).fetchone()

        next_num = row[0]

        # REMEDIATION: Fail-closed limit check
        if next_num > 999:
            # Rollback the increment
            con.rollback()
            raise LimitExceededException(
                f"Decision ID daily limit exceeded for {today}: "
                f"counter would reach {next_num} (max 999)"
            )

        con.commit()

        # Format: DC_YYYYMMDD_NNN (exactly 3 digits)
        return f"DC_{today}_{next_num:03d}"

    except LimitExceededException:
        # Re-raise limit exception without modification
        raise

    except Exception as e:
        con.rollback()
        raise

    finally:
        con.close()

def test_basic_generation():
    """Test 1: Basic ID generation"""
    print("\n[TEST 1] Basic ID Generation")
    print("-" * 60)

    try:
        id1 = next_decision_id_remediated()
        print(f"Generated: {id1}")

        parts = id1.split('_')
        assert len(parts) == 3, f"Expected 3 parts, got {len(parts)}"
        assert parts[0] == 'DC', f"Expected prefix 'DC', got {parts[0]}"
        assert len(parts[2]) == 3, f"Expected suffix length 3, got {len(parts[2])}"
        assert parts[2].isdigit(), f"Expected numeric suffix, got {parts[2]}"

        print(f"✓ Format valid: DC_YYYYMMDD_NNN")
        return True

    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_sequential_generation():
    """Test 2: Sequential generation"""
    print("\n[TEST 2] Sequential Generation")
    print("-" * 60)

    try:
        ids = []
        for i in range(5):
            id_val = next_decision_id_remediated()
            ids.append(id_val)
            num = int(id_val.split('_')[2])
            print(f"  [{i}] {id_val} (num: {num})")

        # Verify monotonic
        nums = [int(id_val.split('_')[2]) for id_val in ids]
        for i in range(1, len(nums)):
            assert nums[i] > nums[i-1], f"Not monotonic: {nums}"

        print(f"✓ Monotonic: {nums[0]} → {nums[-1]}")
        return True

    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_limit_enforcement():
    """Test 3: Daily limit enforcement (counter up to 999)"""
    print("\n[TEST 3] Daily Limit Enforcement (Prep for Limit Test)")
    print("-" * 60)

    try:
        con = _get_sandbox_db()
        today = datetime.date.today().strftime("%Y%m%d")

        # Set counter to 997 (3 away from limit)
        con.execute(
            "UPDATE decision_id_counters SET counter = 997 WHERE date = ?",
            (today,)
        )
        con.commit()
        con.close()

        # Generate IDs until limit
        ids = []
        for i in range(3):
            try:
                id_val = next_decision_id_remediated()
                ids.append(id_val)
                num = int(id_val.split('_')[2])
                print(f"  Generated: {id_val} (num: {num})")
            except LimitExceededException as e:
                print(f"  Limit reached: {e}")
                break

        # Verify we got 998, 999, then limit
        if len(ids) == 2:
            nums = [int(id_val.split('_')[2]) for id_val in ids]
            assert nums == [998, 999], f"Expected [998, 999], got {nums}"
            print(f"✓ Generated up to limit: {nums}")

        return True

    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_limit_exceeded():
    """Test 4: Exceeding daily limit raises exception"""
    print("\n[TEST 4] Limit Exceeded Exception")
    print("-" * 60)

    try:
        con = _get_sandbox_db()
        today = datetime.date.today().strftime("%Y%m%d")

        # Set counter to 999 (at limit)
        con.execute(
            "UPDATE decision_id_counters SET counter = 999 WHERE date = ?",
            (today,)
        )
        con.commit()
        con.close()

        # Try to exceed limit
        try:
            id_val = next_decision_id_remediated()
            print(f"✗ Should have raised exception, got: {id_val}")
            return False
        except LimitExceededException as e:
            print(f"✓ Exception raised (expected):")
            print(f"  {e}")

            # Verify counter is still 999 (rollback worked)
            con = _get_sandbox_db()
            row = con.execute(
                "SELECT counter FROM decision_id_counters WHERE date = ?",
                (today,)
            ).fetchone()
            con.close()

            if row[0] == 999:
                print(f"✓ Counter still at 999 (rollback verified)")
                return True
            else:
                print(f"✗ Counter changed to {row[0]} (rollback failed)")
                return False

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_idempotent_limit():
    """Test 5: Repeated limit exceeds return consistent exception"""
    print("\n[TEST 5] Idempotent Limit Enforcement")
    print("-" * 60)

    try:
        con = _get_sandbox_db()
        today = datetime.date.today().strftime("%Y%m%d")

        # Set counter to 999
        con.execute(
            "UPDATE decision_id_counters SET counter = 999 WHERE date = ?",
            (today,)
        )
        con.commit()
        con.close()

        # Try 3 times, expect 3 exceptions and counter stays 999
        exception_count = 0
        for i in range(3):
            try:
                id_val = next_decision_id_remediated()
                print(f"✗ Attempt {i+1}: Should have raised exception")
                return False
            except LimitExceededException:
                exception_count += 1
                print(f"  Attempt {i+1}: Exception raised (expected)")

        # Verify counter still 999
        con = _get_sandbox_db()
        row = con.execute(
            "SELECT counter FROM decision_id_counters WHERE date = ?",
            (today,)
        ).fetchone()
        con.close()

        if exception_count == 3 and row[0] == 999:
            print(f"✓ All 3 attempts raised exception, counter={row[0]}")
            return True
        else:
            print(f"✗ Inconsistent behavior")
            return False

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def main():
    print("=" * 70)
    print("PHASE 2: FAIL-CLOSED DAILY LIMIT REMEDIATION")
    print("=" * 70)

    results = {}

    # Run tests
    results['Basic Generation'] = test_basic_generation()
    results['Sequential Generation'] = test_sequential_generation()
    results['Limit Enforcement Setup'] = test_limit_enforcement()
    results['Limit Exceeded'] = test_limit_exceeded()
    results['Idempotent Limit'] = test_idempotent_limit()

    # Summary
    print("\n" + "=" * 70)
    print("PHASE 2 SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")

    print("-" * 70)
    print(f"TOTAL: {passed}/{total} passed")

    return 0 if passed == total else 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
