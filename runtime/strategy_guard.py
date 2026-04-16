import json

INPUT_PATH = "runtime/state/strategy.json"
OUTPUT_PATH = "runtime/state/strategy_lock.json"

THRESHOLD = 0.6

def load():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_lock(data):
    locked = {}

    for ctx, info in data.items():
        if info["confidence"] >= THRESHOLD:
            locked[ctx] = {
                "action": info["dominant_action"],
                "locked": True
            }
        else:
            locked[ctx] = {
                "action": info["dominant_action"],
                "locked": False
            }

    return locked

def save(data):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    data = load()
    result = evaluate_lock(data)
    save(result)
    print("STRATEGY LOCK EVALUATED")
