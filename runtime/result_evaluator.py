import json
import os

RESULT_PATH = "action_result.json"
EVAL_PATH = "evaluation.json"

def evaluate_result():
    if not os.path.exists(RESULT_PATH):
        return

    with open(RESULT_PATH, "r", encoding="utf-8") as f:
        result = json.load(f)

    action = result.get("action")

    score = 0

    if action == "ANALYZE":
        score = 1
    elif action == "FIX":
        score = 2
    else:
        score = 0

    evaluation = {
        "action": action,
        "score": score
    }

    with open(EVAL_PATH, "w", encoding="utf-8") as f:
        json.dump(evaluation, f, ensure_ascii=False, indent=2)

    print("EVALUATED:", score)
