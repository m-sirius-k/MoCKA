import json

MODE_PATH = "runtime/state/decision_mode.json"
MUTATION_PATH = "runtime/state/mutations.json"

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def select_action(context):
    mode_data = load_json(MODE_PATH)
    mutations = load_json(MUTATION_PATH)

    if not mode_data:
        return "ANALYZE"

    mode = mode_data.get(context, {}).get("mode")
    base_action = mode_data.get(context, {}).get("action")

    if mode == "EXECUTE":
        return base_action

    if mode == "EXPLORE":
        if mutations:
            for m in mutations:
                if m["context"] == context:
                    return m["new_action"]
        return base_action

    return "ANALYZE"

if __name__ == "__main__":
    action = select_action("error_recovery")
    print(f"MODE ACTION: {action}")
