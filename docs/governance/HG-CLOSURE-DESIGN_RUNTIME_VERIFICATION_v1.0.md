# Runtime Verification Strategy for C1-C16 Closure Conditions

## Document Purpose

This document specifies the **operational methodology** for verifying D6-D12 Closure Design at runtime. Each C1-C16 condition is mapped to concrete verification procedures, test scenarios, and acceptance criteria.

**Status**: Design/Planning Phase → Preparation for DP-4 (Runtime Evidence Collection)

**Scope**: Defines HOW to verify closure without yet executing verification (execution authorization = DP-4)

---

## Overview: Five Verification Layers

```
Layer 1: Structural Verification — Code path existence (static)
Layer 2: Integration Verification — Component connectivity (integration test)
Layer 3: Execution Verification — Runtime behavior (functional test)
Layer 4: Persistence Verification — Data storage confirmation (state verification)
Layer 5: Loop Verification — Central Loop closure (end-to-end test)
```

---

## C1-C5: Identity & Persistence Verification

### C1: Immutable canonical_id (GD_{timestamp}_{hash})

**Verification Method**: Structural + Persistence

**Test Scenario 1.1 — ID Format Validation**
```
Setup: Generate CanonicalDecisionRecord via policy.evaluate()
Action: Check canonical_id format
Expected: "GD_" prefix + 10-digit timestamp + "_" + 8-char hash
Acceptance: Format matches regex ^GD_\d{10}_[0-9a-f]{8}$
Instrumentation: Log decision_record["canonical_id"]
```

**Test Scenario 1.2 — ID Immutability**
```
Setup: Create decision_record, write to events.db, reload from DB
Action: Compare canonical_id before and after reload
Expected: Identical (immutable)
Acceptance: before_id == after_id
Instrumentation: @transactional logging + hash verification
Rollback: If mutable, decision_record schema corrupted
```

**Verification Checklist C1**:
- [ ] canonical_id uniqueness across events.db (no duplicates)
- [ ] Hash collision rate < 1/1000 (test with 1000 synthetic decisions)
- [ ] ID remains unchanged through 3 read cycles
- [ ] ID persists across server restart

---

### C2: Idempotency by (source_event_id, governance_version)

**Verification Method**: Integration + Persistence

**Test Scenario 2.1 — Duplicate Prevention**
```
Setup: Create event E_001 with governance_version="2026-09-09"
Action: Process event → generate decision D_1
         Process same event again (identical source_event_id + version)
Expected: No second decision record created (idempotent)
Acceptance: query_events("governance_decision_event", 
                         source_event_id="E_001") → count == 1
Instrumentation: Log each insert attempt + result
Rollback: If count > 1, idempotency failed
```

**Test Scenario 2.2 — Version-Based Differentiation**
```
Setup: Create event E_001 with governance_version="2026-09-09"
       Create event E_001 with governance_version="2026-09-10" (different)
Action: Process both events
Expected: Two decision records (different versions)
Acceptance: query_events(...) → count == 2 (one per version)
Instrumentation: Log (source_event_id, governance_version) pair
Rollback: If records conflate, version isolation failed
```

**Verification Checklist C2**:
- [ ] Same (source_event_id, version) → skip write (no INSERT)
- [ ] Different source_event_id → new record (INSERT)
- [ ] Same source_event_id, different version → new record (INSERT)
- [ ] Unique index prevents duplicates at DB level

---

### C3: Authorization Status Separate from Decision Status

**Verification Method**: Structural + Integration

**Test Scenario 3.1 — Field Separation**
```
Setup: Generate CanonicalDecisionRecord
Action: Check schema has distinct fields
Expected: decision_status ≠ authorization_status (separate keys)
Acceptance: json.loads(decision_record) has both fields
Instrumentation: Schema introspection
```

