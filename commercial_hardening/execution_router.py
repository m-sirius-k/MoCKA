# -*- coding: utf-8 -*-
"""Execution Router (Phase 6 Commercial Hardening Layer)

制御:
  - safe path selection     : zoneがhealthyならprimary実行パスを選ぶ
  - fallback routing         : zoneがunhealthy、またはprimary実行が失敗したらfallbackへ
  - degraded execution path  : production_mode_managerがSAFE/BALANCEDの場合は
    fallback結果を degraded=True として明示する
"""

from dataclasses import dataclass

from commercial_hardening import failure_containment, production_mode_manager, safe_fallback_engine


@dataclass
class RouteResult:
    path: str  # "primary" | "fallback"
    value: object
    degraded: bool = False


def route(zone_id: str, registry: failure_containment.FailureContainmentRegistry,
          primary_func, fallback_kind: str = "default",
          mode_manager: production_mode_manager.ProductionModeManager = None) -> RouteResult:
    """zoneの健全性に基づき primary/fallback パスを選択して実行する。"""
    mode_manager = mode_manager or production_mode_manager.ProductionModeManager()
    zone = registry.get(zone_id)

    if not zone.healthy:
        fb = safe_fallback_engine.fallback(zone_id, fallback_kind, reason="zone unhealthy")
        return RouteResult(path="fallback", value=fb, degraded=True)

    result = registry.contain(zone_id, primary_func, fallback_kind=fallback_kind)

    if isinstance(result, safe_fallback_engine.FallbackResult):
        return RouteResult(path="fallback", value=result, degraded=True)

    return RouteResult(path="primary", value=result, degraded=False)
