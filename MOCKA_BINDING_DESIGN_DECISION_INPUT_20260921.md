# MoCKA Runtime Binding Design Decision Input
## KUROKO PC 第4弾 - 既存 Runtime 資産評価
**Date:** 2026-09-21  
**Status:** Investigation Complete (No Implementation)  
**Branch:** phase/hgd-up-test-003-v3.2

---

## PHASE 1: EXISTING ID CAPABILITY MATRIX

### A. ID Inventory & Capability Assessment

| ID Type | Exists | Generated | Stored | Can Identify Execution? | Evidence Location |
|---------|--------|-----------|--------|------------------------|-------------------|
| **request_id** | YES | JSON-RPC client | request_executions table; events.request_id field | PARTIAL - Stored in execution table, linked to event via event.request_id | mocka_mcp_server.py:1271, 609, 836; event_gate.py:75 |
| **decision_id** | YES | mocka_mcp_server._next_decision_id() | decision_ledger.jsonl (append-only) | NO - Decision record has no execution/event ref | mocka_mcp_server.py:1125, 437-448 |
| **event_id** | YES | phi_os.event_gate.process_event() | events table | PARTIAL - Generated after execution, no link to req_id in record structure | event_gate.py:130, 43-44 |
| **tool_call_id** | NO | N/A | N/A | N/A | NOT FOUND in codebase |
| **classification_id** | YES | mocka_mcp_server._next_classification_id() | integrity_classification.jsonl (append-only) | NO - No execution reference | mocka_mcp_server.py:1209, 488-500 |
| **task_id** | YES | User input + auto-generation | MOCKA_TODO_ACTIVE.json | NO - Not exec-level identifier | mocka_mcp_server.py:677-690 |
| **run_id** | NO | N/A | N/A | N/A | NOT FOUND in codebase |
| **timestamp** | YES (as when_ts) | System time | events table (when_ts field) | WEAK - Multiple events can have close timestamps | event_gate.py:53, 131 |
| **hash** (trace_id) | YES | phi_os.integrity.sign_event() | events table (trace_id field, related_event_id field) | PARTIAL - Hash chain exists but execution is not explicitly marked | event_gate.py:94-95; integrity.py signature logic |
| **correlation_id** | NO | N/A | N/A | N/A | NOT FOUND in codebase |
| **trace_id** | YES | integrity.sign_event() | events table (trace_id, related_event_id) | PARTIAL - Hash chain for event correlation, but not for execution | event_gate.py:94-95 |

**Summary:** 
- **Execution-to-Decision link:** NOT FOUND
- **Execution-to-Event link:** PARTIAL (request_id in event record, but not as structured binding)
- **Event-to-Request link:** POTENTIAL (via event.request_id, but not yet used for reverse lookup)

---

## PHASE 2: EXISTING EVENT LEDGER ANALYSIS

### A. Event Record Schema (from phi_os/event_gate.py:_write())

```
Event Record Fields:
  - event_id (E{YYYYMMDD}_{micros}{random_hex})
  - when_ts (ISO timestamp)
  - who_actor
  - what_type
  - where_component
  - where_path
  - why_purpose
  - how_trigger
  - before_state
  - after_state
  - title (from what_title)
  - short_summary (from description)
  - session_id (from who_session)
  - _source (live/buffered)
  - free_note (tags + metadata)
  - channel_type (gate/ext/buffered)
  - lifecycle_phase (in_operation)
  - risk_level (normal/incident/etc.)
  - request_id ← CRITICAL FIELD
  - trace_id (hash chain current)
  - related_event_id (hash chain previous)
```

### B. Can We Reconstruct Decision → Execution → Event?

**Test Case:** Given decision_id "DC_20260705_002", find:
1. What execution(s) used this decision?
2. What event(s) resulted from that execution?
3. Can we reverse-engineer the full chain?

**Analysis:**

```
Step 1: Decision → Decision Ledger
  ✓ decision_ledger.jsonl has: decision_id, title, decision, rationale, etc.
  ✗ decision_id record has NO: execution_id, event_id, request_id
  
Step 2: Decision → Execution
  ✗ No reverse link from decision record to execution
  ✗ Execution must provide decision_id as input (forward-only)
  
Step 3: Execution → Event
  ✓ event.request_id field exists
  ✓ events table stores request_id when set
  ✓ But: request_id is NOT automatically extracted/indexed for queries
  
Step 4: Event → Event (chain)
  ✓ trace_id (current hash) + related_event_id (previous hash)
  ✓ Events are linked in chronological chain
  ✗ But: Chain does NOT contain decision_id or request_id
```

**Reconstruction Capability:**

| Path | Can Reconstruct | Method | Evidence |
|------|------------------|--------|----------|
| Decision → Execution | PARTIAL | Must search events.request_id values that mention decision_id in tags/description | Not automatic, manual grep needed |
| Execution → Event | YES | Query: events WHERE request_id = ? | event.request_id field is present |
| Event → Decision | PARTIAL | Search decision_ledger.jsonl for related_events field | Some decisions record events, but not all |
| Full Chain | PARTIAL | Requires cross-file queries (decision_ledger.jsonl + events.db) | No unified index |