**Test Scenario 3.2 — Status Independence**
```
Setup: Create decision with decision_status="defer", authorization_status="PENDING"
       Update authorization_status to "APPROVED" (policy unchanged)
Action: Query events.db, read both fields
Expected: decision_status still "defer", authorization_status now "APPROVED"
Acceptance: Both fields independent (update one, other unchanged)
Instrumentation: Before/after record comparison
```

**Verification Checklist C3**:
- [ ] decision_status values: defer, accept_telemetry, reject, custom
- [ ] authorization_status values: PENDING_HUMAN_REVIEW, APPROVED, REJECTED
- [ ] No field aliasing (decision_status ≠ authorization_status)
- [ ] Updates to authorization don't affect decision_status

---

### C4: Written to events.db with what_type='governance_decision_event'

**Verification Method**: Persistence

**Test Scenario 4.1 — Typed Event Insertion**
```
Setup: Record CanonicalDecisionRecord via EventBuffer.push()
Action: Query events.db for what_type='governance_decision_event'
Expected: Record found with correct what_type
Acceptance: SELECT ... WHERE what_type='governance_decision_event' → 1+ rows
Instrumentation: Query result logging
Rollback: If not found, governance decision not persisted
```

**Test Scenario 4.2 — Schema Validation**
```
Setup: Inspect events.db schema
Action: Verify columns: event_id, what_type, raw_json, ...
Expected: what_type column exists; index on what_type
Acceptance: PRAGMA table_info(events) includes what_type; index_name contains "what_type"
Instrumentation: Schema introspection
```

**Verification Checklist C4**:
- [ ] governance_decision_event records written to events.db
- [ ] what_type='governance_decision_event' query returns all governance decisions
- [ ] Query performance acceptable (index present)
- [ ] No loss of governance decisions during batch write

---

### C5: MemoryContext reads typed governance_decision_event

**Verification Method**: Integration + Functional

**Test Scenario 5.1 — Typed Query**
```
Setup: Populate events.db with governance_decision_event records
Action: Call MemoryContext.load()
Expected: governance_decisions list populated from what_type='governance_decision_event'
Acceptance: len(memory_context.governance_decisions) > 0
Instrumentation: Query logging + record count
```

**Test Scenario 5.2 — Type Filtering (Not String Search)**
```
Setup: Populate events.db with mixed event types (governance_decision_event + other)
Action: Call MemoryContext.load()
Expected: ONLY governance_decision_event records loaded
Acceptance: All records in governance_decisions have decision_status field
           (string search would return partial/mismatched records)
Instrumentation: Type verification on each loaded record
```

**Verification Checklist C5**:
- [ ] MemoryContext._load_governance_decisions() uses what_type filter
- [ ] No string search on why_purpose (typed lookup only)
- [ ] governance_decisions list reflects recent decisions (latest first)
- [ ] JSON parsing succeeds for all records

---

## C6-C10: Execution & Authorization Verification

### C6: Governance decision initiates from policy.evaluate()

**Verification Method**: Execution + Instrumentation

**Test Scenario 6.1 — Decision Source Tracking**
```
Setup: Instrument policy.evaluate() entry/exit
Action: Trigger /collect → RelayKernel.ingest() → policy.evaluate()
Expected: Log entry shows policy.evaluate() called; log exit shows return value
Acceptance: grep "DECISION_SOURCE: policy.evaluate()" logs → found
Instrumentation: @decorator or explicit logging in policy.py
```

**Test Scenario 6.2 — No Manual Governance Writes**
```
Setup: Search codebase for direct writes to governance_decision_event (outside policy.evaluate())
Action: Code review + static analysis
Expected: No manual writes found (all via policy pathway)
Acceptance: grep -r "what_type.*governance_decision" → only in policy.evaluate() context
Instrumentation: Static code analysis
```

**Verification Checklist C6**:
- [ ] policy.evaluate() is sole source of governance decisions
- [ ] No direct INSERT into governance_decision_event (outside policy)
- [ ] Execution trace shows policy.evaluate() invoked before each decision
- [ ] Return value captured (not discarded)

---

### C7: Authorization status explicitly checked BEFORE action routing

