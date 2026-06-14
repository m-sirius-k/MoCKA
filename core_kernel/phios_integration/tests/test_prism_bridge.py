"""
phios_integration.tests.test_prism_bridge

PHI-OS -> Prism 実統合(接続のみ)に関するテスト。
"""

from core_kernel.core_store import LifecycleManager, ModuleMetadata, ModuleRegistry
from core_kernel.event_contracts import build_event
from core_kernel.phios_integration import PrismBridge
from core_kernel.prism import AnalysisResult


def _make_event(event_type="change_start", source_module="test_module", **kwargs):
    return build_event(
        event_type=event_type,
        source_module=source_module,
        payload={"detail": "test"},
        **kwargs,
    )


def test_bridge_starts_uninitialized():
    bridge = PrismBridge()
    assert bridge.is_initialized() is False


def test_initialize_prism_succeeds():
    bridge = PrismBridge()
    result = bridge.initialize_prism()

    assert result["status"] == "ok"
    assert result["health"]["status"] == "ok"
    assert bridge.is_initialized() is True


def test_initialize_prism_with_core_store():
    registry = ModuleRegistry()
    lifecycle = LifecycleManager()
    registry.register("module", ModuleMetadata(
        module_id="orchestra", capability=(), dependency=(),
    ))
    lifecycle.register("orchestra")

    bridge = PrismBridge()
    result = bridge.initialize_prism(registry=registry, lifecycle=lifecycle)

    assert result["status"] == "ok"
    assert result["health"]["pipeline_ready"] is True


def test_analyze_event_without_initialization_returns_error():
    bridge = PrismBridge()
    result = bridge.analyze_event(_make_event())

    assert result["status"] == "error"
    assert result["error_type"] == "provider_not_initialized"


def test_analyze_events_without_initialization_returns_error():
    bridge = PrismBridge()
    result = bridge.analyze_events([_make_event()])

    assert result["status"] == "error"
    assert result["error_type"] == "provider_not_initialized"


def test_analyze_event_success():
    bridge = PrismBridge()
    bridge.initialize_prism()

    event = _make_event()
    result = bridge.analyze_event(event)

    assert result["status"] == "ok"
    assert isinstance(result["result"], AnalysisResult)
    assert result["result"].observation.evidence_event_ids == (event["event_id"],)


def test_analyze_events_success():
    bridge = PrismBridge()
    bridge.initialize_prism()

    events = [_make_event(), _make_event(event_type="change_done")]
    result = bridge.analyze_events(events)

    assert result["status"] == "ok"
    assert len(result["result"].annotations) == 2


def test_analyze_event_validation_failure():
    bridge = PrismBridge()
    bridge.initialize_prism()

    invalid_event = {"event_type": "change_start"}  # 必須フィールド不足
    result = bridge.analyze_event(invalid_event)

    assert result["status"] == "error"
    assert result["error_type"] == "validation_error"


def test_analyze_events_empty_input():
    bridge = PrismBridge()
    bridge.initialize_prism()

    result = bridge.analyze_events([])

    assert result["status"] == "error"
    assert result["error_type"] == "validation_error"


def test_bridge_does_not_mutate_registry():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(
        module_id="orchestra", capability=(), dependency=(),
    ))
    before = registry.snapshot()

    bridge = PrismBridge()
    bridge.initialize_prism(registry=registry)
    bridge.analyze_event(_make_event())
    bridge.analyze_events([_make_event(), _make_event(event_type="change_done")])

    after = registry.snapshot()
    assert before == after


def test_bridge_result_does_not_dispatch_anywhere():
    """analyze結果は単にdictとして返却されるのみであることを確認する。"""
    bridge = PrismBridge()
    bridge.initialize_prism()

    result = bridge.analyze_event(_make_event())

    assert set(result.keys()) == {"status", "result"}
    analysis = result["result"]
    assert hasattr(analysis, "context")
    assert hasattr(analysis, "annotations")
    assert hasattr(analysis, "cognitive_state")
    assert hasattr(analysis, "observation")
