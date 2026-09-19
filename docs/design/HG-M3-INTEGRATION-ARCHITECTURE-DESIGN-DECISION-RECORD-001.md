# HG-M3-INTEGRATION-ARCHITECTURE-DESIGN-DECISION-RECORD-001

## M3 Integration Architecture — Human Gate Decisions

**Date**: 2026-09-19  
**Authority**: Human Gate  
**Status**: ARCHITECTURE DECISION COMPLETE — IMPLEMENTATION NOT AUTHORIZED  
**Cross-Consistency**: VERIFIED (all 8 decisions aligned with M3 Phase1/Phase2, no conflicts)  

---

## CANONICAL M3 INTEGRATION ARCHITECTURE INVARIANT

Every Authority Context flowing through MCP → Decision → Executor → Ledger MUST preserve these distinct dimensions:

```
Authority Context:
  ├─ Identity              (who/what is authorized)
  ├─ Provenance            (evidence/source of authorization)
  ├─ Historical State      (was authority valid at T_decision)
  ├─ Current State         (is authority valid at T_now)
  ├─ Scope                 (decision_type, resource_class)
  ├─ Temporal Validity     (valid_from, valid_until)
  └─ Revocation State      (was authority revoked, when)

CONSTRAINT: These dimensions MUST NOT be collapsed into:
  ✗ Single boolean authorization flag
  ✗ authority_id alone
  ✗ code existence
  ✗ decision generation
  ✗ historical records updated by current state
```

---

## HUMAN GATE DECISION MATRIX

### HG-1: AUTHORITY CONTEXT REPRESENTATION

**Decision**: ACCEPT — **HYBRID**

**Architectural Direction**:

Authority Context shall use dual representation:

1. **Immutable Historical Snapshot** (at decision/execution boundaries)
   - Authority state captured at T_decision
   - Embedded in Decision Ledger entry
   - Unchangeable after recording
   - Evidence of what was authorized when

2. **Current State Reference Lookup** (during validation)
   - Reference to Authority Registry
   - Resolved for revalidation
   - Shows current authority state
   - May differ from historical snapshot

**Principle**:

```
Historical Verification (immutable snapshot)
    +
Current Authorization (authoritative lookup)
```

**Rationale**: 
- Immutable snapshots preserve institutional memory
- Current lookups ensure real-time validation
- Prevents retroactive authorization alteration
- Balances historical accuracy with operational efficiency

**Critical Constraint**:
```
authority_context_id ALONE
    ≠
AUTHORIZATION

Context ID must be paired with:
  - Provenance/verification evidence
  - Current authority state verification
  - Scope matching
  - Temporal validity check
```

**Status**: ACCEPTED ✓

---

### HG-2: AUTHORITY BINDING / PROVENANCE MECHANISM

**Decision**: MODIFY — **HYBRID CONCEPTUAL MODEL**

**Architectural Direction**:

Authority Context binding shall combine:

1. **Provenance Record** (evidence of how authority was granted)
   - Decision ID that granted authority
   - Granting source (Human Gate, delegation from)
   - Grant timestamp
   - Immutable in Decision Ledger

2. **Verification Mechanism** (authority is authentic)
   - Authoritative Authority Registry lookup
   - Read-through verification of context
   - Current state validation
   - NOT cryptographic signing at this stage

3. **Distinction Between**:

```
Context Identity
    ≠
Context Authenticity
    ≠
Current Authorization

A context may be:
  - Identifiable (has context_id) ≠ Authentic (can be verified)
  - Authentic (verified once) ≠ Valid now (revalidation required)
  - Valid at T_decision ≠ Valid at T_now
```

**Explicit Non-Decision**:

The following are NOT decided at this stage and remain implementation-design decisions:
- HMAC vs JWT vs token formats
- Specific cryptographic algorithms
- Key rotation mechanisms
- Signing procedures
- Certificate management

Any future decision to add cryptographic binding requires separate authorization.

**Rationale**: 
- Conceptual provenance model is architecture-level
- Cryptographic implementation is engineering-level detail
- Historical provenance is distinct from current verification
- Multiple verification mechanisms may coexist

**Critical Constraint**:
```
Do NOT treat read-through lookup alone as historical provenance.
Historical provenance requires immutable snapshot in ledger.
Current read-through validates present state.
Both are necessary, distinct.
```

