# HG-M3-INTEGRATION-IMPLEMENTATION-DESIGN-SPECIFICATION-001

## M3 Authority Context Integration — Implementation Design Specification

**Date**: 2026-09-19  
**Purpose**: Define implementation structure IF authorization is granted  
**Status**: DESIGN SPECIFICATION ONLY (Implementation NOT AUTHORIZED)  
**Scope**: MCP → Decision → Executor → Ledger pipeline  

---

## 1. ARCHITECTURE DATA FLOW

Authority Context must propagate explicitly and unidirectionally through the pipeline. No implicit inheritance, no abbreviation, no promotion of context at intermediate stages.

```
[Incoming Request / MCP]
    │
    │ explicit Authority Context
    │ + provenance / verification evidence
    ▼
[MCP Boundary]
    │
    │ validated context
    ▼
[Decision Engine]
    │
    │ Code / Authorization / Evidence
    │ separately evaluated
    ▼
[Executor]
    │
    │ immediate pre-execution revalidation
    ▼
[Decision Ledger]
    │
    │ immutable historical record
    │ + write/read verification
    ▼
[Storage]
```

**Critical Rule**: Authority Context must NOT be:
- Silently inherited between stages
- Abbreviated to ID only
- Elevated/promoted to higher privilege
- Dropped during forwarding
- Retroactively modified

---

## 2. MCP BOUNDARY RESPONSIBILITY

### Function
Validate and accept only explicit Authority Context from incoming requests. Reject requests with absent, unknown, or invalid authorization evidence.

### Rules

✓ **Explicit Authority Required**
- Every consequential request must carry explicit Authority Context
- No implicit authority inheritance based on:
  - Source trust level
  - Administrative permissions
  - Network location
  - Prior authentication

✓ **Validation on Receipt**
- ABSENT authority → REJECT (no implicit fallback)
- UNKNOWN verification state → REJECT (fail-closed)
- INVALID evidence → REJECT
- VERIFIED + valid scope + active → continue

✓ **Context Preservation**
- Do NOT abbreviate to authority_id alone
- Preserve provenance/verification evidence
- Carry full context downstream
- No "trusted source" exceptions

✓ **Cryptographic Neutrality**
- Current stage does NOT select HMAC vs JWT vs other mechanisms
- Accept multiple verification formats if future decision allows
- Preserve evidence chain for revalidation
- Do NOT lock to single crypto algorithm

---

## 3. DECISION ENGINE RESPONSIBILITY

### Function
Bind Authority Context explicitly to Decision Result. Maintain separation between code, authorization, evidence, and decision outcome.

### Mandatory Separation

```
Code Existence (in codebase)
    ≠
Authorization State (who may execute)
    ≠
Evidence / Verification State (proof of authorization)
    ≠
Decision Result (what was chosen)
```

**Principle**: Never conflate code existence with authorization.

### State Dimensions (Kept Separate)

**Runtime Verification State**:
```
VERIFIED        (checked, valid at T_check)
NOT_VERIFIED    (exists but not checked)
INVALID         (checked, found invalid)
UNKNOWN         (cannot determine)
```

**Decision Authorization Outcome**:
```
AUTHORIZED      (explicit approval under valid authority)
DENIED          (explicit rejection)
UNKNOWN         (authorization state unknown)
```

These are **orthogonal dimensions**, not collapsed into one field.

### Rules

✓ Separate evaluation paths:
- Code-level existence check (does function exist?)
- Authorization-level state check (is authority valid?)
- Evidence-level verification (do we have proof?)
- Decision-level evaluation (what action was chosen?)

✓ Capture authority_binding snapshot at T_decision
- Immutable historical snapshot
- Embedded in DecisionResult
- Never retroactively modified

✓ No inference of authorization
- Explicit evidence required
- No "assumption" that code exists → authorization valid
- No "code is approved" as proxy for "authorization is valid"

