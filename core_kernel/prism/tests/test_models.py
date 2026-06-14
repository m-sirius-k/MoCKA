"""
prism.tests.test_models

Prismのデータモデル(Context/SemanticAnnotation/Observation/CognitiveState)
に関するテスト。
"""

import pytest

from core_kernel.prism.models import (
    CognitiveState,
    CognitiveStateValue,
    Context,
    Observation,
    SemanticAnnotation,
)


def test_semantic_annotation_to_dict_round_trip():
    annotation = SemanticAnnotation(
        annotation_id="ann-1",
        event_id="evt-1",
        meaning="テスト",
        category="test",
        confidence=0.9,
        explanation="説明",
        metadata={"k": "v"},
    )
    data = annotation.to_dict()

    assert data == {
        "annotation_id": "ann-1",
        "event_id": "evt-1",
        "meaning": "テスト",
        "category": "test",
        "confidence": 0.9,
        "explanation": "説明",
        "metadata": {"k": "v"},
    }


def test_semantic_annotation_defaults():
    annotation = SemanticAnnotation(
        annotation_id="ann-1",
        event_id="evt-1",
        meaning="テスト",
        category="test",
        confidence=0.5,
    )
    assert annotation.explanation == ""
    assert annotation.metadata == {}


def test_context_to_dict_round_trip():
    context = Context(
        context_id="ctx-1",
        event_ids=("evt-1", "evt-2"),
        time_window=("2026-01-01T00:00:00Z", "2026-01-01T01:00:00Z"),
        actors=("orchestra",),
        topics=("lifecycle",),
        relationships=({"type": "source", "from": "evt-1", "to": "evt-2", "detail": "x"},),
        system_state={"registry": {}},
        metadata={"k": "v"},
    )
    data = context.to_dict()

    assert data["context_id"] == "ctx-1"
    assert data["event_ids"] == ["evt-1", "evt-2"]
    assert data["time_window"] == ["2026-01-01T00:00:00Z", "2026-01-01T01:00:00Z"]
    assert data["actors"] == ["orchestra"]
    assert data["topics"] == ["lifecycle"]
    assert data["relationships"] == [{"type": "source", "from": "evt-1", "to": "evt-2", "detail": "x"}]
    assert data["system_state"] == {"registry": {}}
    assert data["metadata"] == {"k": "v"}


def test_context_defaults():
    context = Context(context_id="ctx-1")
    assert context.event_ids == ()
    assert context.time_window == ()
    assert context.actors == ()
    assert context.topics == ()
    assert context.relationships == ()
    assert context.system_state == {}
    assert context.metadata == {}


def test_observation_to_dict_round_trip():
    observation = Observation(
        observation_id="obs-1",
        timestamp="2026-01-01T00:00:00Z",
        confidence=0.8,
        finding="特に問題なし",
        evidence_event_ids=("evt-1",),
        recommendation="特になし",
        risk_level="low",
        metadata={"cognitive_state": "STABLE"},
    )
    data = observation.to_dict()

    assert data == {
        "observation_id": "obs-1",
        "timestamp": "2026-01-01T00:00:00Z",
        "confidence": 0.8,
        "finding": "特に問題なし",
        "evidence_event_ids": ["evt-1"],
        "recommendation": "特になし",
        "risk_level": "low",
        "metadata": {"cognitive_state": "STABLE"},
    }


def test_observation_defaults():
    observation = Observation(
        observation_id="obs-1",
        timestamp="2026-01-01T00:00:00Z",
        confidence=0.5,
    )
    assert observation.finding == ""
    assert observation.evidence_event_ids == ()
    assert observation.recommendation == ""
    assert observation.risk_level == "unknown"
    assert observation.metadata == {}


def test_cognitive_state_value_constants():
    assert CognitiveStateValue.ALL == (
        "STABLE", "UNSTABLE", "UNCERTAIN", "INCOMPLETE", "CONFLICT",
    )


def test_cognitive_state_to_dict_round_trip():
    state = CognitiveState(
        state=CognitiveStateValue.STABLE,
        confidence=0.95,
        reason="安定",
        metadata={"categories": ["lifecycle"]},
    )
    data = state.to_dict()

    assert data == {
        "state": "STABLE",
        "confidence": 0.95,
        "reason": "安定",
        "metadata": {"categories": ["lifecycle"]},
    }


@pytest.mark.parametrize("dataclass_cls", [Context, Observation, SemanticAnnotation, CognitiveState])
def test_models_are_frozen(dataclass_cls):
    assert dataclass_cls.__dataclass_params__.frozen is True
