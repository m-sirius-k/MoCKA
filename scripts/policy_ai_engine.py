import json
import os
import random

BRANCH_DIR = "runtime/branches"

EVENTS = {
"build_factory":{"economy":10,"energy":-5},
"population_growth":{"population":5,"economy":2},
"technology_breakthrough":{"technology":8,"economy":3},
"energy_investment":{"energy":8,"economy":-3},
"peace_policy":{"conflict":-5},
"military_conflict":{"conflict":6,"population":-3}
}

def list_branches():
    return [
        d for d in os.listdir(BRANCH_DIR)
        if os.path.isdir(os.path.join(BRANCH_DIR,d))
    ]

def load_state(branch):
    path = os.path.join(BRANCH_DIR,branch,"world_state.json")
    with open(path,"r",encoding="utf-8") as f:
        return json.load(f)

def save_state(branch,state):
    path = os.path.join(BRANCH_DIR,branch,"world_state.json")
    with open(path,"w",encoding="utf-8") as f:
        json.dump(state,f,indent=2)

def choose_policy(state):

    if state["energy"] < 10:
        return "energy_investment"

    if state["conflict"] > 40:
        return "peace_policy"

    if state["technology"] < 30:
        return "technology_breakthrough"

    return random.choice(list(EVENTS.keys()))

def apply_event(state,event):

    impact = EVENTS[event]

    for k,v in impact.items():
        state[k] += v
        if state[k] < 0:
            state[k] = 0

    return state

if __name__ == "__main__":

    branches = list_branches()

    for b in branches:

        state = load_state(b)

        policy = choose_policy(state)

        new_state = apply_event(state,policy)

        save_state(b,new_state)

        print("AI POLICY",policy,"→",b)
