from incident_engine import record_event
import json
import os

STATE_FILE = "runtime/mocka_phase_state.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"phase": "Phase18"}
    with open(STATE_FILE,"r",encoding="utf8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE,"w",encoding="utf8") as f:
        json.dump(state,f)


def set_phase(new_phase):

    state = load_state()
    old_phase = state["phase"]

    if old_phase != new_phase:

        record_event(
        event_type="phase_shift",
        actor="system",
        title=f"Phase change {old_phase} → {new_phase}",
        content="MoCKA phase transition",
        source="phase_event_engine",
        phase=new_phase,
        focus_point="system evolution stage change",
        incident_candidate=False
        )

        state["phase"] = new_phase
        save_state(state)

        print("PHASE UPDATED:",new_phase)

    else:
        print("PHASE UNCHANGED")


if __name__ == "__main__":

    set_phase("Phase18")
