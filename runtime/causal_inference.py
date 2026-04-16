import json
import time
import os

LEDGER_PATH = "ledger.json"
CAUSAL_PATH = "causal_graph.json"

def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def normalize(x):
    return str(x).lower().strip()

def main():
    print("=== CAUSAL INFERENCE START ===")

    while True:
        if not os.path.exists(LEDGER_PATH):
            time.sleep(5)
            continue

        ledger = load_json(LEDGER_PATH)

        if not os.path.exists(CAUSAL_PATH):
            causal = {"causal_edges": {}}
        else:
            causal = load_json(CAUSAL_PATH)

        updated = False

        # 連続イベントから因果抽出
        for i in range(len(ledger) - 1):
            current = ledger[i]
            nxt = ledger[i + 1]

            cause = normalize(current.get("selected", ""))
            effect = normalize(nxt.get("selected", ""))

            if not cause or not effect:
                continue

            key = cause + "->" + effect

            if key not in causal["causal_edges"]:
                causal["causal_edges"][key] = {"count": 0}

            causal["causal_edges"][key]["count"] += 1
            updated = True

        if updated:
            save_json(CAUSAL_PATH, causal)
            print("CAUSAL UPDATED:", len(causal["causal_edges"]))

        time.sleep(5)

if __name__ == "__main__":
    main()
