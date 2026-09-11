# Remediation Design Specification v0.1

**Phase**: Remediation Design Specification (Post-Investigation)
**Date**: 2026-09-11
**Purpose**: Design specifications for all identified gaps, no implementation
**System State**: HOLD / FAIL-CLOSED (maintained)

---

## Overview

This specification document designs solutions for:
- CRITICAL-001: HG API Decision/Event Chain Break
- CRITICAL-002: Decision-Evidence Binding Integrity Gap
- Medium Priority: Clock Sync, Role Definitions, Authorization Boundary
- Additional: Task 3 Specification, C2-b Remediation, Dependency Graph

**NOT**: Implementation code, schema changes, runtime modifications, production deployment

---

## Part 1: Decision/Event Chain Binding Design

### Current Problem

```
mocka_decision_write execution:
┌─────────────────────────────────────────┐
│ Caller invokes mocka_decision_write()    │
└────────────┬────────────────────────────┘
             │
       ┌─────▼──────┐
       │Decision Write (ALWAYS succeeds)
       │→ JSONL file│
       └─────┬──────┘
             │
       ┌─────▼──────────────────────┐
       │Event Creation (TRY, silent fail)
       │→ POST to GATE /api/gate/event
       │→ timeout = 5s
       └─────┬──────────────────────┘
             │
             ├─ Success (201)? → event_id = returned
             └─ Failure/timeout? → event_id = null (SILENT)
                     │
                     └─ Exception caught, logged, continue
                
             │
       ┌─────▼───────────────────────────────┐
       │Return to caller
       │{"status": "ok", "event_id": event_id}
       │(caller cannot distinguish success from partial)
       └───────────────────────────────────────┘
```

**Problem**: Caller receives `"status": "ok"` regardless of whether event was created.

### Solution: Atomic Decision/Event Binding

#### Design Option A: Fail-Closed (RECOMMENDED)

```
Caller → mocka_decision_write
         │
         ├─ Validate inputs
         │  ├─ title, context, decision, rationale, impact, approved_by required
         │  └─ alternatives array required (min 1 entry)
         │
         ├─ [TX START: Decision + Event]
         │  │
         │  ├─ TRY:
         │  │  ├─ Write to Decision Ledger (JSONL)
         │  │  └─ Create Event via GATE (with retry)
         │  │
         │  ├─ ON SUCCESS:
         │  │  ├─ decision_id assigned
         │  │  ├─ event_id returned
         │  │  ├─ Both recorded
         │  │  ├─ TX COMMIT
         │  │  └─ Return {"status": "ok", "decision_id": ..., "event_id": ...}
         │  │
         │  ├─ ON GATE TIMEOUT (5s):
         │  │  ├─ Retry: exponential backoff (2s, 4s, 8s) - max 3 attempts
         │  │  ├─ If retries exhaust:
         │  │  │  ├─ TX ROLLBACK (remove decision from JSONL)
         │  │  │  ├─ Log incident: Decision rolled back due to Event creation failure
         │  │  │  └─ Return {"error": "event_creation_timeout", "status": "fail_closed"}
         │  │  │
         │  │  └─ On success: proceed to TX COMMIT
         │  │
         │  ├─ ON GATE ERROR (non-timeout):
         │  │  ├─ TX ROLLBACK (remove decision)
         │  │  ├─ Log incident
         │  │  └─ Return {"error": "gate_error", "detail": "...", "status": "fail_closed"}
         │  │
         │  └─ ON OTHER EXCEPTION:
         │     ├─ TX ROLLBACK
         │     ├─ Log incident
         │     └─ Return {"error": "internal_error", "status": "fail_closed"}
         │
         └─ [TX END]
```

#### Design Option B: Best-Effort with Monitoring

```
Caller → mocka_decision_write
         │
         ├─ Write to Decision Ledger (always succeeds)
         │  └─ Record: decision_id, timestamp, content
         │
         ├─ Create Event (best effort)
         │  ├─ POST to GATE with timeout=5s
         │  ├─ ON SUCCESS: event_id = returned
         │  ├─ ON FAILURE: event_id = null, log to binding_gap_queue
         │  └─ Continue regardless
         │
         ├─ Record binding attempt
         │  ├─ Write to binding_audit log:
         │  │  decision_id, event_id, timestamp, success/failure
         │  └─ If event_id is null → flag for monitoring
         │
         └─ Return {"status": "ok", "decision_id": ..., "event_id": ..., "binding_warning": bool}
```

#### Design Option C: Eventual Consistency

