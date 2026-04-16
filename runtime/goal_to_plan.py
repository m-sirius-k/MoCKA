import json
import os

GOAL_PATH = "goal.json"
PLAN_PATH = "plan.json"

KEYWORD_MAP = {
    # 日本語
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
    # 英語
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

def update_plan_from_goal():
    if not os.path.exists(GOAL_PATH):
        return
    with open(GOAL_PATH, "r", encoding="utf-8") as f:
        goal = json.load(f)
    text = goal.get("target", "")
    text_lower = text.lower()
    steps = []

    for keyword, action in KEYWORD_MAP.items():
        if keyword.lower() in text_lower and action not in steps:
            steps.append(action)

    # コードスニペット判定
    if not steps and any(c in text for c in ["def ", "import ", "class ", "return ", "{", "}"]):
        steps.append("ANALYZE")

    # キーワードなしの場合はEXECUTE
    if not steps:
        steps.append("EXECUTE")

    plan = {
        "steps": steps,
        "source": "intent",
        "raw_goal": text
    }
    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    print("PLAN STRUCTURED")
