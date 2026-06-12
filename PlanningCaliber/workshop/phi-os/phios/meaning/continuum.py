# phios/meaning/continuum.py
"""Meaning Continuum Engine — 意味の時間的変化"""
from __future__ import annotations

from collections import deque

from phios.meaning.state_vector import MeaningStateVector
from phios.meaning.interaction import interact


class MeaningContinuum:
    """
    意味の時間的変化を管理する。
    過去N件の意味ベクトルを保持し、evolve()で融合した現在意味を返す。
    """

    def __init__(self, size: int = 10):
        self.buffer: deque[MeaningStateVector] = deque(maxlen=size)

    def push(self, vector: MeaningStateVector) -> None:
        self.buffer.append(vector)

    def current(self) -> MeaningStateVector | None:
        """バッファの最新ベクトルを返す"""
        return self.buffer[-1] if self.buffer else None

    def evolve(self) -> MeaningStateVector | None:
        """
        過去の意味ベクトルを全て相互作用させ、現在の意味状態を返す。
        バッファが1件以下の場合は最新ベクトルをそのまま返す。
        """
        if not self.buffer:
            return None
        if len(self.buffer) == 1:
            return self.buffer[0]

        result = self.buffer[0]
        for v in list(self.buffer)[1:]:
            result = interact(result, v)
        return result

    def entropy_trend(self) -> float:
        """直近の意味エントロピーの変化傾向（正=増加、負=安定化）"""
        if len(self.buffer) < 2:
            return 0.0
        return self.buffer[-1].entropy - self.buffer[-2].entropy
