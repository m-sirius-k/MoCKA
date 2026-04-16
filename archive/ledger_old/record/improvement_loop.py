"""
improvement_loop.py
調律版：学習エンジン
"""

# 学習メモリ
_improvement_memory = {
    "success": 0,
    "fail": 0,
    "history": []
}

def improvement_loop(data=None):
    """
    実行結果から学習し、次回行動に影響を与える
    """

    if data is None:
        return None

    # 成否判定
    status = data.get("status")

    if status in ["success", "prevented", "approved"]:
        _improvement_memory["success"] += 1
        result = "positive"
    else:
        _improvement_memory["fail"] += 1
        result = "negative"

    # 履歴保存
    _improvement_memory["history"].append({
        "input": data,
        "result": result
    })

    total = _improvement_memory["success"] + _improvement_memory["fail"]

    # 学習出力
    return {
        "learning": result,
        "success_rate": (
            _improvement_memory["success"] / total if total > 0 else 0
        ),
        "total": total
    }