**Status:** PARTIAL - Event Ledger can trace request_id → event_id, but cannot automatically link decision_id → execution without additional context.

---

## PHASE 3: EXISTING DECISION LEDGER ANALYSIS

### A. Decision Record Schema (from DECISION_LEDGER_SCHEMA_v1.md + actual records)

```
Decision Record Fields:
  - decision_id (DC_YYYYMMDD_NNN)
  - title
  - context
  - alternatives []
  - decision
  - rationale
  - impact
  - related_events [] ← PRESENT
  - related_documents []
  - approved_by
  - approved_at
  - supersedes
  - superseded_by
  - status (Active/Superseded/Withdrawn)
```

### B. Missing Reference Fields

| Field | Exists | Why Matters |
|-------|--------|------------|
| execution_id | NO | Can't identify which execution(s) used this decision |
| request_id | NO | Can't link decision to request level |
| tool_call_id | NO | Can't identify tool invocation |
| event_id | PARTIAL | related_events array lists event_ids, but only if manually set |
| run_id | NO | No per-execution tracking |

### C. Companion Event Mechanism (mocka_decision_write)

**Code Path:** mocka_mcp_server.py:1144-1168

```python
# When decision written, create companion event
gate_payload = {
    "what_title": f"[DECISION_MADE] {decision_id}: {title}",
    "tags": f"decision_ledger,{decision_id},{status}",
    ...
    # NOTE: request_id NOT included in companion event payload
}
```

