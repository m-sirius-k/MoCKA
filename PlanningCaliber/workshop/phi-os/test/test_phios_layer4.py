"""
PHI-OS実機テスト Layer4: mocka本体接続(ポーリング) テスト
PHI-OS Test Spec v1.0 (TODO_207) Layer4実装。
PHI-OS-SPEC-001 第5章 5.1準拠。

ログ形式: TEST_START / TEST_STEP / TEST_RESULT / TEST_FAIL_REASON / TEST_END

実行方法:
  vasAI(localhost:6000)・MoCKA(localhost:5002)・MoCKA本体(localhost:5000)を
  起動した状態で実行する。
    python C:/Users/sirok/MoCKA/PlanningCaliber/workshop/phi-os/test/test_phios_layer4.py
"""
import shutil
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from phi_os import PHIOS  # noqa: E402
from phi_os_state import DATA_ROOT  # noqa: E402
from phi_os_poller import poll_once, LIVING_CONTEXT_URL  # noqa: E402

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
# ポーリング成功 -> ingest確認
# ---------------------------------------------------------------------------
def case_poll_success_ingest():
    steps = []
    node_id = "phi-os-test-poll-001"
    _clean(node_id)
    hub = PHIOS("test", "poll", "001")

    before = len(hub.state.raw_store)
    result = poll_once(hub)
    steps.append(f"poll_once() -> {result['status']}")

    if result["status"] != "OK":
        return steps, f"expected status=OK (localhost:5000 /api/living-context), got {result}"

    if result["ingest"].get("source") != "mocka":
        return steps, f"expected ingest source='mocka', got {result['ingest'].get('source')}"

    after = len(hub.state.raw_store)
    steps.append(f"raw_store: {before} -> {after}")
    if after != before + 1:
        return steps, "ポーリング成功時にingest('mocka', payload)がraw_storeに記録されていない"

    _clean(node_id)
    return steps, None


# ---------------------------------------------------------------------------
# ポーリング失敗 -> ERROR記録・継続確認(停止しないこと)
# ---------------------------------------------------------------------------
def case_poll_failure_continues():
    steps = []
    node_id = "phi-os-test-poll-002"
    _clean(node_id)
    hub = PHIOS("test", "poll", "002")

    bad_url = "http://localhost:59999/api/living-context"  # 存在しないポート
    result = poll_once(hub, url=bad_url)
    steps.append(f"poll_once(不正URL) -> {result}")

    if result["status"] != "POLL_FAIL":
        return steps, f"expected status=POLL_FAIL, got {result}"
    if "error" not in result:
        return steps, "POLL_FAIL時にerror情報が含まれない"
    steps.append("MOCKA_POLL_FAIL相当のエラーを記録し、例外を送出せず継続することを確認")

    # 継続確認: 同じhubで2回目のポーリング(正常URL)も問題なく実行できる
    result2 = poll_once(hub)
    steps.append(f"続けて正常URLでpoll_once() -> {result2['status']}")
    if result2["status"] != "OK":
        return steps, "失敗後もポーリングループが継続できることを確認できない"

    _clean(node_id)
    return steps, None


# ---------------------------------------------------------------------------
# 最優先処理の動作確認: ingest('mocka',..)実行中は他のingest()がブロックされる
# ---------------------------------------------------------------------------
def case_mocka_ingest_priority():
    steps = []
    node_id = "phi-os-test-poll-003"
    _clean(node_id)
    hub = PHIOS("test", "poll", "003")

    order = []
    started_mocka = threading.Event()

    def slow_mocka_ingest():
        with hub._ingest_lock:
            order.append("mocka_start")
            started_mocka.set()
            time.sleep(0.3)
            order.append("mocka_end")

    def other_ingest():
        started_mocka.wait()
        order.append("other_start")
        hub.ingest("other_source", {"v": 1})
        order.append("other_end")

    t1 = threading.Thread(target=slow_mocka_ingest)
    t2 = threading.Thread(target=other_ingest)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    steps.append(f"order: {order}")
    if order.index("other_end") < order.index("mocka_end"):
        return steps, f"mocka処理中に他ingestがブロックされていない: {order}"
    steps.append("mocka伝令処理中、他ingest()がブロックされ最優先処理されたことを確認")

    _clean(node_id)
    return steps, None


def main():
    cases = [
        ("ポーリング成功 -> ingest確認", case_poll_success_ingest),
        ("ポーリング失敗 -> ERROR記録・継続確認", case_poll_failure_continues),
        ("mocka伝令の最優先処理確認", case_mocka_ingest_priority),
    ]

    for name, fn in cases:
        run_case(name, fn)

    total = len(_results)
    passed = sum(1 for _, ok, _ in _results if ok is True)
    rate = (passed / total * 100) if total else 100.0

    print("=" * 60)
    print(f"  PHI-OS Layer4 テスト結果: {passed}/{total} PASS ({rate:.1f}%)")
    print(f"  living-context URL: {LIVING_CONTEXT_URL}")
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