✓ Decision outcome must include:
- selected_action
- authority_context (full, not abbreviated)
- authority_binding (immutable snapshot at T_decision)
- verification_evidence
- rationale

---

## 4. EXECUTOR RESPONSIBILITY

### Function
Revalidate Authority Context immediately before execution. Implement fail-closed behavior for any unknown/invalid state.

### Pre-Execution Revalidation Checklist

Before executing consequential action, verify:

```
✓ authority_lifecycle_state
  Valid values: GRANTED_HUMAN, DELEGATED_ACTIVE (not REVOKED, NONE, UNDEFINED)

✓ runtime_verification_state  
  Valid value: VERIFIED (only value permitting execution)

✓ scope matching
  decision_type matches authority.decision_type
  resource_class matches authority.resource_class

✓ temporal_validity
  T_execution >= valid_from
  T_execution < valid_until (if valid_until not null)

✓ revocation_state
  NOT revoked at T_execution
  If revoked between T_decision and T_execution → STOP
```

### Fail-Closed Matrix

```
State                       Action
───────────────────────────────────────
VERIFIED + valid scope
  + valid temporal
  + not revoked            → EXECUTE

UNKNOWN                     → STOP
NOT_VERIFIED                → STOP
INVALID                     → STOP
ABSENT                      → STOP
EXPIRED (valid_until passed) → STOP
REVOKED (between T_d, T_e)  → STOP
SCOPE_MISMATCH              → STOP
```

**No exceptions. No degraded-mode execution.**

### Prospective Revocation Rule

- Revocation changes future authorization (T > T_revoked)
- Historical authorization (T < T_revoked) remains valid
- Do NOT retroactively invalidate past execution records
- Record revocation as separate event

### Rules

✓ Revalidate immediately before execution (not at decision time)
✓ Use current authority state, not decision-time snapshot
✓ VERIFIED only → proceed
✓ All fail-closed states → STOP
✓ Record validation result in execution history
✓ Never skip revalidation (even if Decision was approved)

---

## 5. DECISION LEDGER RESPONSIBILITY

### Function
Record immutable historical snapshot of Authority Context at T_decision. Maintain separation between historical state and current state.

### Historical vs Current Separation

**Historical Record** (immutable, at T_decision):
```
decision_id
authority_id_at_decision
authority_lifecycle_state_at_decision
authority_verification_state_at_decision
scope_at_decision
temporal_validity_at_decision
revocation_state_at_decision
```

**Current State** (queryable, at T_recording / T_now):
```
authority_current_lifecycle_state
authority_current_verification_state
current_scope
current_temporal_validity
revocation_event_if_occurred
```

### Evidence Chain

Implementation must follow this sequence:

```
1. Record decision + authority snapshot
2. Persist to storage
3. Read back from storage
4. Verify consistency
5. Confirm write succeeded
```

Do NOT report success until read-back verification passes.

### Critical Rules

✓ Historical snapshot is immutable
  - Captured at T_decision
  - Never changed after recording
  - Revocation does not rewrite historical records

✓ Current state is queryable
  - Updated if authority state changes
  - Recorded separately if revoked after T_decision
  - Maintains accurate time-series

✓ No schema modification
  - Existing Ledger schema is NOT changed by this authorization
  - Conceptual structure defined, actual schema requires separate decision
  - Implementation design must propose schema changes for new authorization

✓ No retroactive correction
  - Past records cannot be edited
  - Corrections require new ledger entries (amendment pattern)
  - Historical accuracy preserved

---

## 6. TEMPORAL MODEL

### Five Critical Timepoints

```
T_authorized  = when Authority Object was granted/delegated
              └─ Authority.granted_at

T_decision    = when Decision was made
              └─ Authority snapshot captured (immutable)
              └─ DecisionResult.authority_binding recorded

T_execution   = when Executor attempts consequential action
              └─ Authority revalidated against current state
              └─ Execution allowed/denied recorded

T_revoked     = when Authority was revoked (if applicable)
              └─ Authority.revoked_at
              └─ Separate ledger entry

T_now         = current query time
              └─ Current authority state checked
              └─ Historical accuracy verified separately
```

