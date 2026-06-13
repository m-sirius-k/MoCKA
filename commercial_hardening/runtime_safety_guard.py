# -*- coding: utf-8 -*-
"""Runtime Safety Guard (Phase 6 Commercial Hardening Layer)

制御:
  - exception capture     : 任意の例外を捕捉する
  - panic containment      : 例外が呼び出し元に伝播しない
  - graceful degradation   : 失敗時はfallback_modeへ遷移する

ルール (ANY_FAILURE -> fallback_mode):
  guard()でラップされた呼び出しが例外を発生させた場合、
  GuardResult.status は必ず "fallback_mode" になる。
"""

from dataclasses import dataclass, field

from commercial_hardening import safe_fallback_engine


@dataclass
class GuardResult:
    status: str  # "ok" | "fallback_mode"
    value: object = None
    error: str = ""
    fallback: object = None


def guard(func, module: str = "unknown", fallback_kind: str = "default") -> GuardResult:
    """funcを実行する。成功時はstatus="ok"、例外発生時は ANY_FAILURE -> fallback_mode。"""
    try:
        value = func()
        return GuardResult(status="ok", value=value)
    except Exception as exc:  # noqa: BLE001 - panic containment境界
        fb = safe_fallback_engine.fallback(module, fallback_kind, reason=repr(exc))
        return GuardResult(status="fallback_mode", error=repr(exc), fallback=fb)


@dataclass
class GuardedPipelineResult:
    results: list = field(default_factory=list)
    fallback_count: int = 0

    @property
    def all_ok(self) -> bool:
        return self.fallback_count == 0


def guard_pipeline(steps: list) -> GuardedPipelineResult:
    """steps: list[(name, callable)] を順に guard() で実行する。
    1ステップが fallback_mode に入っても残りのステップは継続して実行される
    (panic containment: 1ステップの失敗が全体を停止させない)。
    """
    pipeline_result = GuardedPipelineResult()
    for name, func in steps:
        result = guard(func, module=name)
        pipeline_result.results.append((name, result))
        if result.status == "fallback_mode":
            pipeline_result.fallback_count += 1
    return pipeline_result
