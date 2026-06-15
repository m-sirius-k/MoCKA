"""Drift Engine Core (DRIFT_ENGINE_v1.md SS7-9).

Pipeline: Node Alignment -> Transition Mapping -> Constraint Comparison
-> Output Diff Calculation -> Vector Generation -> Classification -> Severity Scoring.
"""
from __future__ import annotations

from mocka3.glk_runtime_bridge.events import emit_event
from mocka3.drift_engine.types import DriftSummary, DriftType, DriftVector, ExpectedState, ObservedState

STRUCTURAL_WEIGHT = 0.4
SEMANTIC_WEIGHT = 0.3
CONSTRAINT_WEIGHT = 0.3


def _node_alignment(expected: ExpectedState, observed: ObservedState) -> list[DriftVector]:
    vectors: list[DriftVector] = []
    expected_set = set(expected.expected_nodes)
    observed_set = set(observed.observed_nodes)

    for missing in expected_set - observed_set:
        vectors.append(
            DriftVector(
                type=DriftType.STRUCTURAL,
                magnitude=1.0,
                source_node_id=missing,
                target_node_id=None,
                description=f"expected node '{missing}' was not observed",
            )
        )
    for extra in observed_set - expected_set:
        vectors.append(
            DriftVector(
                type=DriftType.STRUCTURAL,
                magnitude=1.0,
                source_node_id=None,
                target_node_id=extra,
                description=f"observed node '{extra}' was not expected",
            )
        )
    return vectors


def _transition_mapping(expected: ExpectedState, observed: ObservedState) -> list[DriftVector]:
    vectors: list[DriftVector] = []
    common_len = min(len(expected.expected_transitions), len(observed.observed_transitions))
    for i in range(common_len):
        exp_id = expected.expected_transitions[i]
        obs_id = observed.observed_transitions[i]
        if exp_id != obs_id:
            vectors.append(
                DriftVector(
                    type=DriftType.STRUCTURAL,
                    magnitude=0.5,
                    source_node_id=exp_id,
                    target_node_id=obs_id,
                    description=f"transition order mismatch at position {i}: expected '{exp_id}', observed '{obs_id}'",
                )
            )
    return vectors


def _constraint_comparison(expected: ExpectedState, observed: ObservedState) -> list[DriftVector]:
    vectors: list[DriftVector] = []
    for constraint_id in expected.expected_constraints:
        status = observed.constraint_satisfaction_report.get(constraint_id)
        if status != "satisfied":
            vectors.append(
                DriftVector(
                    type=DriftType.CONSTRAINT,
                    magnitude=1.0,
                    source_node_id=constraint_id,
                    target_node_id=None,
                    description=f"constraint '{constraint_id}' not satisfied (status={status!r})",
                )
            )
    return vectors


def _output_diff(expected: ExpectedState, observed: ObservedState) -> list[DriftVector]:
    vectors: list[DriftVector] = []
    for node_id, expected_value in expected.expected_outputs.items():
        observed_value = observed.observed_outputs.get(node_id)
        if observed_value is None:
            continue  # already reported by node alignment
        if observed_value != expected_value:
            vectors.append(
                DriftVector(
                    type=DriftType.SEMANTIC,
                    magnitude=0.5,
                    source_node_id=node_id,
                    target_node_id=None,
                    description=(
                        f"output mismatch for '{node_id}': expected '{expected_value}', "
                        f"observed '{observed_value}'"
                    ),
                )
            )
    return vectors


def _classify(vectors: list[DriftVector]) -> list[DriftVector]:
    """SS8 classification rules. STRUCTURAL/SEMANTIC/CONSTRAINT magnitude==1.0
    structural drift on a missing node escalates to CRITICAL (execution-unable level)."""
    classified: list[DriftVector] = []
    for v in vectors:
        if v.type == DriftType.STRUCTURAL and v.source_node_id is not None and v.magnitude >= 1.0:
            classified.append(
                DriftVector(
                    type=DriftType.CRITICAL,
                    magnitude=v.magnitude,
                    source_node_id=v.source_node_id,
                    target_node_id=v.target_node_id,
                    description=v.description,
                )
            )
        else:
            classified.append(v)
    return classified


def _severity_score(vectors: list[DriftVector]) -> float:
    if not vectors:
        return 0.0

    structural = sum(v.magnitude for v in vectors if v.type in (DriftType.STRUCTURAL, DriftType.CRITICAL))
    semantic = sum(v.magnitude for v in vectors if v.type == DriftType.SEMANTIC)
    constraint = sum(v.magnitude for v in vectors if v.type == DriftType.CONSTRAINT)

    n = len(vectors)
    score = (
        STRUCTURAL_WEIGHT * (structural / n)
        + SEMANTIC_WEIGHT * (semantic / n)
        + CONSTRAINT_WEIGHT * (constraint / n)
    )
    return min(1.0, score)


def analyze(
    expected: ExpectedState,
    observed: ObservedState,
    event_sink: list[dict] | None = None,
) -> DriftSummary:
    """SS7.2 Processing Pipeline -> SS7.3 Output (DriftSet, SeverityScore)."""
    raw_vectors: list[DriftVector] = []
    raw_vectors += _node_alignment(expected, observed)
    raw_vectors += _transition_mapping(expected, observed)
    raw_vectors += _constraint_comparison(expected, observed)
    raw_vectors += _output_diff(expected, observed)

    if raw_vectors:
        emit_event("DRIFT_DETECTED", {"vector_count": len(raw_vectors)}, sink=event_sink)

    drift_set = _classify(raw_vectors)
    emit_event("DRIFT_CLASSIFIED", {"types": [v.type.value for v in drift_set]}, sink=event_sink)

    for v in drift_set:
        emit_event(
            "DRIFT_VECTOR_EMITTED",
            {"type": v.type.value, "source": v.source_node_id, "target": v.target_node_id},
            sink=event_sink,
        )

    severity = _severity_score(drift_set)
    return DriftSummary(drift_set=drift_set, severity_score=severity)