### Temporal Validity Rules

**At T_decision**:
- Authority must be valid: T_authorized <= T_decision < valid_until (or null)
- Authority must be active: lifecycle_state = GRANTED_HUMAN or DELEGATED_ACTIVE
- Authority state is snapshot (immutable thereafter)

**At T_execution**:
- Authority must be revalidated: T_authorized <= T_execution < valid_until (or null)
- Authority must not be revoked between T_decision and T_execution
- If revoked: execution STOPS (prospective revocation)
- If expired: execution STOPS

**At T_now**:
- Historical record shows: authority_state_at_decision (unchanged)
- Current record shows: authority_state_at_now (may differ)
- Both records present, separate fields
- Query logic distinguishes which timepoint is relevant

### Example Scenario

```
T_authorized = 2026-09-01 (Authority granted)

T_decision = 2026-09-15 (Decision approved under ACTIVE authority)
  └─ snapshot: authority_state=ACTIVE, verification=VERIFIED
  └─ recorded immutable in ledger

T_execution = 2026-09-15 14:35 (Executor revalidates)
  └─ current state: ACTIVE, verification=VERIFIED
  └─ execution allowed

T_revoked = 2026-09-16 09:00 (Authority revoked)
  └─ separate revocation event recorded

T_now = 2026-09-19 (Query historical decision)
  └─ decision record shows: authority_state_at_decision=ACTIVE (immutable)
  └─ current state shows: authority_state_now=REVOKED
  └─ historical accuracy preserved
  └─ future authorization affected (T > T_revoked rejected)
  └─ past execution remains valid
```

---

## 7. CORE INVARIANTS

The following distinctions MUST be maintained throughout implementation:

### Seven Mandatory Separations

```
UNKNOWN ≠ VERIFIED
  (unknown state never becomes verified by process completion)

Code ≠ Authorization
  (code existence never implies authorization)

Authorization ≠ Scope
  (authority ID never implies correct resource scope)

Authorization ≠ Evidence
  (recorded authority never equals verified authority)

Recorded ≠ Verified
  (ledger entry never equals proof of authorization)

Historical State ≠ Current State
  (snapshot at T_decision never equals state at T_now)

Design ≠ Implementation
  (architectural decision never equals code change)
```

### Unviolable Principles

```
NO implicit authority inheritance
NO retroactive authorization granting
NO retroactive revocation rewrite
NO fail-open execution (UNKNOWN → STOP)
NO AI self-authorization
```

If any of these are violated during implementation, STOP and report INTEGRITY VIOLATION.

---

## 8. IMPLEMENTATION BOUNDARY

### In Scope (May be Implemented if Authorized)

✓ Authority Context propagation through MCP → Decision → Executor → Ledger  
✓ Validation at each boundary (using existing M3 Phase2 modules)  
✓ Immutable historical recording in Decision Ledger  
✓ Revalidation before execution  
✓ Prospective revocation semantics  
✓ Temporal model tracking (5 timepoints)  
✓ Integration tests for pipeline flow  
✓ Evidence verification procedures  

### Explicitly Out of Scope (Not Decided by This Spec)

✗ **Cryptographic Algorithm**
- HMAC vs JWT vs other mechanism not selected
- Key management strategy not specified
- Token format not defined
- Signing procedure not chosen
- If unavoidable during implementation → EVIDENCE GAP, stop

✗ **Token/Signature Format**
- Specific structure not defined
- Serialization format not chosen
- Header/payload format not specified
- If unavoidable → EVIDENCE GAP, stop

✗ **Production Deployment**
- Staging procedures not defined
- Rollback strategy not specified
- Canary deployment not designed
- This is sandbox scope only

