# SB-007 Runtime Failure Audit
## Date: 2026-09-29
## Status: CONTRACT MISMATCH IDENTIFIED

---

## EXECUTIVE SUMMARY

SB-007 (IP-007 lineage implementation) has static code and runtime execution, but fails at Event Gate validation due to payload contract mismatch.

```
CODE EXISTS → RUNTIME EXECUTED → VALIDATION REJECTED → EVENT STORE NOT WRITTEN
```

---

## ACTUAL PAYLOAD STRUCTURE

### What _record_lineage_events() Creates

```json
{
  "what_type": "ai_lineage",
  "where_component": "orchestra",
  "vendor": "gpt",
  "model": "gpt-4",
  "runtime": "orchestra_dispatch",
  "source": "orchestra_runtime",
  "request_id": "test-request-id",
  "session_id": null,
  "who_actor": "orchestra_multi_dispatcher",
  "why_purpose": "Store AI provider lineage metadata",
  "when_ts": "2026-09-29T02:59:46.034045+00:00",
  "title": "AI Lineage: gpt (gpt-4)",
  "short_summary": "Provider: gpt, Model: gpt-4, Status: ok"
}
```

---

## EVENT GATE VALIDATION RULES

### File: phi_os/gate_validator.py

Validation is performed by `validate(payload)` function (governance write mode).

#### REJECT-02: who_session Format

```python
if not payload.get('who_session', '').startswith('SESSION_'):
    errors.append('REJECT-02: who_session形式不正 (SESSION_YYYYMMDD_HHMMSS)')
```

**Status in lineage payload:** `session_id: null`  
**Result:** REJECTED (missing who_session)

#### REJECT-04: how_trigger Required

```python
if not payload.get('how_trigger'):
    errors.append('REJECT-04: how_trigger必須')
```

**Status in lineage payload:** NOT PRESENT  
**Result:** REJECTED (missing how_trigger)

#### REJECT-05: where_path Required

```python
if not payload.get('where_path'):
    errors.append('REJECT-05: where_path必須')
```

**Status in lineage payload:** NOT PRESENT  
**Result:** REJECTED (missing where_path)

#### REJECT-06: what_type Validation

```python
wt = payload.get('what_type', '')
if wt not in ALLOWED_WHAT_TYPES:
    errors.append(f'REJECT-06: what_type不正 ({wt!r}) 許可値: {ALLOWED_WHAT_TYPES}')
```

**Allowed values (ALLOWED_WHAT_TYPES):**
```
'file_write', 'file_delete', 'design', 'config_change',
'git_commit', 'git_push', 'test_run', 'deployment',
'user_voice', 'handshake', 'audit', 'incident', 'todo_update',
'governance_block', 'claude_mcp'
```

**Status in lineage payload:** `what_type: "ai_lineage"`  
**Result:** REJECTED (ai_lineage NOT in ALLOWED_WHAT_TYPES)

#### REJECT-07: Replay Guarantee (before/after)

```python
b = payload.get('before_hash') or payload.get('before_state')
a2 = payload.get('after_hash') or payload.get('after_state')
if not b and not a2:
    errors.append('REJECT-07: before/afterどちらか必須(Replay不能)')
```

**Status in lineage payload:** NONE PRESENT  
**Result:** REJECTED (neither before nor after state)

---

## CONTRACT MISMATCH SUMMARY

| Requirement | Lineage Payload | Status |
|---|---|---|
| who_session (SESSION_YYYYMMDD_HHMMSS) | null | MISSING |
| how_trigger | NOT PRESENT | MISSING |
| where_path (absolute path/URL) | NOT PRESENT | MISSING |
| before_state or after_state or hashes | NOT PRESENT | MISSING |
| what_type in ALLOWED_WHAT_TYPES | "ai_lineage" | NOT ALLOWED |

---

## FAILURE CONSEQUENCE

**Lineage Status:** `RECORDING_FAILURE_UNRECORDED`

The lineage event was rejected by Event Gate validation. When _record_lineage_events() tried to record the failure itself, that failure-event was also rejected (what_type='ai_lineage_failed' also not in ALLOWED_WHAT_TYPES).

**Event Store Write:** NOT OCCURRED  
**Readback:** NOT POSSIBLE (no data in DB)

---

## CORRECTION CANDIDATES

### Option 1: Use validate_operational() for lineage events

**File:** phi_os/gate_validator.py (line 50-69)

```python
def validate_operational(payload: dict) -> list[str]:
    """Lightweight validation for operational/telemetry events"""
    errors = []
    if not payload.get('who_actor'):
        errors.append('OP-REJECT-01: who_actor必須')
    if not payload.get('what_type'):
        errors.append('OP-REJECT-02: what_type必須')
    if not payload.get('where_component'):
        errors.append('OP-REJECT-03: where_component必須')
    if not payload.get('why_purpose'):
        errors.append('OP-REJECT-04: why_purpose必須')
    return errors
```

This is designed for high-frequency operational telemetry and would accept lineage payloads.

**Required change:** Multi_dispatcher._record_lineage_events() would need to pass `event_source='lineage'` parameter and Event Gate would need to route to validate_operational() based on event_source.

### Option 2: Add ai_lineage to ALLOWED_WHAT_TYPES

**File:** phi_os/gate_schema.py (line 8-14)

```python
ALLOWED_WHAT_TYPES = [
    'file_write', 'file_delete', 'design', 'config_change',
    'git_commit', 'git_push', 'test_run', 'deployment',
    'user_voice', 'handshake', 'audit', 'incident', 'todo_update',
    'governance_block', 'claude_mcp',
    'ai_lineage',           # ADD: Orchestra AI lineage events
    'ai_lineage_failed',    # ADD: Lineage recording failures
]
```

Also provide required fields in lineage payload to match governance write validation.

**Required changes:** Multiple fields must be provided (who_session, how_trigger, where_path, before/after state).

### Option 3: Route lineage via alternative path

**File:** phi_os/event_gate.py or event_buffer.py

Create a separate event recording path for lineage events that bypasses governance write validation.

**Risk:** May violate "single event entry point" principle.

---

## AFFECTED FILES

If Option 1 or 2 is chosen:

- `phi_os/gate_validator.py` (validation rules)
- `phi_os/gate_schema.py` (allowed types)
- `gateway/multi_dispatcher.py` (_record_lineage_events() payload construction)
- `phi_os/event_gate.py` (possible routing by event_source)

---

## IP-007 BOUNDARY IMPACT

Current state: IP-007 is CLOSED / STATIC VERIFIED, but runtime contract with Event Gate was not verified.

**Changes required:** Any of the Options 1-3 above would require changes to either:
- Event Gate validation (Option 1 or 2)
- Event type schema (Option 2)
- Event routing logic (Option 1 or 3)

**Boundary decision:** Whether Event Gate Contract should be extended for lineage events, or whether lineage recording should use alternative validation rules.

---

## NEXT STEP

This audit provides:
1. Exact mismatch evidence (REJECT-02, 04, 05, 06, 07)
2. Payload structure that was attempted
3. Validation rules that rejected it
4. Correction candidates (Options 1-3)
5. Affected files
6. Boundary impact assessment

**Decision required:** Which correction approach to use and whether IP-007 boundary needs to change.

---

## STATUS

```
SB-007 RUNTIME VERIFICATION: FAILED
AUDIT RECORD: COMPLETE
CORRECTION DECISION: PENDING HG/IMPLEMENTATION REVIEW
```
