import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def get_decision_ledger():
    return ROOT / "data" / "decisions" / "decision_ledger.jsonl"


def load_first_decision_record():
    ledger = get_decision_ledger()

    with open(ledger, "r", encoding="utf-8") as f:
        return json.loads(f.readline())


def test_state_transition_record_exists():
    ledger = get_decision_ledger()

    assert ledger.exists()


def test_previous_state_exists():
    record = load_first_decision_record()

    assert (
        "previous_state" in record
        or "from_state" in record
        or "current_state" in record
        or "context" in record
    )


def test_next_state_exists():
    record = load_first_decision_record()

    assert (
        "next_state" in record
        or "to_state" in record
        or "result_state" in record
        or "decision" in record
    )


def test_transition_has_evidence_reference():
    record = load_first_decision_record()

    assert (
        "evidence" in record
        or "evidence_ref" in record
        or "context" in record
    )