**Status**: ACCEPTED ✓ (with noted non-decisions)

---

### HG-3: AUTHORITY STATE MODEL

**Decision**: ACCEPT — **SEPARATE RUNTIME AUTHORIZATION STATE FROM PHASE1 LIFECYCLE**

**Preserved M3 Phase1 States** (canonical, unchanged):

```
Authority Lifecycle State (from HG-M3-PHASE1-AUTHORITY-OBJECT-MODEL-v1.0):
  - NONE                (no authority exists)
  - GRANTED_HUMAN       (Human Gate granted)
  - DELEGATED_ACTIVE    (delegated, not yet revoked)
  - DELEGATED_REVOKED   (delegated, then revoked)
  - UNDEFINED           (not defined)
```

**New Orthogonal Dimension** (runtime verification state):

```
Authorization Verification State (runtime, separate from lifecycle):
  - VERIFIED       (checked, valid at T_check)
  - NOT_VERIFIED   (exists but not checked)
  - INVALID        (checked, found invalid)
  - UNKNOWN        (state cannot be determined)
```

**Architectural Principle**:

```
Authority Lifecycle State
    (is this authority object defined, granted, or revoked?)
        ≠
Authorization Verification State
    (did we check it, is it valid now?)

Both dimensions must be tracked separately.
Do not collapse into single state.
```

**Non-Modification Constraint**:
- M3 Phase1 Q1-Q6 remain unchanged
- No Phase1 states are renamed or redefined
- No Phase1 lifecycle decisions are altered
- New verification state is additive only

**Status**: ACCEPTED ✓

---

### HG-4: DECISION LEDGER ARCHITECTURE

**Decision**: ACCEPT — **CONCEPTUALLY BIND AUTHORITY TO EXISTING DECISION LEDGER**

**Architectural Direction**:

Authority provenance shall be bound to the existing Decision Ledger rather than creating a separate institutional-memory system.

**Conceptual Ledger Entry** (defined, NOT schema-changed):

```
Decision Ledger Entry:

  [Decision Information]
  - decision_id, timestamp, action, alternatives, scores

  [Authority at T_decision] ← immutable snapshot
  - authority_id
  - authority_context_id
  - authority_lifecycle_state (from Phase1)
  - authority_verification_state (VERIFIED/NOT_VERIFIED/INVALID)
  - granted_by, granted_at, decision_id (granting decision)
  - valid_from, valid_until, is_indefinite
  - revocation_state (was it revoked by T_decision?)

  [Execution Information]
  - execution_attempted: boolean
  - execution_timestamp: datetime | null
  - revalidation_result (VERIFIED_OK / REVOKED / EXPIRED / UNKNOWN)
  - execution_consequence: object | null
  - execution_success: boolean | null

  [Authority at Recording Time] ← current snapshot (separate)
  - authority_state_at_now (current lifecycle state)
  - authority_verification_at_now (current verification state)
  - current_status_check_timestamp
  - revocation_history (if revoked since decision)
```

**Critical Invariant**:

```
Historical Authority State at T_decision (immutable)
        ≠
Current Authority State at T_now (mutable, queryable)

Both must be present in ledger record.
Historical snapshot never changes.
Current state field is updated if authority is revoked.
Revocation creates separate ledger entry, doesn't alter decision record.
```

**Read-Back Integrity**:

When querying historical decision:
1. Compare authority_state_at_decision against current_authority_state
2. Verify temporal validity at T_decision
3. If revoked, record separately when revocation occurred
4. Historical accuracy is preserved

**Explicit Non-Modification**:

```
NO EXISTING LEDGER SCHEMA IS MODIFIED BY THIS DECISION.
```

The conceptual design defines WHAT information must be recorded.
The actual schema, persistence mechanism, and read/write implementation require a separate implementation authorization.

**Rationale**: 
- Authority and decisions are intrinsically linked
- Single record supports historical queries
- Prevents fragmentation of institutional memory
- Preserves immutability principle

**Status**: ACCEPTED ✓ (conceptually only, no schema changes)

---

### HG-5: MCP AUTHORITY EXTRACTION

**Decision**: ACCEPT

