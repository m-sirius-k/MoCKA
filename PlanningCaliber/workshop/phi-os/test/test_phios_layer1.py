"""
PHI-OS実機テスト Layer1: Stateful Kernel テスト
PHI-OS Test Spec v1.0 (TODO_195) Layer1実装。
PHI-OS-SPEC-001 第3章準拠。

ログ形式: TEST_START / TEST_STEP / TEST_RESULT / TEST_FAIL_REASON / TEST_END

実行方法:
  vasAI(localhost:6000) と MoCKA(localhost:5002)を起動した状態で実行する。
    python C:/Users/sirok/MoCKA/PlanningCaliber/workshop/phi-os/test/test_phios_layer1.py
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from phi_os import PHIOS, PHIOSError  # noqa: E402
from phi_os_state import PHIOSState, StateViolationError, DATA_ROOT  # noqa: E402

_results = []


def _log(line: str):
    print(line)


def run_case(name, fn):
    _log(f"TEST_START: {name}")
    try:
        steps_passed, fail_reason = fn()
        for step in steps_passed:
            _log(f"TEST_STEP: {step}")
        if fail_reason is None:
            _log(f"TEST_RESULT: PASS ({name})")
            _results.append((name, True, None))
        else:
            _log(f"TEST_FAIL_REASON: {fail_reason}")
            _log(f"TEST_RESULT: FAIL ({name})")
            _results.append((name, False, fail_reason))
    except Exception as e:
        _log(f"TEST_FAIL_REASON: unhandled exception: {type(e).__name__}: {e}")
        _log(f"TEST_RESULT: FAIL ({name})")
        _results.append((name, False, str(e)))
    finally:
        _log(f"TEST_END: {name}\n")


def _clean(node_id):
    d = DATA_ROOT / node_id
    if d.exists():
        shutil.rmtree(d)


# ---------------------------------------------------------------------------
# 再起動サバイバルテスト
# ---------------------------------------------------------------------------
def case_restart_survival():
    steps = []
    node_id = "phi-os-test-restart-001"
    _clean(node_id)

    state1 = PHIOSState(node_id)
    state1.append_raw("test_source", {"v": 1})
    state1.append_raw("test_source", {"v": 2})
    steps.append(f"1回目起動: raw_store={len(state1.raw_store)}件追記")

    # 「再起動」を新インスタンス生成で模擬
    state2 = PHIOSState(node_id)
    steps.append(f"2回目起動(再起動模擬): raw_store={len(state2.raw_store)}件ロード")

    if len(state2.raw_store) != 2:
        return steps, f"expected raw_store=2件, got {len(state2.raw_store)}"
    if state2.raw_store[0]["payload"] != {"v": 1} or state2.raw_store[1]["payload"] != {"v": 2}:
        return steps, "raw_store内容が再起動後に一致しない"

    view = state2.generate_view()
    steps.append(f"views再構成: {view}")
    if view["raw_count"] != 2:
        return steps, f"expected views raw_count=2, got {view['raw_count']}"

    _clean(node_id)
    return steps, None


# ---------------------------------------------------------------------------
# append-only違反検知テスト
# ---------------------------------------------------------------------------
def case_append_only_violation():
    steps = []
    node_id = "phi-os-test-violation-001"
    _clean(node_id)

    state1 = PHIOSState(node_id)
    state1.append_raw("test_source", {"v": 1})
    state1.append_raw("test_source", {"v": 2})
    steps.append("raw_storeに2件追記")

    # FORBIDDEN②: raw_store.jsonl を外部から改変(削除)する
    raw_path = DATA_ROOT / node_id / "raw_store.jsonl"
    lines = raw_path.read_text(encoding="utf-8").splitlines()
    raw_path.write_text(lines[0] + "\n", encoding="utf-8")
    steps.append("raw_store.jsonlを外部改変(1行削除)してFORBIDDEN②を再現")

    try:
        PHIOSState(node_id)
        return steps, "StateViolationErrorが送出されなかった"
    except StateViolationError as e:
        steps.append(f"StateViolationError送出を確認: {e}")

    _clean(node_id)
    return steps, None


# ---------------------------------------------------------------------------
# node_id固定テスト
# ---------------------------------------------------------------------------
def case_node_id_immutable():
    steps = []
    hub = PHIOS("mocka", "core", "001")
    expected = "phi-os-mocka-core-001"
    if hub.node_id != expected:
        return steps, f"expected node_id={expected}, got {hub.node_id}"
    steps.append(f"node_id命名規則準拠: {hub.node_id}")

    try:
        hub.node_id = "phi-os-changed-core-001"
        return steps, "node_id再代入がAttributeErrorにならなかった"
    except AttributeError as e:
        steps.append(f"node_id再代入でAttributeError送出を確認: {e}")

    _clean(hub.node_id)
    return steps, None


# ---------------------------------------------------------------------------
# Layer2との結合テスト(リグレッション)
# ---------------------------------------------------------------------------
def case_layer2_regression():
    steps = []
    import test_phios_layer2 as l2

    l2._results.clear()
    for name, fn in [
        ("4.1 正常リクエスト(CONTINUE)", l2.case_normal_continue),
        ("4.1 正常リクエスト(STABLE)", l2.case_normal_stable),
        ("4.2 欠損パラメータ(decision_id)", l2.case_missing_decision_id),
        ("4.2 不正JSON入力", l2.case_invalid_json),
        ("4.2 型エラー(decision_id=数値)", l2.case_type_error_decision_id),
        ("4.3 境界値(空データ)", l2.case_empty_body),
        ("4.3 境界値(最大サイズ)", l2.case_large_payload),
        ("4.3 境界値(null入力)", l2.case_null_fields),
        ("PHIOS.ingest() 入出力", l2.case_phios_ingest),
        ("PHIOS.sync('vasai') STABLE", l2.case_phios_sync_stable),
        ("PHIOS.sync('vasai') LOOP_LIMIT_REACHED", l2.case_phios_sync_loop_limit),
        ("PHIOS.sync(target!='vasai') 異常系", l2.case_phios_sync_invalid_target),
    ]:
        l2.run_case(name, fn)

    total = len(l2._results)
    skipped = sum(1 for _, ok, _ in l2._results if ok is None)
    judged = total - skipped
    passed = sum(1 for _, ok, _ in l2._results if ok is True)
    rate = (passed / judged * 100) if judged else 100.0
    steps.append(f"Layer2再実行結果: {passed}/{judged} PASS ({rate:.1f}%)  SKIP={skipped}")

    if rate < 95.0:
        failed = [n for n, ok, r in l2._results if ok is False]
        return steps, f"Layer2リグレッション失敗: {failed}"

    _clean("phi-os-mocka-core-001")
    return steps, None


def main():
    cases = [
        ("再起動サバイバルテスト(永続化確認)", case_restart_survival),
        ("append-only違反検知テスト(FORBIDDEN②)", case_append_only_violation),
        ("node_id固定テスト", case_node_id_immutable),
        ("Layer2結合テスト(リグレッション12件)", case_layer2_regression),
    ]

    for name, fn in cases:
        run_case(name, fn)

    total = len(_results)
    passed = sum(1 for _, ok, _ in _results if ok is True)
    rate = (passed / total * 100) if total else 100.0

    print("=" * 60)
    print(f"  PHI-OS Layer1 テスト結果: {passed}/{total} PASS ({rate:.1f}%)")
    print("=" * 60)
    for name, ok, reason in _results:
        mark = "PASS" if ok is True else "FAIL"
        line = f"  [{mark}] {name}"
        if ok is not True:
            line += f"  - {reason}"
        print(line)

    sys.exit(0 if rate >= 95.0 else 1)


if __name__ == "__main__":
    main()
