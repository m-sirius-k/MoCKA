import json

STATE_PATH = "runtime/state/state.json"
OUTPUT_PATH = "runtime/state/mutations.json"

def load_state():
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_mutations(state):
    priorities = state.get("action_priority", [])

    mutations = []

    for item in priorities:
        key = item[0]
        score = item[1]

        if score <= 0:
            continue

        action, context = key.split("::")

        # 段階進化
        if "_OPT" in action:
            new_action = action + "2"
        else:
            new_action = action + "_OPT"

        mutations.append({
            "base_action": action,
            "new_action": new_action,
            "context": context,
            "score": score
        })

    return mutations

def save(mutations):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(mutations, f, indent=2)

if __name__ == "__main__":
    state = load_state()
    muts = generate_mutations(state)
    save(muts)
    print("CHAIN MUTATIONS GENERATED")
