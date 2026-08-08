import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_actor_model():
    path = ROOT / "phi_os" / "hab" / "actor_model.json"
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def test_hab_actor_identity_exists():
    model = load_actor_model()

    assert "actors" in model
    assert "human" in model["actors"]
    assert "jarvis" in model["actors"]


def test_hab_human_has_final_authority():
    model = load_actor_model()

    human = model["actors"]["human"]

    assert human["authority"] == "decision"
    assert human["can_finalize"] is True


def test_hab_jarvis_boundary():
    model = load_actor_model()

    jarvis = model["actors"]["jarvis"]

    assert jarvis["authority"] == "advisory"
    assert jarvis["can_finalize"] is False


def test_hab_system_is_execution_only():
    model = load_actor_model()

    system = model["actors"]["system"]

    assert system["authority"] == "execution"
