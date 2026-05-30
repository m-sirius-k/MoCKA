"""
vasAI Core: Pydantic v2 Artifact schema — PHI-OS / vasAI shared contract.
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

ArtifactType = Literal["message", "decision", "todo", "incident", "audit"]
ArtifactStatus = Literal["draft", "reviewed", "shared", "archived"]


class Artifact(BaseModel):
    vasai_version: str = "1.0.0"
    artifact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    artifact_type: ArtifactType
    source_app: str
    source_service: str
    content: dict
    tags: list[str] = Field(default_factory=list)
    status: ArtifactStatus = "draft"
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    hash: str = ""

    @model_validator(mode="after")
    def compute_hash(self) -> "Artifact":
        content_str = json.dumps(self.content, sort_keys=True, ensure_ascii=False)
        self.hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()
        return self

    @field_validator("vasai_version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValueError(f"Invalid version format: {v}")
        return v

    def to_event_content(self) -> dict:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "source_app": self.source_app,
            "source_service": self.source_service,
            "status": self.status,
            "tags": self.tags,
            "hash": self.hash,
        }

    def mark_reviewed(self) -> "Artifact":
        return self.model_copy(
            update={"status": "reviewed", "updated_at": datetime.now(timezone.utc)}
        )

    def mark_shared(self) -> "Artifact":
        return self.model_copy(
            update={"status": "shared", "updated_at": datetime.now(timezone.utc)}
        )

    def mark_archived(self) -> "Artifact":
        return self.model_copy(
            update={"status": "archived", "updated_at": datetime.now(timezone.utc)}
        )
