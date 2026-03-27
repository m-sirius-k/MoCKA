import json
import os
import random

GOAL_PATH = "runtime/goal.json"

GOAL_TYPES = [
    "reduce_error",
    "increase_speed",
    "increase_diversity",
    "stabilize_system"
]

def save(goal):
    with open(GOAL_PATH,"w",encoding="utf-8") as f:
        json.dump(goal,f,indent=2)

def main():
    goal = {
        "target": random.choice(GOAL_TYPES),
        "weight": 1.0
    }

    save(goal)

    print("GOAL (STATE) EVOLVED:", goal)

if __name__=="__main__":
    main()
