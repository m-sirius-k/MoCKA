# IP-007: AI → Event Store Lineage
## Implementation Plan (NOT YET IMPLEMENTED)

**Date:** 2026-09-29  
**HG Decision:** B-1 APPROVED  
**Scope Binding:** APPROVED  
**Status:** PLANNING PHASE (no code changes yet)  
**Sequence:** First implementation (lowest risk)

---

## TARGET

Store Orchestra-specific AI lineage (provider/model/runtime/source metadata) formally in Event Store as immutable records, enabling complete traceability of AI reasoning paths and decision provenance.

---

## EXISTING COMPONENTS (Read-Only)

### Event Store Infrastructure
- **File:** `C:\Users\sirok\MoCKA_runtime_c9effe8\phi_os\event_gate.py`
  - Function: `process_event()` — unified event entry point
  - Function: `_write()` — persistence to events table
  - Current use: Generic event recording (what_type, why_purpose, etc.)
  - **Action:** READ ONLY (no modification)

- **File:** `C:\Users\sirok\MoCKA_runtime_c9effe8\data\mocka_events.db`
  - Table: `events` (existing schema)
  - Columns: event_id, when_ts, who_actor, what_type, where_component, why_purpose, how_trigger, before_state, after_state, title, short_summary, session_id, _source, free_note, channel_type, lifecycle_phase, risk_level, trace_id, related_event_id
  - **Action:** SCHEMA EXTENSION REQUIRED (add Lineage columns)

### Orchestra Components
- **File:** `C:\Users\sirok\MoCKA_runtime_c9effe8\caliber\orchestra\` (Orchestra session tracking)
  - Current use: provider selection, session management
  - **Action:** READ ONLY (query existing session metadata)

---

## NEW COMPONENTS (To Be Created)

**REVISION NOTE:** Existing code analysis (event_gate.py:76-79) confirms vendor/model/runtime/source fields ALREADY EXIST in event_gate._write(). Database schema extension ALREADY IMPLEMENTED. Only integration point required.

### 1. INTEGRATION POINT (no new component needed)
**Method:** Reuse existing event_gate.process_event() — MINIMUM CHANGE

**Call Sequence (REVISED):**
```
Orchestra Session Completion
  ↓
Extract: provider, model, runtime, source from Orchestra metadata
  ↓
event_gate.process_event({
  "what_type": "ai_lineage",
  "where_component": "orchestra",
  "vendor": provider,           # maps to existing vendor field
  "model": model,                # maps to existing model field  
  "runtime": runtime,            # maps to existing runtime field
  "source": source,              # maps to existing source field
  "request_id": request_id,
  "session_id": session_id,
  "who_actor": who_actor,
  "when_ts": ISO8601
})
  ↓
event_gate._write() persists with existing schema
  ↓
integrity.sign_event() applies trace chain
  ↓
Return event_id
```

**RATIONALE:**
- Existing event_gate schema already contains vendor, model, runtime, source columns
- event_gate._write() already maps these fields (confirmed line 76-79)
- No new component required
- No schema migration required
- Leverages existing interface = MINIMUM CHANGE principle

---

## CALL PATH (REVISED)

```
Orchestra Session Completion
    ↓
  Extract metadata: provider, model, runtime, source, request_id
    ↓
EXISTING event_gate.process_event(lineage_payload)
    ↓
  gate_validator.validate() — check vendor/model/runtime/source present
    ↓
_write() → INSERT INTO events WITH existing columns
  - vendor:    provider
  - model:     model
  - runtime:   runtime  
  - source:    source
  - what_type: ai_lineage
  - request_id: from_orchestra
    ↓
integrity.sign_event()
    ↓
UPDATE events SET trace_id, related_event_id
    ↓
COMMIT
    ↓
