# ui/conflict_view_model.py
# Conflict 可視化モデル v1
#
# 責務:
#   PHI / Personal を並列保持し、state をそのまま表現するデータ構造。
#   変更・統合は行わない。観測専用。

from __future__ import annotations
import datetime
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────
# ConflictVisualNode — 1 term の両系ビュー
# ─────────────────────────────────────────────────────────────

@dataclass
class ConflictVisualNode:
    term: str
    phi_value: Optional[str]
    personal_value: Optional[str]
    state: str          # NORMAL / DRIFT / CONFLICT / LOCKED
    severity: float     # 0.0–1.0

    def is_conflicted(self) -> bool:
        return self.state == "CONFLICT"

    def is_drifted(self) -> bool:
        return self.state == "DRIFT"

    def is_locked(self) -> bool:
        return self.state == "LOCKED"


# ─────────────────────────────────────────────────────────────
# ConflictEdge — 2 Node 間の関係（意味の非同一性を表す）
# ─────────────────────────────────────────────────────────────

@dataclass
class ConflictEdge:
    source_term: str
    target_term: str
    relation: str       # e.g. "DEPENDS_ON", "CONFLICTS", "SYNONYM"
    weight: float = 1.0


# ─────────────────────────────────────────────────────────────
# ConflictGraph — Node + Edge の集合
# ─────────────────────────────────────────────────────────────

class ConflictGraph:
    """
    PHI / Personal 両系の状態を並列保持するグラフ構造。
    意味を変えない。Edgeを追加するだけで関係を記録する。
    """

    def __init__(self):
        self._nodes: dict[str, ConflictVisualNode] = {}
        self._edges: list[ConflictEdge] = []
        self.built_at: str = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # ── Node 操作 ─────────────────────────────────────────────

    def add_node(self, node: ConflictVisualNode) -> None:
        self._nodes[node.term] = node

    def get_node(self, term: str) -> Optional[ConflictVisualNode]:
        return self._nodes.get(term)

    def nodes(self) -> list[ConflictVisualNode]:
        return list(self._nodes.values())

    def nodes_by_state(self, state: str) -> list[ConflictVisualNode]:
        return [n for n in self._nodes.values() if n.state == state]

    # ── Edge 操作 ─────────────────────────────────────────────

    def add_edge(self, edge: ConflictEdge) -> None:
        self._edges.append(edge)

    def edges(self) -> list[ConflictEdge]:
        return list(self._edges)

    def edges_for(self, term: str) -> list[ConflictEdge]:
        return [e for e in self._edges if e.source_term == term or e.target_term == term]

    # ── 集計 ──────────────────────────────────────────────────

    def summary(self) -> dict:
        by_state: dict[str, int] = {}
        for n in self._nodes.values():
            by_state[n.state] = by_state.get(n.state, 0) + 1
        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "by_state":    by_state,
            "built_at":    self.built_at,
        }


# ─────────────────────────────────────────────────────────────
# Factory: BridgeRecord / Decision → ConflictGraph 構築
# ─────────────────────────────────────────────────────────────

def build_graph_from_records(records: list, decisions: dict | None = None) -> ConflictGraph:
    """
    BridgeRecord のリストから ConflictGraph を構築する。
    decisions: {term: Decision} で severity を補完できる（省略時は state から算出）。

    意味の変更は行わない。
    """
    from phi_os.phi_bridge_governance import severity_from_state

    graph = ConflictGraph()

    for record in records:
        state_str = record.state.value if hasattr(record.state, "value") else str(record.state)
        severity = 0.0
        if decisions and record.term in decisions:
            severity = decisions[record.term].severity
        else:
            severity = severity_from_state(state_str)

        node = ConflictVisualNode(
            term=record.term,
            phi_value=record.phi_os_meaning,
            personal_value=record.personal_meaning,
            state=state_str,
            severity=severity,
        )
        graph.add_node(node)

    return graph
