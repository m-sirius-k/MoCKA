import json
import os

HISTORY_PATH = "evaluation_history.json"

def choose_best_action(actions):
    if not os.path.exists(HISTORY_PATH):
        return actions

    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        history = json.load(f)

    scores = {}

    for h in history:
        action = h.get("action")
        score = h.get("score", 0)
        scores[action] = scores.get(action, 0) + score

    # スコア順で並び替え
    actions.sort(key=lambda x: scores.get(x, 0), reverse=True)

    return actions