**Canonical Principle**:

```
Every externally originated consequential request
    ↓
MUST carry explicit Authority Context
        OR
MUST carry explicit authorization evidence
    ↓
NO implicit authority inheritance permitted
```

**Required Behavior**:

```
Authority Context State          Action
─────────────────────────────────────────────
ABSENT                           → REJECT (no implicit authority)
UNKNOWN                          → REJECT (fail-closed)
INVALID                          → REJECT (invalid evidence)
VERIFIED + VALID SCOPE + ACTIVE  → continue

```

**No Exceptions at Design Stage**:

No source may silently inherit authority because:
- It is considered trusted
- It has administrative permissions
- It comes from a private network
- It has been authenticated separately

Explicit Authority Context is mandatory.

**Rationale**: 
- Fail-closed by default
- No silent authorization inheritance
- Explicit evidence trail
- Aligns with MoCKA evidence discipline

**Status**: ACCEPTED ✓

---

### HG-6: EXECUTOR REVALIDATION

**Decision**: ACCEPT

**Canonical Principle**:

Authority MUST be revalidated immediately before consequential execution.

```
Authorization at T_decision
        ≠
Authorization automatically valid at T_execution
```

**Required Behavior**:

```
Revalidation Result          Action
─────────────────────────────────────────────
VERIFIED + VALID             → execute
INVALID                      → STOP
UNKNOWN                      → STOP (fail-closed)
ABSENT                       → STOP
EXPIRED (valid_until passed) → STOP
REVOKED (between T_d and T_e)→ STOP

```

**Why Revalidation**:

Authority may change between decision and execution:
- Authority may have been revoked
- Authority may have expired
- Temporal scope may have changed
- Scope may no longer match

**Example Scenario**:

```
T_decision (1 PM):  Decision approved under ACTIVE authority
  ↓
[2 hours pass]
  ↓
T_execution (3 PM): Executor revalidates
  - Authority state has changed: now REVOKED
  - Execution is HALTED
  - Decision was valid, but execution is prevented
  - Recorded: decision approved, execution denied
```

**Explicit Non-Decision**:

Numerical timing thresholds (e.g., "revalidate if delay > X minutes") are NOT decided at this stage. They are implementation-design decisions requiring later specification.

**Rationale**: 
- Catches authority changes between decision and execution
- Fail-closed for unknown/revoked authority
- Prevents executing under revoked/expired authority
- Preserves prospective revocation principle

**Status**: ACCEPTED ✓

---

### HG-7: REVOCATION AND HISTORICAL RECORDS

**Decision**: ACCEPT

**Canonical Principle** (from M3 Phase1):

```
Revocation (at T_revoked)
    ↓
affects future authorization (T > T_revoked)
    ↓
does NOT retroactively invalidate historical execution evidence
```

**Preserved M3 Phase1 Decisions**:

- No retroactive authority (authority granted at T_authorized, cannot be used before)
- Revocation is prospective only (affects T > T_revoked)
- Valid_until=null is indefinite (authority never expires by time, only by revocation)
- Revocation doesn't rewrite history (Decision Ledger entries are immutable)

**Historical Record Treatment**:

```
T_authorized  Authority granted
    ↓
T_decision    Decision made (authority ACTIVE, recorded in ledger)
    ↓
T_execution   Execution completed (recorded as succeeded)
    ↓
T_revoked     Authority revoked by Human Gate
    ↓
T_now         Query historical ledger

Result:
  - Decision record shows: ACTIVE authority at T_decision (immutable)
  - Execution record shows: execution succeeded at T_execution (immutable)
  - Revocation record shows: authority revoked at T_revoked (separate entry)
  - Current state shows: authority is REVOKED now
  - Historical accuracy is preserved
  - Future authorization (T > T_revoked) is affected
  - Past authorization (T < T_revoked) remains valid
```

**No Retroactive Invalidation**:

```
FORBIDDEN:
  ✗ Modifying decision record when authority is revoked
  ✗ Changing execution record to "invalid" after revocation
  ✗ Retroactively marking decisions as unauthorized
  ✗ Rewriting historical authorization evidence

REQUIRED:
  ✓ Immutable historical snapshots
  ✓ Separate revocation records
  ✓ Current state queryable independently
  ✓ Historical accuracy preserved
```

