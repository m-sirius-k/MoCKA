"""公開Pydanticモデル — SDK利用者向け"""
from pydantic import BaseModel
from typing import Any


class RecordedEvent(BaseModel):
    event_id: str


class AuditResult(BaseModel):
    chain_valid: bool
    total_events: int
    broken_events: list[str] = []


class ShadowStatus(BaseModel):
    is_degraded: bool
    available_pct: float
    active_stages: list[str]
    reason: str = ""
