import json
from collections import defaultdict

STATE_PATH = "runtime/state/state.json"
OUTPUT_PATH = "runtime/state/contexts.json"

def load_state():
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def split_contexts(state):
    evaluations = state.get("evaluations", [])
    contexts = defaultdict(list)

    for ev in evaluations:
        ctx = ev.get("context", "default")
        action = ev.get("action")

        contexts[ctx].append(action)

    return contexts

def save(data):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    state = load_state()
    ctxs = split_contexts(state)
    save(ctxs)
    print("CONTEXTS DERIVED")
