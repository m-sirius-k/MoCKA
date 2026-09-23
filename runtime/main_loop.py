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
from plan_validator import load_plan_with_validation
from governance_client import evaluate as governance_evaluate
from hg_gateway import authorize_and_execute
from execution_context import ExecutionContext

PLAN_PATH = "plan.json"
INPUT_PATH = "input.json"

def load_intent():
    if not os.path.exists(INPUT_PATH):
        return None
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("intent")

def main():
    intent = load_intent()

    if intent:
        print("INTENT RECEIVED:", intent["intent_id"])
        append_intent(intent)
        apply_intent_to_goal()
        update_plan_from_goal()

    print("=== DECISION MODE ===")

    # Load and validate plan
    plan_result = load_plan_with_validation()
    plan = plan_result.get("plan")
    validation = plan_result.get("validation")

    if not plan or not validation.get("valid"):
        print("PLAN INVALID:", validation.get("errors"))
        if validation.get("status") == "LEGACY":
            print("Legacy plan detected; execution blocked")
            return
        return

    print("PLAN VALID")

    # Choose best action order (based on evaluation history)
    steps_ordered = choose_best_action(plan)

    # T2: Governance evaluation
    print("=== GOVERNANCE EVALUATION ===")
    governance_result = governance_evaluate(plan)
    print(f"GOVERNANCE DECISION: {governance_result.get('governance_decision')}")
    print(f"DECISION_RECORD_ID: {governance_result.get('decision_record_id')}")

    # T3–T5: HG authorization and execution (CHOKE POINT)
    print("=== HG AUTHORIZATION AND EXECUTION ===")

    def execute_action_with_context(execution_context, step, action_id):
        """Wrapper for execute_action that uses execution_context."""
        # Update trace
        execution_context.add_trace_event("execute_action_start", f"step={step}, action_id={action_id}")

        # Call original execute_action
        try:
            result = execute_action(step)
            execution_context.add_trace_event("execute_action_complete", "status=success")
            return result
        except Exception as e:
            execution_context.add_trace_event("execute_action_failed", f"error={e}")
            raise

    # Authorize and execute (T3–T5 chain)
    execution_context = authorize_and_execute(
        plan=plan,
        governance_decision=governance_result,
        governance_record_id=governance_result.get("decision_record_id"),
        execute_fn=execute_action_with_context
    )

    # Check execution status
    if execution_context.execution_status == "BLOCKED":
        print(f"EXECUTION BLOCKED: {execution_context.execution_status}")
        print(f"Trace: {execution_context.trace}")
        return

    # Post-execution (unchanged from original flow)
    print("=== POST-EXECUTION FLOW ===")
    update_state_from_result()
    evaluate_result()
    update_evaluation_history()

    # Civilization flow
    push_to_civilization(None)  # No per-step push anymore (whole plan executed)

    print("=== CIVILIZATION STEP ===")
    run_civilization_step()

    progress = pull_from_civilization()
    print(f"CIVILIZATION PROGRESS: {progress.get('civilization_progress', 0):.3f}")

    update_causal_graph()

if __name__ == "__main__":
    main()
