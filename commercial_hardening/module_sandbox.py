# -*- coding: utf-8 -*-
"""Module Sandbox (Phase 6 Commercial Hardening Layer)

役割:
  - module execution isolation : 各モジュール呼び出しを独立した実行コンテキストで行う
  - import boundary enforcement : dependency_isolator.ALLOWED_DEPENDENCIES に
    存在しないモジュール名からの呼び出しを拒否する
  - side-effect detection       : prod環境でside-effectを伴う実行を検出・遮断する
    (environment_isolator.guard_side_effect連携)
"""

from dataclasses import dataclass

from commercial_hardening import dependency_isolator, environment_isolator


@dataclass
class SandboxResult:
    success: bool
    value: object = None
    error: str = ""
    blocked: bool = False


def run(func, *, module_name: str, caller: str = None, has_side_effect: bool = False) -> SandboxResult:
    """funcをサンドボックス内で実行する。

    - caller が指定されている場合、import boundary を enforcement する
      (caller -> module_name が ALLOWED_DEPENDENCIES に存在しなければ blocked)
    - has_side_effect=True の場合、現在の環境でside-effectが許可されているか確認する
    """
    if caller is not None:
        allowed = dependency_isolator.ALLOWED_DEPENDENCIES.get(caller, set())
        if module_name not in allowed:
            return SandboxResult(success=False, blocked=True,
                                  error=f"import boundary violation: {caller} -> {module_name}")

    if has_side_effect:
        try:
            environment_isolator.guard_side_effect(module_name)
        except environment_isolator.SideEffectBlocked as exc:
            return SandboxResult(success=False, blocked=True, error=str(exc))

    try:
        value = func()
        return SandboxResult(success=True, value=value)
    except Exception as exc:  # noqa: BLE001 - module isolation境界
        return SandboxResult(success=False, error=repr(exc))
