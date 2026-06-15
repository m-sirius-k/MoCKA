"""
prediction/models.py -- TIC Prediction Models (Phase6)

予測アルゴリズムのみを責務とするモジュール。
インターフェースは固定（将来のモデル差し替えはこのファイルのみで完結する）。

Future: MovingAverage, Exponential, Bayesian, ML, LLM
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trend_engine import least_squares_slope


class LinearModel:
    """slope（trend_engine.least_squares_slope）による線形外挿モデル"""

    name = "linear"

    def predict(self, scores: list, days_ahead: int = 14) -> dict:
        slope = least_squares_slope(scores)
        last_score = scores[-1]
        predicted = last_score + slope * days_ahead
        predicted = max(0.0, min(100.0, predicted))

        n = len(scores)
        confidence = min(0.5 + 0.05 * n, 0.90)

        return {
            "predicted_score": round(predicted, 1),
            "confidence":       round(confidence, 2),
            "model":            self.name,
            "days_ahead":       days_ahead,
        }


def predict(scores: list, days_ahead: int = 14) -> dict:
    """固定インターフェース。現在はLinearModelのみ使用。"""
    return LinearModel().predict(scores, days_ahead)