```
Caller → mocka_decision_write
         │
         ├─ Write to Decision Ledger (succeeds immediately)
         │
         ├─ Queue Event creation for async processing
         │  ├─ Add to event_creation_queue
         │  └─ Return decision_id immediately
         │
         └─ Background process:
            ├─ Polls event_creation_queue every N seconds
            ├─ Attempts Event creation with retry logic
            ├─ On success: marks binding complete
            ├─ On repeated failure: escalates to HG
            └─ Monitors for orphaned decisions
```

### RECOMMENDATION: Option A (Fail-Closed)

**Rationale**:
- Atomic semantics (all-or-nothing)
- Data integrity guaranteed
- Caller cannot be confused (no "silent" failures)
- Recoverable (no orphaned records)

---

## Part 2: Decision/Event Binding State Matrix

### Case Analysis

For each scenario, define:
- **Final State**: What is persisted after operation?
- **Event**: What event(s) are recorded?
- **Evidence**: What evidence exists?
- **Recovery**: How to recover if needed?
- **Audit Result**: What does audit trail show?

### Case 1: Decision Success + Event Success

```
Decision: WRITTEN to JSONL
Event: CREATED in Event Store
Binding: COMPLETE

Final State:
  Decision Ledger: {"decision_id": "DC_20260911_001", ...}
  Event Store: {"event_id": "E20260911_001", "tags": "decision_ledger,DC_20260911_001"}
  Binding Audit: {"decision_id": "DC_20260911_001", "event_id": "E20260911_001", "status": "BOUND"}

Evidence:
  - Decision record in JSONL
  - Event record in Event Store
  - Binding audit record
  - Caller receives: {"status": "ok", "decision_id": "DC_20260911_001", "event_id": "E20260911_001"}

Recovery: None needed

Audit: ✓ PASS - Complete chain
```

### Case 2: Decision Success + Event Timeout (with retry exhaust)

```
Decision: NOT WRITTEN (rolled back per Option A)
Event: NOT CREATED
Binding: FAILED (fail-closed)

Final State:
  Decision Ledger: (empty, rollback completed)
  Event Store: (empty)
  Incident Log: {"incident_id": "INC_20260911_001", "type": "EVENT_TIMEOUT", "decision_id": "DC_20260911_001"}

Evidence:
  - Incident record showing failure
  - Retry log: 3 attempts at 2s, 4s, 8s intervals
  - Caller receives: {"error": "event_creation_timeout", "status": "fail_closed"}

Recovery:
  1. Address root cause (GATE availability?)
  2. Retry mocka_decision_write request
  3. System automatically generates new decision_id

Audit: ✓ PASS - Fail-closed behavior verified
```

### Case 3: Decision Success + Event Partial Failure

```
Definition: Event creation returns 400/500 error (not timeout)

Decision: NOT WRITTEN (rolled back)
Event: NOT CREATED
Binding: FAILED (fail-closed)

Final State:
  Incident Log: {"type": "GATE_ERROR_4XX/5XX", "gate_status": 400, "decision_id": "DC_20260911_001"}

Recovery:
  1. Caller retries mocka_decision_write
  2. New decision_id generated (previous rolled back)

Audit: ✓ PASS - Fail-closed behavior verified
```

### Case 4: Decision Failure (validation)

```
Scenario: Caller omits required "context" parameter

Decision: NOT WRITTEN
Event: NOT CREATED
Binding: NOT ATTEMPTED

Final State:
  (No records)

Evidence:
  - Caller receives: {"error": "context is required"}

Recovery: Caller retries with valid input

Audit: ✓ PASS - Input validation works
```

### Case 5: Duplicate Request (idempotency)

```
Scenario: Same request sent twice within 1 second

Request 1:
  - Decision written: decision_id = "DC_20260911_001"
  - Event created: event_id = "E20260911_001"
  - Return: {"status": "ok", "decision_id": "DC_20260911_001", "event_id": "E20260911_001"}

Request 2 (duplicate):
  Detection: Check Decision Ledger for same decision_id within deduplication window
  
  Option A: Reject as duplicate
    - Return: {"status": "duplicate", "decision_id": "DC_20260911_001", "event_id": "E20260911_001"}
  
  Option B: Idempotent (return same result)
    - Return: {"status": "ok", "decision_id": "DC_20260911_001", "event_id": "E20260911_001"}

Final State: (single decision + event, not duplicated)

Audit: ✓ PASS - Duplicate detection or idempotency verified
```

### Case 6: Orphaned Decision (from legacy or bug)

