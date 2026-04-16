import json
import os
import traceback

DECISION_FILE = "repair_decision.json"
RESULT_FILE = "repair_execution_result.json"

def load_decision():
    if not os.path.exists(DECISION_FILE):
        print("NO_DECISION_FILE")
        return None
    with open(DECISION_FILE,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def execute_repair(decision):

    repair = decision.get("selected_repair",{})
    repair_id = repair.get("repair_id","UNKNOWN")

    result = {
        "repair_id": repair_id,
        "status": "not_executed"
    }

    try:

        if repair_id == "R003":
            result["action"] = "inspect_stacktrace"
            result["status"] = "simulated_fix"

        else:
            result["status"] = "no_action_rule"

    except Exception as e:
        result["status"] = "repair_failed"
        result["error"] = str(e)
        result["trace"] = traceback.format_exc()

    return result

def save_result(result):
    with open(RESULT_FILE,"w",encoding="utf-8-sig") as f:
        json.dump(result,f,indent=2)

def main():

    decision = load_decision()

    if not decision:
        return

    status = decision.get("status")

    if status != "approved":
        print("REPAIR_NOT_APPROVED")
        return

    result = execute_repair(decision)

    save_result(result)

    print("REPAIR_EXECUTED")

if __name__ == "__main__":
    main()

