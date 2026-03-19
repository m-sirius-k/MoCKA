import json
import os

GOAL_FILE = "civilization_goal_state.json"
PLAN_FILE = "civilization_plan.json"

def load_goal():
    if not os.path.exists(GOAL_FILE):
        return None
    with open(GOAL_FILE,"r") as f:
        return json.load(f)

def build_plan(goal):

    g = goal.get("goal","none")

    if g == "increase_stability":
        action = "prioritize_repair"

    elif g == "improve_strategies":
        action = "increase_mutation"

    else:
        action = "optimize_runtime"

    return {
        "goal":g,
        "action":action
    }

def run():

    goal = load_goal()

    if not goal:
        print("NO_GOAL")
        return

    plan = build_plan(goal)

    with open(PLAN_FILE,"w") as f:
        json.dump(plan,f,indent=2)

    print("CIVILIZATION_PLAN_UPDATED")
    print("action:",plan["action"])

if __name__ == "__main__":
    run()
