import json

STATE_PATH = "runtime/state/state.json"
MUTATION_PATH = "runtime/state/mutations.json"

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def filter_mutations(state, mutations):
    if not mutations:
        return []

    priorities = state.get("action_priority", [])

    valid = []

    for m in mutations:
        key = f"{m['new_action']}::{m['context']}"

        for p in priorities:
            if p[0] == key and p[1] > 0:
                valid.append(m)

    return valid

if __name__ == "__main__":
    state = load_json(STATE_PATH)
    mutations = load_json(MUTATION_PATH)

    filtered = filter_mutations(state, mutations)

    save_json(MUTATION_PATH, filtered)

    print("MUTATION FILTERED")
