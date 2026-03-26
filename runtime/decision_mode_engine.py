import json

LOCK_PATH = "runtime/state/strategy_lock.json"
OUTPUT_PATH = "runtime/state/decision_mode.json"

def load():
    with open(LOCK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def decide_mode(data):
    result = {}

    for ctx, info in data.items():
        if info["locked"]:
            mode = "EXECUTE"
        else:
            mode = "EXPLORE"

        result[ctx] = {
            "action": info["action"],
            "mode": mode
        }

    return result

def save(data):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    data = load()
    result = decide_mode(data)
    save(result)
    print("DECISION MODE SET")
