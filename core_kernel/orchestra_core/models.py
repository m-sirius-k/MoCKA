"""
MoCKA Core Kernel — orchestra_core.models

責務:
  Orchestra(意思決定圧縮層)の入力・出力データモデルを定義する。

  - ProposalNode: 提案ノード(確定情報ではなく「提案」として扱う)
  - DecisionPacket: Orchestraの出力(単一の意思決定パケット)
  - DECISION_FIELD_AXES: 評価空間(Decision Field)の固定評価軸

  本フェーズ(Phase 12)中、DECISION_FIELD_AXESは変更してはならない。
  execution_statusはPROPOSED以外の値を取らない(実行状態への遷移は禁止)。
"""

from dataclasses import dataclass, field

ORCHESTRA_SCHEMA_VERSION = "1.0"

# 評価空間(Decision Field)の固定評価軸。Phase 12中は変更禁止。
DECISION_FIELD_AXES = (
    "structural_consistency",
    "temporal_stability",
    "resource_cost",
    "risk_containment",
    "future_compatibility",
)

# 出力のexecution_statusは常にこの値で終了する(実行禁止)。
EXECUTION_STATUS_PROPOSED = "PROPOSED"


@dataclass(frozen=True)
class ProposalNode:
    """Orchestraへの入力となる提案ノード(確定情報ではない)。"""

    proposal_id: str
    source: str
    payload: dict = field(default_factory=dict)
    confidence: float = 0.0
    cost: float = 0.0
    constraints: tuple = ()
    version: str = ORCHESTRA_SCHEMA_VERSION

    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "source": self.source,
            "payload": dict(self.payload),
            "confidence": self.confidence,
            "cost": self.cost,
            "constraints": list(self.constraints),
            "version": self.version,
        }


@dataclass(frozen=True)
class DecisionPacket:
    """Orchestraの出力(単一の意思決定パケット)。

    execution_statusは常に"PROPOSED"であり、実行状態への遷移は禁止される。
    """

    selected_proposal: dict
    rejected_proposals: tuple
    rationale: str
    execution_status: str = EXECUTION_STATUS_PROPOSED
    version: str = ORCHESTRA_SCHEMA_VERSION

    def to_dict(self) -> dict:
        return {
            "selected_proposal": self.selected_proposal,
            "rejected_proposals": list(self.rejected_proposals),
            "rationale": self.rationale,
            "execution_status": self.execution_status,
            "version": self.version,
        }
