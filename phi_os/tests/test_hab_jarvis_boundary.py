import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_actor_model():
    path = ROOT / "phi_os" / "hab" / "actor_model.json"

    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def get_decision_ledger():
    return ROOT / "data" / "decisions" / "decision_ledger.jsonl"


def test_jarvis_is_proposal_only():
    model = load_actor_model()

    jarvis = model["actors"]["jarvis"]

    assert jarvis["authority"] == "advisory"


def test_jarvis_cannot_finalize():
    model = load_actor_model()

    jarvis = model["actors"]["jarvis"]

    assert jarvis["can_finalize"] is False


def test_jarvis_is_not_decision_actor():
    model = load_actor_model()

    jarvis = model["actors"]["jarvis"]

    assert jarvis["authority"] != "decision"


def test_ledger_exists_as_external_decision_record():
    ledger = get_decision_ledger()

    assert ledger.exists()