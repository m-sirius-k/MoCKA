# MoCKA/semantic/query_engine/order_normalizer.py
# Phase7-B-4 - Order Normalization v0 (non-temporal graph alignment)
#
# 契約: docs/contracts/phase7_b4_order_normalization_v1.md
#
# 重要な前提（Phase7-B-3で確定した構造的事実）:
#   このシステムは「時間を持たない意味ネットワーク」である。
#   session_id/timestamp/textのintentは実データに存在しない。
#
# 責務: gap_secondsを「時間」ではなく「順序キー」として扱い、同一
#       from_clusterのmerge試行を整列する。同一edgeに対し複数ソース
#       (decision_trace.json/merge_graph.json)のrelation_typeが
#       一致しない場合を「順序衝突(order collision)」として検知・記録する。
#       衝突の解消(どちらが正しいかの判定)は行わない。
#
# 絶対条件（契約5章より）:
#   - timestamp・絶対時刻の生成は行わない。
#   - 衝突の自動解消は行わない（記録のみ、Human Gateに委ねる）。
#   - 既存StructuralTraceReaderのメソッド・出力構造は変更しない。
#   - 追加のファイルI/Oは行わない（既存readerのin-memory indexを参照するのみ）。

from dataclasses import dataclass, field
from typing import Sequence

from semantic.query_engine.structural_recovery import StructuralTraceReader, _relation_type

SOURCE_DECISION_TRACE = "decision_trace"
SOURCE_MERGE_GRAPH = "merge_graph"


@dataclass(frozen=True)
class OrderedMergeLink:
    from_cluster: str
    to_cluster: str
    relation_type: str
    order_key: float
    source: str


@dataclass(frozen=True)
class OrderCollision:
    from_cluster: str
    to_cluster: str
    relation_types: Sequence[str] = field(default_factory=tuple)
    sources: Sequence[str] = field(default_factory=tuple)


class OrderNormalizer:
    """StructuralTraceReaderの上位ラッパー。

    gap_secondsを順序キーとしてmerge試行を整列し、同一edgeに対する
    relation_type不一致を順序衝突として検知する。解消は行わない。
    """

    def __init__(self, trace_reader: StructuralTraceReader):
        self._trace_reader = trace_reader

    def normalize(self, identifier: str) -> dict:
        links = []

        for attempt in self._trace_reader._decision_trace.get(identifier, []):
            links.append(
                OrderedMergeLink(
                    from_cluster=identifier,
                    to_cluster=attempt.get("to"),
                    relation_type=_relation_type(
                        attempt.get("accepted", False), attempt.get("diameter_limit_hit")
                    ),
                    order_key=attempt.get("gap_seconds", 0.0),
                    source=SOURCE_DECISION_TRACE,
                )
            )

        for edge in self._trace_reader._merge_graph_by_from.get(identifier, []):
            links.append(
                OrderedMergeLink(
                    from_cluster=edge.get("from"),
                    to_cluster=edge.get("to"),
                    relation_type=_relation_type(edge.get("accepted", False), None),
                    order_key=edge.get("gap_seconds", 0.0),
                    source=SOURCE_MERGE_GRAPH,
                )
            )

        ordered_links = tuple(sorted(links, key=lambda link: link.order_key))
        collisions = self._detect_collisions(ordered_links)

        return {
            "session_id": identifier,
            "ordered_merge_links": ordered_links,
            "collisions": collisions,
        }

    @staticmethod
    def _detect_collisions(links: Sequence[OrderedMergeLink]) -> Sequence[OrderCollision]:
        by_edge: dict = {}
        for link in links:
            by_edge.setdefault((link.from_cluster, link.to_cluster), []).append(link)

        collisions = []
        for (from_cluster, to_cluster), edge_links in by_edge.items():
            relation_types = tuple(link.relation_type for link in edge_links)
            if len(set(relation_types)) > 1:
                collisions.append(
                    OrderCollision(
                        from_cluster=from_cluster,
                        to_cluster=to_cluster,
                        relation_types=relation_types,
                        sources=tuple(link.source for link in edge_links),
                    )
                )
        return tuple(collisions)
