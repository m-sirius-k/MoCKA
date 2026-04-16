import json
import os
import random
import math
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))
from dsl_loader import load_dsl

STATE_PATH = "runtime/state.json"
CAUSAL_PATH = "runtime/causal_graph.json"
POLICY_PATH = "runtime/policy.json"
GOAL_PATH = "runtime/goal.json"

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path,"r",encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return default

def build_causal_map(graph):
    m = {}
    for k,v in graph.items():
        try:
            a,b = k.split("->")
            m[(a,b)] = v
        except:
            continue
    return m

def softmax(w):
    if not w:
        return []
    m = max(w)
    exps = [math.exp(x-m) for x in w]
    s = sum(exps)
    return [e/s for e in exps]

def cost(action):
    table = {
        "ANALYZE": 3,
        "EXPLORE": 2,
        "RUN_FAST": 1,
        "SAFE_MODE": 2,
        "OPTIMIZE": 3
    }
    return table.get(action,1)

def goal_bonus(action, goal):
    target = goal.get("target")

    if target == "reduce_error":
        return 10 if action == "ANALYZE" else 0

    if target == "increase_speed":
        return 10 if action == "RUN_FAST" else 0

    if target == "increase_diversity":
        return 10 if action == "EXPLORE" else 0

    if target == "stabilize_system":
        return 10 if action == "SAFE_MODE" else 0

    return 0

def main():
    state = load_json(STATE_PATH,{})
    causal = load_json(CAUSAL_PATH,{})
    policy = load_json(POLICY_PATH,{})
    goal = load_json(GOAL_PATH,{})
    dsl = load_dsl()

    actions = state.get("actions",[])
    prev = state.get("last_actions",[])
    sys_state = state.get("system_state",{})

    error_level = sys_state.get("error_level",0)
    load = sys_state.get("load",0)

    if not actions:
        return

    epsilon = min(0.8, 0.1 + error_level*0.2)

    if random.random() < epsilon:
        choice = random.choice(actions)
        print("ADAPTIVE EXPLORE:", choice)
    else:
        causal_map = build_causal_map(causal)

        weights = []

        for act in actions:
            c_score = sum(causal_map.get((p,act),0) for p in prev)
            d_score = sum(d.get("score",1.0) for d in dsl if d.get("action")==act)
            p_score = policy.get(act,0)

            g_score = goal_bonus(act, goal)

            penalty = cost(act) * load

            weights.append(c_score + d_score + p_score + g_score - penalty)

        probs = softmax(weights)
        choice = random.choices(actions,probs)[0]

        print("GOAL-DOMINANT:", choice)

    state["last_actions"] = [choice]

    with open(STATE_PATH,"w",encoding="utf-8") as f:
        json.dump(state,f,indent=2)

    print("SELECTED FINAL:", choice)

if __name__=="__main__":
    main()
