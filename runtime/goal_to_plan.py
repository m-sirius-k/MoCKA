import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import json
import os
import hashlib

GOAL_PATH = "goal.json"
PLAN_PATH = "plan.json"

KEYWORD_MAP = {
    "解析": "ANALYZE",
    "分析": "ANALYZE",
    "修正": "FIX",
    "修理": "FIX",
    "保存": "SAVE",
    "書き出し": "EXPORT",
    "削除": "DELETE",
    "確認": "VERIFY",
    "実行": "EXECUTE",
    "調査": "RESEARCH",
    "検証": "VERIFY",
    "記録": "RECORD",
    "更新": "UPDATE",
    "analyze": "ANALYZE",
    "fix": "FIX",
    "save": "SAVE",
    "export": "EXPORT",
    "delete": "DELETE",
    "verify": "VERIFY",
    "execute": "EXECUTE",
    "research": "RESEARCH",
    "update": "UPDATE",
    "direct": "EXECUTE",
    "run": "EXECUTE",
    "check": "VERIFY",
}

def _compute_plan_id(intent_id, goal_text, steps):
    """Compute deterministic plan_id: hash(intent_id + goal_text + step_sequence)"""
    content = f"{intent_id}|{goal_text}|{json.dumps(steps)}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def update_plan_from_goal():
    if not os.path.exists(GOAL_PATH):
        return
    with open(GOAL_PATH, "r", encoding="utf-8") as f:
        goal = json.load(f)
    text = goal.get("target", "")
    text_lower = text.lower()
    intent_id = goal.get("intent_id", "UNKNOWN")
    steps = []

    for keyword, action in KEYWORD_MAP.items():
        if keyword.lower() in text_lower and action not in steps:
            steps.append(action)

    if not steps and any(c in text for c in ["def ", "import ", "class ", "return ", "{", "}"]):
        steps.append("ANALYZE")

    if not steps:
        steps.append("EXECUTE")

    plan_id = _compute_plan_id(intent_id, text, steps)

    # Create action_id list (format: {intent_id}:{step_index})
    action_ids = [f"{intent_id}:{i}" for i in range(len(steps))]

    plan = {
        "intent_id": intent_id,
        "plan_id": plan_id,
        "steps": steps,
        "action_ids": action_ids,
        "source": "intent",
        "raw_goal": text
    }
    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    print("PLAN STRUCTURED")
