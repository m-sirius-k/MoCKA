import pytest, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),".."))

from caliber.capability_registry import CapabilityRegistry
from caliber.lifecycle_manager import LifecycleManager
from workers.base_worker import BaseWorker

def test_auto_register_via_subclass():
    class DummyWorker(BaseWorker):
        name = "dummy"
        capabilities = ["dummy_cap"]
        def execute(self, job): return {"success": True}

    names = [w.__name__ for w in CapabilityRegistry.get("dummy_cap")]
    assert "DummyWorker" in names

def test_plugin_x_worker_registered():
    import plugins.x_worker  # noqa: F401
    names = [w.__name__ for w in CapabilityRegistry.get("post_x")]
    assert "XWorker" in names

def test_capability_tag_filter():
    class StagingWorker(BaseWorker):
        name = "staging_only"
        capabilities = ["staging_cap"]
        tags = ["staging"]
        def execute(self, job): return {"success": True}

    from caliber.caliber_manager import request_capability
    assert request_capability("staging_cap", tag="prod") is None
    chosen = request_capability("staging_cap", tag="staging")
    assert chosen is not None
    assert chosen.name == "staging_only"

def test_lifecycle_state_transition():
    lm = LifecycleManager()
    lm.set_state("test_worker", "busy")
    assert lm.get_state("test_worker") == "busy"
    lm.set_state("test_worker", "ready")
    assert lm.get_state("test_worker") == "ready"

def test_lifecycle_invalid_state():
    lm = LifecycleManager()
    lm.set_state("test_worker2", "ready")
    lm.set_state("test_worker2", "not_a_real_state")
    assert lm.get_state("test_worker2") == "ready"

def test_all_capabilities_listed():
    from caliber.caliber_manager import list_capabilities
    caps = list_capabilities()
    assert "post_x" in caps
    assert "post_instagram" in caps
