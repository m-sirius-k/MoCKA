# -*- coding: utf-8 -*-
"""Hardening Integration Test (Phase 6 Commercial Hardening Layer)

usage:
    python -m commercial_hardening.hardening_integration_test

必須確認項目:
  1. environment isolation動作   - RuntimeConfigが固定化され、prod相当ではside-effectが遮断される
  2. dependency isolation動作    - ALLOWED_DEPENDENCIESに循環・未承認依存が無い
  3. module sandbox enforcement  - import boundary違反がblockedとして検出される
  4. runtime safety guard動作    - ANY_FAILURE -> fallback_mode
  5. failure containment動作     - 1zoneの障害が他zoneに伝播しない
  6. execution router動作        - unhealthy zoneはfallback pathを返す
  7. degradation controller動作  - failure_rate>=閾値でdegraded=Trueかつoptional step除外
  8. production mode manager動作 - PERFORMANCE_MODEはallow_unsafeなしで拒否される
  9. deployment gate動作          - 全条件PASSでgate.passed=True、1条件NGでFalse
  10. end-to-end pipeline動作     - hardening_pipeline.run()が例外を出さず完了する
"""

from commercial_hardening import (
    degradation_controller,
    dependency_isolator,
    deployment_gate,
    environment_isolator,
    execution_router,
    failure_containment,
    hardening_pipeline,
    module_sandbox,
    production_mode_manager,
    runtime_safety_guard,
)


def test_environment_isolation():
    environment_isolator.reset()
    cfg1 = environment_isolator.load_config(environment_isolator.Environment.PROD)
    cfg2 = environment_isolator.current()
    assert cfg1 is cfg2, "RuntimeConfigが固定化されていない"
    assert cfg1.allow_side_effects is False, "PRODでside-effectが許可されている"

    try:
        environment_isolator.guard_side_effect("test_write")
        raised = False
    except environment_isolator.SideEffectBlocked:
        raised = True
    assert raised, "PRODでside-effectがブロックされない"
    environment_isolator.reset()
    print("[PASS] test_environment_isolation")


def test_dependency_isolation():
    report = dependency_isolator.verify_self()
    assert report.ok, f"ALLOWED_DEPENDENCIESに問題: cycles={report.cycles} unauthorized={report.unauthorized_edges}"
    print("[PASS] test_dependency_isolation")


def test_module_sandbox_import_boundary():
    result = module_sandbox.run(lambda: 1, module_name="dependency_isolator", caller="deployment_gate")
    assert result.blocked, "deployment_gate -> dependency_isolatorはALLOWED_DEPENDENCIESに無いがblockedされない"

    result_ok = module_sandbox.run(lambda: 1, module_name="safe_fallback_engine", caller="failure_containment")
    assert result_ok.success and not result_ok.blocked, "許可された依存がblockedされた"
    print("[PASS] test_module_sandbox_import_boundary")


def test_runtime_safety_guard():
    def boom():
        raise ValueError("forced crash")

    result = runtime_safety_guard.guard(boom, module="test_module")
    assert result.status == "fallback_mode", f"ANY_FAILURE -> fallback_modeルール違反: status={result.status}"
    assert result.fallback is not None

    ok_result = runtime_safety_guard.guard(lambda: 42, module="test_module")
    assert ok_result.status == "ok" and ok_result.value == 42
    print("[PASS] test_runtime_safety_guard")


def test_failure_containment_no_cascade():
    registry = failure_containment.FailureContainmentRegistry()

    def boom():
        raise RuntimeError("zone A crash")

    registry.contain("zone_a", boom)
    assert "zone_a" in registry.unhealthy_zones()

    # zone_bはzone_aの障害と独立して正常動作すること
    result_b = registry.contain("zone_b", lambda: "ok")
    assert result_b == "ok"
    assert "zone_b" in registry.healthy_zones()
    assert "zone_b" not in registry.unhealthy_zones()
    print("[PASS] test_failure_containment_no_cascade")


def test_execution_router_fallback():
    registry = failure_containment.FailureContainmentRegistry()
    registry.contain("zone_x", lambda: (_ for _ in ()).throw(RuntimeError("down")))

    route_result = execution_router.route("zone_x", registry, lambda: "should not run")
    assert route_result.path == "fallback" and route_result.degraded is True

    route_result_ok = execution_router.route("zone_y", registry, lambda: "value")
    assert route_result_ok.path == "primary" and route_result_ok.value == "value"
    print("[PASS] test_execution_router_fallback")


def test_degradation_controller():
    controller = degradation_controller.DegradationController()
    for _ in range(7):
        controller.record(success=True)
    for _ in range(3):
        controller.record(success=False)

    assert controller.state.degraded, f"failure_rate={controller.state.failure_rate}でdegraded=Falseのまま"
    simplified = controller.simplify_pipeline(["core_execution", "deep_analysis", "reporting"])
    assert "deep_analysis" not in simplified, "degraded時にoptional stepが除外されない"
    assert controller.should_shed("low") is True
    assert controller.should_shed("high") is False
    print("[PASS] test_degradation_controller")


def test_production_mode_manager_safety_default():
    manager = production_mode_manager.ProductionModeManager()
    assert manager.mode == production_mode_manager.Mode.SAFE_MODE, "デフォルトがSAFE_MODEでない"

    try:
        manager.set_mode(production_mode_manager.Mode.PERFORMANCE_MODE)
        rejected = False
    except production_mode_manager.UnsafeModeRejected:
        rejected = True
    assert rejected, "PERFORMANCE_MODEがallow_unsafeなしで許可された"

    manager.set_mode(production_mode_manager.Mode.PERFORMANCE_MODE, allow_unsafe=True)
    assert manager.mode == production_mode_manager.Mode.PERFORMANCE_MODE
    print("[PASS] test_production_mode_manager_safety_default")


def test_deployment_gate():
    passing = deployment_gate.check(True, True, 0.9, True)
    assert passing.passed

    failing = deployment_gate.check(True, True, 0.5, True)
    assert not failing.passed and "consistency score" in failing.reasons[0]
    print("[PASS] test_deployment_gate")


def test_end_to_end_pipeline():
    result = hardening_pipeline.run()
    assert result["gate_result"].passed, f"正常系でgateがFAIL: {result['gate_result'].reasons}"
    assert result["isolation_report"].ok
    print("[PASS] test_end_to_end_pipeline")


def run_all():
    tests = [
        test_environment_isolation,
        test_dependency_isolation,
        test_module_sandbox_import_boundary,
        test_runtime_safety_guard,
        test_failure_containment_no_cascade,
        test_execution_router_fallback,
        test_degradation_controller,
        test_production_mode_manager_safety_default,
        test_deployment_gate,
        test_end_to_end_pipeline,
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