**Rationale**: 
- Matches M3 Phase1 canonical decision
- Preserves institutional memory
- Supports audit trail
- Enables historical compliance verification

**Status**: ACCEPTED ✓

---

### HG-8: FAILURE AND RECOVERY

**Decision**: ACCEPT — **FAIL CLOSED**

**Canonical Principle**:

Authorization verification failure MUST NOT become authorization.

```
Verification failure
    ↓
State: UNKNOWN or NOT_VERIFIED
    ↓
MUST result in FAIL CLOSED
    ↓
NO consequential execution
```

**Required Behavior**:

```
Verification State        Action
─────────────────────────────────────────────
Verification succeeds     → authorization decision made
Verification fails        → UNKNOWN state
Timeout                   → UNKNOWN state
Registry unavailable      → UNKNOWN state
Authority state unknown   → UNKNOWN state

Then:

UNKNOWN state
    ↓
FAIL CLOSED
    ↓
Reject execution
Record failure reason
Human intervention required
```

**Explicit Non-Decisions**:

NOT decided at this stage (reserved for implementation design):
- Timeout values
- Retry logic
- Backoff strategies
- Degraded operation modes
- Recovery procedures

Any future operational retry or degraded-mode behavior MUST NOT silently convert UNKNOWN into VERIFIED.

**Critical Constraint**:

```
retry
    ≠
authorization

A request that retries 10 times is still UNKNOWN authorization.
Each retry must independently verify authority.
Accumulated retries do NOT convert UNKNOWN to VERIFIED.
```

**Rationale**: 
- Security-first approach
- No silent authorization conversion
- Explicit failure over implicit success
- Requires human/administrative action for recovery

**Status**: ACCEPTED ✓

---

## CROSS-CONSISTENCY VERIFICATION

All eight decisions verified against:

✓ **M3 Phase1 Q1-Q6**: No Phase1 decisions modified; new dimensions are additive  
✓ **M3 Phase2 sandbox**: Authority model, revocation semantics, prospective principle preserved  
✓ **MoCKA evidence discipline**: No inferred state; explicit evidence required; recorded ≠ verified  
✓ **M2 Human Gate boundary**: M3 parallel system, M2 unchanged  
✓ **No implicit authority**: Explicit context required at all boundaries  
✓ **No retroactive authority**: Historical records immutable, current state separate  
✓ **Fail-closed execution**: UNKNOWN → STOP, never UNKNOWN → proceed  
✓ **Code ≠ authorization**: Code existence never implies authorization  
✓ **Recorded ≠ verified**: Ledger entry ≠ proof of authorization  
✓ **Design ≠ implementation**: Architectural decisions made, implementation deferred  

**CROSS-CONSISTENCY RESULT: ALL CLEAR — NO CONFLICTS**

---

## PRESERVED M3 PHASE1 DECISIONS

The following M3 Phase1 decisions (Q1-Q6) remain canonical and unchanged:

**Q1: Human Gate Only**
- Only Human Gate may approve delegation
- Maintained: HG-5, HG-6 (explicit authority required)

**Q2: Direct Approval Workflow**
- No separate evaluation phase
- Maintained: HG-1, HG-4 (decision binds authority directly)

**Q3: Atomic Cascade Revocation**
- All delegations revoked together
- Maintained: HG-7 (revocation is atomic, prospective)

**Q4: Prospective Revocation & Immediate Effect**
- Revocation takes effect immediately
- Revocation does not retroactively invalidate past decisions
- Maintained: HG-7 (canonical, unchanged)

**Q5: Indefinite Authority (valid_until=null)**
- Authority with valid_until=null never expires by time
- Only revocation terminates indefinite authority
- Maintained: HG-3, HG-7 (Phase1 states preserved)

**Q6: Decision Ledger Binding**
- Authority state recorded with decision
- decision_id links authority to Human Gate decision
- Maintained: HG-4 (authority bound to Decision Ledger conceptually)

---

## ARCHITECTURAL BOUNDARIES DEFINED

### What Is Authorized (Architecture Level)

