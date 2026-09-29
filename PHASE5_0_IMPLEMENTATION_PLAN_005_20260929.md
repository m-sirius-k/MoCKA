# IP-005: Orchestra → HAB
## Implementation Plan (NOT YET IMPLEMENTED)

**Date:** 2026-09-29  
**HG Decision:** A-1 APPROVED  
**Scope Binding:** APPROVED  
**Status:** PLANNING PHASE (no code changes yet)  
**Sequence:** Second implementation (after IP-007)

---

## TARGET

Establish direct interface between Orchestra execution requests and Human Authority Boundary (HAB) decision layer, ensuring all Orchestra-initiated execution requires explicit HAB authorization before proceeding to AI runtime.

---

## EXISTING COMPONENTS (Read-Only)

### Authorization Layer
- **File:** `C:\Users\sirok\MoCKA_runtime_c9effe8\phi_os\context\execution_context.py`
  - Function: `check()` — Execution Gate policy verification
  - Current use: Authorization boundary validation
  - **Action:** READ ONLY (query existing authorization state)

### Orchestra Components
- **File:** `C:\Users\sirok\MoCKA_runtime_c9effe8\caliber\orchestra\` (Orchestra dispatcher)
  - Current use: Request validation, provider dispatch
  - **Action:** READ ONLY (integrate HAB check after request validation)

### Event Store
- **File:** `C:\Users\sirok\MoCKA_runtime_c9effe8\phi_os\event_gate.py`
  - Current use: Event persistence
  - **Action:** READ ONLY (HAB decisions logged via event_gate)

### HAB Components (Existing)
- **File:** `C:\Users\sirok\MoCKA_runtime_c9effe8\phi_os\hab\` (HAB layer)
  - Current use: Decision authority, policy validation
  - **Action:** READ ONLY (query existing HAB policies)

---

## NEW COMPONENTS (To Be Created)

**REVISION NOTE:** Existing execution_context.py (phi_os/context/) provides GateResult/GateCheck pattern. HAB authorization follows same pattern. Minimal implementation required.

### 1. SINGLE AUTH MODULE: authorization.py
**Purpose:** HAB authorization decision engine + Orchestra integration

**Location:** `C:\Users\sirok\MoCKA_runtime_c9effe8\phi_os\authorization.py`

**Responsibility:**
- Accept Orchestra request with: request_id, provider, model, operation, scope, who_actor, session_id
- Check against runtime_scope (SINGLE SOURCE OF TRUTH per governance)
- Generate HAB decision: APPROVED / REJECTED / DEFERRED
- Sign decision with trace_id
- Log decision to Event Store via event_gate
- Return decision token to Orchestra

**Key Design:**
- Runtime_scope is sole authorization source (human-approved, immutable)
- No new authorization model; use existing HAB authority structure
- Decision outcome is IMMUTABLE once written to Event Store
- Fail-closed: any error → REJECTED (never implicit approval)

**Input Contract:**
```
orchestra_request = {
  "request_id": str,           # Orchestra request ID
  "provider": str,             # gpt / claude / gemini
  "model": str,                # model identifier
  "operation": str,            # execute / retrieve / analyze
  "scope": str,                # affected resource scope
  "who_actor": str,            # requesting user/session
  "session_id": str,           # Orchestra session
  "when_ts": str               # ISO8601
}
```

**Output Contract:**
```
authorization_result = {
  "request_id": str,           # echo from request
  "approval_status": str,      # APPROVED / REJECTED / DEFERRED
  "authority": "Human Gate",   # immutable
  "event_id": str,             # Event Store record
  "trace_id": str,             # signature chain
  "timestamp": str             # ISO8601
}
```

---

## CALL PATH (REVISED — SINGLE COMPONENT)

```
Orchestra Dispatcher (after request validation)
    ↓
authorization.check_hab_approval(orchestra_request)
    ↓
FETCH: runtime_scope (SINGLE SOURCE OF TRUTH, already approved by HG)
    ↓
VALIDATE: request_id/provider/model/operation against runtime_scope
    ↓
IF scope_match AND runtime_scope includes this operation:
  approval_status = APPROVED
ELSE:
  approval_status = REJECTED
    ↓
CREATE: hab_event = {
  what_type: 'hab_authorization',
  request_id: from_request,
  approval_status: computed,
  authority: 'Human Gate',
  where_component: 'authorization'
}
    ↓
event_gate.process_event(hab_event)
    ↓
_write() → INSERT INTO events
    ↓
integrity.sign_event() → UPDATE trace_id/related_event_id
    ↓
COMMIT → Return event_id
    ↓
IF approval_status == APPROVED:
  Return SUCCESS to Orchestra
ELSE:
  Return DENIED to Orchestra → execution blocked
