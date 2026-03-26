import json
import os
import sys
from intent_logger import append_intent
from intent_to_goal import apply_intent_to_goal
from goal_to_plan import update_plan_from_goal
from action_executor import execute_action
from result_to_state import update_state_from_result
from state_to_graph import update_causal_graph
from result_evaluator import evaluate_result
from eval_to_history import update_evaluation_history
from eval_selector import choose_best_action
from civilization_bridge import push_to_civilization, pull_from_civilization, run_civilization_step

PLAN_PATH = "plan.json"
INPUT_PATH = "input.json"

def load_intent():
    if not os.path.exists(INPUT_PATH):
        return None
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("intent")

def load_plan():
    if not os.path.exists(PLAN_PATH):
        return []
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("steps", [])

def main():
    intent = load_intent()

    if intent:
        print("INTENT RECEIVED:", intent["intent_id"])
        append_intent(intent)
        apply_intent_to_goal()
        update_plan_from_goal()

    print("=== DECISION MODE ===")
    steps = load_plan()
    steps = choose_best_action(steps)

    for step in steps:
        print("EXEC:", step)
        execute_action(step)
        update_state_from_result()
        evaluate_result()
        update_evaluation_history()

        # civilization_*との接続
        push_to_civilization(step)

    # civilization_loopを1ステップ実行
    print("=== CIVILIZATION STEP ===")
    run_civilization_step()

    # civilizationの進捗を取得
    progress = pull_from_civilization()
    print(f"CIVILIZATION PROGRESS: {progress.get('civilization_progress', 0):.3f}")

    update_causal_graph()

if __name__ == "__main__":
    main()
