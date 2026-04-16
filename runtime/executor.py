import json
from datetime import datetime

INTENT_PATH = "runtime/selected_intent.json"
HISTORY_PATH = "runtime/intent_history.json"

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def load_history():
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save(history):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def main():
    intent = load_json(INTENT_PATH)
    history = load_history()

    if not intent or "goal" not in intent:
        print("NO INTENT")
        return

    record = {
        "goal": intent["goal"],
        "score": intent.get("score", 0),
        "ts": datetime.now().isoformat(),
        "result": "pending"
    }

    history.append(record)
    save(history)

    print("EXECUTED + HISTORY SAVED")

if __name__ == "__main__":
    main()
