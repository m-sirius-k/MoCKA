import json
import os

LEDGER_PATH = "runtime/ledger.json"
ARCHIVE_DIR = "runtime/dsl_archive"

TOP_N = 2

def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def main():
    if not os.path.exists(LEDGER_PATH):
        print("NO LEDGER")
        return

    ledger = load_json(LEDGER_PATH)

    scores = {}
    dsl_map = {}

    for ev in ledger:
        exp = ev.get("experiment_id")
        if not exp:
            continue

        if exp not in scores:
            scores[exp] = {"score":0, "div":set()}

        if ev.get("type") == "ACTION":
            scores[exp]["score"] += ev.get("weight", 0)
            scores[exp]["div"].add(ev.get("action"))

        if ev.get("type") == "DSL_APPLY":
            path = ev.get("dsl_path")
            if path:
                dsl_map[exp] = path

    ranking = []
    for exp, data in scores.items():
        final = data["score"] + len(data["div"])*5
        if exp in dsl_map:
            ranking.append((exp, final))

    ranking.sort(key=lambda x: x[1], reverse=True)

    keep = set([x[0] for x in ranking[:TOP_N]])

    print("KEEP:", keep)

    for exp, path in dsl_map.items():
        if exp not in keep and os.path.exists(path):
            os.remove(path)
            print("REMOVED:", exp)

if __name__ == "__main__":
    main()