**Verification Method**: Execution

**Test Scenario 7.1 — Pre-Action Authorization Check**
```
Setup: Create decision with authorization_status="PENDING_HUMAN_REVIEW"
Action: Attempt action routing (e.g., STORE_EVENT)
Expected: Authorization check FAILS; action NOT routed
Acceptance: action_router.route() returns {status: "authorization_pending"}
Instrumentation: Log authorization check result before routing
Rollback: If action routes despite PENDING, fail-closed rule violated
```

**Test Scenario 7.2 — Approved Action Execution**
```
Setup: Create decision with authorization_status="APPROVED"
Action: Attempt action routing
Expected: Authorization check PASSES; action routed
Acceptance: action_router.route() returns {action: "STORE_EVENT"} or similar
Instrumentation: Log authorization check result + routing decision
```

**Verification Checklist C7**:
- [ ] action_router.route() checks authorization_status BEFORE routing
- [ ] PENDING → block routing
- [ ] APPROVED → allow routing
- [ ] REJECTED → block routing
- [ ] Check happens at boundary (before any side effects)

---

### C8: Missing authorization → PENDING escalation to Human Gate

**Verification Method**: Execution + Integration

**Test Scenario 8.1 — Escalation on Missing Authorization**
```
Setup: Create decision with authorization_status=None (missing)
Action: Attempt action routing
Expected: Escalation triggered (not default acceptance)
Acceptance: Log contains "ESCALATE_TO_HUMAN_GATE" or similar
Instrumentation: Explicit escalation logging
Rollback: If default acceptance happens, fail-closed violated
```

**Test Scenario 8.2 — Escalation Path**
```
Setup: Configure escalation endpoint (e.g., /api/gate/escalation)
Action: Trigger escalation from missing authorization
Expected: Decision record sent to escalation endpoint
Acceptance: POST request logged; decision_ledger marked PENDING_HUMAN_REVIEW
Instrumentation: HTTP request logging + decision_ledger update
```

**Verification Checklist C8**:
- [ ] Missing authorization triggers escalation (not default accept)
- [ ] Escalation endpoint receives decision record
- [ ] decision_ledger.authorization_status set to PENDING_HUMAN_REVIEW
- [ ] Action execution BLOCKED during escalation

---

### C9-C10: UNKNOWN & NOT_PROVEN Preservation

**Verification Method**: Structural + Execution

**Test Scenario 9.1 — UNKNOWN Preservation in Decision**
```
Setup: Create event with UNKNOWN state (e.g., event_gate validation uncertain)
       Call policy.evaluate() on UNKNOWN state
Action: Check decision_record.unknown_preservation field
Expected: unknown_preservation=true (UNKNOWN preserved)
Acceptance: decision_record["unknown_preservation"] == True
Instrumentation: State tracking through decision creation
```

**Test Scenario 9.2 — UNKNOWN NOT Converted to Default**
```
Setup: UNKNOWN state → decision_record with unknown_preservation=true
Action: Check decision_status field
Expected: NOT converted to "defer" or other default
Acceptance: decision_status remains original (or marked UNCERTAIN)
Instrumentation: Policy logic inspection
```

**Test Scenario 10.1 — NOT_PROVEN Preservation at Execution**
```
Setup: Execution path NOT_PROVEN (e.g., EventBuffer async write pending)
Action: Check decision_record.not_proven_preservation field
Expected: not_proven_preservation=true
Acceptance: decision_record["not_proven_preservation"] == True
Instrumentation: Execution path tracking
```

**Verification Checklist C9-C10**:
- [ ] UNKNOWN states preserved (not converted to defaults)
- [ ] decision_record.unknown_preservation flag set correctly
- [ ] NOT_PROVEN states preserved throughout execution
- [ ] Fail-closed behavior enforced when preservation flags set

---

## C11-C16: Loop Closure & Verification

### C11: Outcome → New Event → Re-entry cycle executes

**Verification Method**: End-to-End Execution