✗ **M2 Behavior Modification**
- M2 requests without authority not decided
- Grace period not specified
- M2 isolation strategy not chosen
- M2 remains unchanged (implementation cannot assume M2 changes)

✗ **Retroactive Migration**
- Existing decision records not updated
- Authority history not backfilled
- Legacy data not reimplemented
- Historical records remain as-is

✗ **Authority Model Redesign**
- Phase1/Phase2 Authority Object not changed
- Lifecycle states not redefined
- New delegation mechanics not added
- Existing model remains canonical

### EVIDENCE GAP / NEW AUTHORIZATION REQUIRED

If during implementation any of the out-of-scope items become unavoidable:

```
STOP

Record:
- what became unavoidable
- why it was not foreseen
- what options remain
- which requires new authorization

Do NOT:
- proceed anyway
- make unauthorized design decision
- add workaround to avoid gap
- modify authorization without recording

Wait for:
- Human Gate review
- New authorization (if decision changes scope)
- Implementation guidance (if decision maintains scope but adds detail)
```

---

## IMPLEMENTATION SEQUENCE (if authorized)

Recommended order IF implementation were authorized:

1. **Authority Context Data Model**
   - Define AuthorityContext dataclass (~24 fields)
   - Implement in runtime/authority_model.py
   - No contract changes required

2. **MCP Boundary Integration**
   - Modify adapter contracts to accept/extract authority_context
   - Implement validate_at_mcp_boundary() call
   - Update MCPGateway.ingest() signature

3. **Decision Engine Integration**
   - Add authority_context and authority_binding to DecisionResult
   - Implement authority snapshot capture at T_decision
   - Update decision_model.py dataclass

4. **Executor Boundary Integration**
   - Modify executor intake to receive decision with authority
   - Implement revalidation before execution
   - Call validate_at_executor_boundary()

5. **Decision Ledger Extension**
   - Design schema for authority fields
   - Implement immutable snapshot storage
   - Implement read-back verification

6. **Integration Testing**
   - End-to-end pipeline tests
   - Boundary validation tests
   - Revocation scenario tests
   - Historical immutability tests

7. **Evidence Verification**
   - Verify Authority Context carries through entire pipeline
   - Verify fail-closed behavior
   - Verify immutability
   - Verify revalidation catches authority changes

8. **Integration Readiness**
   - All boundaries validated
   - All invariants maintained
   - All fail-closed states working
   - Ready for implementation authorization decision

---

## VERIFICATION CHECKLIST (Pre-Implementation)

Before starting implementation, confirm:

- [ ] Canonical Human Gate decisions (HG-1 through HG-8) finalized
- [ ] Canonical Integrity Reconciliation verified
- [ ] All 5 blocking factors have new authorization
- [ ] Cryptographic mechanism is decided (if needed)
- [ ] M2 backward compatibility strategy is decided (if needed)
- [ ] Persistent Ledger schema is authorized (if changing schema)
- [ ] Team understands core invariants and fail-closed behavior
- [ ] Testing strategy aligns with temporal model
- [ ] Evidence chain procedure is documented
- [ ] EVIDENCE GAP / NEW AUTHORIZATION procedure is understood

**Do not proceed without all items confirmed.**

---

## FINAL CRITICAL NOTES

This specification is **DESIGN ONLY**. It describes HOW implementation would be structured IF authorized.

**Implementation is currently NOT AUTHORIZED.**

Proceeding to implementation requires:
1. New Human Gate decisions on 5 blocking factors
2. Separate implementation authorization
3. Completion of this verification checklist
4. Understanding and commitment to core invariants

This specification ensures that IF authorization is granted, implementation can proceed with clear technical direction and safety boundaries.

**No code changes until all prerequisites are met.**

---

**Specification Date**: 2026-09-19  
**Status**: DESIGN REFERENCE (Implementation not authorized)  
**Authority**: Architecture Specification  
**Next Step**: Human Gate authorization decision on 5 blocking factors
