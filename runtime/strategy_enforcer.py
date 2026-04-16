import json

INPUT_PATH = "runtime/state/context_stats.json"
OUTPUT_PATH = "runtime/state/strategy.json"

def load():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_strategy(data):
    strategy = {}

    for ctx, actions in data.items():
        best = actions[0]  # 最上位
        strategy[ctx] = {
            "dominant_action": best["action"],
            "confidence": best["ratio"]
        }

    return strategy

def save(data):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    data = load()
    strategy = build_strategy(data)
    save(strategy)
    print("STRATEGY BUILT")
