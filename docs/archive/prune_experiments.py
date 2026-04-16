import json
import os

LEDGER_PATH = "runtime/ledger.json"
ARCHIVE_DIR = "runtime/dsl_archive"

THRESHOLD = 10  # これ未満は削除

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

    print("=== PRUNE START ===")

    for exp, score in scores.items():
        path = dsl_map.get(exp)

        if not path:
            continue

        if score < THRESHOLD and os.path.exists(path):
            os.remove(path)
            print(f"DELETED: {exp} score={score}")
        else:
            print(f"KEEP: {exp} score={score}")

if __name__ == "__main__":
    main()