```

**KEY:** Runtime_scope is immutable HG-approved authorization source. No cache needed, no re-auth logic. Pure policy lookup + Event Store log.

---

## INPUT / OUTPUT

### Input
- Orchestra execution request with: provider, model, operation, scope, actor, session_id
- Source: Orchestra dispatcher after validation

### Output
- HAB decision: APPROVED / REJECTED / DEFERRED
- Signed authorization token (proof of decision)
- Event Store record of decision + rationale
- Return control to Orchestra with decision

---

## AUTHORIZATION / SCOPE

**Authorization:**
- A-1 (Implement Orchestra → HAB) — HG APPROVED
- Uses existing HAB authority model
- No new authorization scheme introduced

**Scope:**
- Orchestra execution requests only (not generic API calls)
- Authorization decision only (not execution itself)
- Immutable decision record (signature enforced)
- Non-blocking to Orchestra (decision made synchronously)

---

## PERSISTENCE

**Target:** `data/mocka_events.db` → events table

**Guarantee:**
- HAB authorization decisions logged as events
- Signature chain: HAB decision → Event Store → trace_id
- Immutable: INSERT OR IGNORE prevents duplication
- Queryable: SELECT * FROM events WHERE what_type='hab_authorization'

---

## ERROR / FAIL-CLOSED BEHAVIOR

**Error Conditions:**
1. Orchestra request validation fails → REJECT before HAB, log error
2. HAB policy engine unavailable → DEFER (timeout), log error, do not proceed
3. HAB signature verification fails → REJECT, escalate to HG, do not proceed
4. Event Store write fails → ROLLBACK, log error, return denial to Orchestra
5. Token expiration (TTL exceeded) → REJECT execution, require re-authorization

**Fail-Closed:** Any error → Orchestra request DENIED (no implicit approval)

---

## FORBIDDEN CHANGES

- DO NOT create separate hab_bridge.py + auth_interface.py (use single authorization.py)
- DO NOT cache authorization decisions (query runtime_scope each time)
- DO NOT implement TTL-based token validity (rely on immutable Event Store record)
- DO NOT modify Orchestra request structure
- DO NOT implement pre-approved shortcuts or bypass logic
- DO NOT modify PHI-OS core runtime startup sequence
- DO NOT introduce new authorization scheme (use HG-approved runtime_scope)
- DO NOT make authorization optional (fail-closed)

---

## RUNTIME EVIDENCE

**Pass Condition:** All of the following confirmed:

1. **HAB Authorization Event Created**
   - Query: `SELECT * FROM events WHERE what_type='hab_authorization' AND request_id='{test_request_id}'`
   - Expected: 1 row returned with approval_status='APPROVED' or 'REJECTED'

2. **Signature Token Valid**
   - Extract signature_token from event
   - Verify: auth_interface.verify_token(signature_token)
   - Expected: Token validates with HAB's public key

3. **Orchestra Request Blocked Without Approval**
   - Test: Submit Orchestra request directly (bypass HAB) → MUST FAIL
   - Expected: Authorization check fails, denial event logged

4. **TTL Enforcement Active**
   - Create authorization with TTL=60 seconds
   - Wait 65 seconds
   - Attempt execution with expired token → MUST FAIL
   - Expected: Re-authorization required

5. **Failure Path Working**
   - Submit request HAB rejects → denial event logged
   - Orchestra receives rejection → execution blocked
   - Query events for denial: decision_id matches request_id

---

## READBACK

**Pass Condition:** Given request_id, complete authorization history reconstructible:

```sql
SELECT 
  event_id,
  request_id,
  what_type,
  approval_status,
  authority,
  signature_token,
  when_ts,
  trace_id
FROM events 
WHERE request_id='{target_request_id}' 
  AND what_type IN ('hab_authorization', 'hab_denial')
ORDER BY when_ts ASC;
```

**Validation:**
- One authorization decision per request_id
- Signature token present and non-null
- Approval status in {APPROVED, REJECTED, DEFERRED}
- Trace chain intact (trace_id → related_event_id)
- Temporal ordering correct

---

## ROLLBACK / FAILURE CONDITION

**Rollback Condition:** If authorization readback fails validation:

1. Identify failed request_id
2. Mark for manual review
3. Create incident record
4. Halt Orchestra execution until reviewed
5. Manual inspection: verify signature chain integrity

**Non-Recoverable Failure:**
- If signature verification fails → escalate to HG
- If HAB policy engine corrupted → escalate to HG
- If authorization token expired (TTL logic broken) → review cache implementation

---

## DEPENDENCIES (REVISED)

**UPSTREAM DEPENDENCIES:** NONE (INDEPENDENT)
- IP-005 does not require IP-007 or IP-009
- Loads runtime_scope directly from governance layer (HG-approved)
- Does not depend on any other implementation plan

**DOWNSTREAM CONSUMERS:**
- IP-009 will sync authorization decision events (soft dependency for completeness)

**PARALLEL IMPLEMENTATION:** IP-005 can run in parallel with IP-007
- No data flow between them at this stage
- Both feed Event Store independently

**RECOMMENDATION:** Implement IP-007 and IP-005 in parallel; IP-009 requires both

---

## SCOPE VERIFICATION

**HG Approved Scope Check:**
- Target: Implement Orchestra → HAB ✓
- Input: Orchestra request ✓
- Output: HAB authorization decision ✓
- Persistence: Event Store ✓
- Forbidden changes: PHI-OS core untouched ✓
- Scope creep risk: NONE (authorization-only, no execution change)

**Result: WITHIN APPROVED SCOPE**

---

## NEXT PHASE (REVISED — MINIMAL SCOPE)

Upon Implementation Plan Review APPROVAL:
1. Create authorization.py (single module)
2. Load runtime_scope from governance layer (HG-approved)
3. Implement scope_match validation logic
4. Integration point: Orchestra dispatcher → authorization.check_hab_approval()
5. Call event_gate.process_event() for all decisions (APPROVED/REJECTED/DEFERRED)
6. Integration testing: Orchestra request → authorization check → Event Store
7. Failure path testing (rejections)
8. Runtime evidence collection (readback validates approval_status)
9. Institutional memory recording

**NO BRIDGE/INTERFACE SPLIT.** Single authorization module, direct integration with event_gate.

**Current Status:** PLAN REVISED / READY FOR FINAL REVIEW
