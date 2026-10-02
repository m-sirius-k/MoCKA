"""
memory/experience_memory.py: ExperienceMemoryContent schema and writer.

Closes the loop: Consequence -> Experience Memory -> Reassessment.

Contract: docs/contracts/experience_memory_contract_v1.md

IMPORTANT: Does NOT modify the frozen MemoryEntry dataclass.
ExperienceMemoryContent is stored inside MemoryEntry.content dict.
"""
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from memory.memory_model import MemoryEntry

MEMORY_STORE_PATH = Path(__file__).parent / "data" / "memory_store.json"

VALID_LESSON_TYPES = ("SUCCESS_PATTERN", "FAILURE_PATTERN", "DEVIATION_PATTERN")


@dataclass
class ExperienceMemoryContent:
    """Schema for MemoryEntry.content when memory_type='experience'."""
    action_id: str
    assessment_id: str
    consequence_id: str
    outcome: str
    execution_success: bool
    consequence_verified: bool
    deviation: list
    axes_snapshot: dict
    lesson: str
    lesson_type: str

    def to_dict(self) -> dict:
        return asdict(self)


def _extract_lesson(
    outcome: str,
    deviation: list,
    axes_snapshot: dict,
    error_detail: str = "",
) -> tuple[str, str]:
    """Derive (lesson, lesson_type) from consequence data."""
    if outcome == "SUCCESS":
        key_axes = {k: v for k, v in axes_snapshot.items() if v not in (None, "UNKNOWN")}
        lesson = f"Successful execution. Known-good axes: {list(key_axes.keys())}"
        return lesson[:500], "SUCCESS_PATTERN"
    if outcome == "FAILURE":
        detail = error_detail[:200] if error_detail else "execution failed"
        lesson = f"Execution failed: {detail}"
        return lesson[:500], "FAILURE_PATTERN"
    if outcome == "PARTIAL" and deviation:
        lesson = f"Unexpected changes observed: {deviation[:3]}"
        return lesson[:500], "DEVIATION_PATTERN"
    return f"Outcome was {outcome}; no specific lesson extracted.", "DEVIATION_PATTERN"


def create_experience_entry(
    action_id: str,
    assessment_id: str,
    consequence_id: str,
    outcome: str,
    execution_success: bool,
    consequence_verified: bool,
    deviation: list,
    axes_snapshot: dict,
    error_detail: str = "",
    source: str = "aur_pipeline",
    tags: tuple = (),
) -> MemoryEntry:
    """
    Create a MemoryEntry with memory_type='experience' for experience memory storage.
    Does NOT write to disk; caller is responsible for persistence.
    """
    lesson, lesson_type = _extract_lesson(outcome, deviation, axes_snapshot, error_detail)

    content = ExperienceMemoryContent(
        action_id=action_id,
        assessment_id=assessment_id,
        consequence_id=consequence_id,
        outcome=outcome,
        execution_success=execution_success,
        consequence_verified=consequence_verified,
        deviation=list(deviation),
        axes_snapshot=dict(axes_snapshot),
        lesson=lesson,
        lesson_type=lesson_type,
    )

    import uuid
    memory_id = f"MEM-EXP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now(timezone.utc).isoformat()

    return MemoryEntry(
        memory_id=memory_id,
        memory_type="experience",
        timestamp=timestamp,
        source=source,
        content=content.to_dict(),
        metadata={"consequence_id": consequence_id, "outcome": outcome},
        tags=tuple(tags) + ("experience", outcome.lower()),
    )


def write_experience_to_store(entry: MemoryEntry) -> bool:
    """
    Append an experience MemoryEntry to the memory store JSON file.
    Returns True on success, False on failure (fail-soft; caller must log failure).
    """
    try:
        store_path = MEMORY_STORE_PATH
        if store_path.exists():
            raw = store_path.read_text(encoding="utf-8").strip()
            records = json.loads(raw) if raw and raw != "[]" else []
        else:
            records = []

        record = {
            "memory_id": entry.memory_id,
            "memory_type": entry.memory_type,
            "timestamp": entry.timestamp,
            "source": entry.source,
            "content": entry.content,
            "metadata": entry.metadata,
            "tags": list(entry.tags),
        }
        records.append(record)
        store_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False


def load_experience_entries() -> list[dict]:
    """
    Load all experience memory entries from the store.
    Returns list of raw dicts (content fields accessible directly).
    """
    try:
        store_path = MEMORY_STORE_PATH
        if not store_path.exists():
            return []
        raw = store_path.read_text(encoding="utf-8").strip()
        if not raw or raw == "[]":
            return []
        records = json.loads(raw)
        return [r for r in records if r.get("memory_type") == "experience"]
    except Exception:
        return []
