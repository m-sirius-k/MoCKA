"""
prediction/provider.py -- TIC Prediction Provider (Phase6)

risk_history.jsonl からTrace（スコア系列）・対象コンポーネント一覧を
prediction/モデル群に供給する。判断・予測はしない。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trend_engine import load_history, get_score_series


def get_components() -> list:
    history = load_history()
    if not history:
        return []
    return sorted(history[-1].get("scores", {}).keys())


def get_score_series_for(component: str, window: int) -> list:
    history = load_history()
    return get_score_series(component, history, window=window)
