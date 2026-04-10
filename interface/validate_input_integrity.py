# validate_input_integrity.py
# router.pyへの追加モジュール
# Geminiインシデント（沈黙による整合性逃避）の物理的封じ込め

import json
import hashlib
from pathlib import Path

class MoCKA_IntegrityError(Exception):
    pass

def validate_input_integrity(data: dict) -> dict:
    """
    入力データの不整合を検知したら沈黙を禁じる。
    検知した場合、処理を停止し必ず報告する。
    沈黙 = ルール違反。
    """
    errors = []

    # 1. 固定値検知（全フィールドが同一値 = 模擬データの疑い）
    values = [str(v) for v in data.values() if v is not None]
    if len(set(values)) == 1 and len(values) > 2:
        errors.append("FIXED_VALUE_DETECTED: 全フィールドが同一値。模擬データの疑い。")

    # 2. 空欄検知（必須フィールドが空）
    required_fields = ["title", "description", "what_type"]
    for field in required_fields:
        if field in data and (data[field] is None or str(data[field]).strip() == ""):
            errors.append(f"EMPTY_FIELD_DETECTED: {field} が空。")

    # 3. 構造不全検知（フィールド数が最小基準未満）
    if len(data) < 3:
        errors.append(f"STRUCTURE_INCOMPLETE: フィールド数={len(data)}。最小3必須。")

    # 4. エラーがあれば必ず報告（沈黙禁止）
    if errors:
        report = {
            "status": "INTEGRITY_VIOLATION",
            "errors": errors,
            "data_hash": hashlib.sha256(
                json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
            ).hexdigest()[:16],
            "action": "処理を停止。博士に報告する。"
        }
        raise MoCKA_IntegrityError(json.dumps(report, ensure_ascii=False, indent=2))

    return {"status": "OK", "field_count": len(data)}


if __name__ == "__main__":
    # テスト1: 正常データ
    ok_data = {"title": "テスト", "description": "正常データ", "what_type": "record"}
    print("テスト1（正常）:", validate_input_integrity(ok_data))

    # テスト2: 固定値（Gemini型捏造）
    try:
        bad_data = {"title": "0.88", "description": "0.88", "what_type": "0.88", "z_score": "0.88"}
        validate_input_integrity(bad_data)
    except MoCKA_IntegrityError as e:
        print("テスト2（固定値検知）:", e)

    # テスト3: 空欄
    try:
        empty_data = {"title": "", "description": "何か", "what_type": None}
        validate_input_integrity(empty_data)
    except MoCKA_IntegrityError as e:
        print("テスト3（空欄検知）:", e)
