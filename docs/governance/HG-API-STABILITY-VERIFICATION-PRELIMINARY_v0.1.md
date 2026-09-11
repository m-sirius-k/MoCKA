# HG API Stability - Preliminary Verification Report

**Date**: 2026-09-11
**Status**: Investigation In Progress - CRITICAL FINDING
**Classification**: Evidence Gathering Phase 1 - Chain Break Detected

## Critical Finding: Decision-Event Binding Gap

### Code Location

**File**: `/home/user/MoCKA/mocka_mcp_server.py`  
**Function**: `mocka_decision_write` (lines 968-1030)

### Current Implementation Analysis

The HG API chain for decision writing is:

```python
# Line 995: Decision written to ledger
_append_decision(record)

# Lines 1001-1017: Try to create event
try:
    r = requests.post(GATE_URL, json=gate_payload, timeout=5)
    if r.status_code == 201:
        event_id = r.json().get("event_id")
except Exception as _companion_err:
    print(f"[MCP] mocka_decision_write companion event failed: {_companion_err}", flush=True)

# Line 1030: Return success REGARDLESS of event status
return json.dumps({"status": "ok", "decision_id": decision_id, "event_id": event_id}, ensure_ascii=False)
```

### The Problem: Broken Chain

**Expected Chain**:
```
Caller
  ↓
HG API (mocka_decision_write)
  ├─→ Decision Ledger write
  └─→ Event Store write
  ↓
Both succeed OR Both fail (atomic)
  ↓
Caller receives confirmation
```

**Actual Chain** (BROKEN):
```
Caller
  ↓
HG API (mocka_decision_write)
  ├─→ Decision Ledger write (ALWAYS succeeds)
  └─→ Event Store write attempt
       └─→ If timeout/error: silently catch and continue
  ↓
Return success EVEN IF event failed
  ↓
Caller receives success, but event not created
```

### Specific Code Issues

**Issue 1: Unconditional Decision Write** (Line 995)
- Decision is written to JSONL file regardless of subsequent event creation
- No rollback if event creation fails

**Issue 2: Silent Event Failure** (Lines 1015-1017)
- Exception caught and logged, but execution continues
- `event_id` variable remains `None` if event creation fails
- But status returned as `"ok"` regardless

**Issue 3: No Atomic Guarantees** (Line 1030)
- Returns `{"status": "ok", "decision_id": decision_id, "event_id": event_id}`
- Caller cannot distinguish between:
  - Successful decision + successful event (event_id set)
  - Successful decision + failed event (event_id is None)
- Both return `status: "ok"`

### Potential Scenarios

**Scenario 1: GATE Timeout (timeout=5s)**
```
1. mocka_decision_write called
2. Decision written to Decision Ledger (SUCCESS)
3. GATE request times out (5 second timeout)
4. Exception caught, logged as warning
5. Return {"status": "ok", "decision_id": "DC_20260911_001", "event_id": None}
6. Caller sees "ok" - thinks decision is complete
7. Actually: Decision exists, Event does NOT exist
8. BINDING GAP CREATED
```

**Scenario 2: GATE Down**
```
1. Same flow as Scenario 1
2. Event never created even after GATE comes back online
3. No automatic retry or recovery
4. Orphaned decision in ledger
```

**Scenario 3: Concurrent Requests**
```
1. Same decision_id written twice rapidly
2. Both write to Decision Ledger successfully
3. First event created, second event times out
4. Second requester sees success but event missing
5. Duplicate decision in ledger with single event
```

## Evidence Collection

### [1] Event Store Search for Orphaned Decisions

Looking for decisions in DECISION_LEDGER without corresponding events with matching decision_id tag:

**Required Check**:
```
Decision Ledger: Find all "decision_id": "DC_*"
Event Store: Find all "tags": "*DC_*"
Compare: Are there decisions without events?
```

**Status**: Requires access to full Decision Ledger - currently testing data only

### [2] Timeout Behavior Testing

**Required Test**:
```
1. Start mocka_decision_write
2. Stop GATE server
3. Measure request timeout behavior
4. Verify decision was written
5. Verify event was NOT created
```