Return event_id to Orchestra dispatcher
```

**KEY:** No new lineage_recorder component. Direct integration with event_gate via existing interface.

---

## INPUT / OUTPUT

### Input
- Orchestra session object with: provider, model, runtime, source, who_actor, request_id, timestamp
- Source: Orchestra dispatcher upon session completion

### Output
- Immutable record in events table with provider/model/runtime/source/session_id
- Return: event_id confirming write
- Side effect: Event Store contains complete AI lineage

---

## AUTHORIZATION / SCOPE

**Authorization:**
- B-1 (Store Orchestra lineage formally) — HG APPROVED
- No new authorization model required
- Uses existing Orchestra session authorization

**Scope:**
- Orchestra sessions only (not generic AI calls)
- Lineage metadata only (no session transcript storage)
- Append-only (no modification of existing events)
- Immutable once written (signature chain enforced)

---

## PERSISTENCE

**Target:** `data/mocka_events.db` → events table

**Guarantee:** 
- ACID compliance via SQLite transaction
- Signature chain via existing integrity.sign_event()
- Immutable via INSERT OR IGNORE + trace_id hash chain
- Queryable: SELECT * FROM events WHERE provider IS NOT NULL

---

## ERROR / FAIL-CLOSED BEHAVIOR

**Error Conditions:**
1. Invalid provider value → REJECT, log error, return failure
2. Missing required fields → REJECT, log error, return failure
3. Event Store write fails → ROLLBACK transaction, log error, block lineage recording
4. Signature chain broken → ALERT, manual review required

**Fail-Closed:** Any error → lineage recording fails safe (does not create orphaned records or incomplete entries)

---

## FORBIDDEN CHANGES

- DO NOT create lineage_recorder.py (use existing event_gate instead)
- DO NOT extend database schema (vendor/model/runtime/source already exist)
- DO NOT modify `process_event()` signature
- DO NOT modify `_write()` logic
- DO NOT bypass integrity.sign_event()
- DO NOT create separate lineage database
- DO NOT bypass existing gate_validator

---

## RUNTIME EVIDENCE

**Pass Condition:** All of the following confirmed:

1. **Lineage Record Created**
   - Query: `SELECT * FROM events WHERE what_type='ai_lineage' AND request_id='{test_request_id}'`
   - Expected: 1 row returned with provider/model/runtime/source populated

2. **Integrity Chain Valid**
   - Query: `SELECT event_id, trace_id, related_event_id FROM events WHERE what_type='ai_lineage' ORDER BY rowid DESC LIMIT 1`
   - Expected: trace_id non-null, related_event_id matches previous event's trace_id

3. **Session Cross-Reference Valid**
   - Query: `SELECT orchestra_session_id FROM events WHERE what_type='ai_lineage' LIMIT 1`
   - Expected: orchestra_session_id matches source Orchestra session

4. **No Data Loss**
   - Query: `SELECT COUNT(*) FROM events WHERE what_type='ai_lineage' AND provider IS NULL`
   - Expected: 0 (no incomplete records)

5. **Immutability Enforced**
   - Attempt UPDATE on lineage record
   - Expected: UPDATE fails silently (INSERT OR IGNORE behavior on existing event_id)

---

## READBACK

**Pass Condition:** Given request_id, full session lineage reconstructible:

```sql
SELECT 
  event_id,
  session_id,
  provider,
  model,
  runtime,
  source,
  who_actor,
  when_ts,
  trace_id,
  related_event_id
FROM events 
WHERE what_type='ai_lineage' 
  AND request_id='{target_request_id}'
ORDER BY when_ts ASC;
```

**Validation:**
- All provider/model/runtime/source fields populated
- Trace chain intact (trace_id → related_event_id → previous_event)
- Temporal consistency (when_ts in order)
- Uniqueness (one record per request_id)

---

## ROLLBACK / FAILURE CONDITION

**Rollback Condition:** If lineage readback fails any validation:

1. Identify failed event_id
2. Mark for manual review (DO NOT delete)
3. Create incident record (separate from Event Store)
4. Halt new lineage recording until reviewed
5. Manual inspection: verify signature chain integrity

**Non-Recoverable Failure:**
- If Event Store corruption detected → escalate to HG
- If signature chain broken → escalate to HG
- If provider/model/runtime fields NULL → review cause, may indicate incomplete session capture

---

## DEPENDENCIES (REVISED)

**UPSTREAM DEPENDENCIES:** NONE
- IP-007 is fully independent
- No blocking dependency on IP-005 or IP-009
- Implements directly into existing event_gate

**DOWNSTREAM CONSUMERS:**
- IP-009 will consume lineage events (soft dependency for completeness)
- IP-005 may run in parallel (authorization separate from lineage)

**RECOMMENDATION:** Implement IP-007 FIRST (lowest risk, proven interface)

---

## SCOPE VERIFICATION

**HG Approved Scope Check:**
- Target: Store Orchestra lineage ✓
- Input: AI session metadata ✓
- Output: Immutable Event Store records ✓
- Persistence: Event Store ✓
- Forbidden changes: None listed ✓
- Scope creep risk: NONE (additive only)

**Result: WITHIN APPROVED SCOPE**

---

## NEXT PHASE (REVISED — MINIMAL SCOPE)

Upon Implementation Plan Review APPROVAL:
1. Identify Orchestra dispatcher → identify session completion hook
2. Add lineage payload marshaling (vendor/model/runtime/source extraction)
3. Call event_gate.process_event() at completion hook
4. Integration testing: Session complete → Event Store record with vendor/model/runtime/source
5. Runtime evidence collection (readback query validates fields)
6. Institutional memory recording

**NO NEW COMPONENTS NEEDED.** Implementation is pure integration.

**Current Status:** PLAN REVISED / READY FOR FINAL REVIEW
