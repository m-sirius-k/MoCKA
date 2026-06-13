# -*- coding: utf-8 -*-
"""Hardening Stress Test (Phase 6 Commercial Hardening Layer)

usage:
    python -m commercial_hardening.hardening_stress_test

必須確認項目:
  1. forced crash injection      - 全zoneの一部をクラッシュさせてもpipelineは完了する
  2. dependency loop simulation   - 循環依存を含むedgesがcyclesとして検出される
  3. memory leak simulation        - 大量データ蓄積でもregistryが例外を出さず動作する
  4. partial system failure        - 半数のzoneが失敗してもgate判定が破綻なく返る
  5. concurrent stress execution   - 複数threadから同時にpipelineを実行しても破綻しない
"""

import threading

from commercial_hardening import dependency_isolator, hardening_pipeline, production_mode_manager


def test_forced_crash_injection():
    """全zoneのうち一部を強制クラッシュさせてもpipeline全体は完了する (SYSTEM_NEVER_BREAKS)。"""
    crash_zones = {"decision", "feedback", "report"}

    def make_func(zone_id):
        if zone_id in crash_zones:
            def crashing():
                raise RuntimeError(f"forced crash: {zone_id}")
            return crashing
        return lambda z=zone_id: {"zone": z, "status": "OK"}

    zone_funcs = {z: make_func(z) for z in hardening_pipeline.ZONES}

    result = hardening_pipeline.run(zone_funcs=zone_funcs)

    for zone_id in crash_zones:
        assert result["route_results"][zone_id].path == "fallback", f"{zone_id} がfallbackしていない"
    for zone_id in set(hardening_pipeline.ZONES) - crash_zones:
        assert result["route_results"][zone_id].path == "primary", f"{zone_id} が不要にfallbackしている"

    assert not result["registry"].overall_healthy()
    print(f"[PASS] test_forced_crash_injection (crashed={sorted(crash_zones)}, "
          f"gate_passed={result['gate_result'].passed})")


def test_dependency_loop_simulation():
    """循環依存を持つedgesを与えた場合、check_edgesがcyclesを検出すること。"""
    looped_edges = {
        "a": {"b"},
        "b": {"c"},
        "c": {"a"},
    }
    # 全edgeをALLOWED_DEPENDENCIESに無い形で与えるため unauthorized_edgesも検出される想定
    report = dependency_isolator.check_edges(looped_edges)
    assert report.cycles, "循環依存が検出されない"
    assert any(set(cycle) == {"a", "b", "c"} for cycle in [c[:-1] for c in report.cycles]), \
        f"検出されたcycleが期待した循環と一致しない: {report.cycles}"
    print(f"[PASS] test_dependency_loop_simulation (cycles={report.cycles})")


def test_memory_leak_simulation():
    """registryに大量のzoneとfailure履歴を蓄積してもエラーなく動作すること。"""
    from commercial_hardening import failure_containment

    registry = failure_containment.FailureContainmentRegistry()
    n = 5000
    for i in range(n):
        zone_id = f"leak_zone_{i % 50}"
        if i % 7 == 0:
            registry.contain(zone_id, lambda: (_ for _ in ()).throw(RuntimeError("leak crash")))
        else:
            registry.contain(zone_id, lambda: "ok")

    assert len(registry._zones) == 50, f"zone数が期待値と異なる: {len(registry._zones)}"
    total_failures = sum(z.failure_count for z in registry._zones.values())
    assert total_failures > 0
    print(f"[PASS] test_memory_leak_simulation (zones={len(registry._zones)}, total_failures={total_failures})")


def test_partial_system_failure():
    """zoneの半数を失敗させてもdeployment_gateが例外を出さず判定を返すこと。"""
    failing = set(hardening_pipeline.ZONES[: len(hardening_pipeline.ZONES) // 2])

    def make_func(zone_id):
        if zone_id in failing:
            def crashing():
                raise RuntimeError(f"partial failure: {zone_id}")
            return crashing
        return lambda z=zone_id: {"zone": z, "status": "OK"}

    zone_funcs = {z: make_func(z) for z in hardening_pipeline.ZONES}
    result = hardening_pipeline.run(zone_funcs=zone_funcs)

    assert result["gate_result"].passed is False, "半数失敗時にgateがPASSしてしまう"
    assert result["degrader"].state.degraded, "失敗率が高いのにdegraded=Falseのまま"
    assert "deep_analysis" not in result["simplified_steps"]
    print(f"[PASS] test_partial_system_failure (failing={sorted(failing)}, "
          f"failure_rate={result['degrader'].state.failure_rate:.2f})")


def test_concurrent_stress_execution():
    """複数threadから同時にpipelineを実行しても例外を出さず完了すること。"""
    errors = []
    results = []
    lock = threading.Lock()

    def worker(idx):
        try:
            mode_manager = production_mode_manager.ProductionModeManager()
            res = hardening_pipeline.run(mode_manager=mode_manager)
            with lock:
                results.append(res["gate_result"].passed)
        except Exception as exc:  # noqa: BLE001
            with lock:
                errors.append(repr(exc))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"concurrent実行中に例外発生: {errors}"
    assert len(results) == 20
    assert all(results), "正常系concurrent実行でgateがFAILした"
    print(f"[PASS] test_concurrent_stress_execution (threads=20, all_passed={all(results)})")


def run_all():
    tests = [
        test_forced_crash_injection,
        test_dependency_loop_simulation,
        test_memory_leak_simulation,
        test_partial_system_failure,
        test_concurrent_stress_execution,
    ]
    failures = []
    for t in tests:
        try:
            t()
        except AssertionError as exc:
            failures.append((t.__name__, str(exc)))
            print(f"[FAIL] {t.__name__}: {exc}")

    print()
    print(f"RESULT: {len(tests) - len(failures)}/{len(tests)} PASSED")
    return not failures


if __name__ == "__main__":
    import sys
    sys.exit(0 if run_all() else 1)
