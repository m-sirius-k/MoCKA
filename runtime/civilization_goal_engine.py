import json
import os

DIAG_FILE = "civilization_diagnostics.json"
GOAL_FILE = "civilization_goal_state.json"

def load_diag():

    if not os.path.exists(DIAG_FILE):
        return None

    with open(DIAG_FILE,"r") as f:
        return json.load(f)

def determine_goal(diag):

    stability = diag.get("civilization_stability",0)
    fitness = diag.get("avg_strategy_fitness",0)

    if stability < 0.4:
        goal = "increase_stability"

    elif fitness < 0.5:
        goal = "improve_strategies"

    else:
        goal = "optimize_civilization"

    return goal

def run():

    diag = load_diag()

    if not diag:
        print("NO_DIAGNOSTICS")
        return

    goal = determine_goal(diag)

    result = {
        "goal":goal,
        "stability":diag.get("civilization_stability",0),
        "avg_fitness":diag.get("avg_strategy_fitness",0)
    }

    with open(GOAL_FILE,"w") as f:
        json.dump(result,f,indent=2)

    print("CIVILIZATION_GOAL_UPDATED")
    print("goal:",goal)

if __name__ == "__main__":
    run()
