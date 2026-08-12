# Phase 2 Verification Evidence Report
## Actor_ID Binding — End-to-End Integration Verification (Read-Only)

**Date**: 2026-08-13  
**Authority**: Human Gate Decision DC_20260813_003 (Read-Only Verification)  
**Scope**: Existing code only, no new test code, no schema changes  
**Status**: VERIFICATION COMPLETE — CRITICAL GAP IDENTIFIED  

---

## Executive Summary

**Verification Outcome**: PARTIAL PASS with CRITICAL INTEGRATION FAILURE

| Layer | Status | Finding |
|-------|--------|---------|
| Unit-Level (test_actor_binding.py) | ✓ PASS | 9/9 tests pass, fail-closed verification works |
| Code Path Inspection | ✓ PASS | gateway.py correctly adds actor_id to buffer payload |
| Event Buffer Compatibility | ✓ PASS | event_buffer.py accepts actor_id field (schema-agnostic) |
| Batch Endpoint Compatibility | ✗ **FAIL** | /api/gate/event/batch silently drops actor_id (not in schema) |
| **End-to-End Integration** | ✗ **BROKEN** | actor_id propagates to batch but lost at database write |

**Critical Finding**: Actor_ID attribution is broken end-to-end. Field is added by gateway but never persisted.

---

## Verification Method

Per HG-03 authorization:
1. Re-ran existing unit tests (test_actor_binding.py)
2. Inspected existing code paths (gateway.py, auth.py, actor_binding.py)
3. Read-Only query of existing batch endpoint implementation (phi_os/event_gate.py)
4. Read-Only inspection of event buffer schema (interface/event_buffer.py)
5. Read-Only inspection of database schema (phi_os/tests/test_integrity.py)

No new test code created. No schema changes. No data mutation.

---

## Section 1: Unit-Level Verification (PASS)

### Test Execution Result

```
Total: 9 | Passed: 9 | Failed: 0

Test Cases:
✓ Normal Auth + Normal actor_id         → PASS
✓ actor_id missing (None)               → PASS
✓ actor_id mismatch (spoofing attempt)  → PASS
✓ Invalid X-MoCKA-Key                   → PASS
✓ Empty API key ('')                    → PASS
✓ Empty API key (None)                  → PASS
✓ actor_id whitespace normalization     → PASS
✓ Multiple actor isolation              → PASS
✓ Case sensitivity (CLAUDE != claude)   → PASS
```

### Evidence

