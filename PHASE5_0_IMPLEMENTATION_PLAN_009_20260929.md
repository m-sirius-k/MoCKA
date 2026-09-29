# IP-009: PHI-OS → Memory Integration
## Implementation Plan (NOT YET IMPLEMENTED)

**Date:** 2026-09-29  
**HG Decision:** C-1 APPROVED  
**Scope Binding:** APPROVED  
**Status:** PLANNING PHASE (no code changes yet)  
**Sequence:** Third implementation (after IP-007 and IP-005)

---

## TARGET

Establish automatic synchronization between PHI-OS runtime state transitions and Memory Layer, enabling institutional learning from system operations and providing complete context for future decisions.

---

## EXISTING COMPONENTS (Read-Only)

### Event Store
- **File:** `C:\Users\sirok\MoCKA_runtime_c9effe8\phi_os\event_gate.py`
  - Function: `process_event()` — Event recording
  - Table: `data/mocka_events.db` → events
  - Current use: System event persistence
  - **Action:** READ ONLY (query events for sync)

### PHI-OS Runtime
- **File:** `C:\Users\sirok\MoCKA_runtime_c9effe8\phi_os\` (core runtime)
  - Current use: State management, event emission
  - **Action:** READ ONLY (monitor state transitions)

### Memory Store
- **File:** `C:\Users\sirok\MoCKA_runtime_c9effe8\memory\memory_store.py`
  - Current use: Memory persistence (memory/data/memory_store.json)
  - **Action:** READ ONLY (query existing memory structure)

- **File:** `C:\Users\sirok\MoCKA_runtime_c9effe8\memory\memory_writer.py`
  - Function: `write_event()` — Memory recording
  - Current use: Write to MemoryStore
  - **Action:** READ ONLY (call existing write_event interface)

### Memory Index/Retrieval
- **File:** `C:\Users\sirok\MoCKA_runtime_c9effe8\memory\memory_retriever.py`
  - Current use: Query memory by intent, type, etc.
  - **Action:** READ ONLY (query for context validation)

---

## NEW COMPONENTS (To Be Created)

**REVISION NOTE:** Existing memory_writer.write_event() already accepts event dicts. Minimal integration point required.

### 1. SINGLE SYNC FUNCTION: sync_module (attach to event_gate or phi_os)
**Purpose:** Post-event-write trigger to sync PHI-OS events to Memory Layer

**Location:** `C:\Users\sirok\MoCKA_runtime_c9effe8\phi_os\memory_sync.py` OR event_gate integration

**Responsibility:**
- After event_gate.process_event() completes, check if event is PHI-OS type
- If what_type IN ['ai_lineage', 'hab_authorization', 'execution_result']:
  - Extract event_id from Event Store record
  - Call memory_writer.write_event(event_dict)
  - Record event_id → memory_id mapping
  - Track sync status in simple JSON map file
- Implement idempotency: same event_id never syncs twice
- Minimal retry: if MemoryWriter fails, mark for re-attempt, max 3 retries

**Input Contract (from Event Store):**
```
event_record = {
  "event_id": str,           # E20260929_... (UNIQUE KEY)
  "what_type": str,          # ai_lineage / hab_authorization / execution_result
  "who_actor": str,
  "why_purpose": str,
  "when_ts": str,            # ISO8601
  "before_state": str,       # may be null
  "after_state": str,        # may be null
  "title": str,
  "trace_id": str,           # immutable chain
  "session_id": str          # optional
}
```

**Output Contract (to MemoryWriter):**
```
Call: memory_writer.write_event(
  event={
    "event_id": from_record,
    "type": "phi_os_sync",
    "what_type": from_record.what_type,
    "who_actor": from_record.who_actor,
    "why_purpose": from_record.why_purpose,
    "when_ts": from_record.when_ts,
    "state": {
      "before": from_record.before_state,
      "after": from_record.after_state
    },
    "source_event": {
      "title": from_record.title,
      "trace_id": from_record.trace_id,
      "session_id": from_record.session_id
    }
  },
  memory_type=EPISODIC,
  source=PHI_OS,
  tags=["phi-os", from_record.what_type]
)
```

### 2. MAPPING FILE (persistent): event_memory_map.jsonl
**Purpose:** Track event_id ↔ memory_id for idempotency and readback

**Structure (append-only JSONL):**
```
{
  "event_id": "E20260929_...",
  "memory_id": "M_episodic_000001",
  "sync_status": "synced",       # synced / pending / failed
  "sync_timestamp": "2026-09-29T...",
  "retry_count": 0,
  "error_reason": null
}
```

**No database schema change.** Lightweight file-based mapping.

---

## CALL PATH (REVISED — SYNCHRONOUS POST-WRITE)

```
PHI-OS State Transition
    ↓
