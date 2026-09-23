import json
import os

HISTORY_PATH = "evaluation_history.json"

def choose_best_action(steps_or_plan):
    """
    Select best action order based on evaluation history.
    Now preserves step_index through reordering.

    Args:
        steps_or_plan: either list of step strings (legacy) or plan dict (new)

    Returns:
        list of {step, step_index, action_id} dicts if plan provided, else reordered strings (legacy)
    """

    # Handle legacy case (list of strings)
    if isinstance(steps_or_plan, list):
        return _choose_best_action_legacy(steps_or_plan)

    # Handle new case (plan dict)
    plan = steps_or_plan
    steps = plan.get("steps", [])
    action_ids = plan.get("action_ids", [])

    if not os.path.exists(HISTORY_PATH):
        # No history: return steps with indices
        return [{"step": s, "step_index": i, "action_id": aid}
                for i, (s, aid) in enumerate(zip(steps, action_ids))]

    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        history = json.load(f)

    # Score each action
    scores = {}
    for h in history:
        action = h.get("action")
        score = h.get("score", 0)
        scores[action] = scores.get(action, 0) + score

    # Create step objects with indices and action_ids
    step_objects = [{"step": s, "step_index": i, "action_id": aid, "score": scores.get(s, 0)}
                    for i, (s, aid) in enumerate(zip(steps, action_ids))]

    # Sort by score (highest first), but preserve step_index within each step object
    step_objects.sort(key=lambda x: x.get("score", 0), reverse=True)

    # Return with original step_index preserved
    return [{"step": so["step"], "step_index": so["step_index"], "action_id": so["action_id"]}
            for so in step_objects]


def _choose_best_action_legacy(actions):
    """Legacy behavior: just reorder string actions."""
    if not os.path.exists(HISTORY_PATH):
        return actions

    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        history = json.load(f)

    scores = {}
    for h in history:
        action = h.get("action")
        score = h.get("score", 0)
        scores[action] = scores.get(action, 0) + score

    actions.sort(key=lambda x: scores.get(x, 0), reverse=True)
    return actions
