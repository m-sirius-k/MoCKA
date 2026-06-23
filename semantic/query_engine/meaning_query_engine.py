# MoCKA/semantic/query_engine/meaning_query_engine.py
# Phase7-A-2 - Meaning Query Engine v0 (skeleton)。
#
# 契約: docs/contracts/meaning_query_engine_contract_v1.md
#
# 責務: 既存cluster/decision_traceの読み取り検索のみ。
#
# 絶対条件（契約3章・4章より）:
#   - PHI-OSへの書き込みは行わない。
#   - clusterの再計算・embeddingの再生成は行わない。
#   - canonical_search() は単独の座標決定（anchor）。他機能に依存しない。
#   - intent_search() は canonical anchorを基準に意味場を展開する。
#     anchorが無い場合は anchor=None を結果に明示し、anchor確定済みの
#     結果と区別する（契約3.2節）。
#
# 本ファイルはインターフェース定義のみの最小スケルトンであり、
# 実データ（cluster index / decision_trace store）への接続は
# 次段（Phase7-A-2継続）で reader を注入する形で行う。

from dataclasses import dataclass, field
from typing import Optional, Sequence


@dataclass(frozen=True)
class CanonicalSearchResult:
    canonical_trace_id: str
    cluster_id: Optional[str]
    found: bool


@dataclass(frozen=True)
class IntentSearchResult:
    anchor: Optional[CanonicalSearchResult]
    cluster_refs: Sequence[str] = field(default_factory=tuple)


class ClusterReader:
    """既存cluster/decision_traceの読み取りインターフェース。

    実データ接続はPhase7-A-2継続段で具象実装を注入する。
    本クラス自体はread-onlyのプロトコル定義のみ。
    """

    def resolve_canonical(self, canonical_trace_id: str) -> Optional[str]:
        raise NotImplementedError

    def find_clusters_by_intent(self, text_or_key: str, anchor_cluster_id: Optional[str]) -> Sequence[str]:
        raise NotImplementedError


class MeaningQueryEngine:
    """読み取り専用のMeaning Query Engine。

    cluster再計算・embedding再生成・PHI-OSへの書き込みは一切行わない。
    """

    def __init__(self, reader: ClusterReader):
        self._reader = reader

    def canonical_search(self, canonical_trace_id: str) -> CanonicalSearchResult:
        cluster_id = self._reader.resolve_canonical(canonical_trace_id)
        return CanonicalSearchResult(
            canonical_trace_id=canonical_trace_id,
            cluster_id=cluster_id,
            found=cluster_id is not None,
        )

    def intent_search(
        self,
        text_or_key: str,
        anchor: Optional[CanonicalSearchResult] = None,
    ) -> IntentSearchResult:
        anchor_cluster_id = anchor.cluster_id if anchor and anchor.found else None
        cluster_refs = self._reader.find_clusters_by_intent(text_or_key, anchor_cluster_id)
        return IntentSearchResult(anchor=anchor, cluster_refs=tuple(cluster_refs))
