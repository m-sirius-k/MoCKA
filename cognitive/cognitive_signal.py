# cognitive/cognitive_signal.py
# MoCKA v1.2 — Cognitive Signal
# 責務: PHI-OSへの「傾向シグナル」を生成・出力する
# 設計原則: PHI-OSを書き換えない。シグナルファイルをPHI-OSが任意参照する形式。
# PHI-OSへの強制はない。routing確率の「参考値」としてのみ機能する。

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from cognitive.cognitive_loop_engine import CognitiveState


# ─────────────────────────────────────────────────────────────
# SignalLevel — PHI-OSへの傾向ヒント
# ─────────────────────────────────────────────────────────────

class SignalLevel(str, Enum):
    STABLE         = "STABLE"          # 安定。routing変更不要
    MODERATE_DRIFT = "MODERATE_DRIFT"  # 軽度乖離。注視推奨
    HIGH_DRIFT     = "HIGH_DRIFT"      # 高乖離。ROUTE増加傾向
    PHI_BIAS       = "PHI_BIAS"        # PHI偏重。TAG増加傾向
    PERSONAL_BIAS  = "PERSONAL_BIAS"   # PERSONAL偏重。OBSERVE増加傾向


# PHI-OSへのrouting傾向ヒント（強制ではなく参考値）
SIGNAL_ROUTING_HINT: Dict[SignalLevel, str] = {
    SignalLevel.STABLE:         "routing維持",
    SignalLevel.MODERATE_DRIFT: "OBSERVE増加傾向",
    SignalLevel.HIGH_DRIFT:     "ROUTE増加傾向",
    SignalLevel.PHI_BIAS:       "TAG増加傾向",
    SignalLevel.PERSONAL_BIAS:  "OBSERVE増加傾向",
}


# ─────────────────────────────────────────────────────────────
# CognitiveSignal
# ─────────────────────────────────────────────────────────────

class CognitiveSignal:
    """
    CognitiveLoopEngineが生成したシグナルを
    data/cognitive_signal.json に書き出す。
    PHI-OS（event_gate.py等）は起動時にこのファイルを任意参照できる。
    """

    SIGNAL_PATH = Path(__file__).resolve().parent.parent / "data" / "cognitive_signal.json"

    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path or self.SIGNAL_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, level: SignalLevel, state: "CognitiveState") -> None:
        """シグナルファイルを更新する（最新状態のみ保持）。"""
        payload: Dict[str, Any] = {
            "signal":       level.value,
            "routing_hint": SIGNAL_ROUTING_HINT[level],
            "drift":        state.drift,
            "drift_growth": state.drift_growth,
            "bias":         state.bias,
            "stability":    state.stability,
            "emitted_at":   datetime.now(timezone.utc).isoformat(),
        }
        self._path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def read(self) -> Optional[Dict[str, Any]]:
        """現在のシグナルを読む。PHI-OSが参照するインターフェース。"""
        if not self._path.exists():
            return None
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def current_level(self) -> Optional[SignalLevel]:
        """現在のSignalLevelを返す。存在しない場合はNone。"""
        data = self.read()
        if not data:
            return None
        try:
            return SignalLevel(data["signal"])
        except (KeyError, ValueError):
            return None