event_gate.process_event(phi_os_event)
    ↓
_write() → INSERT into events table
    ↓
integrity.sign_event() → UPDATE trace_id/related_event_id
    ↓
COMMIT
    ↓
[POST-COMMIT HOOK] Call memory_sync.sync_to_memory(event_id, event_record)
    ↓
CHECK: event_id in event_memory_map?
    ↓
IF already synced: SKIP (idempotency)
    ↓
ELSE: EXTRACT event fields (what_type, who_actor, why_purpose, when_ts, state)
    ↓
CALL: memory_writer.write_event(
  event=converted_dict,
  memory_type=EPISODIC,
  source=PHI_OS,
  tags=["phi-os", what_type]
)
    ↓
IF success:
  APPEND to event_memory_map.jsonl:
    event_id, memory_id, sync_status=synced, timestamp, retry_count=0
  RETURN confirmation
    ↓
IF failure:
  APPEND to event_memory_map.jsonl:
    event_id, memory_id=null, sync_status=pending, timestamp, retry_count=1
  RETURN error (will retry on next poll or startup)
```

**KEY:** No polling timer needed initially. Sync triggered post-commit. Mapping file is append-only for audit trail.

---

## INPUT / OUTPUT

### Input
- PHI-OS runtime state transitions (via Event Store)
- Queries: event_id → retrieve memory_id

### Output
- Memory entries reflecting system state
- event_id ↔ memory_id mapping in memory/manager.py
- Sync status tracking (success/failure/pending)
- Return: confirmation of sync or error status

---

## AUTHORIZATION / SCOPE

**Authorization:**
- C-1 (Implement PHI-OS → Memory sync) — HG APPROVED
- Uses existing Memory Layer authorization model
- No new authorization scheme needed

**Scope:**
- PHI-OS state transitions only (not arbitrary events)
- System decisions and execution results (not generic logging)
- Automatic sync (no manual intervention)
- One-way push (Event Store → Memory only, not reverse)
- Separation principle maintained (no direct coupling)

---

## PERSISTENCE

**Target 1:** Event Store `data/mocka_events.db` (read-only for sync)

**Target 2:** Memory Store `memory/data/memory_store.json` (write)

**Target 3:** Sync Map `memory/event_memory_map.jsonl` (write)

**Guarantee:**
- Event remains immutable in Event Store
- Memory record created independently (not linked record)
- event_id ↔ memory_id mapping persistent
- Sync status tracking for audit trail

---

## ERROR / FAIL-CLOSED BEHAVIOR

**Error Conditions:**
1. Event Store query fails → retry on next poll cycle, log error
2. MemoryWriter.write_event() fails → mark as pending, retry up to 3 times
3. Sync map corruption → escalate, halt sync until reviewed
4. Event filtering logic error → log error, skip malformed event
5. Circular reference attempt (bidirectional) → REJECT, escalate

**Fail-Closed:** Any error → event marked as failed, manual review required; never corrupt Memory or Event Store

---

## FORBIDDEN CHANGES

- DO NOT create separate memory_sync.py + memory/manager.py (use single sync function)
- DO NOT implement polling timer (use post-commit hook)
- DO NOT query Event Store from Memory Layer (breaks separation)
- DO NOT modify Event Store schema for Memory
- DO NOT implement bidirectional sync (Event Store ← Memory)
- DO NOT delete event_memory_map entries (immutable history)
- DO NOT cache mapping in volatile memory (must be file-based)
- DO NOT bypass MemoryWriter.write_event() interface
- DO NOT make sync retry automatic background task (keep explicit, fail-visible)

---

## RUNTIME EVIDENCE

**Pass Condition:** All of the following confirmed:

1. **Sync Mapping Created**
   - Query: `SELECT * FROM event_memory_map WHERE event_id='{test_event_id}'`
   - Expected: 1 row with memory_id populated, sync_status='synced'

2. **Memory Entry Created**
   - Query MemoryStore: `SELECT * FROM memory_store WHERE memory_id='{returned_memory_id}'`
   - Expected: Memory entry exists with phi_os content

3. **Event Remains Immutable**
   - Query: `SELECT * FROM events WHERE event_id='{test_event_id}'` (before and after sync)
   - Expected: Event unchanged (no sync side-effects on Event Store)

4. **Failed Syncs Retry**
   - Simulate MemoryWriter failure
   - Query: `SELECT sync_status, retry_count FROM event_memory_map WHERE event_id='{test_event_id}'`
   - Expected: sync_status='pending' or 'failed', retry_count > 0

5. **Separation Principle Enforced**
   - Attempt to query Event Store from Memory context
   - Expected: Query fails, isolation boundary maintained

6. **No Circular References**
   - Attempt bidirectional sync (Memory → Event Store)
   - Expected: Attempt rejected, separation enforced

---

## READBACK

**Pass Condition:** Complete PHI-OS runtime state reconstructible from Memory:

```
For target_event_id:
  1. Query Event Store: SELECT * FROM events WHERE event_id = target_event_id
  2. Extract: state before, state after, component, timestamp
  3. Query event_memory_map: SELECT memory_id WHERE event_id = target_event_id
  4. Query MemoryStore: SELECT * FROM memory_store WHERE memory_id = returned_memory_id
  5. Compare: Memory entry content matches Event Store event (same before/after state)
  6. Validate: Metadata matches (who_actor, when_ts, why_purpose all aligned)
