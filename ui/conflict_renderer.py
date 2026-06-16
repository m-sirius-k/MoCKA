# ui/conflict_renderer.py
# Conflict コンソール描画レイヤ v1
#
# 責務:
#   ConflictGraph / ConflictVisualNode を人間が読める形式でコンソール出力する。
#   表示のみ。意味の変更・統合は行わない。

from __future__ import annotations
import io
from typing import Optional

from ui.conflict_view_model import ConflictEdge, ConflictGraph, ConflictVisualNode


# ─────────────────────────────────────────────────────────────
# State → 表示記号
# ─────────────────────────────────────────────────────────────

_STATE_SYMBOL = {
    "NORMAL":   "[ ]",
    "DRIFT":    "[~]",
    "CONFLICT": "[!]",
    "LOCKED":   "[L]",
}

_SEVERITY_BAR_WIDTH = 20


def _severity_bar(severity: float) -> str:
    filled = round(severity * _SEVERITY_BAR_WIDTH)
    return "[" + "#" * filled + "-" * (_SEVERITY_BAR_WIDTH - filled) + "]"


def _truncate(text: Optional[str], width: int = 60) -> str:
    if text is None:
        return "(none)"
    return text if len(text) <= width else text[:width - 3] + "..."


# ─────────────────────────────────────────────────────────────
# ConflictRenderer
# ─────────────────────────────────────────────────────────────

class ConflictRenderer:
    """
    ConflictGraph をコンソールに描画する。
    出力先は stdout（デフォルト）または任意の io.TextIOBase。
    """

    def __init__(self, out: Optional[io.TextIOBase] = None):
        import sys
        self._out = out or sys.stdout

    def _write(self, line: str = "") -> None:
        self._out.write(line + "\n")

    # ─────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────

    def render_graph(self, graph: ConflictGraph) -> None:
        """グラフ全体を描画する。"""
        summary = graph.summary()
        self._write("=" * 70)
        self._write("  CONFLICT GRAPH  —  PHI-OS ↔ Personal Lexicon Bridge")
        self._write("=" * 70)
        self._write(f"  nodes: {summary['total_nodes']}  |  edges: {summary['total_edges']}")
        by_state = summary.get("by_state", {})
        state_line = "  " + "  ".join(
            f"{k}:{v}" for k, v in by_state.items()
        )
        self._write(state_line)
        self._write(f"  built_at: {summary['built_at']}")
        self._write("-" * 70)

        # state 順でソート: CONFLICT > LOCKED > DRIFT > NORMAL
        _order = {"CONFLICT": 0, "LOCKED": 1, "DRIFT": 2, "NORMAL": 3}
        nodes = sorted(graph.nodes(), key=lambda n: (_order.get(n.state, 9), n.term))

        for node in nodes:
            self.render_node(node)
            # そのノードに関連する Edge があれば表示
            edges = graph.edges_for(node.term)
            if edges:
                for edge in edges:
                    self._render_edge_inline(edge, current_term=node.term)
            self._write()

        if not nodes:
            self._write("  (no nodes registered)")

        self._write("=" * 70)

    def render_node(self, node: ConflictVisualNode) -> None:
        """
        1 node を以下フォーマットで描画:
          TERM
          PHI VALUE
          PERSONAL VALUE
          STATE
          SEVERITY
        """
        sym = _STATE_SYMBOL.get(node.state, "[?]")
        self._write(f"{sym} TERM      : {node.term}")
        self._write(f"    PHI      : {_truncate(node.phi_value)}")
        self._write(f"    PERSONAL : {_truncate(node.personal_value)}")
        self._write(f"    STATE    : {node.state}")
        self._write(f"    SEVERITY : {_severity_bar(node.severity)}  {node.severity:.3f}")

    def render_node_by_term(self, graph: ConflictGraph, term: str) -> None:
        """term を指定して単一ノードを描画する。"""
        node = graph.get_node(term)
        if node is None:
            self._write(f"[not found] {term}")
            return
        self.render_node(node)

    def render_conflicts_only(self, graph: ConflictGraph) -> None:
        """CONFLICT 状態のノードのみ描画する。"""
        nodes = graph.nodes_by_state("CONFLICT")
        self._write(f"--- CONFLICT nodes ({len(nodes)}) ---")
        for node in nodes:
            self.render_node(node)
            self._write()

    def render_summary(self, graph: ConflictGraph) -> None:
        """サマリのみ描画する。"""
        s = graph.summary()
        self._write(f"nodes={s['total_nodes']}  edges={s['total_edges']}  "
                    + "  ".join(f"{k}:{v}" for k, v in s.get("by_state", {}).items()))

    def _render_edge_inline(self, edge: ConflictEdge, current_term: str) -> None:
        other = edge.target_term if edge.source_term == current_term else edge.source_term
        direction = "->" if edge.source_term == current_term else "<-"
        self._write(
            f"    EDGE  {direction} [{other}]  rel={edge.relation}  w={edge.weight:.2f}"
        )
