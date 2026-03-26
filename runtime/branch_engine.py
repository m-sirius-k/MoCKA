import json
from collections import defaultdict

STATE_PATH = "runtime/state/state.json"
OUTPUT_PATH = "runtime/state/branches.json"

def load_state():
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_branches(state):
    priorities = state.get("action_priority", [])
    branches = defaultdict(list)

    for item in priorities:
        key, score = item
        action, context = key.split("::")

        branches[context].append({
            "action": action,
            "score": score
        })

    return branches

def save(branches):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(branches, f, indent=2)

if __name__ == "__main__":
    state = load_state()
    branches = build_branches(state)
    save(branches)
    print("BRANCHES BUILT")
