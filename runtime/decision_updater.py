import json
from collections import defaultdict

STATE_PATH = "runtime/state/state.json"

def load_state():
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def update_priority(state):
    evaluations = state.get("evaluations", [])

    score_map = defaultdict(list)

    for ev in evaluations:
        action = ev.get("action")
        context = ev.get("context", "default")
        key = f"{action}::{context}"

        score = ev.get("score", 0)

        if ev.get("success"):
            score += 1
        if ev.get("feedback") == "good":
            score += 1
        if ev.get("feedback") == "bad":
            score -= 1

        score_map[key].append(score)

    avg_scores = {}
    for key, scores in score_map.items():
        avg_scores[key] = sum(scores) / len(scores)

    state["action_priority"] = sorted(
        avg_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return state

if __name__ == "__main__":
    state = load_state()
    state = update_priority(state)
    save_state(state)
    print("CONTEXTUAL DECISION UPDATED")
