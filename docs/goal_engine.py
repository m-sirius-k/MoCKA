import json
import os

GOAL_PATH = "runtime/goal.json"

def save(goal):
    with open(GOAL_PATH,"w",encoding="utf-8") as f:
        json.dump(goal,f,indent=2)

def main():
    # ★ 仮の長期目標
    goal = {
        "target": "reduce_error",
        "weight": 1.0
    }

    save(goal)

    print("GOAL SET:", goal)

if __name__=="__main__":
    main()
