# schema.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

CURRENT_SCHEMA_VERSION = 1

@dataclass
class ProjectStatus:
    phase:    int
    mission:  str
    priority: list[str] = field(default_factory=list)

@dataclass
class Warning:
    id:          str
    level:       str   # "ACTIVE" | "RESOLVED"
    description: str

@dataclass
class TodoItem:
    id:       str
    title:    str
    priority: str
    status:   str

@dataclass
class InstitutionState:
    state_version:          int
    project:                ProjectStatus
    warnings:               list[Warning]
    todos:                  list[TodoItem]
    decision_ledger_rev:    int
    guideline_revision:     int
    # 以下は revision_manager が付与する
    revision:               int                = 0
    state_hash:             str                = ""
    generated_at:           str                = ""

    def to_dict(self) -> dict:
        """JSON直列化用。dataclasses.asdict() でネストも展開される。"""
        import dataclasses
        return dataclasses.asdict(self)

@dataclass
class AISessionEntry:
    last_revision: int
    role:          str
    trust_level:   str
    last_knock:    str = ""

@dataclass
class AISessionState:
    ai_registry: dict[str, AISessionEntry] = field(default_factory=dict)
