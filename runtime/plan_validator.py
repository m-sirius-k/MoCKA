"""
Plan validation and legacy detection for T2-T3 integration.
"""
import json
import os


PLAN_PATH = "plan.json"


def is_legacy_plan(plan_dict):
    """Returns True if plan lacks new metadata fields (intent_id, plan_id)."""
    required_fields = {"intent_id", "plan_id"}
    return not all(field in plan_dict for field in required_fields)


def validate_plan(plan_dict):
    """
    Validate plan structure and metadata completeness.
    Returns: {
        "valid": bool,
        "status": "CURRENT" | "LEGACY" | "INVALID",
        "errors": [str],
        "warnings": [str],
        "plan": dict (enriched with validation metadata)
    }
    """
    errors = []
    warnings = []
    status = "CURRENT"

    # Check for required fields
    if not plan_dict:
        errors.append("Plan is empty")
        return {
            "valid": False,
            "status": "INVALID",
            "errors": errors,
            "warnings": warnings,
            "plan": {}
        }

    # Check legacy vs current
    if is_legacy_plan(plan_dict):
        status = "LEGACY"
        warnings.append("Plan lacks intent_id/plan_id; treated as legacy")
        return {
            "valid": False,  # Legacy plans do not pass validation for new chain
            "status": status,
            "errors": ["Legacy plan: missing intent_id and/or plan_id"],
            "warnings": warnings,
            "plan": plan_dict
        }

    # Validate current plan format
    if "steps" not in plan_dict:
        errors.append("Plan missing 'steps' field")

    if not isinstance(plan_dict.get("steps"), list):
        errors.append("Plan 'steps' must be a list")

    if not plan_dict.get("intent_id"):
        errors.append("Plan missing or empty 'intent_id'")

    if not plan_dict.get("plan_id"):
        errors.append("Plan missing or empty 'plan_id'")

    # Validate action_ids if present
    if "action_ids" in plan_dict:
        action_ids = plan_dict.get("action_ids", [])
        steps = plan_dict.get("steps", [])

        if len(action_ids) != len(steps):
            errors.append(f"action_ids count ({len(action_ids)}) != steps count ({len(steps)})")

        for action_id in action_ids:
            if not isinstance(action_id, str) or ":" not in action_id:
                errors.append(f"Invalid action_id format: {action_id}")

    valid = len(errors) == 0
    status = "CURRENT" if valid else "INVALID"

    return {
        "valid": valid,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "plan": plan_dict
    }


def load_plan_with_validation():
    """
    Load plan.json and validate.
    Returns: {"plan": dict, "validation": validation_result}
    """
    if not os.path.exists(PLAN_PATH):
        return {
            "plan": None,
            "validation": {
                "valid": False,
                "status": "NOT_FOUND",
                "errors": [f"Plan file not found: {PLAN_PATH}"],
                "warnings": []
            }
        }

    try:
        with open(PLAN_PATH, "r", encoding="utf-8") as f:
            plan = json.load(f)
    except json.JSONDecodeError as e:
        return {
            "plan": None,
            "validation": {
                "valid": False,
                "status": "INVALID",
                "errors": [f"Plan JSON parse error: {e}"],
                "warnings": []
            }
        }

    validation = validate_plan(plan)
    return {
        "plan": plan,
        "validation": validation
    }