**Status:** PARTIAL
- Companion event IS created (optional, failure doesn't block)
- decision_id IS in tags
- **request_id is NOT in companion event payload** ← GAP

---

## PHASE 4: BINDING DESIGN OPTIONS COMPARISON

### Option A: Execution Identity (New execution_id)

**Structure:**
```
Decision (decision_id)
  ↓ [user-provided in request]
Request (req_id)
  ↓ [JSON-RPC frame]
Execution (NEW: execution_id) ← Generated during tool execution
  ↓ [unique per invocation]
Event (event_id)
```

**Changes Required:**
1. Generate execution_id in execute_tool() [mocka_mcp_server.py:~610]
2. Create execution_bindings table (req_id, execution_id, result_id, timestamp)
3. Extract result_id before return and record binding
4. Thread execution_id through response (optional)

**Schema Impact:** 
- NEW table: execution_bindings
- NO changes to existing ledgers

**Runtime Impact:**
- +1 generation point (line 610)
- +1 query per tool execution (idempotency check already exists)
- +1 record write per execution

**Evidence Strength:** STRONG - Direct linkage at execution time

**Migration Requirement:** NONE - Purely additive

---

### Option B: Execution Receipt (Enhanced Event Metadata)

**Structure:**
```
Decision (decision_id)
  ↓ [user-provided]
Request (req_id)
  ↓ [JSON-RPC frame]
Execution
  ↓ [proceeds]
Event (event_id) with enriched metadata
  └─ includes: decision_id, req_id, tool_name
```

**Changes Required:**
1. Enhance gate_payload to include decision_id from args
2. Modify companion event for decisions to include request_id
3. Add decision_id field to event record (optional migration)

**Schema Impact:**
- NO new tables
- OPTIONAL: Add decision_id, tool_name columns to events table (backward compatible)
- Enhance gate_payload construction

**Runtime Impact:**
- No new generation point
- Events now carry more metadata
- +2-3 fields per event record

**Evidence Strength:** MEDIUM - Relies on caller to provide decision_id in args

**Migration Requirement:** Optional - Can enrich events forward-only without migrating history

---

### Option C: Existing Correlation (Leverage Current IDs)

**Structure:**
```
Decision (decision_id) → Decision Ledger
  ↓ [user-provided]
Request (req_id) → request_executions table
  ↓ [JSON-RPC]
Execution
  ↓
Event (event_id) → events table
  └─ request_id field (EXISTS - line 75 of event_gate.py)
```

**Query Path:**
```
Q: "Which decision led to event E20260921_abc123?"
1. SELECT request_id FROM events WHERE event_id = 'E20260921_abc123'
2. SELECT tool_name, status FROM request_executions WHERE req_id = ?
3. Search args in decision ledger for decision_id (grep/index query)
```

**Changes Required:**
1. Verify request_id is actually persisted in events table (currently in payload, storage unverified)
2. Create index on events.request_id for fast queries
3. Create decision_id reference in related_events[] during write

**Schema Impact:**
- NO new tables
- OPTIONAL: Add index on events.request_id
- NO schema changes

**Runtime Impact:**
- Minimal - Uses existing fields
- +1 index creation (one-time)

**Evidence Strength:** WEAK - Requires manual correlation through multiple joins

**Migration Requirement:** NONE - All data already exists (assuming request_id persistence verified)

---

## PHASE 5: RISK ANALYSIS

### Risk Matrix

| Aspect | Option A | Option B | Option C |
|--------|----------|----------|----------|
| **Existing Compatibility** | Additive only | Additive + enhancement | Leverages existing |
| **Schema Disruption** | No (new table) | No (metadata enrichment) | No (index only) |
| **Reverse Lookup (Event→Decision)** | STRONG | MEDIUM | WEAK |
| **Forward Tracking (Decision→Execution)** | STRONG | MEDIUM | CANNOT |
| **Implementation Complexity** | MEDIUM | LOW | LOW |
| **Query Performance** | Fast (indexed) | Fast (indexed) | Moderate (grep) |
| **Data Loss Risk** | ZERO | ZERO | ZERO |
| **Verification Needed** | None | request_id persistence verification | request_id persistence verification |
| **Future Extensibility** | execution_id becomes canonical | Event becomes richer but still anonymous executions | Limited by existing structure |

### Critical Unknowns to Verify

**All Options Depend On:** Is request_id actually persisted in events table?

```
Hypothesis: mocka_write_event sets request_id in gate_payload (line 836),
            event_gate._write() maps request_id to events.request_id (line 75),
            but: NO verification that SQLite actually stores the value.
```

**Required Verification:**
```
SELECT request_id FROM events WHERE event_id = 'E20260705_001' LIMIT 1;
```

If this returns NULL/empty when a request_id was in gate_payload:
- Options B & C are weakened
- Option A becomes the only reliable path

---

## CURRENT VERIFIED STATE

### What Works

✓ Idempotency: req_id checked against request_executions table  
✓ Authority: decision_id read from Decision Ledger, status validated  
✓ Event Generation: event_id created, persisted to events table  
✓ Event Metadata: what_type, who_actor, tags, etc. recorded  
✓ Decision Records: decision_id, decision, rationale, impact append-only  
✓ Companion Events: mocka_decision_write creates event with decision_id in tags  

### What Doesn't Work

✗ Execution ID: No unique identifier per invocation  
✗ Execution Binding: No req_id ↔ result_id record  
✗ Reverse Lookup: Can't ask "Which decision led to event X?"  
✗ Consequence Chain: No automatic link (decision → execution → result → next decision)  

### What's Partially Verified

⚠ request_id Persistence: request_id in gate_payload (verified), but actual SQLite storage (UNVERIFIED)  
⚠ companion Event Linking: decision_id in tags, but structured link missing  
⚠ Forward Execution: Can ask "What decision?" but must provide req_id upfront  

---

## BINDING GAP SUMMARY

### The Problem
```
Decision → Execution binding is MISSING
Execution → Event binding is PARTIAL (via request_id, but unverified)
Event → Consequence binding does NOT EXIST (implicit caller re-injection only)
```

### The Root Cause
```
Current flow: req_id (JSON-RPC) → [execution] → result_id (event_id/decision_id)

No connection between them once execution completes.
Events carry request_id (potentially), but this is never used for reverse lookup.
Decision records have related_events[], but this is manual (not automatic).
```

### Minimum Required Binding Point
```
Location: execute_tool() function (mocka_mcp_server.py:595-1260)

Missing: Execution ID generation + Outcome record
Required: (req_id, execution_id, result_type, result_id) binding
Effect: Enables tracing from request through execution to consequence
```

---

## HUMAN GATE DECISION REQUIRED

**Question 1:** Should we verify that request_id is actually persisted in events.request_id field?
- YES → Verify with: SELECT request_id FROM events WHERE event_id = ?
- NO → Assume Option C is risky; proceed with Option A/B

**Question 2:** Which binding design fits MoCKA principles best?

| Option | Principle Fit | Implementation Complexity | Trace Capability |
|--------|---------------|--------------------------|------------------|
| A: execution_id | EXPLICIT (new canonical ID) | MEDIUM | COMPLETE |
| B: Event Enrichment | IMPLICIT (metadata in event) | LOW | PARTIAL |
| C: Existing Correlation | MINIMAL CHANGE | LOW | WEAK |

**Question 3:** Is the binding for "traceability/audit" or for "enforcement/automation"?
- Traceability Only → Options B/C may suffice
- Automation (auto-gate escalation, etc.) → Option A required

**Question 4:** Should execution binding be explicit (standalone table) or implicit (metadata in existing structures)?
- Explicit (Option A) → Slower to implement, faster to query, clear semantics
- Implicit (Option B) → Faster to implement, slower to query, rich event context

---

## DELIVERABLE SUMMARY

### What This Document Provides
1. ✓ Current state: ID inventory + existing capabilities
2. ✓ Binding gap analysis: Specific missing pieces identified
3. ✓ Design options: 3 approaches with trade-off analysis
4. ✓ Risk assessment: Per-option risks and unknowns
5. ✓ Implementation scope: What changes for each option

### What This Document Does NOT Provide
- ✗ Recommendation (for Human Gate to decide)
- ✗ Code changes (investigation only)
- ✗ Execution plan (post-decision)

### Next Steps (Post-Decision)
1. Verify request_id persistence in events table
2. Evaluate each option against MoCKA governance principles
3. Make binding design decision
4. Implement selected option (Phase 7 onwards)

---

**Investigation Status:** COMPLETE  
**Implementation Status:** NOT AUTHORIZED  
**Ready for Human Gate Review:** YES

