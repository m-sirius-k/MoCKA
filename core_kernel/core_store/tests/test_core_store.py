"""
MoCKA Core Kernel — core_store unit tests

Phase 1 成功条件の検証:
  - Core Storeが独立してビルド/import可能
  - Registry / Metadata / ConfigStore / PersistenceBackend の基本動作
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from core_store import (
    CapabilityRegistry,
    ConfigStore,
    InMemoryBackend,
    LifecycleManager,
    LifecycleState,
    ModuleLoader,
    ModuleMetadata,
    ModuleRegistry,
)


# ---------------------------------------------------------------------------
# ModuleMetadata
# ---------------------------------------------------------------------------

def test_metadata_round_trip():
    meta = ModuleMetadata(
        module_id="orchestra",
        version="10.0.0",
        capability=("ai_collab",),
        dependency=(),
    )
    data = meta.to_dict()
    restored = ModuleMetadata.from_dict(data)
    assert restored == meta


def test_metadata_defaults():
    meta = ModuleMetadata(module_id="memory")
    assert meta.version == "0.0.0"
    assert meta.capability == ()
    assert meta.dependency == ()


# ---------------------------------------------------------------------------
# ModuleRegistry
# ---------------------------------------------------------------------------

def test_registry_register_and_get():
    registry = ModuleRegistry()
    meta = ModuleMetadata(module_id="orchestra", version="10.0.0")
    registry.register("module", meta)

    assert registry.is_registered("module", "orchestra")
    assert registry.get("module", "orchestra") == meta
    assert registry.list("module") == (meta,)


def test_registry_duplicate_register_raises():
    registry = ModuleRegistry()
    meta = ModuleMetadata(module_id="orchestra")
    registry.register("module", meta)

    with pytest.raises(ValueError):
        registry.register("module", meta)


def test_registry_overwrite():
    registry = ModuleRegistry()
    v1 = ModuleMetadata(module_id="orchestra", version="1.0.0")
    v2 = ModuleMetadata(module_id="orchestra", version="2.0.0")

    registry.register("module", v1)
    registry.register("module", v2, overwrite=True)

    assert registry.get("module", "orchestra").version == "2.0.0"


def test_registry_unknown_category_raises():
    registry = ModuleRegistry()
    with pytest.raises(ValueError):
        registry.register("unknown_category", ModuleMetadata(module_id="x"))


def test_registry_event_type_category():
    registry = ModuleRegistry()
    meta = ModuleMetadata(module_id="ai_response")
    registry.register("event_type", meta)
    assert registry.list("event_type") == (meta,)
    # 他カテゴリには影響しない
    assert registry.list("module") == ()


def test_registry_unregister():
    registry = ModuleRegistry()
    meta = ModuleMetadata(module_id="orchestra")
    registry.register("module", meta)
    registry.unregister("module", "orchestra")
    assert not registry.is_registered("module", "orchestra")


# ---------------------------------------------------------------------------
# ModuleMetadata: UUID
# ---------------------------------------------------------------------------

def test_metadata_auto_generates_uuid():
    a = ModuleMetadata(module_id="orchestra")
    b = ModuleMetadata(module_id="orchestra")
    assert a.module_uuid
    assert a.module_uuid != b.module_uuid  # 自動発行は呼び出しごとに一意


def test_metadata_explicit_uuid_round_trip():
    meta = ModuleMetadata(module_id="orchestra", module_uuid="fixed-uuid-123")
    data = meta.to_dict()
    assert data["module_uuid"] == "fixed-uuid-123"
    assert ModuleMetadata.from_dict(data).module_uuid == "fixed-uuid-123"


# ---------------------------------------------------------------------------
# ① Registry Snapshot
# ---------------------------------------------------------------------------

def test_registry_snapshot_structure():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="orchestra", version="10.0.0"))
    registry.register("service", ModuleMetadata(module_id="memory_service"))
    registry.register("event_type", ModuleMetadata(module_id="ai_response"))

    snap = registry.snapshot()

    assert set(snap.keys()) == {"modules", "services", "event_types", "frozen"}
    assert snap["modules"]["orchestra"]["version"] == "10.0.0"
    assert "memory_service" in snap["services"]
    assert "ai_response" in snap["event_types"]
    assert snap["frozen"] is False


# ---------------------------------------------------------------------------
# ② Registry Freeze
# ---------------------------------------------------------------------------

def test_registry_freeze_blocks_register():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="orchestra"))
    registry.freeze()

    assert registry.is_frozen
    with pytest.raises(RuntimeError):
        registry.register("module", ModuleMetadata(module_id="relay"))


def test_registry_freeze_blocks_unregister():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="orchestra"))
    registry.freeze()

    with pytest.raises(RuntimeError):
        registry.unregister("module", "orchestra")


def test_registry_freeze_allows_reads():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="orchestra"))
    registry.freeze()

    # 読み取りはfreeze後も可能
    assert registry.is_registered("module", "orchestra")
    assert registry.get("module", "orchestra").module_id == "orchestra"
    assert registry.snapshot()["frozen"] is True


# ---------------------------------------------------------------------------
# ③ Capability Validation
# ---------------------------------------------------------------------------

def test_validate_no_modules_is_valid():
    registry = ModuleRegistry()
    result = registry.validate()
    assert result == {
        "valid": True,
        "missing_dependencies": [],
        "missing_capabilities": [],
        "circular_dependencies": [],
    }


def test_validate_missing_dependency():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="orchestra", dependency=("relay",)))

    result = registry.validate()

    assert result["valid"] is False
    assert {"module_id": "orchestra", "missing": "relay"} in result["missing_dependencies"]
    assert result["circular_dependencies"] == []


def test_validate_satisfied_dependency():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="relay"))
    registry.register("module", ModuleMetadata(module_id="orchestra", dependency=("relay",)))

    result = registry.validate()
    assert result["valid"] is True


def test_validate_missing_capability():
    registry = ModuleRegistry()
    registry.register(
        "module",
        ModuleMetadata(module_id="orchestra", dependency=("capability:memory_write",)),
    )

    result = registry.validate()

    assert result["valid"] is False
    assert {"module_id": "orchestra", "missing": "memory_write"} in result["missing_capabilities"]


def test_validate_satisfied_capability():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="memory", capability=("memory_write",)))
    registry.register(
        "module",
        ModuleMetadata(module_id="orchestra", dependency=("capability:memory_write",)),
    )

    result = registry.validate()
    assert result["valid"] is True


def test_validate_circular_dependency():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="a", dependency=("b",)))
    registry.register("module", ModuleMetadata(module_id="b", dependency=("a",)))

    result = registry.validate()

    assert result["valid"] is False
    assert len(result["circular_dependencies"]) == 1
    cycle = result["circular_dependencies"][0]
    assert set(cycle) == {"a", "b"}


def test_validate_self_dependency_is_circular():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="a", dependency=("a",)))

    result = registry.validate()

    assert result["valid"] is False
    assert result["circular_dependencies"] == [["a", "a"]]


# ---------------------------------------------------------------------------
# ④ Registry Export
# ---------------------------------------------------------------------------

def test_registry_export_returns_json_string():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="orchestra", version="10.0.0"))

    text = registry.export()
    data = json.loads(text)

    assert data["modules"]["orchestra"]["version"] == "10.0.0"


def test_registry_export_writes_file(tmp_path):
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="orchestra"))

    out_path = tmp_path / "registry_export.json"
    registry.export(path=out_path)

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert "orchestra" in data["modules"]


# ---------------------------------------------------------------------------
# ConfigStore
# ---------------------------------------------------------------------------

def test_config_store_defaults_and_overrides():
    store = ConfigStore(defaults={"a": 1, "b": 2})
    store.set("b", 20)
    store.update({"c": 3})

    assert store.get("a") == 1
    assert store.get("b") == 20
    assert store.get("c") == 3
    assert store.get("missing", "fallback") == "fallback"


def test_config_store_from_file(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"emit_event": True}), encoding="utf-8")

    store = ConfigStore.from_file(config_file, defaults={"event_enabled": True, "emit_event": False})

    assert store.get("event_enabled") is True
    assert store.get("emit_event") is True


def test_config_store_from_missing_file_uses_defaults(tmp_path):
    missing = tmp_path / "does_not_exist.json"
    store = ConfigStore.from_file(missing, defaults={"x": 1})
    assert store.as_dict() == {"x": 1}


def test_config_store_from_broken_file_uses_defaults(tmp_path):
    broken = tmp_path / "broken.json"
    broken.write_text("{not valid json", encoding="utf-8")

    store = ConfigStore.from_file(broken, defaults={"x": 1})
    assert store.as_dict() == {"x": 1}


# ---------------------------------------------------------------------------
# PersistenceBackend / InMemoryBackend
# ---------------------------------------------------------------------------

def test_in_memory_backend_basic_operations():
    backend = InMemoryBackend()

    assert backend.get("k") is None
    backend.put("k", {"value": 1})
    assert backend.get("k") == {"value": 1}
    assert backend.keys() == ("k",)

    backend.delete("k")
    assert backend.get("k") is None
    assert backend.keys() == ()


def test_in_memory_backend_delete_missing_key_is_noop():
    backend = InMemoryBackend()
    backend.delete("missing")  # should not raise
    assert backend.keys() == ()


# ---------------------------------------------------------------------------
# CapabilityRegistry
# ---------------------------------------------------------------------------

def test_capability_registry_register_and_lookup():
    caps = CapabilityRegistry()
    caps.register_provider("memory_write", "memory")
    caps.register_provider("memory_write", "memory_v2")

    assert caps.has_provider("memory_write")
    assert caps.providers("memory_write") == ("memory", "memory_v2")
    assert caps.all_capabilities() == ("memory_write",)


def test_capability_registry_unregister():
    caps = CapabilityRegistry()
    caps.register_provider("memory_write", "memory")
    caps.unregister_provider("memory_write", "memory")

    assert not caps.has_provider("memory_write")
    assert caps.all_capabilities() == ()


def test_capability_registry_unregister_missing_is_noop():
    caps = CapabilityRegistry()
    caps.unregister_provider("memory_write", "memory")  # should not raise
    assert caps.all_capabilities() == ()


def test_capability_registry_snapshot():
    caps = CapabilityRegistry()
    caps.register_provider("memory_write", "memory")
    assert caps.snapshot() == {"memory_write": ["memory"]}


# ---------------------------------------------------------------------------
# LifecycleManager
# ---------------------------------------------------------------------------

def test_lifecycle_register_defaults_to_registered():
    lifecycle = LifecycleManager()
    lifecycle.register("orchestra")
    assert lifecycle.get_state("orchestra") == LifecycleState.REGISTERED


def test_lifecycle_register_is_idempotent():
    lifecycle = LifecycleManager()
    lifecycle.register("orchestra")
    lifecycle.transition("orchestra", LifecycleState.INITIALIZING)
    lifecycle.register("orchestra")  # 既存状態を変えない
    assert lifecycle.get_state("orchestra") == LifecycleState.INITIALIZING


def test_lifecycle_valid_transition_sequence():
    lifecycle = LifecycleManager()
    lifecycle.register("orchestra")
    lifecycle.transition("orchestra", LifecycleState.INITIALIZING)
    lifecycle.transition("orchestra", LifecycleState.ACTIVE)
    lifecycle.transition("orchestra", LifecycleState.DEGRADED)
    lifecycle.transition("orchestra", LifecycleState.ACTIVE)
    lifecycle.transition("orchestra", LifecycleState.STOPPED)
    assert lifecycle.get_state("orchestra") == LifecycleState.STOPPED


def test_lifecycle_invalid_transition_raises():
    lifecycle = LifecycleManager()
    lifecycle.register("orchestra")
    with pytest.raises(ValueError):
        lifecycle.transition("orchestra", LifecycleState.ACTIVE)  # REGISTERED -> ACTIVE は不可


def test_lifecycle_unknown_state_raises():
    lifecycle = LifecycleManager()
    lifecycle.register("orchestra")
    with pytest.raises(ValueError):
        lifecycle.transition("orchestra", "not_a_state")


def test_lifecycle_unregistered_module_raises():
    lifecycle = LifecycleManager()
    with pytest.raises(KeyError):
        lifecycle.get_state("orchestra")


def test_lifecycle_can_transition():
    lifecycle = LifecycleManager()
    lifecycle.register("orchestra")
    assert lifecycle.can_transition("orchestra", LifecycleState.INITIALIZING) is True
    assert lifecycle.can_transition("orchestra", LifecycleState.ACTIVE) is False
    assert lifecycle.can_transition("unknown", LifecycleState.ACTIVE) is False


def test_lifecycle_snapshot():
    lifecycle = LifecycleManager()
    lifecycle.register("orchestra")
    lifecycle.register("memory")
    assert lifecycle.snapshot() == {
        "orchestra": LifecycleState.REGISTERED,
        "memory": LifecycleState.REGISTERED,
    }


# ---------------------------------------------------------------------------
# ModuleLoader
# ---------------------------------------------------------------------------

def test_module_loader_load_success():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="orchestra"))

    loader = ModuleLoader(registry)
    loader.register_factory("orchestra", lambda: {"name": "orchestra-instance"})

    instance = loader.load("orchestra")

    assert instance == {"name": "orchestra-instance"}
    assert loader.is_loaded("orchestra")
    assert loader.get_instance("orchestra") is instance
    assert loader.lifecycle.get_state("orchestra") == LifecycleState.ACTIVE


def test_module_loader_load_is_cached():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="orchestra"))

    calls = []

    def factory():
        calls.append(1)
        return object()

    loader = ModuleLoader(registry)
    loader.register_factory("orchestra", factory)

    first = loader.load("orchestra")
    second = loader.load("orchestra")

    assert first is second
    assert len(calls) == 1


def test_module_loader_factory_requires_registered_module():
    registry = ModuleRegistry()
    loader = ModuleLoader(registry)

    with pytest.raises(KeyError):
        loader.register_factory("orchestra", lambda: object())


def test_module_loader_load_without_factory_raises():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="orchestra"))
    loader = ModuleLoader(registry)

    with pytest.raises(KeyError):
        loader.load("orchestra")


def test_module_loader_factory_failure_sets_failed_state():
    registry = ModuleRegistry()
    registry.register("module", ModuleMetadata(module_id="orchestra"))

    loader = ModuleLoader(registry)

    def broken_factory():
        raise RuntimeError("boom")

    loader.register_factory("orchestra", broken_factory)

    with pytest.raises(RuntimeError):
        loader.load("orchestra")

    assert loader.lifecycle.get_state("orchestra") == LifecycleState.FAILED
    assert not loader.is_loaded("orchestra")
