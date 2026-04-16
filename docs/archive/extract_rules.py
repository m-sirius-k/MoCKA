import json
import os

LEDGER_PATH = "runtime/ledger.json"
RULES_PATH = "runtime/memory_rules.json"

THRESHOLD = 50  # 良い実験の基準

def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    if not os.path.exists(LEDGER_PATH):
        print("NO LEDGER")
        return

    ledger = load_json(LEDGER_PATH)

    scores = {}
    actions = {}

    for ev in ledger:
        exp = ev.get("experiment_id")
        if not exp:
            continue

        if exp not in scores:
            scores[exp] = 0
            actions[exp] = []

        if ev.get("type") == "ACTION":
            scores[exp] += ev.get("weight", 0)
            actions[exp].append(ev.get("action"))

    rules = load_json(RULES_PATH)["rules"]

    for exp, score in scores.items():
        if score < THRESHOLD:
            continue

        acts = actions[exp]
        if not acts:
            continue

        rule = {
            "experiment": exp,
            "pattern": list(set(acts)),
            "score": score
        }

        rules.append(rule)

    save_json(RULES_PATH, {"rules": rules})

    print("RULES EXTRACTED")

if __name__ == "__main__":
    main()
