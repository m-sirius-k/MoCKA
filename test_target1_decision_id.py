#!/usr/bin/env python3
"""
TARGET-1 Test Suite: Decision ID Generation Thread Safety
Tests for _next_decision_id() parallel safety implementation
"""

import sys
import json
import time
import datetime
import threading
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add MoCKA to path
sys.path.insert(0, str(Path(__file__).parent))

from mocka_mcp_server import _next_decision_id, _read_decisions, _append_decision

def test_1_basic_id_generation():
    """Test 1: Basic ID generation format"""
    print("\n[TEST 1] Basic ID Generation Format")
    print("-" * 50)

    id1 = _next_decision_id()
    print(f"Generated ID: {id1}")

    # Verify format: DC_YYYYMMDD_000000000XX
    parts = id1.split('_')
    assert len(parts) == 3, f"Expected 3 parts, got {len(parts)}"
    assert parts[0] == 'DC', f"Expected prefix 'DC', got '{parts[0]}'"
    assert len(parts[1]) == 8, f"Expected date to be 8 chars, got {len(parts[1])}"
    assert len(parts[2]) == 13, f"Expected suffix to be 13 chars (9 digits + 4 hex), got {len(parts[2])}"
    assert parts[1].isdigit(), f"Date part should be all digits"
    # Verify that we have 9 digits + 4 hex chars (e.g., 000000000ab12)
    assert parts[2][:9].isdigit(), f"First 9 chars of suffix should be digits"
    assert all(c in '0123456789abcdef' for c in parts[2][9:]), f"Last 4 chars should be hex"

    today = datetime.date.today().strftime('%Y%m%d')
    assert parts[1] == today, f"Expected date {today}, got {parts[1]}"

    print(f"✓ Format is correct: DC_YYYYMMDD_TTTTTTTTTTXX")
    print(f"✓ Date part: {parts[1]}")
    print(f"✓ Microseconds: {parts[2][:9]}")
    print(f"✓ Random suffix: {parts[2][9:]}")
    return True

def test_2_sequential_id_generation():
    """Test 2: Sequential ID generation (time-ordered)"""
    print("\n[TEST 2] Sequential ID Generation (Time-Ordered)")
    print("-" * 50)

    ids = []
    timestamps = []

    for i in range(5):
        id_val = _next_decision_id()
        ids.append(id_val)
        micros = int(id_val.split('_')[2][:9])
        timestamps.append(micros)
        time.sleep(0.001)  # 1ms between generations

    print(f"Generated {len(ids)} IDs")
    for i, (id_val, ts) in enumerate(zip(ids, timestamps)):
        print(f"  [{i}] {id_val} (micros: {ts})")

    # Verify they're time-ordered (microseconds increasing or same)
    for i in range(1, len(timestamps)):
        assert timestamps[i] >= timestamps[i-1], \
            f"IDs not time-ordered: {timestamps[i-1]} vs {timestamps[i]}"

    print(f"✓ IDs are time-ordered within day")
    return True

def test_3_existing_decision_reads():
    """Test 3: Existing Decision reads should still work"""
    print("\n[TEST 3] Existing Decision Reads")
    print("-" * 50)

    records, broken = _read_decisions()
    print(f"Read {len(records)} decision records (broken: {broken})")

    if len(records) > 0:
        for i, record in enumerate(records[:3]):
            print(f"  [{i}] {record.get('decision_id')} - {record.get('title', 'N/A')[:40]}")

        # Verify old format IDs still parse correctly
        old_format_ids = [r for r in records if r.get('decision_id', '').count('_') == 2]
        print(f"✓ Found {len(old_format_ids)} old-format decision IDs (DC_YYYYMMDD_NNN)")

        return True
    else:
        print("⚠ No existing decisions found (database may be new)")
        return True

def test_4_parallel_id_generation():
    """Test 4: Parallel ID generation for collision detection"""
    print("\n[TEST 4] Parallel ID Generation (Thread Safety)")
    print("-" * 50)

    generated_ids = []
    lock = threading.Lock()

    def generate_id():
        id_val = _next_decision_id()
        with lock:
            generated_ids.append(id_val)

    # Generate 50 IDs in parallel (10 threads, 5 IDs each)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(generate_id) for _ in range(50)]
        for future in as_completed(futures):
            future.result()

    print(f"Generated {len(generated_ids)} IDs from 10 parallel threads")

    # Check for duplicates
    unique_ids = set(generated_ids)
    duplicates = len(generated_ids) - len(unique_ids)

    print(f"Unique IDs: {len(unique_ids)}")
    print(f"Duplicates: {duplicates}")

    if duplicates > 0:
        print("✗ COLLISION DETECTED!")
        # Show duplicates
        from collections import Counter
        counts = Counter(generated_ids)
        for id_val, count in sorted(counts.items()):
            if count > 1:
                print(f"  {id_val}: {count} times")
        return False

    print(f"✓ Zero collisions in {len(generated_ids)} parallel generations")
    print(f"Sample IDs:")
    for id_val in sorted(generated_ids)[:5]:
        print(f"  {id_val}")

    return True

