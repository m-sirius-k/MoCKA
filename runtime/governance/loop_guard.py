import os
import json

STATE_PATH = "runtime/state/loop_guard.json"
THRESHOLD = 3

def load_state():
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def check_loop(incident_id):
    state = load_state()

    count = state.get(incident_id, 0) + 1
    state[incident_id] = count

    save_state(state)

    if count > THRESHOLD:
        return {
            "status": "escalation",
            "count": count
        }

    return {
        "status": "ok",
        "count": count
    }

if __name__ == "__main__":
    test_id = "INC_TEST"

    for i in range(5):
        result = check_loop(test_id)
        print(result)
