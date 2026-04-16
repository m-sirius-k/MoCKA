import json
import os

EVAL_PATH = "evaluation.json"
HISTORY_PATH = "evaluation_history.json"

def update_evaluation_history():
    if not os.path.exists(EVAL_PATH):
        return

    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = []

    history.append(eval_data)

    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print("EVAL HISTORY UPDATED")
