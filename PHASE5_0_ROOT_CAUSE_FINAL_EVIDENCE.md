# PHASE 5.0 — ROOT CAUSE INVESTIGATION FINAL REPORT

**Date:** 2026-09-29  
**Status:** Evidence Locked / Investigation Complete / Root Cause NOT YET Definitively Confirmed  
**Authorization:** READ-ONLY INVESTIGATION

---

## Executive Summary

```
Event ID Generated:              E20260929_54766916458a0
Event Signature Created:         ✓ YES (seq=23549)
Primary Event Persisted:         ✗ NO
INSERT OR IGNORE Clause Used:    ✓ YES
Request ID Persisted:            ✗ NO
Decision ID Persisted:           ✗ NO
```

**Critical Finding:** Event successfully signed but NOT persisted to `events` table despite `process_event()` returning `{status: 'ok'}`.

---

## Evidence Chain

### 1. HEAD (cd31c94) Baseline
- `dispatch_multi_request()` contains NO event recording code
- Event recording entirely absent in HEAD version
- Only `dispatch_with_orchestra_session()` handles events via `event_buffer`

### 2. Uncommitted Changes
- `_record_lineage_events()` function added (~195 lines)
- `dispatch_multi_request()` calls `_record_lineage_events()` before returning
- Uses `from phi_os.event_gate import process_event`
- Passes `event_source='orchestra_lineage'` parameter

### 3. Lineage Payload Composition
```python
lineage_payload = {
    "what_type": "audit",                           # ✓ in ALLOWED_WHAT_TYPES
    "who_actor": "orchestra_multi_dispatcher",       # ✓ NOT NULL
    "who_role": "automation",                        # ✓ present
    "who_session": "SESSION_20260929_063219",        # ✓ SESSION_ format
    "where_component": "orchestra",                  # ✓ present
    "where_path": <dispatcher_path>,                 # ✓ present
    "why_purpose": "Record AI provider ...",         # ✓ 10+ chars
    "how_trigger": "dispatch_multi_request()",       # ✓ present
    "after_hash": "26b36b85e62d1fce",               # ✓ present (Replay guarantee)
    "when_ts": "2026-09-29T06:32:19.924397+00:00",   # ✓ NOT NULL value
    "vendor": "gpt",
    "model": "gpt-4",
    "runtime": "orchestra_dispatch",
    "source": "orchestra_runtime",
    "request_id": "f63ae36f-06eb-4663-8dc5-b43de2c94ec1",
    ...
}
```

### 4. Validation Status
- Payload passes all 8 validate() requirements:
  - ✓ REJECT-01: who_actor present
  - ✓ REJECT-02: who_session format OK
  - ✓ REJECT-03: why_purpose 10+ chars
  - ✓ REJECT-04: how_trigger present
  - ✓ REJECT-05: where_path present
  - ✓ REJECT-06: what_type='audit' (ALLOWED)
  - ✓ REJECT-07: after_hash present (Replay)
  - ✓ REJECT-08: where_component present

### 5. Event Schema Constraints
```
events table:
  event_id:         TEXT PRIMARY KEY
  when_ts:          TEXT NOT NULL  ← CRITICAL
  _source:          TEXT NOT NULL  ← CRITICAL
```

Both NOT NULL constraints satisfied in lineage_payload:
- when_ts = "2026-09-29T06:32:19.924397+00:00" ✓
- _source = 'orchestra_lineage' (via event_source param) ✓

### 6. process_event() Flow
```
process_event(lineage_payload, event_source='orchestra_lineage')
  ↓
validate(payload) → errors=[] (passes)
  ↓
payload['event_id'] = 'E20260929_54766916458a0'
payload['when_ts'] = '2026-09-29T06:32:19.924397+00:00'
payload['event_source'] = 'orchestra_lineage'
  ↓
_write(payload)
  ↓
row['_source'] = payload.get('event_source', 'live') = 'orchestra_lineage'
  ↓
INSERT OR IGNORE INTO events (cols...) VALUES (vals...)
  ↓
sign_event() → event_signatures INSERT
  ↓
conn.commit() → ✓ SUCCESS
  ↓
return {status: 'ok', event_id: 'E20260929_54766916458a0'}
```

### 7. Database State AFTER process_event()
```
events table:
  SELECT COUNT(*) WHERE event_id='E20260929_54766916458a0' → 0 rows

event_signatures table:
  SELECT COUNT(*) WHERE event_id='E20260929_54766916458a0' → 1 row (seq=23549)
```

---

## Root Cause Classification

**Current Evidence:**
- `INSERT OR IGNORE` was used
- Validation passed
- NOT NULL constraints were satisfied
- process_event() returned 'ok'
- Signature WAS created
- Primary event WAS NOT created

**Mechanism: INSERT Suppression Without Exception**

The `INSERT OR IGNORE` clause silently ignored the INSERT, causing no rows to be affected, yet no exception was raised. Possible causes:

### Hypothesis A (HIGH PROBABILITY): **Silent Constraint Violation**
- A NOT NULL constraint, UNIQUE constraint, or CHECK constraint was violated
- `INSERT OR IGNORE` suppressed the error
- Primary event was not created
- sign_event() still executed (no exception)
- Result: Signature exists, primary event doesn't

### Hypothesis B (MEDIUM PROBABILITY): **Pre-existing Event ID**
- Event ID `E20260929_54766916458a0` already existed in events table
- `INSERT OR IGNORE` ignored the duplicate
- UPDATE trace_id still executed (0 rows affected)
- Result: Same state (signature exists, event doesn't)

### Hypothesis C (LOW PROBABILITY): **SQL Syntax Error**
- Dynamic SQL construction in INSERT produced invalid syntax
- `INSERT OR IGNORE` silently failed
- No exception raised (due to OR IGNORE)

---

## Critical Discovery: SIGNED ≠ PERSISTED

**New Category of Failure:** Event framework failure where signature is recorded but primary data is not. This represents a bifurcated trust state:
- ✓ Integrity chain started (signature exists)
- ✗ Primary record absent (event doesn't exist)

---

## Evidence Boundaries

**CONFIRMED:**
- Payload structure and values
- Validation passage
- NOT NULL constraint satisfaction
- process_event() success status
- event_signatures row existence
- events table empty for this ID

**NOT YET CONFIRMED:**
- Exact SQLite error that caused INSERT suppression
- Whether constraint violation actually occurred
- INSERT row count / CHANGES() value
- Whether UPDATE trace_id executed

---

## Required for Root Cause Confirmation

1. ✓ Payload when_ts value: CONFIRMED (valid ISO string)
2. ✓ _source value: CONFIRMED (via event_source param)
3. ✗ Actual SQLite error during INSERT: NOT CONFIRMED
4. ✗ INSERT row count: NOT AVAILABLE
5. ✗ UPDATE row count: NOT AVAILABLE

---

## Classification

| Aspect | Status |
|--------|--------|
| **Event ID Exists** | ✓ YES (in event_signatures) |
| **Primary Record Exists** | ✗ NO (in events) |
| **Constraint Violation Likely** | ⚠️ PROBABLE |
| **Direct Proof** | ✗ NOT YET |

---

## Conclusion

**Root Cause Status:** High-Probability Mechanism Identified, Direct Proof Pending

**Next Step:** Requires either:
1. Direct SQLite execution logging (would modify DB/schema)
2. Exception handler instrumentation (would modify code)
3. Accept current evidence as sufficient basis for remediation hypothesis

---

**Authorization Boundary: READ-ONLY INVESTIGATION COMPLETE**
