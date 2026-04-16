import json

INPUT = "input.json"
OUTPUT = "action_override.json"

MAP = {
    "error_recovery": ["FIX"],
    "analyze_state": ["ANALYZE"],
    "optimize_execution": ["ANALYZE","FIX"],
    "build_feature": ["ANALYZE","RUN_FAST"],
    "continue_process": ["RUN_FAST"],
    "context_process": ["ANALYZE"]
}

def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)

    goal = data.get("goal", "context_process")
    actions = MAP.get(goal, ["ANALYZE"])

    override = {
        "goal": goal,
        "actions": actions
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(override, f, indent=2, ensure_ascii=False)

    print("=== ACTION OVERRIDE GENERATED ===")
    print(f"GOAL: {goal}")
    print(f"ACTIONS: {actions}")

if __name__ == "__main__":
    main()
