"""Governance Closure.

Closure means: no REQ, CONTRACT, IMPLEMENTATION, TEST, EVIDENCE or
AUDIT node in the Trace Graph is disconnected. If even one node is
unconnected, the chain for that Requirement is broken and Closure is
not achieved.
"""

from __future__ import annotations

from dataclasses import dataclass

from .trace_graph import TraceGraph


@dataclass(frozen=True)
class ClosureReport:
    is_closed: bool
    unconnected: tuple[tuple[str, str], ...]  # (req_id, layer.value)


def check_closure(graph: TraceGraph) -> ClosureReport:
    unconnected = tuple(
        (req_id, layer.value)
        for req_id, layers in graph.nodes.items()
        for layer, node in layers.items()
        if not node.connected
    )
    return ClosureReport(is_closed=not unconnected, unconnected=unconnected)
