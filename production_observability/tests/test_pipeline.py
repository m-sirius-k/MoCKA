import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from observability_pipeline import ObservabilityPipeline
from telemetry_registry import EventType, Severity, TelemetryEvent


def _decision_event(layer: str, request_id: str, consistency_score: float) -> TelemetryEvent:
    return TelemetryEvent.create(
        EventType.DECISION,
        layer=layer,
        request_id=request_id,
        payload={"consistency_score": consistency_score},
    )


def test_event_replay():
    pipeline = ObservabilityPipeline()
    for i in range(5):
        pipeline.emit(TelemetryEvent.create(EventType.REQUEST_START, layer="gateway", request_id=f"r{i}"))

    replayed = pipeline.collector.replay()
    assert len(replayed) == 5
    assert all(e.event_type == EventType.REQUEST_START for e in replayed)

    # replay from offset
    assert len(pipeline.collector.replay(since_index=3)) == 2


def test_multi_layer_trace_reconstruction():
    pipeline = ObservabilityPipeline()
    rid = "req-1"

    pipeline.emit(TelemetryEvent.create(EventType.REQUEST_START, layer="gateway", request_id=rid))
    pipeline.emit(TelemetryEvent.create(EventType.LAYER_ENTER, layer="semantic", request_id=rid))
    pipeline.emit(TelemetryEvent.create(EventType.DECISION, layer="semantic", request_id=rid,
                                         payload={"consistency_score": 0.95}))
    pipeline.emit(TelemetryEvent.create(EventType.LAYER_EXIT, layer="semantic", request_id=rid))
    pipeline.emit(TelemetryEvent.create(EventType.LAYER_ENTER, layer="decision", request_id=rid))
    pipeline.emit(TelemetryEvent.create(EventType.LAYER_EXIT, layer="decision", request_id=rid))
    pipeline.emit(TelemetryEvent.create(EventType.REQUEST_END, layer="gateway", request_id=rid))

    trace = pipeline.trace_builder.build(rid)
    assert trace.request_id == rid
    assert trace.path == ["semantic", "decision"]
    assert trace.duration is not None
    assert trace.duration >= 0
    assert len(trace.decisions) == 1


def test_drift_injection_simulation_and_control_feedback():
    feedback_calls = []
    pipeline = ObservabilityPipeline(feedback=feedback_calls.append)

    layer = "memory"
    # Healthy baseline: high consistency for ~100 decisions
    for i in range(100):
        pipeline.emit(_decision_event(layer, f"baseline-{i}", 0.95))

    # Inject a slow decline (drift): consistency drops over the recent window
    for i in range(20):
        pipeline.emit(_decision_event(layer, f"drift-{i}", 0.6))

    drift_events = pipeline.drift_detector.drift_events()
    assert len(drift_events) > 0
    assert drift_events[-1].metric == "consistency_score"
    assert drift_events[-1].current < drift_events[-1].baseline

    # Drift should have triggered a control action via the feedback loop
    assert len(feedback_calls) > 0
    decisions = pipeline.control_engine.decisions()
    assert any(d.layer == layer for d in decisions)


def test_failure_correlation_mapping():
    pipeline = ObservabilityPipeline()

    pipeline.emit(TelemetryEvent.create(EventType.FAILURE, layer="gateway", request_id="r1",
                                         severity=Severity.CRITICAL))
    pipeline.emit(TelemetryEvent.create(EventType.FAILURE, layer="memory", request_id="r2",
                                         severity=Severity.CRITICAL))
    time.sleep(0.01)
    pipeline.emit(TelemetryEvent.create(EventType.FAILURE, layer="decision", request_id="r3",
                                         severity=Severity.CRITICAL))

    correlated = pipeline.aggregator.correlate_failures(window_seconds=5.0)
    assert len(correlated) == 1
    assert len(correlated[0]) == 3


def test_long_run_degradation_simulation_and_dashboard():
    pipeline = ObservabilityPipeline()
    layer = "decision"

    # Long run: gradually degrading consistency score
    for i in range(150):
        score = max(0.5, 0.98 - i * 0.003)
        pipeline.emit(_decision_event(layer, f"req-{i}", score))
        pipeline.emit(TelemetryEvent.create(EventType.LAYER_ENTER, layer=layer, request_id=f"req-{i}"))
        pipeline.emit(TelemetryEvent.create(EventType.LAYER_EXIT, layer=layer, request_id=f"req-{i}"))

    snapshot = pipeline.snapshot()
    assert 0.0 <= snapshot.system_health_score <= 1.0
    assert layer in snapshot.layer_health
    assert layer in snapshot.layer_stability_index
    # Drift should have been detected as consistency declines
    assert any(d["layer"] == layer for d in snapshot.drift_map)


@pytest.mark.parametrize("n_streams", [1000])
def test_stress_concurrent_event_streams(n_streams):
    """1000+ concurrent event streams with artificial latency injection."""
    import random
    import threading

    pipeline = ObservabilityPipeline()

    def worker(i: int) -> None:
        rid = f"stress-{i}"
        layer = f"layer-{i % 5}"
        pipeline.emit(TelemetryEvent.create(EventType.REQUEST_START, layer=layer, request_id=rid))
        pipeline.emit(TelemetryEvent.create(EventType.LAYER_ENTER, layer=layer, request_id=rid))
        # artificial latency injection
        if i % 50 == 0:
            time.sleep(0.001 * (i % 5))
        if i % 97 == 0:
            pipeline.emit(TelemetryEvent.create(EventType.FAILURE, layer=layer, request_id=rid,
                                                 severity=Severity.CRITICAL))
        pipeline.emit(TelemetryEvent.create(EventType.LAYER_EXIT, layer=layer, request_id=rid))
        pipeline.emit(TelemetryEvent.create(EventType.REQUEST_END, layer=layer, request_id=rid))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_streams)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected_failures = len([i for i in range(n_streams) if i % 97 == 0])
    assert len(pipeline.collector) == n_streams * 4 + expected_failures
    snapshot = pipeline.snapshot()
    assert snapshot.system_health_score >= 0.0

    # cascading failure visualization data is available
    assert sum(snapshot.failure_heatmap.values()) > 0


def test_control_feedback_loop_stability_under_repeated_drift():
    pipeline = ObservabilityPipeline()
    layer = "semantic"

    for i in range(100):
        pipeline.emit(_decision_event(layer, f"base-{i}", 0.95))

    # repeated severe drift bursts shouldn't crash or grow unboundedly
    for burst in range(3):
        for i in range(25):
            pipeline.emit(_decision_event(layer, f"burst{burst}-{i}", 0.3))

    decisions = pipeline.control_engine.decisions()
    assert len(decisions) > 0
    # safe mode should engage under sustained severe drift
    assert pipeline.control_engine.is_safe_mode(layer) or any(
        d.layer == layer for d in decisions
    )
