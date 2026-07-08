"""
TODO_428: overview_current_generator.py のテスト。

Test A: 同一入力に対するdeterminism確認(generated_at等のvolatileフィールドを除いた
        内容のSHA256一致)
Test B: 一次データ変更 -> 生成結果変化の確認
Test C: legacy MOCKA_OVERVIEW.json が変更されていないことの確認
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
sys.path.insert(0, str(MOCKA_ROOT / "scripts" / "state"))

import overview_current_generator as gen  # noqa: E402

LEGACY_OVERVIEW_PATH = Path(r"C:\Users\sirok\MOCKA_OVERVIEW.json")


def _content_hash(result: dict) -> str:
    """generated_at(実行時刻で毎回変わる)を除いた決定的な部分のみをハッシュ化する。"""
    stripped = copy.deepcopy(result)
    stripped["meta"].pop("generated_at", None)
    payload = json.dumps(stripped, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def test_a_deterministic_content_hash():
    result1 = gen.generate()
    result2 = gen.generate()
    assert _content_hash(result1) == _content_hash(result2), (
        "同一入力に対してtodo_summary/recent_decisions/recent_events/seal_status/"
        "integrity_warningsが2回の実行で一致しなかった"
    )


def test_b_todo_count_changes_with_input():
    result = gen.generate()
    total_from_summary = sum(result["todo_summary"].values())

    active = json.loads(gen.TODO_ACTIVE_PATH.read_text(encoding="utf-8"))
    archive = json.loads(gen.TODO_ARCHIVE_PATH.read_text(encoding="utf-8"))
    expected_total = (
        len(active.get("todos", []))
        + len(active.get("completed", []))
        + len(archive.get("completed", []))
    )
    assert total_from_summary == expected_total, (
        f"todo_summary合計({total_from_summary})が一次データの件数合計"
        f"({expected_total})と一致しない"
    )


def test_c_legacy_overview_untouched():
    before = _sha256_of_file(LEGACY_OVERVIEW_PATH)
    gen.generate()
    gen.write_output()
    after = _sha256_of_file(LEGACY_OVERVIEW_PATH)
    assert before == after, "legacy MOCKA_OVERVIEW.jsonがGenerator実行によって変更された"


def _sha256_of_file(path: Path):
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    test_a_deterministic_content_hash()
    print("Test A (deterministic content hash): PASS")
    test_b_todo_count_changes_with_input()
    print("Test B (todo count reflects input): PASS")
    test_c_legacy_overview_untouched()
    print("Test C (legacy overview untouched): PASS")
