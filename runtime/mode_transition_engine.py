import json

STRATEGY_PATH = "runtime/state/strategy.json"
MODE_PATH = "runtime/state/decision_mode.json"

THRESHOLD = 0.6

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def update_mode(strategy, mode_data):
    for ctx, info in strategy.items():
        confidence = info["confidence"]
        action = info["dominant_action"]

        if confidence >= THRESHOLD:
            mode_data[ctx] = {
                "action": action,
                "mode": "EXECUTE"
            }
        else:
            mode_data[ctx] = {
                "action": action,
                "mode": "EXPLORE"
            }

    return mode_data

if __name__ == "__main__":
    strategy = load(STRATEGY_PATH)
    mode_data = load(MODE_PATH)

    updated = update_mode(strategy, mode_data)

    save(MODE_PATH, updated)

    print("MODE TRANSITION UPDATED")