```

**Validation:**
- Memory entry accurately reflects original PHI-OS event
- State transitions match (before → after)
- Timestamps aligned (Event Store ts ≈ Memory ts)
- Mapping is 1:1 (no duplication, no loss)
- Separation maintained (no Event Store references in Memory)

---

## ROLLBACK / FAILURE CONDITION

**Rollback Condition:** If sync readback fails:

1. Identify failed event_id and memory_id
2. Query event_memory_map for sync history
3. Inspect Event Store event (must be immutable)
4. Inspect Memory entry for corruption
5. If Memory entry corrupted: remove from memory_store.json, mark for re-sync
6. If sync map corrupted: recreate mapping from Event Store audit trail
7. Manual review: why did sync fail?

**Non-Recoverable Failure:**
- If Event Store and Memory entries diverge → escalate to HG
- If separation principle violated (bidirectional references) → escalate to HG
- If sync map irretrievably corrupted → reconstruct from Event Store

---

## DEPENDENCIES (REVISED)

**UPSTREAM DEPENDENCIES:** SOFT (recommended but not blocking)
- IP-007 (Lineage) — Provides lineage events to sync
  - Benefit: Complete AI reasoning path in Memory
  - Not blocking: IP-009 can start with any Event Store events

- IP-005 (Authorization) — Provides authorization decisions to sync
  - Benefit: Authorization history in Memory
  - Not blocking: IP-009 can start with any Event Store events

**EXECUTION ORDER RECOMMENDATION:**
1. IP-007 and IP-005: Implement in parallel (both independent)
2. IP-009: Implement after (consumes events from Step 1)

**Note:** IP-009 will work with any Event Store events (lineage or authorization). Implementation order is for completeness, not technical blocking.

---

## SCOPE VERIFICATION

**HG Approved Scope Check:**
- Target: Implement PHI-OS → Memory auto-sync ✓
- Input: PHI-OS state transitions ✓
- Output: Memory auto-indexed context ✓
- Persistence: Both systems preserved ✓
- Separation principle: Maintained ✓
- Scope creep risk: NONE (one-way sync only)

**Result: WITHIN APPROVED SCOPE**

---

## NEXT PHASE (REVISED — MINIMAL SCOPE)

Upon Implementation Plan Review APPROVAL:
1. Create memory_sync.py (single sync function, ~50 lines)
2. Create event_memory_map.jsonl file (append-only format)
3. Identify post-commit integration point in event_gate
4. Implement idempotency check (event_id lookup in mapping file)
5. Implement field extraction and memory_writer.write_event() call
6. Implement retry counter for failed syncs (max 3)
7. Integration testing: Event Store event → Memory sync
8. Failure path testing (memory writer unavailable)
9. Idempotency testing (same event_id should not sync twice)
10. Runtime evidence collection
11. Readback validation (event_id ↔ memory_id mapping intact)

**NO SEPARATE MANAGER COMPONENT.** Sync function + append-only mapping file.

**Current Status:** PLAN REVISED / READY FOR FINAL REVIEW