✓ HYBRID Authority Context representation (immutable snapshot + current lookup)  
✓ Conceptual provenance binding to Decision Ledger  
✓ Separate runtime authorization state from Phase1 lifecycle  
✓ Explicit authority required at MCP boundary  
✓ Revalidation before execution  
✓ Prospective revocation (no retroactive alteration)  
✓ Fail-closed on verification failure  

### What Is NOT Authorized (Reserved for Implementation Design)

✗ Cryptographic algorithms (HMAC, JWT, signing mechanism)  
✗ Key management or rotation procedures  
✗ Specific timeout/retry values  
✗ Persistent ledger schema (only conceptual structure defined)  
✗ MCP adapter contract changes  
✗ Decision model modifications  
✗ Executor implementation  
✗ Ledger write/read implementation  

### What Remains Unresolved (Implementation Design Phase)

The following require implementation-design decisions later:

1. **Cryptographic Binding Mechanism**
   - How is Authority Context authenticity verified?
   - HMAC, JWT, token, signature algorithm?
   - Key management strategy?

2. **MCP Authority Extraction**
   - Where does Authority Context come from in HTTP requests?
   - Header-based, payload-based, external mapping?
   - Per-adapter extraction logic?

3. **Persistent Ledger Schema**
   - Exact JSON/database structure?
   - Migration path for existing ledger?
   - Backwards compatibility?

4. **Executor Integration**
   - How does Executor receive decision with authority_id?
   - Intent JSON structure changes?
   - Storage mechanism for pending decisions?

5. **Operational Procedures**
   - Timeout values for verification retries?
   - Manual recovery procedures for UNKNOWN authority?
   - Alert/logging strategy for failed verifications?

---

## EXISTING SYSTEM GAP ANALYSIS (REFERENCED FROM DESIGN PHASE)

These gaps remain and are prerequisites for implementation authorization:

| Component | Current | Required | Status |
|-----------|---------|----------|--------|
| **MCP** | Parses requests | Extract authority_id/decision_type | CONTRACT CHANGE REQUIRED |
| **Decision Engine** | Generates decisions | Bind authority_context/authority_binding | CONTRACT CHANGE REQUIRED |
| **Executor** | Executes actions | Validate authority before execution | CONTRACT CHANGE REQUIRED |
| **Decision Ledger** | Stores decisions | Add authority fields (schema) | GOVERNANCE DECISION REQUIRED |
| **M2** | Unchanged | Remain unchanged | VERIFIED ✓ |

---

## IMPLEMENTATION AUTHORIZATION BOUNDARY

**CRITICAL DISTINCTION**:

```
ARCHITECTURE DECISION COMPLETE
        ≠
IMPLEMENTATION AUTHORIZED

This document authorizes architectural direction only.
No code changes are permitted under this decision.
No contracts may be modified until implementation design is separately authorized.
No deployment or runtime activation is authorized.
```

**Proceeding to Implementation Requires**:

1. Separate Human Gate authorization for:
   - MCP adapter contract changes
   - Decision model contract changes
   - Executor integration
   - Persistent Ledger schema

2. Implementation design phase defining:
   - Exact cryptographic binding mechanism
   - Authority extraction per adapter
   - Ledger persistence and migration
   - Integration points

3. Implementation phase with:
   - Code changes
   - Testing
   - Verification
   - Staged deployment

**No implementation can proceed based on this architecture decision alone.**

---

## FINAL STATUS

**ARCHITECTURE DECISION COMPLETE**

- ✓ 8 Human Gate decisions recorded
- ✓ Cross-consistency verified (no conflicts)
- ✓ M3 Phase1/Phase2 preserved
- ✓ Existing gaps identified
- ✓ Implementation boundary established
- ✓ Unresolved design items documented

**IMPLEMENTATION NOT AUTHORIZED**

- ✗ No code changes permitted
- ✗ No MCP modifications
- ✗ No Decision model changes
- ✗ No Executor integration
- ✗ No Ledger schema modifications
- ✗ No deployment
- ✗ No runtime activation

**NEXT POSSIBLE PHASE**:

`M3-INTEGRATION-IMPLEMENTATION-DESIGN-001` (not authorized by this directive)

---

**Document Created**: 2026-09-19  
**Authority**: Human Gate  
**Status**: FINAL  
**Validity**: Canonical until superseded by Human Gate decision