**Test Scenario 11.1 — Action Outcome Recording**
```
Setup: AI executes approved action (e.g., update database record)
Action: outcome_recorder.record_outcome() called
Expected: Outcome event created with action_id, action_type, result_code
Acceptance: Log contains "OUTCOME_RECORDED: action_id={id}, result_code={code}"
Instrumentation: outcome_recorder logging
```

**Test Scenario 11.2 — New Event Generated**
```
Setup: Outcome recorded
Action: Check events.db for action_outcome_event
Expected: New row with what_type='action_outcome_event'
Acceptance: SELECT ... WHERE what_type='action_outcome_event' → 1+ rows
Instrumentation: events.db query
```

**Verification Checklist C11**:
- [ ] Outcome recorded immediately after action execution
- [ ] New event created in events.db (action_outcome_event)
- [ ] Event contains: action_id, action_type, result_code, result_data
- [ ] Event timestamped at execution time

---

### C12: New event re-enters /collect endpoint

**Verification Method**: Integration + Execution

**Test Scenario 12.1 — POST /collect Re-entry**
```
Setup: outcome_recorder.record_outcome() generates new event
Action: HTTP POST to http://localhost:5000/collect with outcome event
Expected: /collect endpoint receives and processes
Acceptance: HTTP 200 response; event_buffer.push() called
Instrumentation: HTTP request/response logging; EventBuffer instrumentation
```

**Test Scenario 12.2 — Event Propagation**
```
Setup: Re-entry event posted to /collect
Action: Check EventBuffer queue
Expected: Event added to buffer; async flush to /api/gate/event/batch
Acceptance: Log shows "EVENT_BUFFERED: {event_id}" → "EVENT_FLUSHED: {event_id}"
Instrumentation: EventBuffer logging
```

**Verification Checklist C12**:
- [ ] outcome_recorder calls requests.post("http://localhost:5000/collect", ...)
- [ ] /collect endpoint receives POST request
- [ ] Event parsed and added to EventBuffer
- [ ] No rejection at /collect entry point (event well-formed)

---

### C13: Re-entered event triggers new policy.evaluate()

**Verification Method**: Execution

**Test Scenario 13.1 — Policy Re-Evaluation**
```
Setup: outcome event re-entered via /collect
Action: RelayKernel.ingest() called; policy.evaluate() invoked on re-entered event
Expected: NEW policy.evaluate() call (not cached from original event)
Acceptance: Log shows "DECISION_SOURCE: policy.evaluate() invoked" for re-entered event
Instrumentation: policy.evaluate() entry/exit logging
Rollback: If policy evaluation skipped, loop incomplete
```

**Test Scenario 13.2 — New Decision Generated**
```
Setup: Re-entered event processed through policy.evaluate()
Action: Check for NEW CanonicalDecisionRecord
Expected: New decision_id (different from original decision)
Acceptance: decision_id_original ≠ decision_id_new
Instrumentation: Decision ID logging
```

**Verification Checklist C13**:
- [ ] Re-entered event NOT skipped by caching/deduplication
- [ ] policy.evaluate() invoked on re-entered event
- [ ] New governance decision generated (idempotency key different)
- [ ] No bypass of governance layer

---

### C14: Fail-Closed blocking rules enforced

**Verification Method**: Execution

**Test Scenario 14.1 — Persistence Failure Blocks Execution**
```
Setup: Mock events.db write failure
Action: Attempt to write governance_decision_event; write fails
Expected: Return {status: "governance_bind_failed"}; action NOT routed
Acceptance: action_router.route() NOT called
Instrumentation: Exception handling + error logging
Rollback: If action routes despite failure, fail-closed violated
```

**Test Scenario 14.2 — Missing Decision Blocks Routing**
```
Setup: policy.evaluate() returns NO decision dict (error case)
Action: Attempt action routing
Expected: routing BLOCKED; escalation triggered
Acceptance: Log shows "ROUTING_BLOCKED: no_decision" or similar
Instrumentation: Null/missing decision handling
```

