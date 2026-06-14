"""
MoCKA Core Kernel — orchestra.orchestrator_api

Orchestra実行層への外部IF。
"""

import time

from .orchestra_engine import OrchestraEngine
from .types import Event

engine = OrchestraEngine()


def emit_event(event_type, session_id, payload):
    event = Event(
        event_id=str(time.time()),
        event_type=event_type,
        session_id=session_id,
        timestamp=time.time(),
        payload=payload,
    )
    return engine.on_event(event)


def register_node(node_id, handler):
    engine.register_node(node_id, handler)
