import json
import os
import math

LEDGER_PATH = "runtime/ledger.json"

def main():
    with open(LEDGER_PATH, "r", encoding="utf-8-sig") as f:
        ledger = json.load(f)

    experiments = {}

    for ev in ledger:
        exp = ev.get("experiment_id", "LEGACY")

        if exp not in experiments:
            experiments[exp] = {
                "score": 0,
                "diversity": set()
            }

        if ev.get("type") == "ACTION_SET":
            actions = ev.get("actions", [])
            w = ev.get("weight", 0)

            experiments[exp]["score"] += w
            for a in actions:
                experiments[exp]["diversity"].add(a)

    print("=== EXPERIMENT EVALUATION ===")

    for exp, data in experiments.items():
        score = data["score"]
        diversity = len(data["diversity"])

        if diversity == 0:
            continue

        final = math.sqrt(score) * (diversity ** 2)

        if exp == "LEGACY":
            final *= 0.1

        print(f"EXP {exp} | total={score} diversity={diversity} final={round(final,2)}")

if __name__ == "__main__":
    main()