**Verification Checklist C14**:
- [ ] Persistence failure → block execution (not silent retry)
- [ ] Missing decision → block action routing
- [ ] Missing context → block execution
- [ ] Invalid source_id → block idempotency verification
- [ ] All blocks logged + escalated

---

### C15: Human Gate decision recorded in decision_ledger BEFORE action execution

**Verification Method**: Integration + Persistence

**Test Scenario 15.1 — Decision_Ledger Write Timing**
```
Setup: Decision approved by Human Gate
Action: Check decision_ledger.write() called BEFORE action_router.route()
Expected: decision_ledger entry written first
Acceptance: Log shows "DECISION_LEDGER_WRITE: ..." BEFORE "ACTION_EXECUTE: ..."
Instrumentation: Timestamp logging in both operations
Rollback: If action executes before ledger write, orphaned action
```

**Test Scenario 15.2 — Ledger Entry Confirmation**
```
Setup: Human Gate approval recorded in decision_ledger
Action: Query decision_ledger for entry
Expected: Entry found with: decision_id, authorization_timestamp, authorizing_actor
Acceptance: SELECT ... WHERE decision_id={id} → row with authorizing_actor="human:*"
Instrumentation: decision_ledger query logging
```

**Verification Checklist C15**:
- [ ] decision_ledger.write() called before action execution
- [ ] Ledger entry persisted to storage (not in-memory only)
- [ ] Entry contains: decision_id, authorizing_actor, timestamp
- [ ] Entry readable immediately after write (durability verified)

---

### C16: Loop re-entry within 5sec RT window

**Verification Method**: Performance/Timing

**Test Scenario 16.1 — Re-entry Response Time**
```
Setup: outcome_recorder.record_outcome() calls requests.post() to /collect
Action: Measure time from POST to response received
Expected: < 5 seconds
Acceptance: response_time < 5.0
Instrumentation: Timer logging in outcome_recorder + /collect endpoint
Rollback: If > 5sec, performance SLA violated
```

**Test Scenario 16.2 — End-to-End Loop Time**
```
Setup: Event enters /collect → Relay → policy → governance decision → action routing → outcome recording → re-entry
Action: Measure time from initial /collect to /collect re-entry POST
Expected: < 10 seconds (2x 5sec windows for buffers)
Acceptance: loop_time < 10.0
Instrumentation: Distributed tracing (correlation IDs) + latency logging
```

**Verification Checklist C16**:
- [ ] outcome_recorder re-entry POST completes in < 5sec
- [ ] /collect re-entry request processed immediately
- [ ] Full Central Loop cycle < 10sec (nominal case)
- [ ] No unbounded delays in event_buffer async flush

---

## Layer 5: Central Loop Closure Verification

### E2E Test: Complete Central Runtime Loop

**Test Scenario: Loop Closure E2E**

