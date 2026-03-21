import os
import json
import random

BRANCH_DIR = "runtime/branches"

TECH_FIELDS = [
    "agriculture",
    "industry",
    "energy_tech",
    "military",
    "science"
]


def list_branches():
    branches = []
    for d in os.listdir(BRANCH_DIR):
        path = os.path.join(BRANCH_DIR, d)
        if os.path.isdir(path):
            branches.append(d)
    return branches


def load_state(branch):
    path = os.path.join(BRANCH_DIR, branch, "world_state.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(branch, state):
    path = os.path.join(BRANCH_DIR, branch, "world_state.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def ensure_tree(state):

    if "tech_tree" not in state:

        state["tech_tree"] = {
            "agriculture":0,
            "industry":0,
            "energy_tech":0,
            "military":0,
            "science":0
        }

    return state


def evolve_tree(state):

    tech = state["technology"]

    if tech < 10:
        return state

    branch = random.choice(TECH_FIELDS)

    state["tech_tree"][branch] += 1

    if branch == "agriculture":
        state["population"] += 2

    if branch == "industry":
        state["economy"] += 5

    if branch == "energy_tech":
        state["energy"] += 5

    if branch == "military":
        state["conflict"] += 3

    if branch == "science":
        state["technology"] += 2

    return state


if __name__ == "__main__":

    branches = list_branches()

    for b in branches:

        state = load_state(b)

        state = ensure_tree(state)

        state = evolve_tree(state)

        save_state(b, state)

        print("TECH TREE EVOLVE →", b)