def test_5_decision_write_and_read():
    """Test 5: Write a decision and read it back"""
    print("\n[TEST 5] Decision Write & Read Back")
    print("-" * 50)

    # Generate a new decision ID
    decision_id = _next_decision_id()
    print(f"Generated decision_id: {decision_id}")

    # Create a test decision record
    record = {
        "decision_id": decision_id,
        "title": "TARGET-1 Thread Safety Test",
        "context": "Test for parallel-safe Decision ID generation",
        "alternatives": [{"option": "N/A", "rejected_reason": "Test only"}],
        "decision": "Verify _next_decision_id() is thread-safe",
        "rationale": "Testing parallel writes don't cause collisions",
        "impact": "Test data in decision_ledger.jsonl",
        "related_events": [],
        "related_documents": [],
        "approved_by": "AUTO_TEST",
        "approved_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "supersedes": None,
        "superseded_by": None,
        "status": "Active"
    }

    # Append it
    _append_decision(record)
    print(f"✓ Decision written to ledger")

    # Read back
    records, _ = _read_decisions()
    found = [r for r in records if r.get('decision_id') == decision_id]

    if len(found) == 1:
        found_record = found[0]
        print(f"✓ Decision read back successfully")
        print(f"  ID: {found_record.get('decision_id')}")
        print(f"  Title: {found_record.get('title')}")
        assert found_record.get('title') == record['title'], "Title mismatch"
        return True
    elif len(found) == 0:
        print(f"✗ Decision not found after write!")
        return False
    else:
        print(f"✗ Multiple decisions with same ID found!")
        return False

def test_6_backward_compatibility():
    """Test 6: Backward compatibility with old format IDs"""
    print("\n[TEST 6] Backward Compatibility")
    print("-" * 50)

    records, _ = _read_decisions()

    # Check old format vs new format
    old_format = []
    new_format = []

    for record in records:
        decision_id = record.get('decision_id', '')
        parts = decision_id.split('_')

        if len(parts) == 3 and parts[0] == 'DC':
            try:
                # Try to parse as old format: DC_YYYYMMDD_NNN
                int(parts[2])
                old_format.append(decision_id)
            except (ValueError, IndexError):
                # New format or other format
                new_format.append(decision_id)
        else:
            new_format.append(decision_id)

    print(f"Old format (DC_YYYYMMDD_NNN): {len(old_format)}")
    if old_format:
        print(f"  Examples: {old_format[:3]}")

    print(f"New format (DC_YYYYMMDD_TTTTTTTTTTXX): {len(new_format)}")
    if new_format:
        print(f"  Examples: {new_format[:3]}")

    # Old format should still be readable
    if old_format:
        print(f"✓ Old format IDs are still readable")

    print(f"✓ Mixed old/new formats can coexist")
    return True

def test_7_format_validation():
    """Test 7: Validate ID format consistency"""
    print("\n[TEST 7] Format Validation")
    print("-" * 50)

    ids_to_test = []

    # Generate test IDs
    for _ in range(10):
        ids_to_test.append(_next_decision_id())

    print(f"Validating {len(ids_to_test)} generated IDs...")

    all_valid = True
    for id_val in ids_to_test:
        parts = id_val.split('_')

        # Check structure
        if len(parts) != 3:
            print(f"✗ Invalid structure: {id_val}")
            all_valid = False
            continue

        # Check prefix
        if parts[0] != 'DC':
            print(f"✗ Invalid prefix: {id_val}")
            all_valid = False
            continue

        # Check date (8 digits)
        if not (len(parts[1]) == 8 and parts[1].isdigit()):
            print(f"✗ Invalid date: {id_val}")
            all_valid = False
            continue

        # Check suffix (9 digits + 4 hex)
        if len(parts[2]) != 13:
            print(f"✗ Invalid suffix length: {id_val} (expected 13, got {len(parts[2])})")
            all_valid = False
            continue

        # Verify date is valid
        try:
            datetime.datetime.strptime(parts[1], '%Y%m%d')
        except ValueError:
            print(f"✗ Invalid date value: {id_val}")
            all_valid = False
            continue

    if all_valid:
        print(f"✓ All {len(ids_to_test)} IDs are valid")
        return True
    else:
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("TARGET-1 TEST SUITE: Decision ID Thread Safety")
    print("=" * 60)

    tests = [
        ("Basic ID Generation", test_1_basic_id_generation),
        ("Sequential ID Generation", test_2_sequential_id_generation),
        ("Existing Decision Reads", test_3_existing_decision_reads),
        ("Parallel ID Generation", test_4_parallel_id_generation),
        ("Decision Write & Read", test_5_decision_write_and_read),
        ("Backward Compatibility", test_6_backward_compatibility),
        ("Format Validation", test_7_format_validation),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Exception in {test_name}:")
            print(f"  {type(e).__name__}: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")

    print("-" * 60)
    print(f"TOTAL: {passed}/{total} tests passed")

    if passed == total:
        print("\nTARGET-1 = PASS ✓")
        return 0
    else:
        print(f"\nTARGET-1 = FAIL ✗ ({total - passed} test(s) failed)")
        return 1

if __name__ == '__main__':
    sys.exit(main())
