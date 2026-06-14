"""
MoCKA Core Kernel — orchestra_core.orchestra

責務:
  複数のProposalNodeをDecision Field(固定評価軸)上で評価し、
  単一のDecisionPacketへ圧縮する(意思決定圧縮層)。

  Orchestraは意思決定のみを担い、実行責任を持たない。

禁止事項(Phase 12):
  - 実行トリガーの生成
  - PHI-OSへの状態変更命令
  - Memoryへの永続書き込み命令
  - 外部モジュール制御フラグの設定
  - 自動ワークフロー起動

  本クラスはいずれの操作も行わない。すべての出力はProposalNode/
  DecisionPacketのto_dict()による単純なデータ構造であり、
  execution_statusは常に"PROPOSED"で終了する。
"""

from .models import DECISION_FIELD_AXES, DecisionPacket, ProposalNode


class Orchestra:
    """提案ノード群を評価し、単一の意思決定パケットへ圧縮する。

    PHI-OS/Relay/Memory/PrismBridgeのいずれも保持・制御しない
    (純粋な評価ロジックのみ)。
    """

    def evaluate(self, proposal: ProposalNode) -> dict:
        """単一のProposalNodeをDecision Field(固定評価軸)上で評価する。

        Returns:
            dict: DECISION_FIELD_AXES各軸のスコア(0〜1)を持つdict
        """
        confidence = max(0.0, min(1.0, proposal.confidence))
        cost = max(0.0, min(1.0, proposal.cost))
        constraint_penalty = min(1.0, len(proposal.constraints) * 0.1)

        return {
            "structural_consistency": confidence,
            "temporal_stability": confidence * (1.0 - constraint_penalty),
            "resource_cost": 1.0 - cost,
            "risk_containment": 1.0 - constraint_penalty,
            "future_compatibility": confidence * (1.0 - cost),
        }

    def score(self, proposal: ProposalNode) -> float:
        """評価軸スコアの平均値を返す。"""
        axis_scores = self.evaluate(proposal)
        return sum(axis_scores[axis] for axis in DECISION_FIELD_AXES) / len(DECISION_FIELD_AXES)

    def decide(self, proposals) -> DecisionPacket:
        """提案ノード群から単一のDecisionPacketを構築する。

        Args:
            proposals: ProposalNodeのiterable(空の場合はselected_proposalが
                Noneのまま"提案なし"として返却される)。

        Returns:
            DecisionPacket: execution_statusは常に"PROPOSED"。
        """
        proposals = list(proposals)

        if not proposals:
            return DecisionPacket(
                selected_proposal=None,
                rejected_proposals=(),
                rationale="提案が存在しないため、選択は行われませんでした。",
            )

        scored = [(self.score(proposal), proposal) for proposal in proposals]
        best_score, best_proposal = max(scored, key=lambda item: item[0])

        rejected = tuple(
            proposal.to_dict()
            for _, proposal in scored
            if proposal.proposal_id != best_proposal.proposal_id
        )

        rationale = (
            f"proposal_id={best_proposal.proposal_id!r} (source={best_proposal.source!r}) "
            f"がDecision Field評価で最高スコア({best_score:.4f})となったため選択されました。"
        )

        return DecisionPacket(
            selected_proposal=best_proposal.to_dict(),
            rejected_proposals=rejected,
            rationale=rationale,
        )
