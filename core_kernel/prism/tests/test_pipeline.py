"""
prism.tests.test_pipeline

PrismPipeline / PrismAnalyzer に関するテスト。
"""

import pytest

from core_kernel.event_contracts import build_event
from core_kernel.prism import (
    AnalysisResult,
    CognitiveState,
    Context,
    InvalidEventError,
    Observation,
    PrismAnalyzer,
)
from core_kernel.prism.pipeline import PrismPipeline


def _make_event(event_type="change_start", source_module="test_module", **kwargs):
    return build_event(
        event_type=event_type,
        source_module=source_module,
        payload={"detail": "test"},
        **kwargs,
    )


def test_pipeline_run_with_single_event():
    pipeline = PrismPipeline()
    event = _make_event()

    result = pipeline.run([event])

    assert len(result.annotations) == 1
    assert isinstance(result.context, Context)
    assert isinstance(result.cognitive_state, CognitiveState)
    assert isinstance(result.observation, Observation)
    assert result.context.event_ids == (event["event_id"],)


def test_pipeline_run_with_invalid_event_raises():
    pipeline = PrismPipeline()
    invalid_event = {"event_type": "change_start"}  # 必須フィールド不足

    with pytest.raises(InvalidEventError):
        pipeline.run([invalid_event])


def test_pipeline_run_with_empty_events():
    pipeline = PrismPipeline()

    result = pipeline.run([])

    assert result.annotations == ()
    assert result.context.event_ids == ()
    assert result.cognitive_state.state == "INCOMPLETE"


def test_pipeline_fixed_stage_order_produces_consistent_result():
    pipeline = PrismPipeline()
    event1 = _make_event(event_type="change_start", source_module="orchestra")
    event2 = _make_event(event_type="change_done", source_module="orchestra")

    result = pipeline.run([event1, event2])

    assert len(result.annotations) == 2
    assert set(result.context.event_ids) == {event1["event_id"], event2["event_id"]}
    assert result.context.actors == ("orchestra",)
    # source相関により1件以上のrelationshipが生成される
    assert any(r["type"] == "source" for r in result.context.relationships)


def test_analyzer_analyze_single_event():
    analyzer = PrismAnalyzer()
    event = _make_event()

    result = analyzer.analyze(event)

    assert isinstance(result, AnalysisResult)
    assert len(result.annotations) == 1
    assert result.observation.evidence_event_ids == (event["event_id"],)


def test_analyzer_analyze_many_events():
    analyzer = PrismAnalyzer()
    events = [_make_event(), _make_event(event_type="change_done")]

    result = analyzer.analyze_many(events)

    assert len(result.annotations) == 2
    assert isinstance(result.context, Context)


def test_pipeline_multi_category_is_unstable():
    pipeline = PrismPipeline()
    event1 = _make_event(event_type="change_start", source_module="orchestra")
    event2 = _make_event(event_type="context_capture", source_module="orchestra")

    result = pipeline.run([event1, event2])

    assert result.cognitive_state.state == "UNSTABLE"
    assert result.observation.risk_level == "medium"
    assert result.observation.finding


def test_pipeline_unknown_events_are_uncertain():
    pipeline = PrismPipeline()
    event1 = _make_event(event_type="totally_unknown_type")
    event2 = _make_event(event_type="another_unknown_type")

    result = pipeline.run([event1, event2])

    assert result.cognitive_state.state == "UNCERTAIN"


def test_pipeline_circular_causality_is_conflict():
    pipeline = PrismPipeline()
    event1 = _make_event(event_type="change_start", source_module="orchestra")
    event2 = _make_event(
        event_type="change_done",
        source_module="orchestra",
        metadata={"caused_by_event_id": event1["event_id"]},
    )
    # event1がevent2に起因する、という循環関係を追加する
    event1["metadata"] = {"caused_by_event_id": event2["event_id"]}

    result = pipeline.run([event1, event2])

    assert result.cognitive_state.state == "CONFLICT"
    assert result.observation.risk_level == "high"


def test_pipeline_timestamp_correlation():
    pipeline = PrismPipeline()
    event1 = _make_event(event_type="change_start", source_module="a")
    event2 = _make_event(event_type="change_done", source_module="b", timestamp=event1["timestamp"])

    result = pipeline.run([event1, event2])

    assert any(r["type"] == "timestamp" for r in result.context.relationships)


def test_analyzer_public_api_surface():
    analyzer = PrismAnalyzer()
    public_methods = {
        name for name in dir(analyzer)
        if not name.startswith("_") and callable(getattr(analyzer, name))
    }
    assert public_methods == {"analyze", "analyze_many"}
