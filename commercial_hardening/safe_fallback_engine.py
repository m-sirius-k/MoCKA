# -*- coding: utf-8 -*-
"""Safe Fallback Engine (Phase 6 Commercial Hardening Layer)

役割:
  - partial failure時の代替ロジックを提供する
  - minimal output を保証する (空でも構造を満たすdict/値)
  - degraded but stable な応答を返す

このモジュールは失敗しない。どんな入力でも必ず何らかの値を返す。
"""

from dataclasses import dataclass, field


@dataclass
class FallbackResult:
    module: str
    value: object
    degraded: bool = True
    reason: str = ""


# モジュール名ごとのminimal output定義
_MINIMAL_OUTPUTS = {
    "default": {},
    "list": [],
    "score": 0.0,
    "status": "DEGRADED",
}


def minimal_output(kind: str = "default"):
    return _MINIMAL_OUTPUTS.get(kind, _MINIMAL_OUTPUTS["default"])


def fallback(module: str, kind: str = "default", reason: str = "upstream failure") -> FallbackResult:
    """与えられたモジュール用のminimal/stableな代替結果を返す。"""
    return FallbackResult(module=module, value=minimal_output(kind), degraded=True, reason=reason)


def wrap_with_fallback(func, module: str, kind: str = "default", reason_prefix: str = "exception"):
    """func()を実行し、失敗時はFallbackResultを返す。成功時はその値をそのまま返す。"""
    try:
        return func()
    except Exception as exc:  # noqa: BLE001 - フォールバック境界として意図的に広く捕捉
        return fallback(module, kind, reason=f"{reason_prefix}: {exc!r}")
