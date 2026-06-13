# -*- coding: utf-8 -*-
"""Conflict Clusterer (Phase 5 Cross-Layer Consistency Engine)

役割:
  - 複数のInconsistencyを「関与レイヤーの重なり」でグループ化する
  - root_cause推定 (dependency_graphの依存順で最も上流のレイヤーを推定root候補とする)
  - impact_radius計算 (クラスタが影響するユニークレイヤー数)

root_cause推定は「dependency_graphにおいてクラスタ内の関与レイヤーのうち
最も依存元(上流)に位置するレイヤー」を機械的に選ぶのみであり、
因果関係の証明ではない(推測の明示)。
"""

from dataclasses import dataclass, field

from cross_layer_consistency.dependency_graph_builder import ALL_LAYERS, DEPENDENCY_EDGES


@dataclass
class ConflictCluster:
    cluster_id: str
    inconsistencies: list = field(default_factory=list)
    layers_involved: set = field(default_factory=set)
    root_cause_candidate: str = ""
    impact_radius: int = 0


def _upstream_rank(layer: str) -> int:
    """依存グラフ上での'上流度'を返す(小さいほど上流)。
    semantic(0) -> decision(1) -> memory(2) -> self_audit(3) -> feedback(4) -> learning(5)
    reality(0) -> report(1)
    上記2系統を結合した順位表。reality/report系はsemantic系より優先(独立した上流とみなす)。
    """
    order = ["reality", "report", "semantic", "decision", "memory", "self_audit", "feedback", "learning"]
    return order.index(layer) if layer in order else len(order)


def cluster(inconsistencies: list) -> list:
    """関与レイヤーが1つでも重なるInconsistency同士を同一クラスタにまとめる
    (Union-Find簡易実装)。"""
    if not inconsistencies:
        return []

    parent = list(range(len(inconsistencies)))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i in range(len(inconsistencies)):
        for j in range(i + 1, len(inconsistencies)):
            if set(inconsistencies[i].layers_involved) & set(inconsistencies[j].layers_involved):
                union(i, j)

    groups: dict = {}
    for i in range(len(inconsistencies)):
        root = find(i)
        groups.setdefault(root, []).append(inconsistencies[i])

    clusters = []
    for idx, (root, items) in enumerate(groups.items()):
        layers_involved = set()
        for inc in items:
            layers_involved.update(inc.layers_involved)

        root_cause_candidate = min(layers_involved, key=_upstream_rank)

        clusters.append(ConflictCluster(
            cluster_id=f"CLUSTER_{idx+1}",
            inconsistencies=items,
            layers_involved=layers_involved,
            root_cause_candidate=root_cause_candidate,
            impact_radius=len(layers_involved),
        ))

    return clusters


if __name__ == "__main__":
    from cross_layer_consistency.layer_snapshot_builder import build
    from cross_layer_consistency.consistency_score_engine import compute
    from cross_layer_consistency.inconsistency_detector import detect

    snap = build()
    result = compute(snap)
    incs = detect(snap, result.sub_scores)

    for c in cluster(incs):
        print(c.cluster_id, "layers=", c.layers_involved, "root=", c.root_cause_candidate,
              "impact_radius=", c.impact_radius, "n_inc=", len(c.inconsistencies))
