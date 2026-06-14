"""
prism.tests.test_provider

PrismProvider (PHI-OS統合準備の接続口) に関するテスト。
"""

from core_kernel.core_store import LifecycleManager, ModuleMetadata, ModuleRegistry
from core_kernel.event_contracts import build_event
from core_kernel.prism import (
    AnalysisResult,
    CAPABILITY_COGNITION,
    PRISM_VERSION,
    PrismProvider,
)


def _make_event(event_type="change_start", source_module="test_module", **kwargs):
    return build_event(
        event_type=event_type,
        source_module=source_module,
        payload={"detail": "test"},
        **kwargs,
    )


def test_provider_can_be_constructed_without_dependencies():
    provider = PrismProvider()
    assert isinstance(provider, PrismProvider)


def test_provider_get_capabilities_returns_cognition():
    provider = PrismProvider()
    capabilities = provider.get_capabilities()

    assert capabilities == (CAPABILITY_COGNITION,)


def test_provider_get_version():
    provider = PrismProvider()
    assert provider.get_version() == PRISM_VERSION


def test_provider_health_check_structure():
    provider = PrismProvider()
    health = provider.health_check()

    assert set(health.keys()) == {
        "version",
        "status",
        "pipeline_ready",
        "engine_status",
        "supported_capabilities",
    }
    assert health["version"] == PRISM_VERSION
    assert health["status"] == "ok"
    assert health["pipeline_ready"] is True
    assert health["supported_capabilities"] == [CAPABILITY_COGNITION]


def test_provider_health_check_engine_status_all_present():
    provider = PrismProvider()
    health = provider.health_check()

    expected_engines = {
        "semantic_engine",
        "correlation_engine",
        "context_engine",
        "cognitive_state_engine",
        "observation_engine",
    }
    assert set(health["engine_status"].keys()) == expected_engines
    assert all(health["engine_status"].values())


def test_provider_analyze_single_event():
    provider = PrismProvider()
    event = _make_event()

    result = provider.analyze(event)

    assert isinstance(result, AnalysisResult)
    assert len(result.annotations) == 1
    assert result.observation.evidence_event_ids == (event["event_id"],)


def test_provider_analyze_many_events():
    provider = PrismProvider()
    events = [_make_event(), _make_event(event_type="change_done")]

    result = provider.analyze_many(events)

    assert len(result.annotations) == 2


def test_provider_with_core_store_registry_and_lifecycle():
    registry = ModuleRegistry()
    lifecycle = LifecycleManager()

    registry.register("module", ModuleMetadata(
        module_id="orchestra",
        capability=("event_emission",),
        dependency=(),
    ))
    lifecycle.register("orchestra")

    provider = PrismProvider(registry=registry, lifecycle=lifecycle)
    event = _make_event()

    result = provider.analyze(event)

    assert "registry" in result.context.system_state
    assert "lifecycle" in result.context.system_state
    # Registryは未変更のまま(Read Onlyであることの確認)
    assert registry.snapshot()["modules"]["orchestra"]["module_id"] == "orchestra"


def test_provider_read_only_does_not_mutate_registry():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(
        module_id="orchestra",
        capability=(),
        dependency=(),
    ))
    before = registry.snapshot()

    provider = PrismProvider(registry=registry)
    provider.analyze(_make_event())
    provider.analyze_many([_make_event(), _make_event(event_type="change_done")])
    provider.health_check()

    after = registry.snapshot()
    assert before == after


def test_provider_public_api_surface():
    provider = PrismProvider()
    public_methods = {
        name for name in dir(provider)
        if not name.startswith("_") and callable(getattr(provider, name))
    }
    assert public_methods == {
        "analyze",
        "analyze_many",
        "get_capabilities",
        "get_version",
        "health_check",
    }
