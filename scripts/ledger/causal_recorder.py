import json
import os
from collections import defaultdict

LEDGER_PATH = "runtime/ledger.json"
CAUSAL_PATH = "runtime/causal_graph.json"

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    ledger = load_json(LEDGER_PATH)
    causal = defaultdict(int)

    prev_actions = None

    for ev in ledger:
        if ev.get("type") != "ACTION_SET":
            continue

        actions = ev.get("actions", [])

        if prev_actions:
            for a in prev_actions:
                for b in actions:
                    key = a + "->" + b
                    causal[key] += 1

        prev_actions = actions

    save_json(CAUSAL_PATH, dict(causal))

    print("CAUSAL GRAPH UPDATED")

if __name__ == "__main__":
    main()
