"""
MoCKA Core Kernel — prism.observation_engine

責務:
  Context・CognitiveStateから、Observation(観測結果)を生成する。

  recommendationはあくまで「示唆」であり、Action/Command/Workflowの
  実行指示ではない。
"""

import uuid
from datetime import datetime, timezone

from .models import CognitiveStateValue, Observation


_RECOMMENDATIONS = {
    CognitiveStateValue.STABLE: "現状の解釈は安定しています。特段の対応は不要です。",
    CognitiveStateValue.UNCERTAIN: "未分類のイベントが多いため、event_typeの拡充を検討してください。",
    CognitiveStateValue.INCOMPLETE: "解析対象のイベントが不足しています。",
    CognitiveStateValue.CONFLICT: "矛盾する解釈が検出されました。詳細を確認してください。",
    CognitiveStateValue.LEARNING: "複数カテゴリのイベントが混在しています。傾向を継続観察してください。",
}

_RISK_LEVELS = {
    CognitiveStateValue.STABLE: "low",
    CognitiveStateValue.UNCERTAIN: "medium",
    CognitiveStateValue.INCOMPLETE: "low",
    CognitiveStateValue.CONFLICT: "high",
    CognitiveStateValue.LEARNING: "low",
}


class ObservationEngine:
    """ContextとCognitiveStateからObservationを生成する。"""

    def observe(self, context, cognitive_state) -> Observation:
        recommendation = _RECOMMENDATIONS.get(cognitive_state.state, "")
        risk_level = _RISK_LEVELS.get(cognitive_state.state, "unknown")

        return Observation(
            observation_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            confidence=cognitive_state.confidence,
            evidence_event_ids=context.event_ids,
            recommendation=recommendation,
            risk_level=risk_level,
            metadata={"cognitive_state": cognitive_state.state},
        )
