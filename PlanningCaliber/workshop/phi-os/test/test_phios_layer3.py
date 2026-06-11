"""
PHI-OS実機テスト Layer3: View Engine テスト
PHI-OS Test Spec v1.0 (TODO_205) Layer3実装。
PHI-OS-SPEC-001 第6章準拠。

ログ形式: TEST_START / TEST_STEP / TEST_RESULT / TEST_FAIL_REASON / TEST_END

実行方法:
  vasAI(localhost:6000) と MoCKA(localhost:5002)を起動した状態で実行する。
    python C:/Users/sirok/MoCKA/PlanningCaliber/workshop/phi-os/test/test_phios_layer3.py
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from phi_os import PHIOS, PHIOSError  # noqa: E402
from phi_os_state import DATA_ROOT  # noqa: E402
from phi_os_view import HIGH_DENSITY_THRESHOLD  # noqa: E402

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
# default視点
# ---------------------------------------------------------------------------
def case_view_default():
    steps = []
    node_id = "phi-os-test-view3-001"
    _clean(node_id)
    hub = PHIOS("test", "view3", "001")
    hub.ingest("source_a", {"k1": "v1"})

    view = hub.generate_view("default")
    steps.append(f"default view: {view}")
    if view["view_type"] != "default":
        return steps, f"expected view_type=default, got {view['view_type']}"
    if "semantic_map" not in view:
        return steps, "default viewにsemantic_mapが含まれない"
    if "source_a" not in view["semantic_map"]:
        return steps, "semantic_mapにsource_aが含まれない"

    _clean(node_id)
    return steps, None


# ---------------------------------------------------------------------------
# risk視点: high_density検知
# ---------------------------------------------------------------------------
def case_view_risk_high_density():
    steps = []
    node_id = "phi-os-test-view3-002"
    _clean(node_id)
    hub = PHIOS("test", "view3", "002")

    n = HIGH_DENSITY_THRESHOLD + 1
    for i in range(n):
        hub.ingest("hot_source", {"i": i})

    view = hub.generate_view("risk")
    steps.append(f"risk view: density={view['density']}, high_density={view['high_density']}")
    if view["view_type"] != "risk":
        return steps, f"expected view_type=risk, got {view['view_type']}"
    if view["density"].get("hot_source") != n:
        return steps, f"expected density['hot_source']={n}, got {view['density'].get('hot_source')}"
    if "hot_source" not in view["high_density"]:
        return steps, f"hot_source(書込み{n}回 > 閾値{HIGH_DENSITY_THRESHOLD})がhigh_densityに含まれない"

    _clean(node_id)
    return steps, None


# ---------------------------------------------------------------------------
# fusion視点: 複数ソースのマージ＋差異抽出
# ---------------------------------------------------------------------------
def case_view_fusion_merge_and_diff():
    steps = []
    node_id = "phi-os-test-view3-003"
    _clean(node_id)
    hub = PHIOS("test", "view3", "003")

    hub.ingest("source_a", {"shared_key": "from_a", "only_a": 1})
    hub.ingest("source_b", {"shared_key": "from_b", "only_b": 2})

    view = hub.generate_view("fusion")
    steps.append(f"fusion view: merged={view['merged']}, diffs={view['diffs']}")
    if view["view_type"] != "fusion":
        return steps, f"expected view_type=fusion, got {view['view_type']}"
    if view["merged"].get("only_a") != 1 or view["merged"].get("only_b") != 2:
        return steps, "mergedに各ソース固有キーが含まれない"
    if "shared_key" not in view["diffs"]:
        return steps, "shared_keyの値差異がdiffsに抽出されない"

    _clean(node_id)
    return steps, None


# ---------------------------------------------------------------------------
# timeline視点: raw_store全件の時系列整列
# ---------------------------------------------------------------------------
def case_view_timeline():
    steps = []
    node_id = "phi-os-test-view3-004"
    _clean(node_id)
    hub = PHIOS("test", "view3", "004")

    hub.ingest("source_a", {"v": 1})
    hub.ingest("source_b", {"v": 2})
    hub.ingest("source_a", {"v": 3})

    view = hub.generate_view("timeline")
    steps.append(f"timeline view events count: {len(view['events'])}")
    if view["view_type"] != "timeline":
        return steps, f"expected view_type=timeline, got {view['view_type']}"
    if len(view["events"]) != 3:
        return steps, f"expected 3 events, got {len(view['events'])}"
    timestamps = [e["ts"] for e in view["events"]]
    if timestamps != sorted(timestamps):
        return steps, "eventsが時系列順に整列されていない"
    steps.append("eventsが時系列順に整列されていることを確認")

    _clean(node_id)
    return steps, None


# ---------------------------------------------------------------------------
# キャッシュinvalidateテスト
# ---------------------------------------------------------------------------
def case_view_cache_invalidate():
    steps = []
    node_id = "phi-os-test-view3-005"
    _clean(node_id)
    hub = PHIOS("test", "view3", "005")

    hub.ingest("source_a", {"v": 1})
    view1 = hub.generate_view("timeline")
    steps.append(f"1回目 timeline events: {len(view1['events'])}")

    hub.ingest("source_a", {"v": 2})
    view2 = hub.generate_view("timeline")
    steps.append(f"raw_store更新後 timeline events: {len(view2['events'])}")

    if len(view2["events"]) != len(view1["events"]) + 1:
        return steps, "raw_store更新後にviewキャッシュがinvalidateされていない"
    steps.append("raw_store更新でviewキャッシュが自動invalidateされたことを確認")

    _clean(node_id)
    return steps, None


# ---------------------------------------------------------------------------
# UNKNOWN_VIEW_TYPEエラー記録テスト
# ---------------------------------------------------------------------------
def case_unknown_view_type():
    steps = []
    node_id = "phi-os-test-view3-006"
    _clean(node_id)
    hub = PHIOS("test", "view3", "006")

    try:
        hub.generate_view("no_such_view")
        return steps, "PHIOSErrorが送出されなかった"
    except PHIOSError as e:
        steps.append(f"未知のview_typeでPHIOSError送出を確認: {e}")

    _clean(node_id)
    return steps, None


def main():
    cases = [
        ("default視点: semantic_map標準出力", case_view_default),
        ("risk視点: high_density検知", case_view_risk_high_density),
        ("fusion視点: 意味マージ＋差異抽出", case_view_fusion_merge_and_diff),
        ("timeline視点: raw_store時系列整列", case_view_timeline),
        ("viewキャッシュinvalidateテスト", case_view_cache_invalidate),
        ("UNKNOWN_VIEW_TYPEエラー記録テスト", case_unknown_view_type),
    ]

    for name, fn in cases:
        run_case(name, fn)

    total = len(_results)
    passed = sum(1 for _, ok, _ in _results if ok is True)
    rate = (passed / total * 100) if total else 100.0

    print("=" * 60)
    print(f"  PHI-OS Layer3 テスト結果: {passed}/{total} PASS ({rate:.1f}%)")
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
