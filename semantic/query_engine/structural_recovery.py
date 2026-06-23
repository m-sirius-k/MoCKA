# MoCKA/semantic/query_engine/structural_recovery.py
# Phase7-B-3 - Structural Recovery Layer v0 (read-only, no interpretation)
#
# 契約: docs/contracts/phase7_b3_structural_recovery_v1.md
#
# 重要な区別: StructuralTraceReaderはMeaning Reconstruction Engineではない。
# decision_trace.json / merge_graph.json / adapter_enrichment.jsonlの
# 構造をそのまま列挙するだけであり、意味解釈・推論・cluster再計算・
# merge新規生成は一切行わない。
#
# 絶対条件（契約4章・くろこ指示より）:
#   1. 推論禁止（意味解釈しない）
#   2. intentは再評価に使わない（ルーティング専用、intent_scoreをそのまま渡す）
#   3. merge_graphは新規意味生成禁止（接続のみ）
#   4. 書き込み禁止（書き込みメソッドは構造的に存在しない）
#
# 既存ExplanationBuilder.TraceReader / DecisionReplaySystem.DecisionTraceReader
# のメソッド署名は変更しない。本ファイルは新規の別クラスとして追加する。

import json
from pathlib import Path
from typing import Optional

DEFAULT_DECISION_TRACE_PATH = (
    Path(__file__).resolve().parents[2] / "canonical" / "trace" / "_phase6" / "decision_trace.json"
)
DEFAULT_MERGE_GRAPH_PATH = (
    Path(__file__).resolve().parents[2] / "canonical" / "trace" / "_phase5b_v3" / "merge_graph.json"
)
DEFAULT_ADAPTER_ENRICHMENT_PATH = (
    Path(__file__).resolve().parents[2] / "canonical" / "trace" / "_phase6" / "adapter_enrichment.jsonl"
)


def _relation_type(accepted: bool, diameter_limit_hit: Optional[bool]) -> str:
    if accepted:
        return "accepted"
    if diameter_limit_hit:
        return "rejected_diameter_limit"
    return "rejected"


class StructuralTraceReader:
    """decision_trace.json / merge_graph.json / adapter_enrichment.jsonlの
    構造を読み取り専用で復元するStructural Recovery Layer。

    意味解釈・推論・cluster再計算・merge新規生成は一切行わない。
    書き込みメソッドは構造的に存在しない。
    """

    def __init__(
        self,
        decision_trace_path: Path = DEFAULT_DECISION_TRACE_PATH,
        merge_graph_path: Path = DEFAULT_MERGE_GRAPH_PATH,
        adapter_enrichment_path: Path = DEFAULT_ADAPTER_ENRICHMENT_PATH,
    ):
        self._decision_trace = self._load_decision_trace(decision_trace_path)
        self._merge_graph_by_from = self._load_merge_graph(merge_graph_path)
        self._enrichment_by_cluster = self._load_adapter_enrichment(adapter_enrichment_path)

    @staticmethod
    def _load_decision_trace(path: Path) -> dict:
        if not path.exists():
            return {}
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _load_merge_graph(path: Path) -> dict:
        if not path.exists():
            return {}
        with open(path, encoding="utf-8") as f:
            edges = json.load(f)
        by_from: dict = {}
        for edge in edges:
            by_from.setdefault(edge["from"], []).append(edge)
        return by_from

    @staticmethod
    def _load_adapter_enrichment(path: Path) -> dict:
        by_cluster: dict = {}
        if not path.exists():
            return by_cluster
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                cluster_id = record.get("cluster_id")
                by_cluster.setdefault(cluster_id, []).append(record)
        return by_cluster

    def recover_structure(self, identifier: str) -> dict:
        """identifier(cluster_id等の呼び出し識別子)を起点に構造を復元する。

        session_idは実データに存在しないため、identifierをそのまま
        プレースホルダーとして格納する（契約2章）。
        """
        trace_chain = [
            {
                "intent": record.get("intent_score"),
                "canonical_cluster_id": record.get("cluster_id"),
                "timestamp": None,  # 実データに存在しないため常にnull(契約2章)
            }
            for record in self._enrichment_by_cluster.get(identifier, [])
        ]

        merge_links = []
        for attempt in self._decision_trace.get(identifier, []):
            merge_links.append(
                {
                    "from_cluster": identifier,
                    "to_cluster": attempt.get("to"),
                    "relation_type": _relation_type(
                        attempt.get("accepted", False), attempt.get("diameter_limit_hit")
                    ),
                }
            )
        for edge in self._merge_graph_by_from.get(identifier, []):
            merge_links.append(
                {
                    "from_cluster": edge.get("from"),
                    "to_cluster": edge.get("to"),
                    "relation_type": _relation_type(edge.get("accepted", False), None),
                }
            )

        return {
            "session_id": identifier,
            "trace_chain": trace_chain,
            "merge_links": merge_links,
        }
