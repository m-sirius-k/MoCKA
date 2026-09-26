# Priority 8: Event Schema Consistency Analysis

**Date:** 2026-09-26  
**Status:** ANALYSIS COMPLETE - Non-Blocking Findings  
**Scope:** Identify all event schema patterns; document inconsistencies; recommend validation

---

## Summary

Multiple event schema patterns exist across MoCKA components. All patterns are currently compatible with the unified phi_os/event_gate entry point, which normalizes disparate formats into canonical events.db schema. **No blocking issues found.** Recommendation: Add optional schema documentation for clarity.

---

## Event Schemas Found

### Schema 1: Event Buffer Format (interface/event_buffer.py)

**Usage:** Local async buffering for high-frequency events (handshake, telemetry)

**Pattern:**
```python
{
  "idempotency_key": "auto-generated hex if not provided",
  "event_source": "buffered",  # auto-set
  ... rest of event fields per source
}
```

**Route:** `push()` → EventBuffer → `/api/gate/event/batch` → event_gate.process_buffered_event()

**Validation:** validate_operational() - lightweight operational telemetry validation

---

### Schema 2: PHI-OS Event Gate Format (phi_os/event_gate.py)

**Usage:** Single canonical entry point for ALL events

**Mandatory Fields:**
- `event_id` - Time-ordered with random suffix (E{YYYYMMDD}_{micros:09d}{random:4hex})
- `when_ts` - ISO8601 timestamp
- `who_actor` - Actor identifier
- `what_type` - Event classification
- `where_component` - Component source
- `where_path` - Path context
- `why_purpose` - Purpose/reason
- `how_trigger` - Trigger mechanism
- `before_state` - Pre-change state
- `after_state` - Post-change state
- `channel_type` - Fixed to 'gate' at normalization
- `event_source` - Source classification (live, buffered, direct_allowed:{channel})

**Route:** 
- `/api/gate/event` (governance write - strict validate)
- `/api/gate/event/batch` (operational telemetry - validate_operational)
- `/api/gate/event/extension` (Chrome extension write - validate_operational)

**Validation:** validate() OR validate_operational() depending on source

**Normalization:** _write() maps flexible input fields to canonical DB columns:
- `title`/`what_title` → `title` (canonical)
- `description`/`short_summary` → `short_summary` (canonical)
- `session_id`/`who_session` → `session_id` (canonical)

---

### Schema 3: JARVIS Engine Output (runtime/jarvis/core/engine.py)

**Usage:** Decision evaluation result

**Pattern:**
```python
{
  "decision_id": "string",
  "status": "WAITING|APPROVED|REJECTED",
  "authority": "human"
}
```

**Route:** `/api/jarvis/evaluate` → (currently not recorded as event)

**Issue:** No automatic event recording. Caller must manually record if needed.

---

### Schema 4: HAB Dispatch Result (gateway/hab_bridge.py:dispatch_to_ai)

**Usage:** AI Socket routing response

**Pattern:**
```python
{
  "status": "routed|error",
  "socket_id": "socket_{type}",
  "trace_id": "TR_{YYYYMMDD}_{nnnnn}",
  "adapter": "gpt|gemini|copilot|perplexity|genspark",
  "request_payload": {...},
  "error": "string (if status=error)"
}
```

**Route:** `/api/v1/hab/dispatch` endpoint in gateway.py

**Issue:** Response is not automatically recorded to event_gate. Caller must manually record if needed.

---

### Schema 5: HAB AI Response Format (gateway/hab_bridge.py:receive_from_ai)

**Usage:** AI provider response preparation for Event Gate

**Pattern:**
```python
{
  "event_id": "E_{YYYYMMDD}_{nnnnn}",
  "source_socket": "socket_{type}",
  "socket_type": "gpt|gemini|copilot|perplexity|genspark",
  "received_at": "ISO8601",
  "payload": {...},  # vendor-specific AI response
  "ready_for_gate": true
}
```

**Route:** Can be passed to HAB.route_to_phi_os() → Event Buffer → `/api/gate/event/batch`

**Status:** Compatible with event_gate, ready for batch ingestion

---

