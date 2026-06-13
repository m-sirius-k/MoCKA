# -*- coding: utf-8 -*-
"""Production Mode Manager (Phase 6 Commercial Hardening Layer)

モード:
  - SAFE_MODE (default)  : 全ての安全機構を最大適用。性能は最低保証ライン。
  - BALANCED_MODE        : 安全機構を保持しつつ通常性能で動作。
  - PERFORMANCE_MODE     : 安全機構の一部 (非致命的チェック) を省略する。explicit opt-inのみ。

safety is default: set_mode(PERFORMANCE_MODE) は allow_unsafe=True を
明示しない限り拒否される。
"""

from dataclasses import dataclass
from enum import Enum


class Mode(Enum):
    SAFE_MODE = "SAFE_MODE"
    BALANCED_MODE = "BALANCED_MODE"
    PERFORMANCE_MODE = "PERFORMANCE_MODE"


@dataclass
class ModeState:
    mode: Mode = Mode.SAFE_MODE


class UnsafeModeRejected(Exception):
    """PERFORMANCE_MODEがallow_unsafe=Trueなしで要求された場合に投げられる。"""


class ProductionModeManager:
    def __init__(self):
        self._state = ModeState()

    @property
    def mode(self) -> Mode:
        return self._state.mode

    def set_mode(self, mode: Mode, allow_unsafe: bool = False) -> ModeState:
        if mode == Mode.PERFORMANCE_MODE and not allow_unsafe:
            raise UnsafeModeRejected("PERFORMANCE_MODE requires explicit allow_unsafe=True (opt-in)")
        self._state = ModeState(mode=mode)
        return self._state

    def is_safe(self) -> bool:
        return self._state.mode in (Mode.SAFE_MODE, Mode.BALANCED_MODE)

    def skip_nonfatal_checks(self) -> bool:
        """非致命的チェック(性能寄与の安全チェック)を省略してよいか。PERFORMANCE_MODEのみTrue。"""
        return self._state.mode == Mode.PERFORMANCE_MODE

    def reset(self):
        self._state = ModeState()
