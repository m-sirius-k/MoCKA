#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_jarvis_recall_implementation.py

テスト: JarvisEngine.recall_experience()の実装を検証
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from runtime.jarvis.core.engine import JarvisEngine


def test_jarvis_recall_experience():
    """Test JARVIS recall_experience() method"""
    print("\n" + "="*80)
    print("Test: JarvisEngine.recall_experience() Implementation")
    print("="*80)

    # Initialize JARVIS
    jarvis = JarvisEngine()

    # Test 1: Basic recall
    print("\n[TEST 1] Basic recall with empty intent")
    result = jarvis.recall_experience(current_intent="Test")

    print(f"Status: {result['status']}")
    print(f"Matches: {len(result['matches'])}")

    if result['matches']:
        match = result['matches'][0]
        print(f"\nRetrieved Decision:")
        print(f"  decision_id: {match.get('decision_id')}")
        print(f"  title: {match.get('title')[:60]}...")
        print(f"  approved_by: {match.get('approved_by')}")
        print(f"  status: {match.get('status')}")

        assert result['status'] == 'found', "Status should be 'found'"
        assert match.get('decision_id'), "decision_id should exist"
        assert match.get('status') == 'Active', "Status should be 'Active'"
        print("\n  OK Test 1 PASSED")
    else:
        print(f"  Gap: {result['gap']}")
        print("\n  NG Test 1 FAILED")
        return False

    # Test 2: Multiple calls should be consistent
    print("\n[TEST 2] Consistency check (multiple calls)")
    result2 = jarvis.recall_experience(current_intent="Test again")

    if result['matches'][0]['decision_id'] == result2['matches'][0]['decision_id']:
        print(f"  OK Same decision returned: {result['matches'][0]['decision_id']}")
        print("\n  OK Test 2 PASSED")
    else:
        print(f"  NG Different decisions returned")
        print(f"    First call: {result['matches'][0]['decision_id']}")
        print(f"    Second call: {result2['matches'][0]['decision_id']}")
        print("\n  NG Test 2 FAILED")
        return False

    # Test 3: Return format validation
    print("\n[TEST 3] Return format validation")
    required_fields = ['decision_id', 'title', 'decision', 'rationale', 'approved_by', 'approved_at', 'status']
    match = result['matches'][0]

    all_present = all(field in match for field in required_fields)
    if all_present:
        print(f"  OK All required fields present: {required_fields}")
        print("\n  OK Test 3 PASSED")
    else:
        missing = [f for f in required_fields if f not in match]
        print(f"  NG Missing fields: {missing}")
        print("\n  NG Test 3 FAILED")
        return False

    # Test 4: Verify it's a read-only operation (no side effects)
    print("\n[TEST 4] Read-only operation verification")
    gate_status_before = jarvis.gate.status
    result3 = jarvis.recall_experience()
    gate_status_after = jarvis.gate.status

    if gate_status_before == gate_status_after:
        print(f"  OK Gate status unchanged: {gate_status_before}")
        print("\n  OK Test 4 PASSED")
    else:
        print(f"  NG Gate status changed: {gate_status_before} -> {gate_status_after}")
        print("\n  NG Test 4 FAILED")
        return False

    print("\n" + "="*80)
    print("ALL TESTS PASSED")
    print("="*80 + "\n")
    return True


if __name__ == "__main__":
    success = test_jarvis_recall_experience()
    sys.exit(0 if success else 1)
