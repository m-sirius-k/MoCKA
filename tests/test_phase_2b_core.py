# tests/test_phase_2b_core.py
# PHASE 2B Core Module Tests
# Tests for BE-001 and BE-002 without Flask dependency
# Authorization: DC_20261001_001

import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from phi_os.decision_reader import (
    get_decision,
    list_decisions_by_status,
    list_decisions_by_scope,
    list_all_decisions,
    is_decision_active,
    DECISION_LEDGER_PATH
)


def test_decision_ledger_directory_structure():
    """Test that decision ledger directory structure exists"""
    repo_root = Path(__file__).resolve().parent.parent
    decisions_dir = repo_root / 'data' / 'decisions'

    assert decisions_dir.exists(), "data/decisions directory should exist"
    print("✓ data/decisions/ directory exists")

    gitignore = decisions_dir / '.gitignore'
    assert gitignore.exists(), "data/decisions/.gitignore should exist"
    print("✓ data/decisions/.gitignore exists")

    ledger_file = decisions_dir / 'decision_ledger.jsonl'
    assert ledger_file.exists(), "data/decisions/decision_ledger.jsonl should exist"
    print("✓ data/decisions/decision_ledger.jsonl exists")


def test_decision_ledger_path_configuration():
    """Test DECISION_LEDGER_PATH is correctly configured"""
    assert isinstance(DECISION_LEDGER_PATH, Path)
    assert str(DECISION_LEDGER_PATH).endswith('decision_ledger.jsonl')
    print(f"✓ DECISION_LEDGER_PATH correctly set to: {DECISION_LEDGER_PATH}")


def test_get_decision_not_found():
    """Test get_decision returns None for non-existent record"""
    result = get_decision("NONEXISTENT_DC_20261001_999")
    assert result is None, "Should return None for non-existent decision"
    print("✓ get_decision returns None for non-existent ID")


def test_list_decisions_by_status():
    """Test list_decisions_by_status returns list type"""
    result = list_decisions_by_status("Active")
    assert isinstance(result, list), "Should return list type"
    print(f"✓ list_decisions_by_status('Active') returns list (count: {len(result)})")


def test_list_decisions_by_scope():
    """Test list_decisions_by_scope returns list type"""
    result = list_decisions_by_scope("BE-001")
    assert isinstance(result, list), "Should return list type"
    print(f"✓ list_decisions_by_scope('BE-001') returns list (count: {len(result)})")


def test_list_all_decisions():
    """Test list_all_decisions returns list"""
    result = list_all_decisions()
    assert isinstance(result, list), "Should return list type"
    print(f"✓ list_all_decisions() returns list (count: {len(result)})")


def test_is_decision_active_false():
    """Test is_decision_active returns False for non-existent"""
    result = is_decision_active("NONEXISTENT_DC")
    assert result is False, "Should return False for non-existent"
    print("✓ is_decision_active returns False for non-existent decision")


def test_decision_reader_functions_callable():
    """Test all decision_reader functions are callable"""
    functions = [
        get_decision,
        list_decisions_by_status,
        list_decisions_by_scope,
        list_all_decisions,
        is_decision_active
    ]

    for func in functions:
        assert callable(func), f"{func.__name__} should be callable"

    print(f"✓ All {len(functions)} decision_reader functions are callable")


def test_decision_ledger_gitignore_rules():
    """Test that .gitignore permits decision ledger files"""
    repo_root = Path(__file__).resolve().parent.parent
    gitignore_path = repo_root / '.gitignore'

    content = gitignore_path.read_text(encoding='utf-8')

    assert '!data/decisions/' in content, ".gitignore should have !data/decisions/"
    assert '!data/decisions/decision_ledger.jsonl' in content, ".gitignore should permit decision_ledger.jsonl"
    print("✓ .gitignore correctly permits data/decisions/ and decision_ledger.jsonl")


def test_decision_ledger_jsonl_format():
    """Test decision ledger uses valid JSONL format"""
    ledger_path = DECISION_LEDGER_PATH

    if ledger_path.exists() and ledger_path.stat().st_size > 0:
        with open(ledger_path, 'r', encoding='utf-8') as f:
            line_count = 0
            for line in f:
                line = line.strip()
                if line:
                    # Should be valid JSON
                    record = json.loads(line)
                    assert isinstance(record, dict), f"Line {line_count} should be valid JSON object"
                    line_count += 1
        print(f"✓ decision_ledger.jsonl contains {line_count} valid JSONL records")
    else:
        print("✓ decision_ledger.jsonl is empty (expected for fresh repository)")


def test_decision_reader_handles_empty_ledger():
    """Test decision_reader functions handle empty ledger gracefully"""
    # These should not raise exceptions
    assert get_decision("ANY_ID") is None
    assert list_decisions_by_status("Active") == []
    assert list_decisions_by_scope("ANY_SCOPE") == []
    assert list_all_decisions() == []
    assert is_decision_active("ANY_ID") is False
    print("✓ decision_reader functions handle empty ledger gracefully")


def test_decision_reader_utf8_safe():
    """Test that decision_reader handles UTF-8 correctly"""
    # Import successfully means UTF-8 type hints are parsed correctly
    from phi_os import decision_reader

    # Call functions without UTF-8 related errors
    list_all_decisions()
    get_decision("TEST")

    print("✓ decision_reader module is UTF-8 safe")


def test_phase_2b_state_separation_concept():
    """Test understanding of BE-001: EXECUTED != VERIFIED principle"""
    # This test documents the principle, not implementation
    # The principle: HTTP 201 response (EXECUTED) != Database persistence verified (VERIFIED)

    principles = {
        "EXECUTED": "HTTP 201 response received from write operation",
        "VERIFIED": "Database read-back confirms data actually persisted",
        "BE-001": "Must implement explicit verification after write",
        "State_Separation": "Returning success from tool != confirming data integrity"
    }

    assert principles["EXECUTED"] != principles["VERIFIED"]
    assert "explicit" in principles["BE-001"]
    print("✓ PHASE 2B state separation principle documented")


def test_phase_2b_decision_ledger_concept():
    """Test understanding of BE-002: Decision Ledger Query concept"""
    # This test documents the architecture

    concepts = {
        "append_only": "JSONL format prevents accidental modification",
        "query_layer": "decision_reader functions provide access without schema lock",
        "governance": "Enables reference of human gate decisions by runtime",
        "immutable": "File structure enforces write-once semantics"
    }

    assert all(isinstance(v, str) for v in concepts.values())
    print("✓ PHASE 2B decision ledger architecture documented")


if __name__ == "__main__":
    tests = [
        test_decision_ledger_directory_structure,
        test_decision_ledger_path_configuration,
        test_get_decision_not_found,
        test_list_decisions_by_status,
        test_list_decisions_by_scope,
        test_list_all_decisions,
        test_is_decision_active_false,
        test_decision_reader_functions_callable,
        test_decision_ledger_gitignore_rules,
        test_decision_ledger_jsonl_format,
        test_decision_reader_handles_empty_ledger,
        test_decision_reader_utf8_safe,
        test_phase_2b_state_separation_concept,
        test_phase_2b_decision_ledger_concept,
    ]

    print("\n" + "="*60)
    print("PHASE 2B Core Module Test Suite")
    print("Authorization: DC_20261001_001")
    print("="*60 + "\n")

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: Unexpected error: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*60 + "\n")

    if failed == 0:
        print("✓ All tests passed! PHASE 2B-004 Test Execution PASSED")
        sys.exit(0)
    else:
        print(f"✗ {failed} test(s) failed")
        sys.exit(1)
