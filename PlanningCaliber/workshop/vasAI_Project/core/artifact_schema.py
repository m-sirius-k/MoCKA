"""
vasAI Core: Artifact hash計算・バリデーション・変換。
"""
import hashlib
import json
from datetime import datetime, timezone

from core.models import Artifact


def compute_hash(artifact: Artifact) -> str:
    content_str = json.dumps(artifact.content, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(content_str.encode("utf-8")).hexdigest()


def validate(data: dict) -> Artifact:
    artifact = Artifact.model_validate(data)
    artifact.hash = compute_hash(artifact)
    return artifact


def to_event_content(artifact: Artifact) -> dict:
    return {
        "artifact_id":    artifact.artifact_id,
        "artifact_type":  artifact.artifact_type,
        "source_app":     artifact.source_app,
        "source_service": artifact.source_service,
        "status":         artifact.status,
        "tags":           artifact.tags,
        "hash":           artifact.hash,
    }


def from_raw(
    raw_input: dict,
    artifact_type: str = "message",
    source_app: str = "vasAI",
    source_service: str = "default",
) -> Artifact:
    artifact = Artifact(
        artifact_type=artifact_type,
        source_app=source_app,
        source_service=source_service,
        content=raw_input,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    artifact.hash = compute_hash(artifact)
    return artifact
