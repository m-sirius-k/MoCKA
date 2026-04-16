import json
import os

RESULT_PATH = "action_result.json"
STATE_PATH = "state.json"

def update_state_from_result():
    if not os.path.exists(RESULT_PATH):
        return

    with open(RESULT_PATH, "r", encoding="utf-8") as f:
        result = json.load(f)

    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {}

    # 安全初期化
    if "history" not in state or not isinstance(state["history"], list):
        state["history"] = []

    state["history"].append(result)

    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print("STATE UPDATED")
