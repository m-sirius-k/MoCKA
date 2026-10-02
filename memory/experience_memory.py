"""
memory/experience_memory.py: ExperienceMemoryContent schema and writer.

Closes the loop: Consequence -> Experience Memory -> Reassessment.

Contract: docs/contracts/experience_memory_contract_v1.md

IMPORTANT: Does NOT modify the frozen MemoryEntry dataclass.
ExperienceMemoryContent is stored inside MemoryEntry.content dict.

Write path: write_experience_to_store() -> MemoryStore.append()
  - retention policy applied by MemoryStore
  - no direct JSON write
"""
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from memory.memory_model import MemoryEntry
from memory.memory_store import MemoryStore

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
) -> tuple:
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
    Does NOT write to disk; caller must call write_experience_to_store().
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
    Append an experience MemoryEntry to the memory store via MemoryStore.
    Uses MemoryStore.append() so retention policy and schema are applied.
    Returns True on success, False on failure (fail-soft).
    """
    try:
        store = MemoryStore()
        store.append(entry)
        return True
    except Exception:
        return False


def load_experience_entries() -> list:
    """
    Load all experience memory entries from the store.
    Returns list of raw dicts (content fields accessible directly).
    """
    try:
        store = MemoryStore()
        return [
            e.to_dict()
            for e in store.all()
            if e.memory_type == "experience"
        ]
    except Exception:
        return []
