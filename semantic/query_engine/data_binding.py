# MoCKA/semantic/query_engine/data_binding.py
# Phase7-A-4 / Phase7-A-4-Intent - Real Data Binding v0 (Meaning Input Layer)
#
# 契約: docs/contracts/phase7_a4_real_data_binding_v1.md
#       docs/contracts/phase7_a4_intent_real_data_binding_v1.md
#
# 責務: compressed_canonical_clusters.json / embedding_index.jsonを
#       起動時に読み込み、canonical解決とanchor必須のintent一致検証を
#       in-memoryで提供する。
#
# 絶対条件:
#   - compressed_canonical_clusters.json / embedding_index.jsonへの
#     書き込みは行わない（書き込みメソッドは構造的に存在しない）。
#   - 既存persisted embeddingの再生成は行わない。query textのbigram化は
#     呼び出しごとのephemeral計算であり永続化しない（intent契約3章で区別）。
#   - anchor_cluster_idが無い場合のintent展開は本v1のスコープ外
#     （NotImplementedErrorのまま）。

import json
import math
from pathlib import Path
from typing import Dict, Optional, Sequence

from semantic.query_engine.meaning_query_engine import ClusterReader

DEFAULT_CLUSTERS_PATH = (
    Path(__file__).resolve().parents[2]
    / "canonical" / "trace" / "_phase5b_v3" / "compressed_canonical_clusters.json"
)
DEFAULT_EMBEDDING_INDEX_PATH = (
    Path(__file__).resolve().parents[2]
    / "canonical" / "trace" / "_phase5b_v3" / "embedding_index.json"
)

INTENT_MATCH_THRESHOLD = 0.15


def bigram_vector(text: str) -> Dict[str, int]:
    """textのephemeralな文字2-gram頻度ベクトルを計算する(永続化しない)。"""
    vector: Dict[str, int] = {}
    for i in range(len(text) - 1):
        bigram = text[i:i + 2]
        vector[bigram] = vector.get(bigram, 0) + 1
    return vector


def cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    if not vec_a or not vec_b:
        return 0.0
    dot = sum(weight * vec_b.get(key, 0.0) for key, weight in vec_a.items())
    norm_a = math.sqrt(sum(weight * weight for weight in vec_a.values()))
    norm_b = math.sqrt(sum(weight * weight for weight in vec_b.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class RealClusterReader(ClusterReader):
    """compressed_canonical_clusters.json / embedding_index.jsonに基づく
    読み取り専用ClusterReader。

    起動時に1回だけJSONを読み込み、member_trace_id -> cluster_id の
    逆引きインデックスとcluster_id -> member一覧、member embeddingを
    in-memoryで保持する。以降の呼び出しはin-memory参照とephemeralな
    query vector計算のみ。
    """

    def __init__(
        self,
        clusters_path: Path = DEFAULT_CLUSTERS_PATH,
        embedding_index_path: Path = DEFAULT_EMBEDDING_INDEX_PATH,
    ):
        self._clusters_path = clusters_path
        self._embedding_index_path = embedding_index_path
        self._cluster_to_members, self._trace_to_cluster = self._build_cluster_index(clusters_path)
        self._embedding_index = self._load_embedding_index(embedding_index_path)

    @staticmethod
    def _build_cluster_index(clusters_path: Path):
        with open(clusters_path, encoding="utf-8") as f:
            clusters = json.load(f)

        if not clusters:
            raise ValueError(f"empty cluster baseline loaded from {clusters_path}")

        trace_to_cluster = {}
        for cluster_id, member_ids in clusters.items():
            for member_id in member_ids:
                trace_to_cluster[member_id] = cluster_id
        return clusters, trace_to_cluster

    @staticmethod
    def _load_embedding_index(embedding_index_path: Path) -> dict:
        with open(embedding_index_path, encoding="utf-8") as f:
            return json.load(f)

    def resolve_canonical(self, canonical_trace_id: str) -> Optional[str]:
        return self._trace_to_cluster.get(canonical_trace_id)

    def find_clusters_by_intent(self, text_or_key: str, anchor_cluster_id: Optional[str]) -> Sequence[str]:
        if anchor_cluster_id is None:
            raise NotImplementedError(
                "anchor-less intent search is out of scope for Phase7-A-4-Intent "
                "(see docs/contracts/phase7_a4_intent_real_data_binding_v1.md section 2)"
            )

        members = self._cluster_to_members.get(anchor_cluster_id, [])
        member_vectors = [
            self._embedding_index[m] for m in members if m in self._embedding_index
        ]
        if not member_vectors:
            return tuple()

        anchor_vector = self._mean_vector(member_vectors)
        query_vector = bigram_vector(text_or_key)
        similarity = cosine_similarity(query_vector, anchor_vector)

        return (anchor_cluster_id,) if similarity >= INTENT_MATCH_THRESHOLD else tuple()

    @staticmethod
    def _mean_vector(vectors) -> Dict[str, float]:
        sums: Dict[str, float] = {}
        for vector in vectors:
            for key, weight in vector.items():
                sums[key] = sums.get(key, 0.0) + weight
        count = len(vectors)
        return {key: total / count for key, total in sums.items()}
