# -*- coding: utf-8 -*-
"""Resolution Strategy Engine (Phase 5 Cross-Layer Consistency Engine)

役割: ConflictClusterに対して解決戦略の「提案」を生成する。
実行は行わない(Queueへの登録のみ、Applierが別途条件判定する)。

戦略一覧:
  - priority_override     : LAYER_PRIORITY上位のレイヤーの状態を優先採用
  - layer_suppression       : 下流レイヤーの矛盾報告を一時抑制
  - reconciliation_merge    : 複数レイヤーのスコアを再計算・統合
  - rollback_suggestion     : learning側の最新更新のロールバックを提案
  - learning_adjustment_suggestion: learning側の重み調整を提案

各clusterに対し、root_cause_candidateとinconsistency_typeに基づき
1つ以上の戦略を機械的に選択する。
"""

from dataclasses import dataclass, field

from cross_layer_consistency.consistency_registry import LAYER_PRIORITY, SUPPRESSION_RULES


@dataclass
class ResolutionStrategy:
    cluster_id: str
    strategy_type: str
    description: str
    target_layers: list = field(default_factory=list)
    rationale: str = ""


STRATEGY_RULES = {
    "REALITY_VS_REPORT_DIVERGENCE": "priority_override",
    "MEMORY_VS_LEARNING_DRIFT": "rollback_suggestion",
    "FEEDBACK_VS_LEARNING_INCONSISTENCY": "learning_adjustment_suggestion",
    "DECISION_VS_MEMORY": "reconciliation_merge",
    "SEMANTIC_VS_DECISION": "reconciliation_merge",
}


def propose(clusters: list) -> list:
    strategies = []

    for c in clusters:
        types_in_cluster = {inc.inconsistency_type for inc in c.inconsistencies}

        # 1. 各inconsistency_typeに対応する基本戦略
        for inc in c.inconsistencies:
            strategy_type = STRATEGY_RULES.get(inc.inconsistency_type, "reconciliation_merge")

            if strategy_type == "priority_override":
                # LAYER_PRIORITY最上位レイヤーの状態を採用
                winner = min(inc.layers_involved, key=lambda l: LAYER_PRIORITY.get(l, 99))
                strategies.append(ResolutionStrategy(
                    cluster_id=c.cluster_id,
                    strategy_type="priority_override",
                    description=f"{inc.layers_involved} のうち優先度最上位のレイヤー '{winner}' "
                                 f"(priority={LAYER_PRIORITY.get(winner)}) の状態をクラスタ全体の真実として採用する。",
                    target_layers=inc.layers_involved,
                    rationale=f"inconsistency_type={inc.inconsistency_type}; LAYER_PRIORITY準拠",
                ))

            elif strategy_type == "rollback_suggestion":
                strategies.append(ResolutionStrategy(
                    cluster_id=c.cluster_id,
                    strategy_type="rollback_suggestion",
                    description="learning側の直近の重み更新(該当があれば)を1ステップロールバックし、"
                                 "memory_coherenceとの再整合を図ることを提案する。"
                                 "(実行はLearningPipeline.rollback()によって別途承認後に行う)",
                    target_layers=["learning", "memory"],
                    rationale=f"inconsistency_type={inc.inconsistency_type}",
                ))

            elif strategy_type == "learning_adjustment_suggestion":
                strategies.append(ResolutionStrategy(
                    cluster_id=c.cluster_id,
                    strategy_type="learning_adjustment_suggestion",
                    description=f"Feedback Layerが生成した提案 "
                                 f"(target_layers={inc.evidence.get('target_layers')}) を "
                                 f"Learning Engineで処理しLearningActionへ変換するよう調整することを提案する。",
                    target_layers=["feedback", "learning"],
                    rationale=f"inconsistency_type={inc.inconsistency_type}; "
                              f"proposal_count={inc.evidence.get('proposal_count')} vs "
                              f"update_count={inc.evidence.get('update_count')}",
                ))

            elif strategy_type == "reconciliation_merge":
                strategies.append(ResolutionStrategy(
                    cluster_id=c.cluster_id,
                    strategy_type="reconciliation_merge",
                    description=f"{inc.layers_involved} のスコアを再計算し、"
                                 f"両者のサンプルケースを統合した再評価を提案する。",
                    target_layers=inc.layers_involved,
                    rationale=f"inconsistency_type={inc.inconsistency_type}",
                ))

        # 2. layer_suppression: SUPPRESSION_RULESに該当するtypeがあれば抑制を追加提案
        for t in types_in_cluster:
            if t in SUPPRESSION_RULES:
                strategies.append(ResolutionStrategy(
                    cluster_id=c.cluster_id,
                    strategy_type="layer_suppression",
                    description=f"{t} はSUPPRESSION_RULESに該当するため、"
                                 f"Queue上で状態='{SUPPRESSION_RULES[t]}'に固定し、Applierに到達させない。",
                    target_layers=list(c.layers_involved),
                    rationale=f"consistency_registry.SUPPRESSION_RULES['{t}']='{SUPPRESSION_RULES[t]}'",
                ))

    return strategies


if __name__ == "__main__":
    from cross_layer_consistency.layer_snapshot_builder import build
    from cross_layer_consistency.consistency_score_engine import compute
    from cross_layer_consistency.inconsistency_detector import detect
    from cross_layer_consistency.conflict_clusterer import cluster

    snap = build()
    result = compute(snap)
    incs = detect(snap, result.sub_scores)
    clusters = cluster(incs)

    for s in propose(clusters):
        print(s)
