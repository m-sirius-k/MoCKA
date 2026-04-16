import json

STATE_PATH = "runtime/state/state.json"
HUMAN_EVAL_PATH = "runtime/state/human_evaluation.json"

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def integrate():
    state = load_json(STATE_PATH)
    human_eval = load_json(HUMAN_EVAL_PATH)

    if human_eval is None:
        print("NO HUMAN EVAL")
        return

    if state is None:
        state = {}

    if "evaluations" not in state:
        state["evaluations"] = []

    state["evaluations"].append(human_eval)

    save_json(STATE_PATH, state)
    print("EVALUATION INTEGRATED")

if __name__ == "__main__":
    integrate()
