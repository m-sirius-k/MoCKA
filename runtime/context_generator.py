import json

INPUT_PATH = "runtime/input/human_feedback.json"
OUTPUT_PATH = "runtime/state/context.json"

def load_input():
    try:
        with open(INPUT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def generate_context(data):
    if not data:
        return {"context": "unknown"}

    action = data.get("action", "")

    if action == "FIX":
        return {"context": "error_recovery"}
    elif action == "ANALYZE":
        return {"context": "investigation"}
    else:
        return {"context": "general"}

def save(ctx):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(ctx, f, indent=2)

if __name__ == "__main__":
    data = load_input()
    ctx = generate_context(data)
    save(ctx)
    print("CONTEXT GENERATED")
