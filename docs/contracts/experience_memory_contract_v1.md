# Contract D: Experience Memory Contract v1.0

## ID: CONT-EXPERIENCE-MEMORY-v1.0
## Status: ACTIVE
## Date: 2026-10-02
## Author: MoCKA Implementation Session (E20261002_981617553cb52)

---

## 1. Purpose

Experience Memory is the mechanism by which actual consequences of executed
actions are stored in a form that can improve future assessments. This closes
the loop:

  Consequence -> Experience Memory -> Reassessment -> Assessment

Without this loop, the system cannot learn from its own actions.

---

## 2. Scope

This contract governs:
- ExperienceMemoryContent schema (the content dict inside MemoryEntry)
- What triggers an experience memory write
- How experience memory is distinguished from other memory types
- How experience memory feeds into reassessment

---

## 3. MemoryEntry Integration

The existing MemoryEntry (memory/memory_model.py) is a frozen dataclass.
This contract does NOT modify MemoryEntry.

Instead, this contract defines the schema for the `content` dict field
when memory_type = "experience".

ExperienceMemoryContent fields (all stored inside content dict):
- action_id: str              (the action that was executed)
- assessment_id: str          (links to AssessmentRecord)
- consequence_id: str         (links to ConsequenceRecord)
- outcome: str                (SUCCESS | PARTIAL | FAILURE | UNKNOWN)
- execution_success: bool     (from ConsequenceRecord)
- consequence_verified: bool  (from ConsequenceRecord)
- deviation: list[str]        (unexpected changes observed)
- axes_snapshot: dict         (XYZ+T+S+K values at time of assessment)
- lesson: str                 (extracted learning from outcome)
- lesson_type: str            (SUCCESS_PATTERN | FAILURE_PATTERN | DEVIATION_PATTERN)

---

## 4. Memory Type Requirement

Experience memory entries MUST use memory_type = "experience".
This distinguishes them from other memory types (decision, event, etc.)
and allows the Reassessment module to query them specifically.

---

## 5. Lesson Extraction

The `lesson` field captures the key takeaway from this experience.
Format: free text, max 500 characters.

The `lesson_type` field classifies the lesson:
- SUCCESS_PATTERN: what conditions led to successful execution
- FAILURE_PATTERN: what conditions led to failed execution
- DEVIATION_PATTERN: what conditions led to unexpected deviations

Lesson extraction is performed by aur/reassessment.py.

---

## 6. Write Trigger

An ExperienceMemoryContent MUST be written when:
1. A ConsequenceRecord has been created (regardless of outcome)
2. The outcome is not None

An ExperienceMemoryContent MUST NOT be written when:
1. No ConsequenceRecord exists
2. The action was not executed (denied at enforcement point)
3. The consequence recording itself failed

---

## 7. Memory Store Integration

Experience memory entries are written via the existing memory_writer.py.
The memory_store.json file MUST be the target for write operations.
The memory_retriever.py MUST be able to query by memory_type="experience".

---

## 8. Retrieval for Reassessment

The Reassessment module (Contract E) queries experience memory with:
- Filter: memory_type="experience"
- Filter: content.outcome in ["FAILURE", "PARTIAL", "UNKNOWN"] (for warning)
- Filter: content.axes_snapshot (for similarity matching)

The result is a list of ScoredMemory objects with relevance scores.

---

## 9. Retention Policy

Experience memory entries are retained indefinitely (append-only, per MoCKA
record-keeping principle). No automatic deletion or archival is performed.
