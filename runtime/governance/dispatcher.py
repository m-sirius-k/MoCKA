"""
dispatcher.py
調律版：行動決定エンジン
"""

def dispatch_event(event=None):
    """
    execution_order の判断結果を受け取り、
    実行すべき行動へ変換する
    """

    if event is None:
        return {"status": "idle", "action": None}

    # 判断結果をそのまま受け取る前提
    if isinstance(event, dict):

        action = event.get("action")
        priority = event.get("priority", 0)

        if action == "prevent":
            return {
                "status": "executed",
                "type": "preventive_action",
                "priority": priority
            }

        if action == "repair":
            return {
                "status": "executed",
                "type": "repair_action",
                "priority": priority
            }

    # デフォルト処理
    return {
        "status": "executed",
        "type": "normal_action",
        "priority": 10
    }
