import json
import os
import subprocess

LEDGER_PATH = "runtime/ledger.json"
DSL_PATH = "runtime/dsl/multi_context.json"

def main():
    if not os.path.exists(LEDGER_PATH):
        print("NO LEDGER")
        return

    with open(LEDGER_PATH, "r", encoding="utf-8-sig") as f:
        ledger = json.load(f)

    scores = {}
    dsl_map = {}

    for ev in ledger:
        exp = ev.get("experiment_id")

        if not exp:
            continue

        if exp not in scores:
            scores[exp] = 0

        if ev.get("type") == "ACTION":
            scores[exp] += ev.get("weight", 0)

        if ev.get("type") == "DSL_APPLY":
            path = ev.get("dsl_path")
            if path:
                dsl_map[exp] = path

    valid_exps = [e for e in scores if e in dsl_map and dsl_map[e]]

    if not valid_exps:
        print("NO VALID EXP WITH DSL")
        return

    best = max(valid_exps, key=lambda x: scores[x])

    print("BEST EXP:", best, "score=", scores[best])

    dsl_path = dsl_map[best]

    if not os.path.exists(dsl_path):
        print("DSL FILE MISSING:", dsl_path)
        return

    with open(dsl_path, "r", encoding="utf-8-sig") as f:
        dsl = json.load(f)

    with open(DSL_PATH, "w", encoding="utf-8") as f:
        json.dump(dsl, f, indent=2)

    print("DSL RESTORED FROM", dsl_path)

    subprocess.run(["python", "apply_dsl.py"])
    subprocess.run(["python", "runtime/action_selector.py"])

if __name__ == "__main__":
    main()
