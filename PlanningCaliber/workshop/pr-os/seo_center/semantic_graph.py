"""
SEMANTIC GRAPH + LLM CITATION MODE — TODO_332

設計思想:
  記事 = ノード（KS ID + タイトル + タグ + semantic_vector）
  主張 = エッジ（記事間の意味的関係: supports / contradicts / extends / cites）
  引用 = 重み（llm_index スコア × citation_fitness による重みづけ）

目的:
  「読まれる」ではなく「引用される」設計。
  LLMがMoCKA知識グラフを参照・引用する際の最適フォーマットを自動生成する。

TODO_330連携:
  DistributionRouterV2 の llm_index 出力 を ノードの citation_weight として使用する。

データ永続化:
  C:/Users/sirok/MoCKA/PlanningCaliber/workshop/pr-os/data/semantic_graph.json
  append-only原則（MoCKA ledger設計準拠）
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

_DATA_DIR   = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_GRAPH_FILE = os.path.join(_DATA_DIR, "semantic_graph.json")

# エッジ種別
EDGE_SUPPORTS     = "supports"      # AはBの主張を支持する
EDGE_EXTENDS      = "extends"       # AはBを拡張する
EDGE_CITES        = "cites"         # AはBを引用する
EDGE_CONTRADICTS  = "contradicts"   # AはBと対立する

EDGE_TYPES = {EDGE_SUPPORTS, EDGE_EXTENDS, EDGE_CITES, EDGE_CONTRADICTS}


# ── データ構造 ────────────────────────────────────────────────

@dataclass
class GraphNode:
    """KS記事ノード"""
    ks_id:           str
    title:           str
    tags:            list[str]
    category:        str
    summary:         str
    semantic_vector: dict          # {s1, s2, s3, s4, s5} from gate.py
    citation_weight: float         # llm_index スコア from DistributionRouterV2
    added_at:        str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def citation_fitness(self) -> float:
        """S3: LLM抽出適性"""
        return self.semantic_vector.get("s3", 0.0)

    @property
    def retrieval_fit(self) -> float:
        """S4: 検索適合性"""
        return self.semantic_vector.get("s4", 0.0)

    @property
    def effective_weight(self) -> float:
        """実効引用重み = llm_index × citation_fitness"""
        return round(self.citation_weight * max(self.citation_fitness, 0.3), 3)


@dataclass
class GraphEdge:
    """記事間の意味的関係エッジ"""
    source_id:   str   # 主張元KS ID
    target_id:   str   # 主張先KS ID
    edge_type:   str   # supports / extends / cites / contradicts
    weight:      float # エッジ重み（0.0-1.0）
    claim:       str   # 主張の内容（一文）
    added_at:    str   = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


# ── Semantic Graph ────────────────────────────────────────────

class SemanticGraph:
    """
    KS記事間の意味的関係グラフ。

    ノード: KS記事（semantic_vector + citation_weight 付き）
    エッジ: 記事間の主張関係（4タイプ × 重みづけ）

    永続化: data/semantic_graph.json（append-only）
    """

    def __init__(self):
        self._nodes: dict[str, GraphNode] = {}
        self._edges: list[GraphEdge]      = []
        self._load()

    # ── 永続化 ───────────────────────────────────────────────

    def _load(self):
        """グラフファイルを読み込む（ファイルがなければ空グラフ）"""
        if not os.path.exists(_GRAPH_FILE):
            return
        try:
            with open(_GRAPH_FILE, encoding="utf-8") as f:
                data = json.load(f)
            for n in data.get("nodes", []):
                node = GraphNode(**n)
                self._nodes[node.ks_id] = node
            for e in data.get("edges", []):
                self._edges.append(GraphEdge(**e))
        except Exception as ex:
            print(f"[SemanticGraph] 読み込みエラー（空グラフで継続）: {ex}")

    def save(self):
        """グラフをファイルに保存する"""
        os.makedirs(_DATA_DIR, exist_ok=True)
        data = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [e.to_dict() for e in self._edges],
        }
        with open(_GRAPH_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ── ノード操作 ────────────────────────────────────────────

    def add_node(self,
                 ks_id:           str,
                 title:           str,
                 tags:            list[str],
                 category:        str,
                 summary:         str,
                 semantic_vector: dict,
                 llm_index_score: float) -> GraphNode:
        """
        KS記事をノードとして追加する。
        既存ノードがあれば citation_weight と semantic_vector を更新する。

        Args:
            llm_index_score: DistributionRouterV2 の distribution_policy["llm_index"]
        """
        if ks_id in self._nodes:
            # 既存ノード更新（スコア更新のみ）
            node = self._nodes[ks_id]
            node.semantic_vector = semantic_vector
            node.citation_weight = llm_index_score
        else:
            node = GraphNode(
                ks_id           = ks_id,
                title           = title,
                tags            = list(tags),
                category        = category,
                summary         = summary,
                semantic_vector = semantic_vector,
                citation_weight = llm_index_score,
            )
            self._nodes[ks_id] = node

        self.save()
        return node

    def add_edge(self,
                 source_id: str,
                 target_id: str,
                 edge_type: str,
                 claim:     str,
                 weight:    Optional[float] = None) -> GraphEdge:
        """
        記事間エッジを追加する。
        weight 省略時は両ノードの effective_weight の平均から算出。
        """
        if edge_type not in EDGE_TYPES:
            raise ValueError(f"edge_type は {EDGE_TYPES} のいずれかを指定してください")
        if source_id not in self._nodes:
            raise KeyError(f"ノードが存在しません: {source_id}")
        if target_id not in self._nodes:
            raise KeyError(f"ノードが存在しません: {target_id}")

        if weight is None:
            s = self._nodes[source_id].effective_weight
            t = self._nodes[target_id].effective_weight
            weight = round((s + t) / 2, 3)

        edge = GraphEdge(
            source_id = source_id,
            target_id = target_id,
            edge_type = edge_type,
            weight    = weight,
            claim     = claim[:500],
        )
        self._edges.append(edge)
        self.save()
        return edge

    # ── クエリ ────────────────────────────────────────────────

    def get_node(self, ks_id: str) -> Optional[GraphNode]:
        return self._nodes.get(ks_id)

    def get_outgoing_edges(self, ks_id: str) -> list[GraphEdge]:
        return [e for e in self._edges if e.source_id == ks_id]

    def get_incoming_edges(self, ks_id: str) -> list[GraphEdge]:
        return [e for e in self._edges if e.target_id == ks_id]

    def top_cited_nodes(self, n: int = 10) -> list[tuple[GraphNode, float]]:
        """
        引用重み上位ノードを返す（llm_index × citation_fitness の実効重み順）。
        LLMが最も参照すべき記事ランキング。
        """
        ranked = sorted(
            self._nodes.values(),
            key=lambda node: node.effective_weight,
            reverse=True
        )
        return [(node, node.effective_weight) for node in ranked[:n]]

    def related_nodes(self, ks_id: str,
                      edge_type: Optional[str] = None) -> list[GraphNode]:
        """指定記事から到達可能なノードを返す（エッジタイプでフィルタ可）"""
        edges = self.get_outgoing_edges(ks_id)
        if edge_type:
            edges = [e for e in edges if e.edge_type == edge_type]
        result = []
        for e in edges:
            node = self._nodes.get(e.target_id)
            if node:
                result.append(node)
        return result

    def stats(self) -> dict:
        return {
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "edge_type_counts": {
                et: sum(1 for e in self._edges if e.edge_type == et)
                for et in EDGE_TYPES
            },
        }


# ── LLM Citation Mode ─────────────────────────────────────────

def generate_citation_block(node: GraphNode,
                             related: Optional[list[GraphNode]] = None,
                             max_related: int = 3) -> str:
    """
    LLM引用最適化フォーマットでノード情報を出力する。

    このフォーマットはLLMが記事内容を引用する際に最適な構造を持つ：
    - CLAIM: 記事の主要主張（1文）
    - EVIDENCE: 引用の根拠（semantic_vector）
    - RELATED: 関連記事（LLMが文脈を辿れるよう）

    Returns:
        Markdown形式のLLM引用ブロック
    """
    sv = node.semantic_vector
    related = related or []

    lines = [
        f"## [{node.ks_id}] {node.title}",
        f"",
        f"**CLAIM**: {node.summary}",
        f"",
        f"**EVIDENCE** (Semantic Quality Vector):",
        f"- S1 Semantic Coverage: {sv.get('s1', 0):.3f}",
        f"- S2 Structure Completeness: {sv.get('s2', 0):.3f}",
        f"- S3 Citation Fitness: {sv.get('s3', 0):.3f}",
        f"- S4 Retrieval Fit: {sv.get('s4', 0):.3f}",
        f"- S5 Reusability: {sv.get('s5', 0):.3f}",
        f"- Citation Weight (llm_index × s3): {node.effective_weight:.3f}",
        f"",
        f"**TAGS**: {', '.join(node.tags)}",
        f"**CATEGORY**: {node.category}",
    ]

    if related:
        lines += ["", "**RELATED**:"]
        for r in related[:max_related]:
            lines.append(f"- [{r.ks_id}] {r.title} (weight={r.effective_weight:.3f})")

    return "\n".join(lines)


def generate_graph_index(graph: SemanticGraph, top_n: int = 20) -> str:
    """
    グラフ全体のLLM引用インデックスを生成する。
    LLMが「MoCKA知識グラフ」を参照する際の入口として機能する。
    """
    top = graph.top_cited_nodes(top_n)
    stats = graph.stats()

    lines = [
        "# MoCKA Knowledge Graph - LLM Citation Index",
        f"",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"Nodes: {stats['node_count']} / Edges: {stats['edge_count']}",
        f"",
        f"## Top Cited Articles (by llm_index × citation_fitness)",
        f"",
    ]

    for rank, (node, weight) in enumerate(top, 1):
        lines.append(
            f"{rank}. **[{node.ks_id}]** {node.title}  "
            f"(weight={weight:.3f}, tags={', '.join(node.tags[:3])})"
        )

    lines += [
        "",
        "## Edge Summary",
        "",
    ]
    for et, count in stats["edge_type_counts"].items():
        if count > 0:
            lines.append(f"- {et}: {count} edges")

    return "\n".join(lines)


# ── pros.py連携インターフェース ───────────────────────────────

def register_ks_article(ks_id:           str,
                        title:           str,
                        tags:            list[str],
                        category:        str,
                        summary:         str,
                        semantic_vector: dict,
                        distribution_policy: dict) -> GraphNode:
    """
    KS記事をSemanticGraphに登録するpros.py向けヘルパー。

    Args:
        distribution_policy: DistributionRouterV2.route().to_dict()["distribution_policy"]
    """
    graph = SemanticGraph()
    llm_index_score = distribution_policy.get("llm_index", 0.3)
    node = graph.add_node(
        ks_id           = ks_id,
        title           = title,
        tags            = tags,
        category        = category,
        summary         = summary,
        semantic_vector = semantic_vector,
        llm_index_score = llm_index_score,
    )
    print(f"[SemanticGraph] ノード登録: {ks_id} / weight={node.effective_weight:.3f}")
    return node


if __name__ == "__main__":
    # 動作確認
    graph = SemanticGraph()

    # テストノード追加
    n1 = graph.add_node(
        ks_id="KS_001", title="MoCKA Silence Prohibition Protocol",
        tags=["research", "governance", "ai"],
        category="research",
        summary="沈黙禁止プロトコルはAIガバナンスの基盤として機能する。",
        semantic_vector={"s1": 0.85, "s2": 0.92, "s3": 0.78, "s4": 0.71, "s5": 0.88},
        llm_index_score=0.803,
    )
    n2 = graph.add_node(
        ks_id="KS_002", title="Distribution Router v2 設計",
        tags=["technical", "seo-os", "router"],
        category="development",
        summary="配信の確率分布を決める意思決定関数として設計されたDistribution Router v2。",
        semantic_vector={"s1": 0.80, "s2": 0.88, "s3": 0.72, "s4": 0.65, "s5": 0.82},
        llm_index_score=0.778,
    )

    # エッジ追加
    graph.add_edge(
        source_id="KS_002",
        target_id="KS_001",
        edge_type=EDGE_EXTENDS,
        claim="Distribution Router v2 はMoCKA制度核の知識配信インフラを拡張する。"
    )

    print("=== Stats ===")
    print(json.dumps(graph.stats(), ensure_ascii=False, indent=2))

    print("\n=== Top Cited ===")
    for node, w in graph.top_cited_nodes(5):
        print(f"  {node.ks_id}: {node.title} (effective_weight={w:.3f})")

    print("\n=== LLM Citation Block: KS_001 ===")
    related = graph.related_nodes("KS_002", EDGE_EXTENDS)
    print(generate_citation_block(n1, related=related))

    print("\n=== Graph Index ===")
    print(generate_graph_index(graph))
