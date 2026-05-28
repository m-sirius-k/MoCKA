# test_restore.py — DNA_v3 Step4 テスト
import json
import os
import subprocess
import sys

RESTORE_ENGINE = r"C:\Users\sirok\MoCKA\PlanningCaliber\workshop\phi-os\core\restore-engine.js"
PACKET_PATH    = r"C:\Users\sirok\MoCKA\data\storage\infield\PACKET\restore_packet.json"


def test_restore_engine_runs():
    result = subprocess.run(
        ["node", RESTORE_ENGINE, "--context", "テスト実行"],
        capture_output=True, text=True, encoding="utf-8", timeout=30
    )
    assert result.returncode == 0, f"restore-engine 終了コード異常: {result.returncode}\n{result.stderr}"
    print("[PASS] restore-engine 実行成功")


def test_restore_packet_exists():
    assert os.path.exists(PACKET_PATH), f"restore_packet.json が存在しない: {PACKET_PATH}"
    print("[PASS] restore_packet.json 存在確認")


def test_restore_packet_schema():
    with open(PACKET_PATH, encoding="utf-8") as f:
        packet = json.load(f)

    required_keys = ["version", "generated_at", "immutable", "restore_5points"]
    for key in required_keys:
        assert key in packet, f"必須キー {key} が存在しない"

    assert packet["version"] == "3.0", f"バージョン不一致: {packet['version']}"

    r5 = packet["restore_5points"]
    for point in ["1_personality", "2_current_goal", "3_active_work", "4_tensions", "5_recent_decisions"]:
        assert point in r5, f"restore_5points に {point} がない"

    print("[PASS] restore_packet スキーマ確認")


def test_immutable_not_empty():
    with open(PACKET_PATH, encoding="utf-8") as f:
        packet = json.load(f)

    immutable = packet["immutable"]
    assert len(immutable.get("philosophy", [])) > 0, "IMMUTABLE philosophy が空"
    assert len(immutable.get("forbidden", []))  > 0, "IMMUTABLE forbidden が空"
    assert len(immutable.get("values", []))     > 0, "IMMUTABLE values が空"
    print("[PASS] IMMUTABLE 層 非空確認")


def test_immutable_is_first_key():
    with open(PACKET_PATH, encoding="utf-8") as f:
        packet = json.load(f)
    keys = list(packet.keys())
    assert "immutable" in keys, "immutable キーがない"
    idx = keys.index("immutable")
    assert idx <= 4, f"immutable の位置が遅すぎる: {idx} ({keys})"
    print(f"[PASS] immutable キー位置確認 (index={idx})")


def test_packet_is_utf8():
    with open(PACKET_PATH, encoding="utf-8") as f:
        content = f.read()
    assert "できない" in content or "記録" in content, "UTF-8 日本語コンテンツが見つからない"
    print("[PASS] UTF-8 エンコーディング確認")


if __name__ == "__main__":
    test_restore_engine_runs()
    test_restore_packet_exists()
    test_restore_packet_schema()
    test_immutable_not_empty()
    test_immutable_is_first_key()
    test_packet_is_utf8()
    print("=== restore テスト全PASS ===")
