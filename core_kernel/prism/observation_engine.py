"""
MoCKA Core Kernel — prism.observation_engine

責務:
  Context・CognitiveStateから、Observation(観測結果)を生成する。

  findingは「何が観測されたか」、recommendationは「示唆」であり、
  Action/Command/Workflowの実行指示ではない。
"""

import uuid
from datetime import datetime, timezone

from .models import CognitiveStateValue, Observation


_FINDINGS = {
    CognitiveStateValue.STABLE: "イベント群は一貫したカテゴリで解釈でき、状況は安定している。",
    CognitiveStateValue.UNSTABLE: "複数の異なるカテゴリのイベントが混在しており、解釈が一貫していない。",
    CognitiveStateValue.UNCERTAIN: "未分類のイベントが多数を占めており、十分な解釈ができない。",
    CognitiveStateValue.INCOMPLETE: "解析対象のイベントが存在しない。",
    CognitiveStateValue.CONFLICT: "イベント間に矛盾する因果関係が検出された。",
}

_RECOMMENDATIONS = {
    CognitiveStateValue.STABLE: "現状の解釈は安定しています。特段の対応は不要です。",
    CognitiveStateValue.UNSTABLE: "カテゴリの混在状況を確認し、必要であればevent_typeの分類を見直してください。",
    CognitiveStateValue.UNCERTAIN: "未分類のイベントが多いため、event_typeの拡充を検討してください。",
    CognitiveStateValue.INCOMPLETE: "解析対象のイベントが不足しています。",
    CognitiveStateValue.CONFLICT: "矛盾する因果関係が検出されました。詳細を確認してください。",
}

_RISK_LEVELS = {
    CognitiveStateValue.STABLE: "low",
    CognitiveStateValue.UNSTABLE: "medium",
    CognitiveStateValue.UNCERTAIN: "medium",
    CognitiveStateValue.INCOMPLETE: "low",
    CognitiveStateValue.CONFLICT: "high",
}


class ObservationEngine:
    """ContextとCognitiveStateからObservationを生成する。"""

    def observe(self, context, cognitive_state) -> Observation:
        finding = _FINDINGS.get(cognitive_state.state, "")
        recommendation = _RECOMMENDATIONS.get(cognitive_state.state, "")
        risk_level = _RISK_LEVELS.get(cognitive_state.state, "unknown")

        return Observation(
            observation_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            confidence=cognitive_state.confidence,
            finding=finding,
            evidence_event_ids=context.event_ids,
            recommendation=recommendation,
            risk_level=risk_level,
            metadata={"cognitive_state": cognitive_state.state},
        )
