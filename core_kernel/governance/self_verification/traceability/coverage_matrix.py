"""Coverage Matrix.

Flattens a TraceGraph into a req_id x layer boolean matrix plus
aggregate coverage percentages, and surfaces the three required
categories from the くろこ指示書:

  - REQカバレッジ            -> per_requirement
  - Contract未実装検出        -> contract_without_implementation
  - 実装済み未テスト検出       -> implementation_without_test
  - テスト未証跡検出           -> test_without_evidence_or_audit
"""

from __future__ import annotations

from dataclasses import dataclass

from .trace_graph import TraceGraph, TraceLayer


@dataclass(frozen=True)
class CoverageMatrix:
    matrix: dict[str, dict[TraceLayer, bool]]
    coverage_percent: float
    contract_without_implementation: tuple[str, ...]
    implementation_without_test: tuple[str, ...]
    test_without_evidence_or_audit: tuple[str, ...]


def build_coverage_matrix(graph: TraceGraph) -> CoverageMatrix:
    matrix: dict[str, dict[TraceLayer, bool]] = {
        req_id: {layer: node.connected for layer, node in layers.items()}
        for req_id, layers in graph.nodes.items()
    }

    total = sum(len(row) for row in matrix.values())
    connected = sum(1 for row in matrix.values() for v in row.values() if v)
    coverage_percent = 100.0 * connected / total if total else 0.0

    contract_without_implementation = tuple(
        req_id
        for req_id, row in matrix.items()
        if row[TraceLayer.CONTRACT] and not row[TraceLayer.IMPLEMENTATION]
    )
    implementation_without_test = tuple(
        req_id
        for req_id, row in matrix.items()
        if row[TraceLayer.IMPLEMENTATION] and not row[TraceLayer.TEST]
    )
    test_without_evidence_or_audit = tuple(
        req_id
        for req_id, row in matrix.items()
        if row[TraceLayer.TEST] and not (row[TraceLayer.EVIDENCE] and row[TraceLayer.AUDIT])
    )

    return CoverageMatrix(
        matrix=matrix,
        coverage_percent=coverage_percent,
        contract_without_implementation=contract_without_implementation,
        implementation_without_test=implementation_without_test,
        test_without_evidence_or_audit=test_without_evidence_or_audit,
    )
