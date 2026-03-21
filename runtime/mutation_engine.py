import json
import random
from datetime import datetime

HISTORY_PATH = "runtime/intent_history.json"

MUTATIONS = [
    "optimize_execution",
    "explore_strategy",
    "reduce_latency",
    "improve_accuracy",
    "stabilize_system"
]

def load():
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save(data):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    history = load()

    new_goal = random.choice(MUTATIONS)

    new_item = {
        "goal": new_goal,
        "score": 0,
        "ts": datetime.now().isoformat(),
        "result": "pending",
        "mutation": True
    }

    history.append(new_item)
    save(history)

    print("MUTATION ADDED:", new_goal)

if __name__ == "__main__":
    main()
