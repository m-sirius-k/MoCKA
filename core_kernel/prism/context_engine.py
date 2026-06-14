"""
MoCKA Core Kernel — prism.context_engine

責務:
  Event群・SemanticAnnotation群・relationshipsから、
  状況スナップショットであるContextを構築する。

  system_stateは、Core Kernel(Registry/Lifecycle)からの
  読み取り専用スナップショットのみを保持する。
"""

import uuid


class ContextEngine:
    """Event群からContextを構築する。"""

    def __init__(self, registry=None, lifecycle=None):
        """
        Args:
            registry: core_store.ModuleRegistry (読み取り専用利用)
            lifecycle: core_store.LifecycleManager (読み取り専用利用)
        """
        self._registry = registry
        self._lifecycle = lifecycle

    def build(self, events, annotations, relationships):
        from .models import Context

        event_ids = tuple(event.get("event_id", "") for event in events)
        timestamps = sorted(
            event.get("timestamp", "") for event in events if event.get("timestamp")
        )
        time_window = (timestamps[0], timestamps[-1]) if timestamps else ()

        actors = tuple(sorted({
            event.get("source_module", "") for event in events if event.get("source_module")
        }))

        topics = tuple(sorted({
            annotation.category for annotation in annotations if annotation.category
        }))

        system_state = self._read_system_state()

        return Context(
            context_id=str(uuid.uuid4()),
            event_ids=event_ids,
            time_window=time_window,
            actors=actors,
            topics=topics,
            relationships=relationships,
            system_state=system_state,
            metadata={},
        )

    def _read_system_state(self) -> dict:
        state = {}
        if self._registry is not None:
            try:
                state["registry"] = self._registry.snapshot()
            except Exception:
                pass
        if self._lifecycle is not None:
            try:
                state["lifecycle"] = self._lifecycle.snapshot()
            except Exception:
                pass
        return state