### Schema 6: Relay Kernel Contract (relay/relay_kernel.py:ingest)

**Usage:** State projection from event history

**Input:**
```python
event: dict  # Any event dict; Relay's reduce() extracts what it needs
```

**Output:**
```python
{
  "state": {...},           # Current projected state
  "policy": {...},          # PolicyEngine evaluation result
  "action": {...},          # ActionRouter decision (QUEUE_EVENT|DEFER|DISCARD)
}
```

**Route:** Non-blocking, tries to ingest all events from event_gate:process_buffered_event()

**Compatibility:** Relay.reduce() is schema-agnostic; extracts field names from event dynamically

---

## Consistency Analysis

### Compatible Patterns (No Conflicts)

✓ Event Buffer → event_gate normalization: Works (adds idempotency_key, event_source)
✓ HAB AI Response → Event Buffer: Works (event_id pre-generated, ready_for_gate flag)
✓ Relay ingestion: Works (schema-agnostic reduce engine)
✓ ID generation: All use datetime-based prefix; format variations are expected

### Documentation Gaps (Non-Blocking)

- JARVIS evaluation results (Schema 3) not automatically persisted as events
  * **Mitigation:** Caller responsible; pattern is optional
  
- HAB dispatch results (Schema 4) not automatically persisted as events
  * **Mitigation:** Caller responsible; pattern is optional
  
- No canonical EVENT_SCHEMA document in docs/mocka3/
  * **Mitigation:** Can document separately (non-critical)

### Validation Coverage

| Schema | Validator | Status |
|--------|-----------|--------|
| Event Buffer | implicit (pushed as-is) | OK |
| Event Gate (governance) | validate() | OK |
| Event Gate (operational) | validate_operational() | OK |
| JARVIS output | none (output-only) | OK (no validation needed) |
| HAB dispatch | none (output-only) | OK (no validation needed) |
| HAB AI response | implicit (ready_for_gate flag) | OK |
| Relay input | none (schema-agnostic) | OK |

---

## Findings

**No schema blocking issues found.** The system handles multiple event patterns gracefully:

1. **Unified entry point:** Event Gate normalizes all inputs to canonical schema
2. **Optional enrichment:** JARVIS/HAB results are optional, not mandatory in main flow
3. **Flexible fields:** Gate accepts both strict and flexible field names (title/what_title, etc.)
4. **Agnostic consumers:** Relay's reduce() doesn't require schema conformance

---

## Recommendations (Non-Critical)

### Option A: Document As-Is (Minimal Effort)

Create `docs/mocka3/EVENT_SCHEMA_PATTERNS.md` listing all 6 patterns with examples.

```
- Pattern 1: Event Buffer (idempotency_key, event_source)
- Pattern 2: Event Gate Canonical (all 13 W5H1 fields)
- Pattern 3: JARVIS Output (decision_id, status, authority)
- Pattern 4: HAB Dispatch (status, trace_id, adapter)
- Pattern 5: HAB AI Response (event_id, socket_type, payload, ready_for_gate)
- Pattern 6: Relay Input (flexible, schema-agnostic)
```

**Effort:** ~2 hours  
**Benefit:** Clarity for future integrators  
**Blocker Status:** None

### Option B: Add Schema Validation Middleware (Higher Effort)

Create optional schema validator in phi_os/schema_validator.py to warn about non-canonical patterns before sending to Event Gate.

```python
def validate_schema(event, strict=False):
    # Warn if missing W5H1 fields (non-blocking)
    # Allow flexible field name variants
    # Log schema mismatches for audit
```

**Effort:** ~4 hours  
**Benefit:** Early detection of schema drift  
**Blocker Status:** None (optional middleware)

---

## Action Items

- [ ] Document final decision on schema documentation approach
- [ ] If Option A chosen: Create docs/mocka3/EVENT_SCHEMA_PATTERNS.md
- [ ] Update WEB_STAGE3_IMPLEMENTATION_REPORT.md with findings
- [ ] No code changes required (all patterns already compatible)

---

## Next Priority

**Priority 10:** Dead-end/duplicate path audit (code inspection)

---

**Status:** ✓ ANALYSIS COMPLETE - Ready to move to Priority 10