**Status**: Not yet performed

### [3] Concurrent Request Testing

**Required Test**:
```
1. Send 10 concurrent mocka_decision_write requests
2. Check for race conditions in decision_id generation
3. Check for event creation failures
```

**Status**: Not yet performed

## Current Assessment

### What IS Proven

1. HG API endpoints exist (mocka_decision_write, mocka_decision_get, mocka_decision_list)
2. Decision Ledger is written to
3. Companion event creation is attempted
4. Timeout handling exists (5-second timeout)

### What IS NOT Proven (CRITICAL)

1. **Event Creation Reliability**: No guarantee event is created for every decision
2. **Atomic Guarantees**: No all-or-nothing semantics for decision + event
3. **Timeout Behavior**: Silent failure on timeout (may be acceptable or not depending on design intent)
4. **Error Visibility**: Caller cannot distinguish success from "partial success"
5. **Recovery**: No automatic retry or recovery if event creation fails
6. **Fail-Closed Behavior**: System does NOT fail-close on event creation failure

### Root Cause of NOT_PROVEN Status

HG API Stability is NOT_PROVEN because:

1. **Missing Specification**: No formal specification of desired behavior:
   - Should decision write fail if event creation fails?
   - Should timeout be retried?
   - Should timeout be fail-closed?

2. **Silent Failure**: Current implementation hides failures from caller
   - Caller sees `"status": "ok"` but may not know event failed
   - No indication that binding is incomplete

3. **Incomplete Chain**: Decision -> Event chain is not atomic
   - Can have decision without event
   - Can have event without decision (unlikely given direction)

## Design Requirements

### Design Question 1: Atomicity

**Option A: Atomic (All-or-Nothing)**
```
mocka_decision_write {
  TRY {
    Write decision to ledger
    Write event to store (must succeed)
  }
  ON FAILURE: {
    Rollback decision from ledger
    Return error to caller
  }
}
```

**Option B: Best-Effort (Current)**
```
mocka_decision_write {
  Write decision to ledger (must succeed)
  TRY {
    Write event to store
  }
  ON FAILURE: {
    Log error
    Return success anyway (event_id = null)
  }
}
```

**Option C: Eventual Consistency**
```
mocka_decision_write {
  Write decision to ledger (must succeed)
  Queue event creation for async processing
  Return decision_id to caller
  Monitor queue for completion
}
```

### Design Question 2: Timeout Behavior

Should 5-second timeout be:
- Retried? (how many times? exponential backoff?)
- Fail-closed? (return error to caller?)
- Escalated? (create incident?)
- Logged? (currently just prints)

### Design Question 3: Error Visibility

Should caller be able to distinguish:
- Successful decision + successful event? YES (clear case)
- Successful decision + failed event? Currently NO (returns "ok" with event_id=null)
- Failed decision? YES (returns error)

## Remediation Path

### Phase 1: Evidence Collection (Current)
- [ ] Analyze Decision Ledger for orphaned decisions
- [ ] Test GATE timeout scenarios
- [ ] Test concurrent request scenarios
- [ ] Measure current event loss rate (if any)

### Phase 2: Design Decision
- [ ] Choose atomicity model (A/B/C above)
- [ ] Choose timeout behavior
- [ ] Define error response format
- [ ] Design recovery mechanism

### Phase 3: Implementation
- [ ] Implement chosen design
- [ ] Add comprehensive error handling
- [ ] Add monitoring/alerting for failures

### Phase 4: Verification
- [ ] Test atomic guarantees
- [ ] Test timeout behavior
- [ ] Test concurrent access
- [ ] Test error visibility

## Summary

**Status**: NOT_PROVEN (Confirmed - Chain Break Detected)
**Severity**: HIGH (Silent failure can create orphaned decisions)
**Blocking**: YES - This affects Decision-Evidence Binding (Item #5)
**Next Step**: Complete Evidence Collection Phase 1, then proceed to Design Phase

**Critical Issue**: Current implementation does NOT guarantee Caller -> HG API -> Decision -> Event chain completion. Decisions can be written without events, creating binding gap.

---

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
