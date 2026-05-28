"""
add_immutable_layer.py
lever_essence.json への IMMUTABLE 層追加の監査証跡スクリプト。
実際の編集は DNA_v3 Step1 で実施済み（2026-05-28）。
このスクリプトは IMMUTABLE 層の現状検証に使用する。
"""
import json
import sys

ESSENCE_PATH = r"C:\Users\sirok\MoCKA\interface\lever_essence.json"

def verify_immutable_layer():
    with open(ESSENCE_PATH, encoding="utf-8") as f:
        data = json.load(f)

    assert "IMMUTABLE" in data, "IMMUTABLE 層が存在しない"
    imm = data["IMMUTABLE"]

    first_key = list(data.keys())[0]
    assert first_key == "IMMUTABLE", f"IMMUTABLE が先頭でない: {first_key}"

    for field in ("philosophy", "forbidden", "values"):
        assert field in imm, f"IMMUTABLE.{field} が存在しない"
        assert len(imm[field]) > 0, f"IMMUTABLE.{field} が空"

    print("[PASS] IMMUTABLE 層存在確認")
    print("[PASS] IMMUTABLE 先頭位置確認")
    print("[PASS] philosophy/forbidden/values 全フィールド確認")
    print(f"  philosophy: {len(imm['philosophy'])} 件")
    print(f"  forbidden:  {len(imm['forbidden'])} 件")
    print(f"  values:     {len(imm['values'])} 件")
    return True

if __name__ == "__main__":
    try:
        verify_immutable_layer()
        print("=== Step1 検証 PASS ===")
    except AssertionError as e:
        print(f"[FAIL] {e}", file=sys.stderr)
        sys.exit(1)