```
Scenario: Existing decision_id with no corresponding event

Detection:
  - Cross-reference Decision Ledger with Event Store
  - Find: decision_id = "DC_20260901_001" has no event with tag "DC_20260901_001"

Classification:
  - Status: ORPHANED
  - Age: 10 days old
  - Criticality: MEDIUM

Recovery Options:
  1. Manual: Human Gate creates event for existing decision
  2. Automatic: System creates compensating event with tag "orphan_recovery"
  3. Quarantine: Decision marked as "binding_incomplete" pending HG decision

Audit: ✓ ALERT - Orphaned decision found, recovery initiated

Resolution: Decision marked "binding_recovered" once event created or HG approves quarantine
```

---

## Part 3: Orphan Detection and Recovery Design

### Orphan Detection Mechanism

**Trigger**: Daily scheduled audit (or on-demand)

```
Algorithm:
1. Load all decision_ids from Decision Ledger
2. For each decision_id:
   a. Search Event Store for event with matching tag "decision_ledger,{decision_id}"
   b. If NOT found:
      - Classify as ORPHANED
      - Record: decision_id, decision_timestamp, missing_event_id
      - Add to orphan_recovery_queue
   c. If found:
      - Verify binding hash matches
      - Mark as BOUND
```

**Output**: Orphan Registry (JSONL format, append-only)

```json
{"orphan_id": "ORP_20260911_001", "decision_id": "DC_20260901_001", "decision_ts": "2026-09-01T10:00:00Z", "discovered_at": "2026-09-11T05:00:00Z", "status": "OPEN"}
```

### Recovery Options

1. **Automatic Event Creation**
   - Create event with tag "decision_ledger,{decision_id},orphan_recovery"
   - Timestamp: current (not original decision timestamp)
   - Authority: "system_recovery"
   - Status: "binding_recovered"

2. **Human Gate Decision**
   - Escalate to HG for decision:
     - A. Create event (accept existing decision)
     - B. Quarantine decision (mark invalid)
     - C. Delete decision (rollback if possible)

3. **Quarantine**
   - Mark decision: "binding_status": "quarantined_pending_hg"
   - Prevent runtime enforcement of decision
   - Require HG resolution before use

---

## Part 4: Failure Semantics Definition

### API Response Contract

Success case:
```json
{
  "status": "ok",
  "decision_id": "DC_20260911_001",
  "event_id": "E20260911_001",
  "when": "2026-09-11T05:15:30Z"
}
```

Failure cases:
```json
// Event creation timeout
{
  "status": "fail_closed",
  "error": "event_creation_timeout",
  "decision_id": null,
  "message": "Decision rolled back after 3 retry attempts"
}

// GATE server error
{
  "status": "fail_closed",
  "error": "gate_error",
  "gate_status": 500,
  "decision_id": null,
  "message": "Event store unavailable"
}

// Validation error
{
  "status": "validation_error",
  "error": "missing_required_field",
  "field": "context",
  "decision_id": null
}

// Duplicate request
{
  "status": "duplicate",
  "decision_id": "DC_20260911_001",
  "event_id": "E20260911_001",
  "message": "Duplicate request detected and suppressed"
}
```

### Caller-Facing Behavior

| Scenario | HTTP Code | Status | Error | Decision Written? | Event Created? | Binding Complete? |
|----------|-----------|--------|-------|-------------------|-----------------|-------------------|
| Success | 201 | ok | none | YES | YES | YES |
| Timeout (retry exhaust) | 500 | fail_closed | event_creation_timeout | NO (rollback) | NO | NO |
| GATE error | 500 | fail_closed | gate_error | NO (rollback) | NO | NO |
| Validation error | 400 | validation_error | missing_field | NO | NO | NO |
| Duplicate (within window) | 200 | duplicate | none | NO (existing) | NO (existing) | YES (from before) |

---

## Summary: Decision/Event Chain Design

**Design Selected**: Option A (Fail-Closed with Retry)

**Key Attributes**:
- Atomic semantics (Decision + Event both succeed or both fail)
- Automatic retry on timeout (up to 3 attempts)
- Fail-closed on exhausted retries
- No orphaned decisions
- Caller receives clear status
- Complete audit trail
- Recovery procedure for legacy orphans

**Not Implemented Yet**: This is design only

---

**Document Version**: 0.1 (Design Specification, not Implementation)
**Status**: Ready for HG Review
**Co-Authored-By**: Claude Haiku 4.5 <noreply@anthropic.com>
