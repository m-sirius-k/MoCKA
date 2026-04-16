import json
import os

GOAL_PATH = "goal.json"

def decide_action_from_goal():
    if not os.path.exists(GOAL_PATH):
        return []

    with open(GOAL_PATH, "r", encoding="utf-8") as f:
        goal = json.load(f)

    text = goal.get("target", "")

    actions = []

    # 順序を簡易抽出
    if "解析" in text or "分析" in text:
        actions.append("ANALYZE")

    if "修正" in text or "直せ" in text:
        actions.append("FIX")

    if "実装" in text or "作成" in text:
        actions.append("BUILD")

    if not actions:
        actions.append("EXPLORE")

    return actions
