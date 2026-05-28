# test_commit.py — DNA_v3 Step3 テスト
import subprocess
import json
import sqlite3
import sys

DB_PATH = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
COMMIT_ENGINE = r"C:\Users\sirok\MoCKA\PlanningCaliber\workshop\phi-os\core\commit-engine.js"


def call_commit(payload):
    result = subprocess.run(
        ["node", COMMIT_ENGINE, "--data", json.dumps(payload, ensure_ascii=False)],
        capture_output=True, text=True, encoding="utf-8"
    )
    try:
        return json.loads(result.stdout.strip()), result.returncode
    except Exception:
        return {"raw": result.stdout, "stderr": result.stderr}, result.returncode


def cleanup(event_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM judgement_reason WHERE event_id=?", (event_id,))
    conn.commit()
    conn.close()


def test_commit_engine_import():
    result = subprocess.run(
        ["node", "-e", "const e = require('./core/commit-engine'); console.log('ok:', typeof e.commitSession)"],
        capture_output=True, text=True, cwd=r"C:\Users\sirok\MoCKA\PlanningCaliber\workshop\phi-os"
    )
    assert result.returncode == 0, f"import失敗: {result.stderr}"
    assert "function" in result.stdout, f"commitSession が関数でない: {result.stdout}"
    print("[PASS] commit-engine import 確認")


def test_commit_valid():
    payload = {
        "event_id":    "E_TEST_COMMIT_001",
        "session_date": "2026-05-28",
        "decision":    "採用",
        "reason":      "テスト: 正常コミット",
        "tension":     "テスト違和感",
        "tension_severity": 2,
        "tags":        "tension,unresolved"
    }
    out, code = call_commit(payload)
    cleanup("E_TEST_COMMIT_001")
    assert code == 0, f"終了コード異常: {code}, {out}"
    assert out.get("ok") is True, f"ok=True でない: {out}"
    assert "id" in out, f"id が返らない: {out}"
    print(f"[PASS] 正常コミット確認 (id={out['id']})")


def test_commit_invalid_missing_reason():
    payload = {
        "event_id":    "E_TEST_COMMIT_002",
        "session_date": "2026-05-28",
        "decision":    "採用",
    }
    out, code = call_commit(payload)
    assert code != 0, "reason なしでも成功してしまった"
    assert out.get("ok") is not True
    print("[PASS] reason 未指定バリデーション確認")


def test_commit_rejected_without_reason():
    payload = {
        "event_id":    "E_TEST_COMMIT_003",
        "session_date": "2026-05-28",
        "decision":    "却下",
        "reason":      "WHY",
    }
    out, code = call_commit(payload)
    assert code != 0, "却下+rejected_reason なしでも成功してしまった"
    print("[PASS] 却下+rejected_reason 必須バリデーション確認")


def test_commit_tension_high():
    payload = {
        "event_id":    "E_TEST_COMMIT_004",
        "session_date": "2026-05-28",
        "decision":    "保留",
        "reason":      "重大違和感のため保留",
        "tension":     "この実装は将来DBを壊す可能性がある",
        "tension_severity": 5,
        "tags":        "tension,unresolved,anomaly"
    }
    out, code = call_commit(payload)
    cleanup("E_TEST_COMMIT_004")
    assert code == 0, f"終了コード異常: {code}"
    assert out.get("ok") is True
    print("[PASS] tension_severity=5 コミット確認")


if __name__ == "__main__":
    test_commit_engine_import()
    test_commit_valid()
    test_commit_invalid_missing_reason()
    test_commit_rejected_without_reason()
    test_commit_tension_high()
    print("=== commit テスト全PASS ===")
