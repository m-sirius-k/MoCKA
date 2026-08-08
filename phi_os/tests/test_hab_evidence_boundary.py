import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def get_decision_ledger():
    return ROOT / "data" / "decisions" / "decision_ledger.jsonl"


def load_actor_model():
    path = ROOT / "phi_os" / "hab" / "actor_model.json"

    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_first_decision_record():
    ledger = get_decision_ledger()

    with open(ledger, "r", encoding="utf-8") as f:
        return json.loads(f.readline())


def test_decision_ledger_exists():
    ledger = get_decision_ledger()

    assert ledger.exists()


def test_decision_ledger_has_records():
    ledger = get_decision_ledger()

    with open(ledger, "r", encoding="utf-8") as f:
        first_line = f.readline()

    assert first_line.strip() != ""


def test_decision_ledger_contains_timestamp():
    record = load_first_decision_record()

    assert (
        "timestamp" in record
        or "created_at" in record
        or "approved_at" in record
    )


def test_jarvis_cannot_make_decision():
    model = load_actor_model()

    jarvis = model["actors"]["jarvis"]

    assert jarvis["authority"] != "decision"
    assert jarvis["can_finalize"] is False
