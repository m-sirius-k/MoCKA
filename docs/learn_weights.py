import json
import os

LEDGER_PATH = "runtime/ledger.json"
DSL_PATH = "runtime/dsl/multi_context.json"

DECAY = 0.9
BOOST = 2  # 探索成功強化

def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def main():
    if not os.path.exists(LEDGER_PATH) or not os.path.exists(DSL_PATH):
        print("MISSING FILE")
        return

    ledger = load_json(LEDGER_PATH)
    dsl = load_json(DSL_PATH)

    counts = {}

    for ev in ledger:
        if ev.get("type") == "ACTION":
            key = (ev.get("context"), ev.get("action"))
            base = counts.get(key, 0)

            if ev.get("mode") == "EXPLORE":
                counts[key] = base + BOOST
            else:
                counts[key] = base + 1

    for ctx in dsl.get("contexts", []):
        name = ctx.get("name")

        for edge in ctx.get("edges", []):
            key = (name, edge.get("to"))
            freq = counts.get(key, 0)

            base = edge.get("weight", 1) * DECAY
            edge["weight"] = max(1, int(base + freq))

    with open(DSL_PATH, "w", encoding="utf-8") as f:
        json.dump(dsl, f, indent=2)

    print("LEARNED (EXPLORE BOOST)")

if __name__ == "__main__":
    main()
