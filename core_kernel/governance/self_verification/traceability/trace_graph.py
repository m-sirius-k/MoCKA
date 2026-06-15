"""Trace Graph.

Builds the REQ -> CONTRACT -> IMPLEMENTATION -> TEST -> EVIDENCE -> AUDIT
chain for every Requirement in requirement_map.REQUIREMENTS, as a graph
of TraceNodes. A node is "connected" if the corresponding artifact
exists (file on disk) or was observed (Evidence/Audit record).

This module only observes; it does not judge whether the *content* of
a node is correct (that is unit/integration tests' job) — it answers
"does this link in the chain exist at all".
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from ..evidence import EvidenceBundle
from ..requirement_map import REQUIREMENTS, Requirement


class TraceLayer(str, Enum):
    REQ = "REQ"
    CONTRACT = "CONTRACT"
    IMPLEMENTATION = "IMPLEMENTATION"
    TEST = "TEST"
    EVIDENCE = "EVIDENCE"
    AUDIT = "AUDIT"


TRACE_LAYER_ORDER: tuple[TraceLayer, ...] = tuple(TraceLayer)


@dataclass(frozen=True)
class TraceNode:
    req_id: str
    layer: TraceLayer
    connected: bool
    detail: str


@dataclass(frozen=True)
class TraceGraph:
    """req_id -> {layer -> TraceNode}, in TRACE_LAYER_ORDER."""

    nodes: dict[str, dict[TraceLayer, TraceNode]]

    def edges(self) -> list[tuple[str, TraceLayer, TraceLayer]]:
        """All (req_id, from_layer, to_layer) edges in the fixed chain."""
        edges = []
        for req_id in self.nodes:
            for a, b in zip(TRACE_LAYER_ORDER[:-1], TRACE_LAYER_ORDER[1:]):
                edges.append((req_id, a, b))
        return edges


def _contract_node(req: Requirement, root: Path) -> TraceNode:
    connected = (root / req.contract).exists()
    return TraceNode(req.req_id, TraceLayer.CONTRACT, connected, str(req.contract))


def _implementation_node(req: Requirement, root: Path) -> TraceNode:
    missing = [str(p) for p in req.implementation if not (root / p).exists()]
    return TraceNode(req.req_id, TraceLayer.IMPLEMENTATION, not missing, ",".join(str(p) for p in req.implementation))


def _test_node(req: Requirement, root: Path) -> TraceNode:
    paths = [req.unit_test] + ([req.integration_test] if req.integration_test else [])
    missing = [str(p) for p in paths if not (root / p).exists()]
    return TraceNode(req.req_id, TraceLayer.TEST, not missing, ",".join(str(p) for p in paths))


def _evidence_node(req: Requirement, evidence: EvidenceBundle) -> TraceNode:
    connected = len(evidence.audit_records) > 0 and len(evidence.results) > 0
    return TraceNode(req.req_id, TraceLayer.EVIDENCE, connected, f"{len(evidence.audit_records)} audit records")


def _audit_node(req: Requirement, evidence: EvidenceBundle) -> TraceNode:
    engines_present = {r.engine for r in evidence.audit_records}
    if req.audit_engines:
        missing = [e for e in req.audit_engines if e not in engines_present]
        return TraceNode(req.req_id, TraceLayer.AUDIT, not missing, f"engines={req.audit_engines}")
    connected = len(evidence.audit_records) > 0
    return TraceNode(req.req_id, TraceLayer.AUDIT, connected, "any audit record")


def build_trace_graph(evidence: EvidenceBundle, root: Path) -> TraceGraph:
    nodes: dict[str, dict[TraceLayer, TraceNode]] = {}
    for req in REQUIREMENTS:
        nodes[req.req_id] = {
            TraceLayer.REQ: TraceNode(req.req_id, TraceLayer.REQ, True, req.title),
            TraceLayer.CONTRACT: _contract_node(req, root),
            TraceLayer.IMPLEMENTATION: _implementation_node(req, root),
            TraceLayer.TEST: _test_node(req, root),
            TraceLayer.EVIDENCE: _evidence_node(req, evidence),
            TraceLayer.AUDIT: _audit_node(req, evidence),
        }
    return TraceGraph(nodes=nodes)
