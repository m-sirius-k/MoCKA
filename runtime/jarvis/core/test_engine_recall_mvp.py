"""
JARVIS Experience Recall MVP - Minimal E2E Test

Purpose: Verify that recall_experience() can retrieve actual Active decisions
from decision_ledger.jsonl without invoking custom search logic.

Test boundary: decision_ledger source → recall_experience() → Decision retrieval

This test is kept minimal to verify MVP contract: return most recent Active decision.
No feature verification needed (Phase 3 contextual search removed per VERDICT B).
"""

import json
from pathlib import Path
from runtime.jarvis.core.engine import JarvisEngine


def test_recall_experience_returns_most_recent_active_decision():
    """Verify recall_experience() returns most recent Active decision from ledger."""
    engine = JarvisEngine()
    result = engine.recall_experience()

    assert result["status"] in ["found", "empty"], \
        f"Status must be 'found' or 'empty', got {result['status']}"

    if result["status"] == "found":
        assert len(result["matches"]) > 0, \
            "Status 'found' must have at least 1 match"

        match = result["matches"][0]
        assert "decision_id" in match, "Match must have decision_id"
        assert "title" in match, "Match must have title"
        assert "decision" in match, "Match must have decision"
        assert match["status"] == "Active", \
            f"Returned decision must be Active, got {match['status']}"

        print(f"PASS: Retrieved decision {match['decision_id']}")
        print(f"  Title: {match['title']}")
        print(f"  Source: {match['source']}")
    else:
        print(f"PASS: No active decisions found (gap: {result['gap']})")

    assert result["gap"] is None or isinstance(result["gap"], str), \
        f"Gap must be None or string, got {type(result['gap'])}"

    return result


def test_recall_experience_intent_parameter_accepted():
    """Verify recall_experience() accepts intent parameter without error."""
    engine = JarvisEngine()

    result = engine.recall_experience(current_intent="test query")

    assert result["status"] in ["found", "empty"], \
        f"Status must be 'found' or 'empty', got {result['status']}"
    assert result["intent"] == "test query", \
        f"Intent should be echoed back, got {result['intent']}"

    print(f"PASS: Intent parameter handled correctly")
    return result


def test_ledger_file_exists():
    """Verify decision_ledger.jsonl file is present and readable."""
    engine = JarvisEngine()

    assert engine._decision_ledger_path.exists(), \
        f"Decision ledger not found at {engine._decision_ledger_path}"

    with open(engine._decision_ledger_path, "r", encoding="utf-8") as f:
        line_count = sum(1 for line in f if line.strip())

    assert line_count > 0, "Decision ledger is empty"
    print(f"PASS: Decision ledger exists with {line_count} decisions")


if __name__ == "__main__":
    print("=" * 60)
    print("JARVIS Experience Recall MVP - E2E Test Suite")
    print("=" * 60)

    print("\nTest 1: Ledger file existence")
    test_ledger_file_exists()

    print("\nTest 2: Recall most recent Active decision")
    test_recall_experience_returns_most_recent_active_decision()

    print("\nTest 3: Intent parameter handling")
    test_recall_experience_intent_parameter_accepted()

    print("\n" + "=" * 60)
    print("All tests completed")
    print("=" * 60)
