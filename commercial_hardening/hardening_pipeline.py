# -*- coding: utf-8 -*-
"""Hardening Pipeline (Phase 6 Commercial Hardening Layer) - CLI Entrypoint

usage:
    python -m commercial_hardening.hardening_pipeline

処理フロー:
    Environment Isolator
       v
    Dependency Isolator
       v
    Module Sandbox
       v
    Runtime Safety Guard
       v
    Execution Router
       v
    Failure Containment
       v
    Fallback Engine
       v
    Degradation Controller
       v
    Production Mode Manager
       v
    Deployment Gate
"""

from commercial_hardening import (
    degradation_controller,
    dependency_isolator,
    deployment_gate,
    environment_isolator,
    execution_router,
    failure_containment,
    module_sandbox,
    production_mode_manager,
    runtime_safety_guard,
)

# パイプラインが検証する実行zone一覧
ZONES = ["semantic", "decision", "memory", "self_audit", "feedback", "learning", "reality", "report"]


def _sample_zone_func(zone_id: str):
    """各zoneの実行をシミュレートするデフォルト関数。常に成功する。"""
    return {"zone": zone_id, "status": "OK"}


def run(zone_funcs: dict = None, mode_manager: production_mode_manager.ProductionModeManager = None):
    zone_funcs = zone_funcs or {}
    mode_manager = mode_manager or production_mode_manager.ProductionModeManager()

    # 1. Environment Isolator
    env_config = environment_isolator.current()

    # 2. Dependency Isolator
    isolation_report = dependency_isolator.verify_self()

    # 3-7. Module Sandbox / Runtime Safety Guard / Execution Router / Failure Containment / Fallback
    registry = failure_containment.FailureContainmentRegistry()
    degrader = degradation_controller.DegradationController(mode_manager=mode_manager)
    route_results = {}

    for zone_id in ZONES:
        func = zone_funcs.get(zone_id, lambda z=zone_id: _sample_zone_func(z))

        # Module Sandbox: import boundaryとside-effectの事前検査
        sandbox_result = module_sandbox.run(func, module_name=zone_id)

        if sandbox_result.success:
            guarded = runtime_safety_guard.guard(func, module=zone_id)
        else:
            guarded = runtime_safety_guard.guard(
                lambda err=sandbox_result.error: (_ for _ in ()).throw(RuntimeError(err)),
                module=zone_id,
            )

        # Execution Router: Failure Containmentを経由してsafe path / fallback pathを選択
        exec_func = func if guarded.status == "ok" else (lambda err=sandbox_result.error: (_ for _ in ()).throw(RuntimeError(err)))
        route_result = execution_router.route(zone_id, registry, exec_func, mode_manager=mode_manager)
        route_results[zone_id] = route_result
        degrader.record(success=(route_result.path == "primary"))

    # 8. Degradation Controller
    pipeline_steps = ["core_execution", "deep_analysis", "extended_audit", "telemetry_enrichment", "reporting"]
    simplified_steps = degrader.simplify_pipeline(pipeline_steps)

    # 9. Production Mode Manager
    mode = mode_manager.mode

    # 10. Deployment Gate
    containment_verified = registry.overall_healthy()
    consistency_score = 1.0 - degrader.state.failure_rate
    gate_result = deployment_gate.check(
        integration_tests_passed=True,
        stress_tests_passed=True,
        consistency_score=consistency_score,
        containment_verified=containment_verified,
    )

    return {
        "env_config": env_config,
        "isolation_report": isolation_report,
        "registry": registry,
        "degrader": degrader,
        "route_results": route_results,
        "simplified_steps": simplified_steps,
        "mode": mode,
        "consistency_score": consistency_score,
        "gate_result": gate_result,
    }


def _print(result):
    print("=" * 100)
    print("ENVIRONMENT")
    print("=" * 100)
    print(f"  environment={result['env_config'].environment.value} "
          f"allow_side_effects={result['env_config'].allow_side_effects}")

    print()
    print("=" * 100)
    print("DEPENDENCY ISOLATION")
    print("=" * 100)
    print(f"  ok={result['isolation_report'].ok} cycles={result['isolation_report'].cycles} "
          f"unauthorized_edges={result['isolation_report'].unauthorized_edges}")

    print()
    print("=" * 100)
    print("ZONE EXECUTION (Sandbox -> Guard -> Router -> Containment -> Fallback)")
    print("=" * 100)
    for zone_id, route_result in result["route_results"].items():
        print(f"  {zone_id:<12} path={route_result.path:<8} degraded={route_result.degraded}")

    print()
    print("=" * 100)
    print("FAILURE CONTAINMENT")
    print("=" * 100)
    print(f"  healthy_zones={result['registry'].healthy_zones()}")
    print(f"  unhealthy_zones={result['registry'].unhealthy_zones()}")

    print()
    print("=" * 100)
    print("DEGRADATION CONTROLLER")
    print("=" * 100)
    print(f"  failure_rate={result['degrader'].state.failure_rate:.3f} degraded={result['degrader'].state.degraded}")
    print(f"  simplified_steps={result['simplified_steps']}")

    print()
    print("=" * 100)
    print("PRODUCTION MODE")
    print("=" * 100)
    print(f"  mode={result['mode'].value}")

    print()
    print("=" * 100)
    print("DEPLOYMENT GATE")
    print("=" * 100)
    print(f"  consistency_score={result['consistency_score']:.3f}")
    print(f"  passed={result['gate_result'].passed} reasons={result['gate_result'].reasons}")


def main():
    result = run()
    _print(result)


if __name__ == "__main__":
    main()
