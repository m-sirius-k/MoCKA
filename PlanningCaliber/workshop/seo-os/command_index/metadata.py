"""command_index/metadata.py — CommandMetadata データクラス"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CommandStatus(str, Enum):
    ACTIVE      = "active"
    DEPRECATED  = "deprecated"
    EXPERIMENTAL = "experimental"
    DISABLED    = "disabled"


@dataclass
class CommandMetadata:
    id: str
    name: str
    description: str
    category: str
    status: CommandStatus = CommandStatus.ACTIVE
    version: str = "1.0.0"
    aliases: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    # Usage stats (populated by LearningEngine)
    use_count: int = 0
    success_rate: float = 1.0
    last_used: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "status": self.status.value,
            "version": self.version,
            "aliases": self.aliases,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "use_count": self.use_count,
            "success_rate": self.success_rate,
            "last_used": self.last_used,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CommandMetadata":
        return cls(
            id=d["id"],
            name=d["name"],
            description=d["description"],
            category=d["category"],
            status=CommandStatus(d.get("status", "active")),
            version=d.get("version", "1.0.0"),
            aliases=d.get("aliases", []),
            tags=d.get("tags", []),
            dependencies=d.get("dependencies", []),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            use_count=d.get("use_count", 0),
            success_rate=d.get("success_rate", 1.0),
            last_used=d.get("last_used"),
        )
