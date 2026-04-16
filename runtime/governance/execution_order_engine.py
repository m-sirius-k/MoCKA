"""
execution_order_engine.py
調律版：判断型実行順序エンジン
"""

def execute_order(task=None):
    """
    状態に応じて実行優先度と分岐を決定する
    """

    if task is None:
        return {"action": "idle", "priority": 0}

    # 予防優先
    if isinstance(task, dict) and task.get("recurrence"):
        return {
            "action": "prevent",
            "priority": 100,
            "reason": "recurrence_detected"
        }

    # インシデント対応
    if isinstance(task, dict) and task.get("incident"):
        return {
            "action": "repair",
            "priority": 80,
            "reason": "incident_detected"
        }

    # 通常処理
    return {
        "action": "execute",
        "priority": 10,
        "reason": "normal_flow"
    }
