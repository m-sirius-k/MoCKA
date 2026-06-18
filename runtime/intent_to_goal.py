import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json
import os

INPUT_PATH = "input.json"
GOAL_PATH = "goal.json"

def apply_intent_to_goal():
    if not os.path.exists(INPUT_PATH):
        return

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    intent = data.get("intent")
    if not intent:
        return

    new_goal = {
        "target": intent["goal"],
        "source": "intent",
        "intent_id": intent["intent_id"]
    }

    with open(GOAL_PATH, "w", encoding="utf-8") as f:
        json.dump(new_goal, f, ensure_ascii=False, indent=2)

    print("GOAL UPDATED FROM INTENT")
