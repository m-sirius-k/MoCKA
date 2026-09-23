#!/usr/bin/env python3
"""
TARGET-1 Process-Level Concurrency Verification
Tests multiple independent Python processes accessing sandbox DB
"""

import multiprocessing as mp
import sqlite3
import datetime
from pathlib import Path
import time
from collections import defaultdict

SANDBOX_DB_PATH = Path(r"C:\Users\sirok\MoCKA\sandbox\mocka_events_sandbox.db")

class LimitExceededException(Exception):
    pass

def worker_generate_ids(process_id, num_ids, results_queue):
    """
    Worker process: generate IDs and report results
    Completely independent process (separate Python interpreter)
    """
    con = sqlite3.connect(str(SANDBOX_DB_PATH), timeout=30.0)
    generated_ids = []
    limit_exceeds = 0
    errors = []

    try:
        for i in range(num_ids):
            try:
                today = datetime.date.today().strftime("%Y%m%d")

                con.execute("BEGIN IMMEDIATE")
                con.execute(
                    "INSERT OR IGNORE INTO decision_id_counters (date, counter) VALUES (?, 0)",
                    (today,)
                )
                con.execute(
                    "UPDATE decision_id_counters SET counter = counter + 1 WHERE date = ?",
                    (today,)
                )

                row = con.execute(
                    "SELECT counter FROM decision_id_counters WHERE date = ?",
                    (today,)
                ).fetchone()

                next_num = row[0]

                # Fail-closed check
                if next_num > 999:
                    con.rollback()
                    limit_exceeds += 1
                    continue

                con.commit()
                id_val = f"DC_{today}_{next_num:03d}"
                generated_ids.append(id_val)

            except Exception as e:
                con.rollback()
                errors.append(f"Error in attempt {i}: {e}")

    finally:
        con.close()

    # Report results
    results_queue.put({
        'process_id': process_id,
        'generated': generated_ids,
        'limit_exceeds': limit_exceeds,
        'errors': errors
    })

def test_concurrent_processes(num_processes, ids_per_process):
    """Run concurrent process test"""
    print(f"\n[PROCESS-LEVEL CONCURRENCY TEST]")
    print(f"Configuration: {num_processes} processes × {ids_per_process} IDs/process")
    print("-" * 70)

    # Reset sandbox counter to 0
    con = sqlite3.connect(str(SANDBOX_DB_PATH), timeout=10.0)
    today = datetime.date.today().strftime("%Y%m%d")
    con.execute("DELETE FROM decision_id_counters WHERE date = ?", (today,))
    con.commit()
    con.close()

    print(f"Sandbox counter reset for {today}")

    # Start processes
    results_queue = mp.Queue()
    processes = []
    start_time = time.time()

    for p_id in range(num_processes):
        p = mp.Process(
            target=worker_generate_ids,
            args=(p_id, ids_per_process, results_queue)
        )
        p.start()
        processes.append(p)

    # Wait for completion
    for p in processes:
        p.join()

    elapsed = time.time() - start_time

    # Collect results
    all_ids = []
    total_limit_exceeds = 0
    all_errors = []

    while not results_queue.empty():
        result = results_queue.get()
        all_ids.extend(result['generated'])
        total_limit_exceeds += result['limit_exceeds']
        all_errors.extend(result['errors'])

        print(f"  Process {result['process_id']}: {len(result['generated'])} IDs, "
              f"{result['limit_exceeds']} limit exceeds")

    # Verify results
    unique_ids = set(all_ids)
    duplicates = len(all_ids) - len(unique_ids)
    expected_total = num_processes * ids_per_process - total_limit_exceeds

    print()
    print(f"Total IDs generated: {len(all_ids)}")
    print(f"Unique IDs: {len(unique_ids)}")
    print(f"Duplicates: {duplicates}")
    print(f"Limit exceeds: {total_limit_exceeds}")
    print(f"Time elapsed: {elapsed:.3f}s")
    print(f"Rate: {len(all_ids)/elapsed:.0f} IDs/sec")

    if all_errors:
        print(f"\nErrors:")
        for err in all_errors[:5]:
            print(f"  {err}")

    # Verify counter consistency
    con = sqlite3.connect(str(SANDBOX_DB_PATH), timeout=10.0)
    row = con.execute(
        "SELECT counter FROM decision_id_counters WHERE date = ?",
        (today,)
    ).fetchone()
    con.close()

    counter_value = row[0] if row else 0
    print(f"\nCounter value: {counter_value}")
    print(f"Counter = Unique IDs? {counter_value == len(unique_ids)}")

    # Summary
    print()
    if duplicates == 0 and counter_value == len(unique_ids):
        print(f"✓ PASS: Zero collisions, counter consistent")
        return True
    else:
        if duplicates > 0:
            print(f"✗ FAIL: {duplicates} collisions detected")
        if counter_value != len(unique_ids):
            print(f"✗ FAIL: Counter mismatch (counter={counter_value}, unique={len(unique_ids)})")
        return False

def main():
    print("=" * 70)
    print("PHASE 3: PROCESS-LEVEL CONCURRENCY VERIFICATION")
    print("=" * 70)

    results = {}

    # Test 1: 5 processes × 20 IDs
    results['5 processes × 20 IDs'] = test_concurrent_processes(5, 20)

    # Test 2: 10 processes × 50 IDs
    results['10 processes × 50 IDs'] = test_concurrent_processes(10, 50)

    # Test 3: 20 processes × 50 IDs (similar to original Test 6)
    results['20 processes × 50 IDs'] = test_concurrent_processes(20, 50)

    # Summary
    print("\n" + "=" * 70)
    print("PHASE 3 SUMMARY")
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
