"""MoCKA 3.0 - MetaIntent data structure (MGL_SPEC_v1.md Phase1)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MetaIntent:
    meta_intent_id: str
    target_layer_range: list[int]          # e.g. [0, 1, 2, 3]
    structural_goal: str                    # what structural change is wanted
    constraint_policy: list[str]            # Layer1 constraint IDs that must hold
    evolution_pressure: str                 # "drift_observation" | "human_directive" | "scheduled_review"
    stability_threshold: float              # drift convergence threshold (P3)
    generation_priority: int                # lower = higher priority
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "draft"                   # draft|reviewed|approved|rejected|applied
    approved_by: str | None = None