```
Test Setup:
1. Start MoCKA services (app.py, phi_os services, events.db)
2. Initialize instrumentation (logging, tracing)
3. Prepare test event (5W1H complete, well-formed)

Test Execution:
STEP 1: Event Entry (E1)
  - POST /collect with test event
  - Check: event added to EventBuffer
  - Instrument: correlation_id assigned

STEP 2: Record (E2)
  - EventBuffer flushes batch to /api/gate/event/batch
  - events.db write confirmed
  - Check: event persisted (events.db query)
  - Instrument: event_id confirmed in DB

STEP 3: Governance (E3)
  - RelayKernel.ingest() called (correlation_id matched)
  - policy.evaluate() returns decision dict
  - CanonicalDecisionRecord created
  - governance_decision_event written to events.db (idempotency check passed)
  - Check: C1-C5 conditions verified
  - Instrument: decision_id logged, authorization_status="PENDING_HUMAN_REVIEW"

STEP 4: Memory (E4)
  - MemoryContext.load() queries governance_decision_event (typed search)
  - governance_decisions list populated
  - Check: C5 condition verified
  - Instrument: memory_context.governance_decisions updated

STEP 5: Context (E4 cont'd)
  - WorkingContext created from Memory
  - Check: authorized_actions empty (PENDING decision)
  - Instrument: working_context state logged

STEP 6: Human Gate Approval (E4 authorization)
  - Simulate Human Gate approving decision
  - Update decision_ledger: authorization_status="APPROVED"
  - Update CanonicalDecisionRecord: authorizing_actor="human:test"
  - Check: C15 condition verified
  - Instrument: approval timestamp logged

STEP 7: AI Execution (E5)
  - WorkingContext.can_execute_action() checks authorization_status
  - Returns TRUE (APPROVED)
  - Action router called with STORE_EVENT
  - Action executed (e.g., state update)
  - Check: C7 authorization check passed
  - Instrument: action_id assigned, execution_timestamp logged

STEP 8: Outcome Recording (E6)
  - outcome_recorder.record_outcome() called with action_id, result_code
  - action_outcome_event created
  - Check: C11 condition verified
  - Instrument: outcome_event_id logged

STEP 9: Re-entry (E6a)
  - outcome_recorder POSTs action_outcome_event to /collect
  - Check: response_time < 5sec (C16 timing)
  - /collect receives POST, adds to EventBuffer
  - EventBuffer flushes to events.db
  - Check: C12 re-entry confirmed
  - Instrument: reentry_timestamp logged

STEP 10: Loop Continuation (E3 restart)
  - RelayKernel.ingest() called on outcome event
  - policy.evaluate() invoked on outcome
  - NEW governance decision generated (different decision_id)
  - Idempotency check passed (source_event_id different)
  - Check: C13 policy re-evaluation confirmed, C2 idempotency confirmed
  - Instrument: new_decision_id logged

Central Loop Status:
  - Event → Record → Governance → Memory → Context → AI → Outcome → New Event → Re-entry → CONFIRMED
  - All 16 conditions (C1-C16) verified at runtime
  - Loop closure achieved: E6a re-enters to E1 (Central Loop continues)

Expected Outcome:
  ✓ Log file contains: DECISION_SOURCE × 2, EVENT_BUFFERED × 2, OUTCOME_RECORDED × 1, 
    REENTRY_SUCCESS × 1
  ✓ decision_ledger contains: 2 decisions (original + outcome)
  ✓ events.db contains: 3 records (test_event, governance_decision_event, action_outcome_event)
  ✓ Total loop execution time: < 10 seconds
  ✓ No blocked escalations (all authorizations successful)
```

---

## Verification Acceptance Criteria (Design/Planning)

For Design Phase to PASS Runtime Verification:

- [ ] All C1-C16 conditions have defined verification procedures
- [ ] Each procedure has concrete test scenario(s)
- [ ] Acceptance criteria are measurable (not subjective)
- [ ] Instrumentation points identified (logging, metrics, tracing)
- [ ] Rollback procedures defined for each failure mode
- [ ] E2E test scenario covers full Central Loop closure
- [ ] Performance SLA defined (C16: 5sec/10sec windows)
- [ ] Decision Ledger integration confirmed
- [ ] Human Gate approval pathway validated

**Design/Planning Status**: ✓ Verification strategy complete and ready for DP-4 authorization

---

## Next Phase: DP-4 (Runtime Evidence Collection)

Upon DP-4 authorization, implementation will:

1. Deploy instrumentation (logging, tracing, metrics)
2. Run C1-C16 verification test suite
3. Execute E2E Central Loop closure test
4. Collect evidence logs + decision_ledger records
5. Generate verification report (C1-C16 compliance summary)
6. Submit evidence to Human Gate DP-5 (Loop Closure Verification)

---

**Document Version**: v1.0
**Finalized**: 2026-09-09
**Purpose**: Design/Planning Phase → Runtime Verification Methodology
**Status**: Ready for DP-4 Authorization (Deployment + Evidence Collection)
