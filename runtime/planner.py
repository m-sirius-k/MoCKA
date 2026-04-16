import json
import time
import os

STATE_PATH = "state.json"
PLAN_PATH = "plan.json"

def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def analyze_state(state):
    scores = {}
    for k, v in state.items():
        if v["count"] > 0:
            scores[k] = v["score"] / v["count"]
        else:
            scores[k] = 0
    return scores

def generate_plan(scores):
    sorted_actions = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    plan = []
    for action, score in sorted_actions:
        plan.append({
            "action": action,
            "priority": score
        })

    return plan

def main():
    print("=== PLANNER START ===")

    while True:
        if not os.path.exists(STATE_PATH):
            time.sleep(5)
            continue

        state = load_json(STATE_PATH)
        scores = analyze_state(state)

        plan = generate_plan(scores)

        save_json(PLAN_PATH, {"plan": plan})

        print("PLAN UPDATED:", plan)

        time.sleep(10)

if __name__ == "__main__":
    main()
