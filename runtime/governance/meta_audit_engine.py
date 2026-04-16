"""
meta_audit_engine.py
調律版：統制・整合監査エンジン
"""

def meta_audit(data=None):
    """
    全体整合性を監査し、安全な状態のみ通過させる
    """

    if data is None:
        return {
            "audit": "no_input",
            "status": "blocked"
        }

    # 基本検証
    if not isinstance(data, dict):
        return {
            "audit": "invalid_format",
            "status": "blocked"
        }

    # 必須キー確認（最低限）
    required_keys = ["status"]

    for key in required_keys:
        if key not in data:
            return {
                "audit": "missing_key",
                "status": "blocked",
                "missing": key
            }

    # 異常検知（例：priority異常）
    if data.get("priority", 0) < 0:
        return {
            "audit": "invalid_priority",
            "status": "blocked"
        }

    # 正常通過
    return {
        "audit": "ok",
        "status": "approved",
        "data": data
    }
