"""
vasAI Core: 全Pydanticモデル定義 — 全ファイルはここからimportする。
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class MovementStage(str, Enum):
    OBSERVATION = "OBSERVATION"
    RECORD      = "RECORD"
    INCIDENT    = "INCIDENT"
    RECURRENCE  = "RECURRENCE"
    PREVENTION  = "PREVENTION"
    DECISION    = "DECISION"
    ACTION      = "ACTION"
    AUDIT       = "AUDIT"


class RiskLevel(str, Enum):
    NORMAL   = "NORMAL"
    CAUTION  = "CAUTION"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"


class DecisionStatus(str, Enum):
    PENDING       = "PENDING"
    APPROVED      = "APPROVED"
    REJECTED      = "REJECTED"
    AUTO_APPROVED = "AUTO_APPROVED"


class Artifact(BaseModel):
    vasai_version:  str = "1.0.0"
    artifact_id:    str = Field(default_factory=lambda: str(uuid.uuid4()))
    artifact_type:  Literal["message", "decision", "todo", "incident", "audit"]
    source_app:     str
    source_service: str
    content:        dict[str, Any]
    tags:           list[str] = []
    status:         Literal["draft", "reviewed", "shared", "archived"] = "draft"
    created_at:     datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at:     datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    hash:           str = ""


class Decision(BaseModel):
    decision_id:            str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id:               str
    risk_level:             RiskLevel
    status:                 DecisionStatus = DecisionStatus.PENDING
    reason:                 str = ""
    decided_by:             str = ""
    decided_at:             datetime | None = None
    prevention_candidates:  list[dict] = []


class ActionResult(BaseModel):
    action_id:   str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    success:     bool
    stage:       MovementStage = MovementStage.ACTION
    message:     str = ""
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditReport(BaseModel):
    report_id:     str = Field(default_factory=lambda: str(uuid.uuid4()))
    chain_valid:   bool
    total_events:  int
    broken_events: list[str] = []
    seal_hash:     str = ""
    generated_at:  datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DegradedStatus(BaseModel):
    is_degraded:   bool
    available_pct: float
    active_stages: list[MovementStage]
    reason:        str = ""
    entered_at:    datetime | None = None


class ApprovalRule(BaseModel):
    rule_id:       str
    risk_level:    RiskLevel
    auto_approve:  bool
    approver_role: str = ""
    conditions:    dict = {}
