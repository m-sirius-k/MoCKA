# cognitive/cognitive_loop_engine.py
# MoCKA v1.2 — Cognitive Loop Engine
# 責務: MoCKA全体状態の定期再評価 → 傾向シグナル生成
# 設計原則: データを一切変更しない（読むだけ）。書くのはCognitiveSignalのみ。

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from timeline.semantic_timeline_engine import SemanticTimelineEngine
from phi_os.decision_log_analyzer import DecisionLogAnalyzer
from cognitive.cognitive_signal import CognitiveSignal, SignalLevel


# ─────────────────────────────────────────────────────────────
# CognitiveState — ループ1サイクルの評価結果
# ─────────────────────────────────────────────────────────────

@dataclass
class CognitiveState:
    timestamp: str
    drift: float           # next_drift_probability (0.0〜1.0)
    drift_growth: float    # expected_conflict_growth
    bias: str              # PHI偏重 / BALANCED / PERSONAL偏重
    routing: Dict[str, Any]
    stability: str         # HIGH / MEDIUM / LOW
    signal: SignalLevel    # 生成したCOGNITIVE_SIGNAL

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["signal"] = self.signal.value
        return d


# ─────────────────────────────────────────────────────────────
# CognitiveLoopEngine
# ─────────────────────────────────────────────────────────────

class CognitiveLoopEngine:
    """
    「観測 → 分析 → シグナル生成 → 再観測」の循環を担う中核エンジン。

    - Timeline / Analyzer からデータを読む（書かない）
    - CognitiveSignal を生成してファイル出力する（PHI-OSが任意参照）
    - 評価履歴を cognitive_history.jsonl に追記する（append only）
    """

    HISTORY_PATH = Path(__file__).resolve().parent.parent / "data" / "cognitive_history.jsonl"

    def __init__(
        self,
        timeline: Optional[SemanticTimelineEngine] = None,
        analyzer: Optional[DecisionLogAnalyzer] = None,
        signal: Optional[CognitiveSignal] = None,
    ) -> None:
        self.timeline = timeline or SemanticTimelineEngine()
        self.analyzer = analyzer or DecisionLogAnalyzer(self.timeline)
        self.signal   = signal   or CognitiveSignal()
        self.HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)

    # ── メインループ ──────────────────────────────────────────

    def run_cycle(self, window: int = 20) -> CognitiveState:
        """
        MoCKA全体状態を再評価し、CognitiveStateを返す。
        副作用: CognitiveSignalファイル更新 + 履歴JSONL追記のみ。
        """
        prediction = self.timeline.predict_next_state(window=window)
        bias_result = self.analyzer.analyze_bias()
        routing_result = self.analyzer.detect_routing_pattern()
        stab_result = self.analyzer.stability_score(window=window)

        drift      = prediction["next_drift_probability"]
        drift_growth = prediction["expected_conflict_growth"]
        bias       = bias_result.get("bias", "NO_DATA")
        stability  = stab_result.get("level", "NO_DATA")

        # シグナルレベル決定（ルールベース）
        sig_level = self._decide_signal(drift, bias, stability)

        state = CognitiveState(
            timestamp   = datetime.now(timezone.utc).isoformat(),
            drift       = drift,
            drift_growth= drift_growth,
            bias        = bias,
            routing     = routing_result,
            stability   = stability,
            signal      = sig_level,
        )

        # シグナル出力（PHI-OSが任意参照）
        self.signal.emit(sig_level, state)

        # 履歴追記（append only）
        self._append_history(state)

        return state

    # ── シグナル決定ロジック ──────────────────────────────────

    def _decide_signal(
        self,
        drift: float,
        bias: str,
        stability: str,
    ) -> SignalLevel:
        """
        観測値からCOGNITIVE_SIGNALレベルを決定するルールベースロジック。
        PHI-OSへの強制はしない。傾向を示すだけ。
        """
        if drift >= 0.6 or stability == "LOW":
            return SignalLevel.HIGH_DRIFT
        if bias == "PHI偏重":
            return SignalLevel.PHI_BIAS
        if bias == "PERSONAL偏重":
            return SignalLevel.PERSONAL_BIAS
        if drift >= 0.3 or stability == "MEDIUM":
            return SignalLevel.MODERATE_DRIFT
        return SignalLevel.STABLE

    # ── 履歴追記 ─────────────────────────────────────────────

    def _append_history(self, state: CognitiveState) -> None:
        with self.HISTORY_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(state.to_dict(), ensure_ascii=False) + "\n")

    # ── 連続値drift curve ─────────────────────────────────────

    def drift_curve(self) -> List[Dict[str, Any]]:
        """
        過去のrun_cycle()結果からdriftの連続値推移を返す。
        driftが連続値になる（v1.2必須条件）。
        """
        if not self.HISTORY_PATH.exists():
            return []
        curve: List[Dict[str, Any]] = []
        with self.HISTORY_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        d = json.loads(line)
                        curve.append({
                            "timestamp":   d.get("timestamp"),
                            "drift":       d.get("drift", 0.0),
                            "drift_growth":d.get("drift_growth", 0.0),
                            "stability":   d.get("stability"),
                            "signal":      d.get("signal"),
                        })
                    except Exception:
                        pass
        return curve

    # ── 状態サマリ ────────────────────────────────────────────

    def status_report(self) -> str:
        """直近のCognitiveStateをテキスト形式で返す。"""
        curve = self.drift_curve()
        if not curve:
            return "COGNITIVE LOOP: NO HISTORY"
        latest = curve[-1]
        lines = [
            "=== COGNITIVE LOOP STATUS ===",
            f'TIMESTAMP:    {latest["timestamp"]}',
            f'DRIFT:        {latest["drift"]:.4f}',
            f'DRIFT GROWTH: {latest["drift_growth"]:+.4f}',
            f'STABILITY:    {latest["stability"]}',
            f'SIGNAL:       {latest["signal"]}',
            f'HISTORY:      {len(curve)} cycles',
        ]
        return "\n".join(lines)
