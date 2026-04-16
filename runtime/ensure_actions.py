import json
import os
import random

STATE_PATH = "runtime/state.json"

DEFAULT_ACTIONS = [
    "ANALYZE","FIX","RETRY","EXPLORE",
    "SAFE_MODE","RUN_FAST","DIAGNOSE","OPTIMIZE"
]

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        print("STATE BROKEN → RESET")
        return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    state = load_json(STATE_PATH)

    actions = state.get("actions", [])

    if not actions:
        actions = random.sample(DEFAULT_ACTIONS, k=3)
        state["actions"] = actions
        state["weights"] = [1.0]*len(actions)

    save_json(STATE_PATH, state)

    print("ACTIONS READY:", actions)

if __name__ == "__main__":
    main()
