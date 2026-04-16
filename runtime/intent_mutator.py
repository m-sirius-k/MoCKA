# FILE: runtime\intent_mutator.py

import json
import os
import random
from datetime import datetime

MEM_PATH = os.path.join("runtime", "intent_memory.json")

GOAL_POOL = [
    "prevent_incident",
    "explore",
    "optimize_execution",
    "increase_knowledge"
]

def load():
    with open(MEM_PATH, encoding="utf-8-sig") as f:
        return json.load(f)

def save(mem):
    with open(MEM_PATH, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

def mutate():

    mem = load()

    new_goal = random.choice(GOAL_POOL)

    intent = {
        "goal": new_goal,
        "ts": datetime.now().isoformat(),
        "mutation": True
    }

    mem["history"].append(intent)
    save(mem)

    print("MUTATED:", intent)

if __name__ == "__main__":
    mutate()
