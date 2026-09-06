#!/usr/bin/env python3
"""
Test traceability index functionality
"""

import json
from pathlib import Path

def test_traceability_lookup():
    """Test Event -> Decision lookup"""

    index_file = Path('data/tic/traceability_index.jsonl')
    assert index_file.exists(), "traceability_index.jsonl not found at canonical location data/tic/"

    print("Test 1: Load traceability index...")
    records = []
    with open(index_file, 'r', encoding='utf-8') as f:
        for line in f:
            records.append(json.loads(line))

    assert len(records) > 0, "No records loaded"
    print(f"  PASS - Loaded {len(records)} records")

    print("\nTest 2: Verify Event->Decision links...")
    events_with_decisions = [r for r in records if any(d.get('decision_id') for d in r.get('decisions', []))]
    assert len(events_with_decisions) > 0, "No Event->Decision links found"
    print(f"  PASS - Found {len(events_with_decisions)} events with decisions")

    print("\nTest 3: Verify NOT_ESTABLISHED states preserved...")
    record = records[0]
    assert len(record['evidence']) > 0, "Evidence field empty"
    assert record['evidence'][0].get('status') == 'NOT_ESTABLISHED', "Evidence not marked NOT_ESTABLISHED"
    assert record['audit'][0].get('status') == 'NOT_ESTABLISHED', "Audit not marked NOT_ESTABLISHED"
    assert record['authority'][0].get('status') == 'NOT_ESTABLISHED', "Authority not marked NOT_ESTABLISHED"
    print("  PASS - Unknown links properly marked as NOT_ESTABLISHED")

    print("\nTest 4: Sample traceability lookup...")
    sample = events_with_decisions[0]
    print(f"  Event: {sample['event_id']}")
    print(f"  Decisions: {[d['decision_id'] for d in sample['decisions'] if 'decision_id' in d]}")
    print(f"  Status: {sample['status']}")
    print("  PASS - Lookup working")

    print("\n=== All Tests PASSED ===")
    return True

if __name__ == '__main__':
    test_traceability_lookup()
