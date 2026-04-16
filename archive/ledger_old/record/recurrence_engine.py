"""
recurrence_engine.py
調律版：傾向検知エンジン
"""

# 簡易履歴（メモリ内）
_recurrence_memory = {}

def detect_recurrence(event=None):
    """
    過去発生履歴から再発傾向を検知する
    """

    if event is None:
        return None

    # イベントキー生成（簡易）
    key = str(event)

    # カウント
    _recurrence_memory[key] = _recurrence_memory.get(key, 0) + 1
    count = _recurrence_memory[key]

    # 閾値判定（2回以上で再発）
    if count >= 2:
        return {
            "recurrence": True,
            "event": event,
            "count": count,
            "trend": "increasing"
        }

    return {
        "recurrence": False,
        "event": event,
        "count": count,
        "trend": "first_occurrence"
    }
