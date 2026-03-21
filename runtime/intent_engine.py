# FILE: runtime\intent_engine.py

import json
import os
import csv
from datetime import datetime

CSV_PATH = os.path.join("runtime", "index", "event_timeline.csv")
MEM_PATH = os.path.join("runtime", "intent_memory.json")

def load_state():
    incidents = 0
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["type"] == "incident" and r["status"] == "active":
                incidents += 1
    return incidents

def load_memory():
    # ★ 修正ポイント
    with open(MEM_PATH, encoding="utf-8-sig") as f:
        return json.load(f)

def save_memory(mem):
    with open(MEM_PATH, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

def generate_intent():

    incidents = load_state()
    mem = load_memory()

    if incidents > 0:
        goal = "prevent_incident"
    else:
        goal = "explore"

    intent = {
        "goal": goal,
        "ts": datetime.now().isoformat()
    }

    mem["history"].append(intent)
    save_memory(mem)

    return intent


if __name__ == "__main__":
    print(generate_intent())