- **File**: gateway/test_actor_binding.py (existing, unchanged)
- **Scope**: Component-level unit tests only
- **Coverage**: 
  - Fail-closed behavior: ✓ Verified (mismatch → False)
  - Canonical mapping: ✓ Verified (X-MoCKA-Key → actor_id)
  - Identity isolation: ✓ Verified (4 actor pairs don't cross-authenticate)

### Limitation

Unit tests verify actor_binding functions in isolation. They do NOT test:
- Flask request context
- X-MoCKA-Key header authentication flow
- Event buffer integration
- Batch endpoint acceptance
- Database persistence

**Classification**: Unit-level VERIFIED. System-level behavior UNTESTED.

---

## Section 2: Code Path Inspection (PASS)

### gateway.py POST /api/v1/event Endpoint (Lines 142-196)

```
REQUEST ARRIVES:
  X-MoCKA-Key: [authenticated header]
  body.actor.id: [payload actor_id, may differ]
        |
        v
Line 151:
  payload_actor_id = actor.get("id")
  [Extract from payload]
        |
        v
Line 154:
  verify_event_actor_id(payload_actor_id)
  [FAIL-CLOSED: abort(403) if mismatch]
        |
        v
Line 157:
  canonical_actor_id = get_request_actor_id()
  [Get from X-MoCKA-Key, NOT from payload]
        |
        v
Lines 180-192:
  get_buffer().push({
    ...
    "actor_id": canonical_actor_id,  [LINE 186]
    ...
  })
  [Add CANONICAL actor_id to buffer]
```

### Evidence

**Canonical Source Enforcement**:
- X-MoCKA-Key header extracted in auth.py get_request_actor_id() (line 134)
- Maps via actor_binding.get_authenticated_actor_id() (hardcoded mapping)
- Payload actor_id verified but never used for attribution ✓

**Fail-Closed Verification**:
- verify_event_actor_id() calls verify_actor_id_binding() (auth.py line 166)
- Returns abort(403) on mismatch ✓

**Propagation**:
- Canonical actor_id passed to get_buffer().push() (gateway.py line 186)
- Field name: "actor_id" ✓

**Classification**: Code path implementation VERIFIED as intended.

---

## Section 3: Event Buffer Compatibility (PASS)

### event_buffer.py Structure (Lines 48-54)

```python
def push(self, event: dict) -> None:
    ev = dict(event)  # Create copy
    ev.setdefault("idempotency_key", uuid.uuid4().hex)
    ev.setdefault("event_source", "buffered")
    with self._lock:
        self._queue.append(ev)  # Store as-is
```

### Evidence

**Schema Acceptance**:
- No field validation at buffer level (schema-agnostic design)
- actor_id field accepted without rejection ✓
- Field preserved through buffer queue ✓

**Propagation**:
- Event dict stored and later serialized to JSON
- JSON sent to /api/gate/event/batch (line 66) ✓

**Classification**: Event buffer accepts actor_id. Field passes through unchanged.

---

## Section 4: Batch Endpoint Compatibility (CRITICAL FAILURE)

### /api/gate/event/batch Endpoint (phi_os/event_gate.py Lines 215-251)

```
REQUEST ARRIVES at /api/gate/event/batch:
  {
    "events": [
      {
        ...existing fields...,
        "actor_id": "claude",  [from gateway buffer]
        ...
      }
    ]
  }
        |
        v
Line 234:
  for ev in events:
    result = process_buffered_event(ev, conn)
        |
        v
process_buffered_event() (line 147):
  Line 164: errors = validate_operational(ev)
  [Validates: who_actor, what_type, where_component, why_purpose]
  [Does NOT validate actor_id]
        |
        v
  Line 179: _write(ev, conn=conn)
  [THIS IS WHERE ACTOR_ID IS LOST]
```

### Database Schema Mapping (event_gate.py _write(), lines 51-75)

```python
row = {
    'event_id':        payload.get('event_id', ''),
    'when_ts':         payload.get('when_ts') or payload.get('when', ''),
    'who_actor':       payload.get('who_actor', ''),
    'what_type':       payload.get('what_type', ''),
    'where_component': payload.get('where_component', ''),
    'where_path':      payload.get('where_path', ''),
    'why_purpose':     payload.get('why_purpose', ''),
    'how_trigger':     payload.get('how_trigger', ''),
    'before_state':    payload.get('before_state', ''),
    'after_state':     payload.get('after_state', ''),
    'title':           payload.get('what_title') or payload.get('title', ''),
    'short_summary':   payload.get('description') or payload.get('short_summary', ''),
    'session_id':      payload.get('who_session') or payload.get('session_id', ''),
    '_source':         payload.get('event_source', 'live'),
    'free_note': '|'.join(filter(None, [...])),
    'channel_type':    'gate',
    'lifecycle_phase': 'in_operation',
    'risk_level':      'normal',
}
# ACTOR_ID NOT MAPPED
```

### Database Column Inventory (phi_os/tests/test_integrity.py Lines 24-57)

Events table columns:
- event_id, when_ts, who_actor, what_type, where_component, where_path
- why_purpose, how_trigger, channel_type, lifecycle_phase, risk_level
- category_ab, target_class, title, short_summary
- before_state, after_state, change_type, impact_scope, impact_result
- related_event_id, trace_id, free_note, _imported_at, _source
- ai_actor, session_id, severity, pattern_score, recurrence_flag, verified_by

**actor_id column: NOT PRESENT**

### CRITICAL FINDING

```
actor_id Propagation Path:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ gateway.py creates:       "actor_id": "claude"
✓ event_buffer.push() stores it unchanged
✓ /api/gate/event/batch receives it in payload
✓ validate_operational() ignores it (unknown field, not validated)
✗ _write() does NOT map it to any database column
✗ Database INSERT statement does not include actor_id
✗ Event record created WITHOUT actor_id field
✗ actor_id is SILENTLY DROPPED

Result: actor_id field disappears during database write.
        Attribution is broken end-to-end.
```

### Evidence

**What Happens**:
1. gateway.py line 186: `"actor_id": canonical_actor_id` added to buffer payload
2. batch endpoint line 234: `process_buffered_event(ev, conn)` called
3. event_gate.py line 179: `_write(ev, conn=conn)` called
4. _write() line 51-75: Explicit column mapping, actor_id NOT included
5. _write() line 82-87: Only explicitly mapped columns are inserted
6. Database: Event record created WITHOUT actor_id

**Silent Failure**: No error is raised. No warning is logged. Field is simply dropped.

**Database Schema**: No actor_id column exists to receive it.

**Alternative column (ai_actor)**: Already mapped to `payload.get('ai_actor')` (line 185), different source, not available for actor_id.

**Classification**: ✗ **BATCH SCHEMA COMPATIBILITY = FAIL**

---

## Section 5: End-to-End Integration Status

### Propagation Summary

| Stage | Field Present | Status | Evidence |
|-------|---|---|---|
| gateway.py add | ✓ Yes | ✓ Verified (line 186) | "actor_id": canonical_actor_id |
| event_buffer store | ✓ Yes | ✓ Verified (dict preserved) | No schema validation |
| batch endpoint receive | ✓ Yes | ✓ Inferred (JSON payload) | Events array contains field |
| batch validation | ⊗ Not checked | ✓ Verified (actor_id not in validate_operational) | No validation error |
| database write | ✗ No | ✗ Verified (not in _write mapping) | Column mapping explicit list |
| **database storage** | ✗ No | ✗ **NOT STORED** | No actor_id column exists |

### End-to-End Result

**Flow Status**: BROKEN

```
Actor_ID Binding Implementation:
  Unit Level:      ✓ PASS (fail-closed verification works)
  Code Path:       ✓ PASS (canonical source correctly isolated)
  Buffer:          ✓ PASS (accepts and preserves field)
  Batch Protocol:  ✗ FAIL (field not mapped to storage)
  Database:        ✗ FAIL (no column to store field)
  
Net Effect:       Attribution is BROKEN
                  actor_id never reaches persistent storage
                  Events recorded without actor attribution
```

---

## Section 6: Unresolved Questions

### Q1: Database Schema Modification Needed?

**Issue**: events table lacks actor_id column.

**Options**:
1. Add actor_id column to events table (requires schema migration)
2. Map actor_id to existing column (what is appropriate mapping?)
3. Abandon actor_id persistence (revert Phase 2 to unit-level only)

**Current Status**: UNKNOWN. Not within verification scope (no schema changes permitted).

### Q2: Validator Update Needed?

**Issue**: validate_operational() does not validate actor_id presence/format.

**Questions**:
- Should actor_id be required in batch events?
- Should it be validated for format/type?
- Should missing actor_id cause batch rejection or silent acceptance?

**Current Status**: UNKNOWN. Not within verification scope.

### Q3: Mapping in _write() Needed?

**Issue**: _write() function does not map actor_id from payload to database.

**Questions**:
- Should actor_id be explicitly mapped when column exists?
- Is unmapped actor_id intentional (testing phase) or oversight?

**Current Status**: UNKNOWN. Not within verification scope.

---

## Section 7: Boundary Violations Assessment

### No Code Modifications Made

- ✓ No implementation changes
- ✓ No schema changes
- ✓ No validator changes
- ✓ No batch endpoint changes
- ✓ No database changes

### No Data Mutations

- ✓ Read-Only verification only
- ✓ No test data created
- ✓ No production data touched

### No Strategic Freeze Violations

- ✓ No commits made
- ✓ No history rewrites
- ✓ No Genesis modifications

**Boundary Compliance**: ✓ VERIFIED

---

## Section 8: Remaining Verification Gaps

### Cannot Be Closed with Read-Only Access

1. **Database Schema Confirmation**: Cannot verify if actor_id column should exist without schema modification authorization
2. **Validator Rules**: Cannot determine if actor_id should be required/optional without validation logic changes
3. **Batch Behavior**: Cannot test actual batch endpoint behavior with live requests (would require data mutation)
4. **Storage Verification**: Cannot query database to confirm field disposition (would require write authorization)

### Would Require Additional Authorization

- Schema audit and modification (if needed)
- Validator update (if needed)
- Live batch endpoint testing with test data
- Database query to verify field fate

---

## Section 9: Classification

### Verification Result Mapping

**HG-01 (X-MoCKA-Key as Canonical Source)**:
- Status: ✓ VERIFIED at code level
- Finding: Correctly isolated in authentication flow, not overridable by payload
- Confidence: HIGH (code inspection + unit tests)

**HG-02 (actor_id in Event Schema)**:
- Status: ✗ PARTIALLY FAILED
- Finding: Field added to buffer, not accepted by batch endpoint, not persisted to database
- Confidence: HIGH (schema inspection + code path tracing)

**HG-03 (End-to-End Verification)**:
- Status: ✗ FAILED — CRITICAL GAP DISCOVERED
- Finding: actor_id propagates through buffer but is silently dropped at database write
- Confidence: HIGH (explicit code review of _write() function)

**HG-04 (Authorization Consolidation)**:
- Status: ✓ VERIFIED (orthogonal to actor_id binding)
- Finding: All authorization checks in auth.py (require_api_key, verify_event_actor_id)
- Confidence: MEDIUM (not directly tested)

**HG-05 (Strategic Freeze Compliance)**:
- Status: ✓ APPEARS COMPLIANT (not formally audited)
- Finding: No historical commits modified, no schema changes, no gateway changes during freeze
- Confidence: MEDIUM (not formal audit)

---

## Section 10: Required Actions Before Merge

### BLOCKING ISSUES

**Issue 1: Database Schema Gap**
- Actor_ID is created at gateway but database has no column to store it
- Events recorded without actor attribution
- **Resolution Required**: 
  - Add actor_id column to events table, OR
  - Map actor_id to existing column (if appropriate), OR
  - Remove actor_id from Phase 2 implementation (revert)

**Issue 2: Batch Endpoint Mapping Gap**
- _write() function does not map actor_id from payload
- Field silently dropped during INSERT
- **Resolution Required**:
  - Add actor_id to _write() column mapping (once schema issue resolved)

**Issue 3: Validator Gap**
- validate_operational() does not validate actor_id
- Unknown if field should be required or optional
- **Resolution Required**:
  - Define schema rules for actor_id presence/format
  - Update validator if required validation is needed

### NON-BLOCKING

- Authorization consolidation already done (auth.py) ✓
- Strategic Freeze compliance verified (no violations detected) ✓
- Canonical source isolation verified (code inspection) ✓

---

## Section 11: Summary Table

| Item | Status | Evidence | Impact |
|------|--------|----------|--------|
| Unit tests (9/9) | ✓ PASS | test_actor_binding.py re-run | Component level verified |
| Fail-closed verification | ✓ PASS | auth.py verify_event_actor_id() | Spoofing prevention works |
| Canonical source isolation | ✓ PASS | gateway.py get_request_actor_id() | Payload cannot override auth |
| Event buffer acceptance | ✓ PASS | event_buffer.py schema-agnostic | Field passes through |
| **Batch endpoint mapping** | ✗ FAIL | event_gate.py _write() missing actor_id | **actor_id NOT PERSISTED** |
| **Database schema** | ✗ FAIL | test_integrity.py events schema | **No actor_id column** |
| Boundary violations | ✓ PASS | Code inspection | No Phase 2 violations detected |

---

## Section 12: Merge Readiness Assessment

**Verification Outcome**: ✗ **NOT READY FOR MERGE**

**Reason**: Critical integration failure discovered.

**Evidence**: actor_id field added by Phase 2 implementation is silently dropped at database write. End-to-end attribution is broken.

**Path Forward**:
1. Decide on resolution (schema column, mapping, or revert)
2. Implement required changes (outside Phase 2 scope)
3. Re-run integration verification
4. Re-assess merge readiness

---

## Section 13: Next Human Authority Decision

### Decision Required

Before proceeding to merge, Human Authority must decide:

**Q1**: Should actor_id be persisted to database?
- If YES: Add actor_id column (schema change required)
- If NO: Remove actor_id from Phase 2 implementation (revert to unit-level only)

**Q2**: Is the integration gap a blocker for merge?
- If YES: Defer merge until resolution
- If NO: Accept unit-level implementation with documented gap

**Q3**: Should additional phases address end-to-end integration?
- If YES: Create Phase 3 task for schema/batch/storage integration
- If NO: Leave as current state (broken end-to-end, working at component level)

---

## Conclusion

**Phase 2 Verification Evidence**:
- Unit-level implementation: ✓ VERIFIED WORKING
- Code path isolation: ✓ VERIFIED WORKING
- End-to-end integration: ✗ **BROKEN** (actor_id silently dropped)

**Recommendation**: Do not merge without resolving database schema and batch endpoint mapping gaps.

---

**Report Generated**: 2026-08-13  
**Verification Method**: Read-Only code inspection and existing test re-execution  
**Verification Status**: COMPLETE  
**Next Step**: Human Authority decision on Q1-Q3 above

