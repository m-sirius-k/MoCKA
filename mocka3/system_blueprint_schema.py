"""MoCKA 3.0 - SystemBlueprint data structure (MGL_SPEC_v1.md Phase1)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SystemBlueprint:
    blueprint_id: str
    source_meta_intent_id: str
    layer_definitions: dict                 # {"layer0": {...}, ..., "layer4": {...}}
    intent_schema_version: str
    graph_topology: dict                    # edge types / node relations
    drift_model: dict                       # placeholder, may be empty in Phase1
    governance_loop_definition: dict        # GLK lifecycle + decision logic refs
    lifecycle_state: str = "evolving"       # active|constrained|evolving|restructured|deprecated
    validation_status: str = "pending"      # pending|passed|failed
    created_at: datetime = field(default_factory=datetime.now)
