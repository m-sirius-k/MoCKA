"""
PHI-OS実機テスト Layer2: API / Routing整合性テスト
PHI-OS Test Spec v1.0 (TODO_195) Layer2実装。

対象: vasAI(localhost:6000) /phios/feedback エンドポイント、
      phi_os.PHIOS.ingest() / sync('vasai')

ログ形式: TEST_START / TEST_STEP / TEST_RESULT / TEST_FAIL_REASON / TEST_END
（spec 8章準拠）

実行方法:
  vasAI(localhost:6000) と MoCKA(localhost:5002)を起動した状態で実行する。
    cd C:/Users/sirok/MoCKA/PlanningCaliber/workshop/vasAI_Project
    python -m api.app
    python C:/Users/sirok/MoCKA/PlanningCaliber/workshop/phi-os/test/test_phios_layer2.py
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from phi_os import PHIOS, PHIOSError, MAX_LOOP_COUNT  # noqa: E402

VASAI_FEEDBACK_URL = "http://localhost:6000/phios/feedback"
REQUEST_TIMEOUT = 5

_results = []


def _log(line: str):
    print(line)


def _post(url, payload, raw=False):
    body = payload if raw else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            data = json.loads(e.read().decode("utf-8"))
        except Exception:
            data = None
        return e.code, data


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
    except PHIOSError as e:
        if "MoCKAへのevent記録に失敗" in str(e):
            _log(f"TEST_RESULT: SKIP ({name}) - MoCKA(localhost:5002)未起動のため環境依存スキップ: {e}")
            _results.append((name, None, str(e)))
        else:
            _log(f"TEST_FAIL_REASON: unhandled PHIOSError: {e}")
            _log(f"TEST_RESULT: FAIL ({name})")
            _results.append((name, False, str(e)))
    except Exception as e:
        _log(f"TEST_FAIL_REASON: unhandled exception: {type(e).__name__}: {e}")
        _log(f"TEST_RESULT: FAIL ({name})")
        _results.append((name, False, str(e)))
    finally:
        _log(f"TEST_END: {name}\n")


# ---------------------------------------------------------------------------
# 4.1 入力→出力整合
# ---------------------------------------------------------------------------
def case_normal_continue():
    steps = []
    status, data = _post(VASAI_FEEDBACK_URL, {
        "decision_id": "T_LAYER2_001",
        "why": "test", "reason": "test", "decision_summary": "test",
    })
    steps.append(f"POST /phios/feedback (no outcome) -> HTTP {status}")
    if status != 200:
        return steps, f"expected HTTP 200, got {status}"
    for key in ("status", "dna_id", "reason"):
        if key not in data:
            return steps, f"response missing key: {key}"
    steps.append(f"response schema OK: {data}")
    if data["status"] != "CONTINUE":
        return steps, f"expected status=CONTINUE, got {data['status']}"
    steps.append("status == CONTINUE (outcome未指定のため)")
    return steps, None


def case_normal_stable():
    steps = []
    status, data = _post(VASAI_FEEDBACK_URL, {
        "decision_id": "T_LAYER2_002",
        "why": "test", "reason": "test", "decision_summary": "test",
        "outcome": "success",
    })
    steps.append(f"POST /phios/feedback (with outcome) -> HTTP {status}")
    if status != 200:
        return steps, f"expected HTTP 200, got {status}"
    if data.get("status") != "STABLE":
        return steps, f"expected status=STABLE, got {data.get('status')}"
    steps.append("status == STABLE (outcome指定済みのため)")
    return steps, None


# ---------------------------------------------------------------------------
# 4.2 異常系
# ---------------------------------------------------------------------------
def case_missing_decision_id():
    steps = []
    status, data = _post(VASAI_FEEDBACK_URL, {
        "why": "test", "reason": "test", "decision_summary": "test",
    })
    steps.append(f"POST /phios/feedback (decision_id欠損) -> HTTP {status}")
    if status != 400:
        return steps, f"expected HTTP 400, got {status}"
    if "error" not in (data or {}):
        return steps, "expected 'error' key in response body"
    steps.append(f"400応答かつerrorフィールドあり: {data}")
    return steps, None


def case_invalid_json():
    steps = []
    status, _ = _post(VASAI_FEEDBACK_URL, b"not a json", raw=True)
    steps.append(f"POST /phios/feedback (不正JSON) -> HTTP {status}")
    if status >= 500:
        return steps, f"unexpected 500系エラー: {status}"
    steps.append("500系エラーは発生しない")
    return steps, None


def case_type_error_decision_id():
    steps = []
    status, data = _post(VASAI_FEEDBACK_URL, {
        "decision_id": 12345,  # 型エラー（本来str）
        "why": "test", "reason": "test", "decision_summary": "test",
    })
    steps.append(f"POST /phios/feedback (decision_idが数値) -> HTTP {status}")
    if status >= 500:
        return steps, f"unexpected 500系エラー: {status}"
    steps.append(f"500系エラーは発生しない (HTTP {status})")
    return steps, None


# ---------------------------------------------------------------------------
# 4.3 境界値
# ---------------------------------------------------------------------------
def case_empty_body():
    steps = []
    status, data = _post(VASAI_FEEDBACK_URL, {})
    steps.append(f"POST /phios/feedback (空データ) -> HTTP {status}")
    if status != 400:
        return steps, f"expected HTTP 400, got {status}"
    steps.append("空データは400で拒否される")
    return steps, None


def case_large_payload():
    steps = []
    status, data = _post(VASAI_FEEDBACK_URL, {
        "decision_id": "T_LAYER2_LARGE",
        "why": "x" * 100_000,
        "reason": "test", "decision_summary": "test",
    })
    steps.append(f"POST /phios/feedback (why=100,000文字) -> HTTP {status}")
    if status >= 500:
        return steps, f"unexpected 500系エラー: {status}"
    steps.append(f"最大サイズ入力でも500系エラーなし (HTTP {status})")
    return steps, None


def case_null_fields():
    steps = []
    status, data = _post(VASAI_FEEDBACK_URL, {
        "decision_id": "T_LAYER2_NULL",
        "why": None, "reason": None, "decision_summary": None,
    })
    steps.append(f"POST /phios/feedback (why/reason/decision_summary=null) -> HTTP {status}")
    if status >= 500:
        return steps, f"unexpected 500系エラー: {status}"
    steps.append(f"null入力でも500系エラーなし (HTTP {status})")
    return steps, None


# ---------------------------------------------------------------------------
# phi_os.PHIOS 側の入出力テスト
# ---------------------------------------------------------------------------
def case_phios_ingest():
    steps = []
    hub = PHIOS("mocka", "core", "001")
    result = hub.ingest("layer2_test", {"k": "v"})
    steps.append(f"PHIOS.ingest() -> {result}")
    if result.get("recorded") is not True:
        return steps, "ingest() did not report recorded=True"
    if result.get("node_id") != "phi-os-mocka-core-001":
        return steps, f"unexpected node_id: {result.get('node_id')}"
    steps.append("node_id命名規則 phi-os-{layer}-{product}-{instance} 準拠")
    return steps, None


def case_phios_sync_stable():
    steps = []
    hub = PHIOS("mocka", "core", "001")
    result = hub.sync("vasai", {
        "decision_id": "T_LAYER2_SYNC_STABLE",
        "why": "test", "reason": "test", "decision_summary": "test",
        "outcome": "success",
    })
    steps.append(f"PHIOS.sync('vasai', outcome付き) -> {result['status']} (loops={result['loop_count']})")
    if result["status"] != "STABLE":
        return steps, f"expected STABLE, got {result['status']}"
    if result["loop_count"] != 0:
        return steps, f"expected loop_count=0, got {result['loop_count']}"
    return steps, None


def case_phios_sync_loop_limit():
    steps = []
    hub = PHIOS("mocka", "core", "001")
    result = hub.sync("vasai", {
        "decision_id": "T_LAYER2_SYNC_LOOP",
        "why": "test", "reason": "test", "decision_summary": "test",
    })
    steps.append(f"PHIOS.sync('vasai', outcomeなし) -> {result['status']} (loops={result['loop_count']})")
    if result["status"] != "LOOP_LIMIT_REACHED":
        return steps, f"expected LOOP_LIMIT_REACHED, got {result['status']}"
    if result["loop_count"] != MAX_LOOP_COUNT + 1:
        return steps, f"expected loop_count=MAX_LOOP_COUNT+1={MAX_LOOP_COUNT+1}, got {result['loop_count']}"
    steps.append(f"MAX_LOOP_COUNT={MAX_LOOP_COUNT} 超過で停止を確認")
    return steps, None


def case_phios_sync_invalid_target():
    steps = []
    hub = PHIOS("mocka", "core", "001")
    try:
        hub.sync("not_vasai", {})
        return steps, "expected PHIOSError for target != 'vasai'"
    except PHIOSError as e:
        steps.append(f"target!='vasai' でPHIOSError送出を確認: {e}")
    return steps, None


def main():
    cases = [
        ("4.1 正常リクエスト(CONTINUE)", case_normal_continue),
        ("4.1 正常リクエスト(STABLE)", case_normal_stable),
        ("4.2 欠損パラメータ(decision_id)", case_missing_decision_id),
        ("4.2 不正JSON入力", case_invalid_json),
        ("4.2 型エラー(decision_id=数値)", case_type_error_decision_id),
        ("4.3 境界値(空データ)", case_empty_body),
        ("4.3 境界値(最大サイズ)", case_large_payload),
        ("4.3 境界値(null入力)", case_null_fields),
        ("PHIOS.ingest() 入出力", case_phios_ingest),
        ("PHIOS.sync('vasai') STABLE", case_phios_sync_stable),
        ("PHIOS.sync('vasai') LOOP_LIMIT_REACHED", case_phios_sync_loop_limit),
        ("PHIOS.sync(target!='vasai') 異常系", case_phios_sync_invalid_target),
    ]

    for name, fn in cases:
        run_case(name, fn)

    total = len(_results)
    skipped = sum(1 for _, ok, _ in _results if ok is None)
    judged = total - skipped
    passed = sum(1 for _, ok, _ in _results if ok is True)
    rate = (passed / judged * 100) if judged else 100.0

    print("=" * 60)
    print(f"  PHI-OS Layer2 テスト結果: {passed}/{judged} PASS ({rate:.1f}%)  SKIP={skipped}")
    print("=" * 60)
    for name, ok, reason in _results:
        mark = "PASS" if ok is True else ("SKIP" if ok is None else "FAIL")
        line = f"  [{mark}] {name}"
        if ok is not True:
            line += f"  - {reason}"
        print(line)

    # spec 7章: Layer2は95%以上成功でPASS（環境依存SKIPは判定対象外）
    sys.exit(0 if rate >= 95.0 else 1)


if __name__ == "__main__":
    main()
