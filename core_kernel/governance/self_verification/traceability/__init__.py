"""Traceability & Governance Closure (Phase 6).

Converts the per-Requirement layer paths in requirement_map and the
Evidence collected by evidence.collect_evidence into a single Trace
Graph:

    REQ -> CONTRACT -> IMPLEMENTATION -> TEST -> EVIDENCE -> AUDIT

from which a Coverage Matrix, a Governance Closure check (no
unconnected nodes), and Drift Detection are derived.
"""

from .trace_graph import TraceGraph, TraceLayer, TraceNode, build_trace_graph
from .coverage_matrix import CoverageMatrix, build_coverage_matrix
from .governance_closure import ClosureReport, check_closure
from .drift_detection import DriftFinding, detect_drift

__all__ = [
    "TraceGraph",
    "TraceLayer",
    "TraceNode",
    "build_trace_graph",
    "CoverageMatrix",
    "build_coverage_matrix",
    "ClosureReport",
    "check_closure",
    "DriftFinding",
    "detect_drift",
]
