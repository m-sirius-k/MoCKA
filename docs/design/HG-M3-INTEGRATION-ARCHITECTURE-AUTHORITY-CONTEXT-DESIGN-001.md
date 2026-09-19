# HG-M3-INTEGRATION-ARCHITECTURE-AUTHORITY-CONTEXT-DESIGN-001

## M3 Authority Context Carriage Architecture Design

**Date**: 2026-09-19  
**Phase**: Design Only (No Implementation Authorized)  
**Scope**: Conceptual architecture for Authority Context flow across MCP → Decision → Executor → Decision Ledger  
**Constraint**: No code changes, no contract modifications, no production deployment  

---

## STEP 1: AUTHORITY CONTEXT MODEL

### Conceptual Authority Context (Minimum Fields)

An **Authority Context** is a self-contained evidence bundle that flows with a decision through the MoCKA pipeline. It is distinct from the Authority Object model defined in M3 Phase1.

#### Required Fields

```
Authority Context:
  - authority_context_id       : string (unique identifier for this context instance)
  - authority_id               : string (reference to underlying Authority Object)
  - decision_type              : string (what kind of decision this context authorizes)
  - resource_class             : string (what resources this context applies to)
  - authority_state_at_entry   : enum (ACTIVE, REVOKED, EXPIRED, UNKNOWN)
  - temporal_validity          : object
    - valid_from               : datetime
    - valid_until              : datetime | null
    - is_indefinite            : boolean (valid_until == null)
  - provenance                 : object
    - granted_by               : string (Human Gate or delegating authority)
    - granted_at               : datetime
    - decision_id              : string (Human Gate decision that created this authority)
  - revocation_state           : object | null
    - revoked_at               : datetime | null
    - revoked_by               : string | null
    - revocation_decision_id    : string | null
  - verification_status        : enum (VERIFIED, NOT_VERIFIED, INVALID, UNKNOWN)
  - verification_timestamp     : datetime (when this context was last verified)
  - verification_boundary      : enum (MCP, EXECUTOR, NONE)
```

#### Critical Distinctions

```
Authority Context ID (unique per instance)
        ≠
Authority ID (underlying Authority Object)
        ≠
Authority State at Verification Time (was valid when checked)
        ≠
Authority State at T_now (may have changed)
        ≠
Historical Authority State at T_decision (what was true when decision was made)

Authority has been GRANTED
        ≠
Authority has been VERIFIED (checked, still valid)
        ≠
Authority is RECORDED (in Decision Ledger)
        ≠
Authority AUTHORIZED EXECUTION (both verified and in scope)
```

### Implicit Authority Prevention

**Principle**: No field in Authority Context may be inferred, assumed, or defaulted.

- If authority_id is absent → REJECT (do not assume implicit authority)
- If verification_status is UNKNOWN → REJECT (do not assume verified)
- If decision_type is absent → REJECT (do not assume scope)
- If authority_state_at_entry is UNKNOWN → REJECT (do not assume valid)

---

## STEP 2: MCP BOUNDARY CONTRACT

### MCP Boundary Responsibilities

The MCP Boundary is the **first validation point**. It receives external requests and must determine whether to accept them for further processing.

#### Input: Request + Authority Context

```
MCP Request:
  - source              : string (github, http, filesystem, browser)
  - payload             : object (source-specific data)
  - authority_context   : Authority Context | null
```

#### Processing Model

```
MCP.ingest(source, payload, authority_context):
  1. Parse request from source adapter
  2. Validate Authority Context presence and structure
  3. Verify authorization for the requested action
  4. Record MCP boundary decision
  5. Pass to Decision Engine or REJECT
```

### MCP Boundary Authorization Rules

#### Case 1: Authority Context VALID

```
Condition:
  - authority_context is present
  - verification_status == VERIFIED
  - authority_state_at_entry == ACTIVE
  - decision_type matches requested action type
  - resource_class matches requested resource
  - temporal_validity.is_within_scope(now) == true

Action:
  - ACCEPT request
  - Pass Authority Context to Decision Engine
  - Record: {request_id, authority_id, action_type, ACCEPTED}
```

#### Case 2: Authority Context INVALID

```
Conditions (any of):
  - verification_status == INVALID
  - authority_state_at_entry == REVOKED
  - authority_state_at_entry == EXPIRED
  - decision_type does not match requested action
  - resource_class does not match requested resource
  - temporal_validity.is_within_scope(now) == false

Action:
  - REJECT request
  - Record: {request_id, authority_id, reason: "INVALID_CONTEXT", REJECTED}
  - Return error to source
  - Do NOT pass to Decision Engine
```

#### Case 3: Authority Context UNKNOWN

```
Conditions (any of):
  - authority_context is null
  - authority_id is missing
  - verification_status == UNKNOWN
  - verification_status == NOT_VERIFIED
  - authority_state_at_entry == UNKNOWN
  - Verification timestamp is stale (older than X minutes)

Action:
  - REJECT request (fail-closed)
  - Record: {request_id, reason: "UNKNOWN_AUTHORITY", REJECTED}
  - Return error to source
  - Do NOT pass to Decision Engine
  - Do NOT attempt re-verification at MCP boundary
```

#### Case 4: Authority Context ABSENT

```
Condition:
  - authority_context is null
  - No implicit authority can be assumed from request source

Action:
  - REJECT request (fail-closed)
  - Record: {request_id, reason: "NO_AUTHORITY", REJECTED}
  - Return error to source
```

### MCP Boundary State Recording

After MCP validation, record:

```
MCP Validation Record:
  - validation_id        : string (unique)
  - timestamp            : datetime
  - source               : string
  - request_id           : string
  - authority_id         : string
  - decision_type        : string
  - resource_class       : string
  - action               : enum (ACCEPTED, REJECTED)
  - reason               : string (if rejected)
  - verification_status  : enum
  - authority_state      : enum
```

### Contract Authenticity Verification

**Principle**: Authority Context must be cryptographically bound to the Authority Object it references.

```
Required (Design Phase):
  - Define how Authority Context authenticity is verified
  - Define cryptographic binding mechanism (signature, hash, token, etc.)
  - Define verification failure response (INVALID vs UNKNOWN)
  - Define key rotation/refresh strategy

Potential Mechanisms (not authorized yet):
  - HMAC signature over authority_id + provenance + state
  - Delegation chain signature
  - Time-bound token with embedded authority claims
  - Read-through from Authority Registry with timestamp verification
```

---

## STEP 3: DECISION ENGINE CONTRACT

### Decision Engine Responsibilities

The Decision Engine receives an MCP-validated request and generates a **Decision** that encodes what action to take, based on the decision logic (priority, risk, etc.).

#### Input: MCP Result + Authority Context

```
Decision Engine Input:
  - mcp_validation     : MCP Validation Record (ACCEPTED status only)
  - authority_context  : Authority Context (passed from MCP)
  - semantic_result    : Semantic analysis (intent, confidence, candidates)
  - decision_profile   : Decision registry entry for intent
```

#### Output: Decision Result with Authority Binding

```
Decision Result:
  - decision_id        : string (unique)
  - timestamp          : datetime (T_decision)
  - selected_action    : string (recommended action)
  - alternatives       : list (alternative actions)
  - priority_score     : float
  - risk_score         : float
  - confidence         : float
  - authority_context  : Authority Context (passed through)
  - authority_binding  : object
    - authority_id_at_decision  : string (authority that enabled this decision)
    - verified_scope            : object (decision_type, resource_class)
    - verified_temporal         : object (valid_from, valid_until, is_indefinite)
    - authority_state_snapshot  : enum (what we knew at decision time)
  - required_governance_check   : boolean (always true for M3)
  - risk_factors       : list
```

### Critical State Separations

The Decision Engine MUST NOT collapse these distinct states:

```
Code Exists              ← decision_profile.selected_action exists in registry
      ≠
Authorization Exists    ← authority_context.authority_id is valid and in scope
      ≠
Evidence State          ← authority_context.verification_status == VERIFIED
      ≠
Decision State          ← DecisionResult has been generated

A decision can be GENERATED even if:
  - Multiple alternative actions exist (code exists)
  - Authority is QUESTIONABLE (evidence uncertain)
  - Risk is HIGH (governance oversight required)

A decision CANNOT be generated if:
  - Authority is INVALID (rejected at MCP)
  - Authority Context is ABSENT (rejected at MCP)
```

### Evidence State Vocabulary

Every Decision Result MUST include:

```
Authority Evidence State (at decision time):
  - VERIFIED       : Authority was checked, found valid, scope matched
  - NOT_VERIFIED   : Authority exists but was not checked (SHOULD NOT OCCUR past MCP)
  - INVALID        : Authority was checked, found invalid (SHOULD NOT OCCUR past MCP)
  - UNKNOWN        : Authority state cannot be determined (SHOULD NOT OCCUR past MCP)
```

### Preventing Evidence Collapse

```
FORBIDDEN:
  - Treating "code exists" as "authorization exists"
  - Treating "decision generated" as "authority verified"
  - Treating "recorded in history" as "verified"

REQUIRED:
  - Explicit authority_binding in DecisionResult
  - Separate authority_context from decision payload
  - Clear evidence_state tracking
  - Distinction between mcp_validation record and decision_result
```

### Authority State Snapshot

At decision time, capture **what we know about authority**:

```
Authority State Snapshot at T_decision:
  - authority_id                : string
  - authority_state_at_t_decision : enum (ACTIVE, REVOKED, EXPIRED)
  - valid_until                 : datetime | null
  - is_indefinite               : boolean (valid_until == null)
  - temporal_valid_at_t_decision : boolean (is_within_scope(T_decision))
  - revocation_state            : object | null (was authority revoked by T_decision?)
  - recorded_by_decision_id     : string (which decision granted this authority)
```

This snapshot is **immutable** in the Decision Ledger. It represents "what was true when the decision was made."

---

## STEP 4: EXECUTOR CONTRACT

### Executor Responsibilities

The Executor receives an approved Decision and carries out the specified action. Before execution, the Executor MUST revalidate the authority.

#### Input: Approved Decision + Authority Context

```
Executor Input:
  - decision          : Decision Result (approved by Governance Layer)
  - authority_context : Authority Context (from Decision)
  - T_execution       : datetime (when execution actually happens)
```

#### Pre-Execution Validation

```
Executor.execute(decision, authority_context, T_execution):
  1. Revalidate authority_context
  2. Check current authority state (may have changed since T_decision)
  3. Verify temporal validity at T_execution
  4. Verify scope (decision_type, resource_class)
  5. Check revocation state
  6. If ALL checks pass: execute action
  7. If ANY check fails: REJECT and record reason
```

### Revalidation Requirements

**Principle**: Authorization verified at Decision time ≠ Authorization automatically valid at Execution time

```
Executor MUST revalidate:
  - authority_state_at_execution (compare against authority_state_at_t_decision)
  - temporal_validity at T_execution (not T_decision)
  - revocation_state (authority may have been revoked since decision)
  - scope (verify decision_type and resource_class still match)

Executor MUST NOT:
  - Assume authorization is still valid because Decision was approved
  - Skip revalidation if Governance approved the Decision
  - Use stale authority state from Decision time
```

### Revalidation State Cases

#### Case A: Authority Still Valid at T_execution

```
Condition:
  - authority_state_at_t_execution == ACTIVE
  - temporal_validity.is_within_scope(T_execution) == true
  - revocation_state == null (not revoked)
  - scope matches decision

Action:
  - PROCEED with execution
  - Record: {decision_id, T_execution, authority_id, REVALIDATED_OK}
  - Execute action
  - Record execution consequence
```

#### Case B: Authority Revoked Between T_decision and T_execution

```
Condition:
  - authority_state_at_t_execution == REVOKED
  - authority.revoked_at is between T_decision and T_execution

Action:
  - HALT execution (fail-closed)
  - Record: {decision_id, T_execution, authority_id, REVOKED_SINCE_DECISION}
  - Return error
  - Decision consequence: NOT EXECUTED
  - Historical record: Decision was approved but execution was prevented
```

#### Case C: Authority Expired Between T_decision and T_execution

```
Condition:
  - valid_until is not null
  - T_execution >= valid_until

Action:
  - HALT execution (fail-closed)
  - Record: {decision_id, T_execution, authority_id, EXPIRED}
  - Return error
  - Decision consequence: NOT EXECUTED
```

#### Case D: Authority State at T_execution is UNKNOWN

```
Condition:
  - Cannot determine current authority state
  - Verification fails or times out

Action:
  - HALT execution (fail-closed)
  - Record: {decision_id, T_execution, authority_id, VERIFICATION_FAILED}
  - Return error
  - Do NOT proceed
```

### Production Lock / Runtime Lock Interaction

```
Executor MUST respect existing production lock mechanisms:
  - If production is locked → HALT execution regardless of authority
  - If runtime is locked → HALT execution regardless of authority
  - Authority validation is INDEPENDENT of lock state
  - Locks are fail-safe, additional to authority checks
```

### Execution Consequence Recording

```
Execution Record:
  - execution_id           : string (unique)
  - decision_id            : string (which decision was executed)
  - T_execution            : datetime (when execution occurred)
  - authority_id           : string (which authority enabled execution)
  - revalidation_result    : enum (REVALIDATED_OK, REVOKED, EXPIRED, UNKNOWN)
  - action_executed        : string
  - consequence            : object (action-specific result)
  - success                : boolean
  - reason_if_failed       : string | null
```

---

## STEP 5: DECISION LEDGER CONTRACT (PROVENANCE MODEL)

### Decision Ledger Responsibilities

The Decision Ledger is the **institutional memory**. It records:
1. What was decided
2. Who had authority to decide
3. What authority state was (at decision time)
4. Whether execution was attempted
5. What actually happened

### Core Provenance Principle

```
Historical Authority State at T_decision
        ≠
Current Authority State at T_now

A historical Decision record MUST remain historically accurate even after
later authority is revoked or expires.

Example:
  T_authorized (authority granted)
    ↓
  T_decision (decision made, authority was ACTIVE)
    ↓
  T_execution (execution completed successfully)
    ↓
  T_revoked (authority revoked by Human Gate)
    ↓
  T_now (current time)

The Decision Ledger entry MUST record:
  - Decision was made at T_decision with ACTIVE authority
  - Decision was executed at T_execution
  - Authority state snapshot at T_decision
  - Authority was later revoked at T_revoked
  - Current authority state is REVOKED

The historical record is IMMUTABLE.
Revocation does NOT alter the historical decision record.
```

### Ledger Entry Structure

```
Decision Ledger Entry:
  
  [Decision Information]
  - decision_id              : string (unique)
  - decision_timestamp       : datetime (T_decision)
  - decision_type            : string
  - selected_action          : string
  - alternatives             : list
  - priority_score           : float
  - risk_score               : float
  - confidence               : float
  - rationale                : string
  
  [Authority Information at Decision Time]
  - authority_id             : string
  - authority_context_id     : string (context instance that enabled decision)
  - authority_state_at_decision  : enum (ACTIVE, REVOKED, EXPIRED)
  - authority_granted_by     : string
  - authority_decision_id    : string (decision that granted this authority)
  - authority_valid_from     : datetime
  - authority_valid_until    : datetime | null
  - authority_is_indefinite  : boolean
  
  [Execution Information]
  - execution_attempted      : boolean
  - execution_timestamp      : datetime | null (T_execution, if executed)
  - execution_id             : string | null
  - execution_consequence    : object | null
  - execution_success        : boolean | null
  - execution_reason_if_failed : string | null
  
  [Authority State at Recording Time]
  - authority_state_at_recording : enum (what is true NOW)
  - authority_revoked_at     : datetime | null (when was it revoked)
  - authority_revocation_decision_id : string | null (which decision revoked it)
  - current_status_check_timestamp : datetime (when was current state verified)
  
  [Governance Metadata]
  - governance_check_required : boolean
  - governance_approval_id   : string | null
  - governance_approval_timestamp : datetime | null
  - required_human_gate_check : boolean
```

### Read-Back Integrity Requirements

```
When reading a historical Decision Ledger entry:

1. Distinguish T_decision from T_now
   - Authority state at decision time is immutable
   - Authority state at now may have changed
   
2. Validate temporal consistency
   - valid_from <= T_decision < valid_until (or valid_until is null)
   - This ensures decision was within authority scope at time of decision

3. Record revocation history separately
   - Do NOT modify historical decision record when authority is revoked
   - Add revocation event to separate ledger
   - Link revocation event to original authority_id

4. Support historical queries
   - "Was this authority valid at T_decision?" → check historical snapshot
   - "Is this authority valid at T_now?" → check current state
   - "When was this authority revoked?" → check revocation ledger
```

### Preventing Historical Rewriting

```
FORBIDDEN:
  - Modifying authority_state_at_decision after the fact
  - Deleting or altering historical decision records
  - Retroactively invalidating a decision by changing authority record
  - Treating revocation as authority state change in historical record

REQUIRED:
  - Immutable historical snapshot of authority state at T_decision
  - Separate ledger for revocation events
  - Temporal evidence that cannot be altered
  - Audit trail showing when authority state changed
```

---

## STEP 6: TEMPORAL MODEL

### Five Critical Timepoints

Every decision lifecycle involves five distinct time points:

```
T_authorized  = when authority was granted/delegated
                Authority Object.granted_at

T_decision    = when the decision was made
                Decision.timestamp
                This is when authority state is captured for the ledger

T_execution   = when the action was actually carried out
                Execution.timestamp
                Authority must be revalidated at this point

T_revoked     = when authority was revoked (if applicable)
                Authority.revoked_at
                May be after T_execution

T_now         = current time
                When queries/audits are performed
                May be long after T_revoked
```

### Authority Validity Evaluation

#### At T_decision (in Decision Engine)

```
Authority is valid at T_decision if:
  - T_authorized <= T_decision
  - (valid_until is null) OR (T_decision < valid_until)
  - authority.state == ACTIVE
  - T_revoked does not exist (authority not yet revoked)
  
Snapshot captured in Ledger: IMMUTABLE
```

#### At T_execution (in Executor)

```
Authority MUST be revalidated at T_execution:
  - T_authorized <= T_execution
  - (valid_until is null) OR (T_execution < valid_until)
  - authority.state == ACTIVE (check current state, not historical)
  - If authority was revoked between T_decision and T_execution:
      → HALT execution (fail-closed)
      
Snapshot recorded: execution was blocked or allowed
```

#### At T_now (Audit/Query)

```
When reviewing historical decision:
  - Do NOT retroactively change decision based on current authority state
  - Do NOT assume decision was invalid because authority is now revoked
  - Compare historical snapshot (at T_decision) against current state
  - Record: "Authority was valid at T_decision, now revoked at T_revoked"
  
Principle: Revocation is prospective, not retroactive
```

### M3 Phase1 Preserved Decisions

```
NO RETROACTIVE AUTHORITY:
  - Authority granted at T_authorized
  - Cannot be used for decisions before T_authorized
  - Decision at T < T_authorized is INVALID regardless of current state

REVOCATION IS PROSPECTIVE:
  - Authority valid until T_revoked
  - Decisions made before T_revoked remain valid
  - Decisions made after T_revoked are invalid
  - Decisions pending execution at T_revoked may be halted

valid_until = null IS INDEFINITE:
  - Authority remains valid unless revoked
  - Does not expire by passage of time
  - Only revocation terminates indefinite authority

REVOCATION DOES NOT REWRITE HISTORY:
  - Historical decision records immutable
  - Revocation is recorded separately
  - No decision Ledger entry is altered when authority is revoked
```

---

## STEP 7: END-TO-END CONTRACT TRACE

### Complete Authority Context Flow

```
1. EXTERNAL REQUEST ARRIVES
   ├─ Source: HTTP, GitHub, filesystem, browser
   ├─ Payload: source-specific data
   └─ Authority Context: present or absent
   
2. MCP BOUNDARY VALIDATION
   ├─ Parse Authority Context
   ├─ Validate structure (all required fields present)
   ├─ Verify authenticity (cryptographic binding)
   ├─ Check authority state (ACTIVE, REVOKED, EXPIRED, UNKNOWN)
   ├─ Verify scope (decision_type, resource_class)
   ├─ Verify temporal validity at T_mcp (now)
   ├─ Determine: VALID / INVALID / UNKNOWN / ABSENT
   └─ Decision:
       VALID   → ACCEPT, pass to Decision Engine
       INVALID → REJECT, record reason, return error
       UNKNOWN → REJECT (fail-closed), record reason, return error
       ABSENT  → REJECT (fail-closed), record reason, return error
   
3. MCP VALIDATION RECORDING
   ├─ Record: validation_id, timestamp, authority_id, decision
   ├─ Record: verification_status, authority_state
   └─ Ledger destination: MCP validation log (not yet persistent Decision Ledger)
   
4. DECISION ENGINE (if MCP accepted)
   ├─ Receive: mcp_validation (ACCEPTED), authority_context, semantic_result
   ├─ Process: decision logic (priority, risk, alternatives)
   ├─ Capture: authority_binding (snapshot of authority state at T_decision)
   ├─ Generate: DecisionResult with:
   │  ├─ decision_id
   │  ├─ T_decision (timestamp)
   │  ├─ selected_action, alternatives
   │  ├─ authority_context (passed through)
   │  ├─ authority_binding (state snapshot at T_decision)
   │  ├─ authority_state_snapshot (immutable historical record)
   │  └─ required_governance_check = true
   └─ Output: DecisionResult → Governance Layer
   
5. GOVERNANCE LAYER (GL1-GL7)
   ├─ Receive: DecisionResult
   ├─ Evaluate: risk, priority, governance conditions
   ├─ Determine: APPROVED / REJECTED / CONDITIONAL
   ├─ Decision:
   │  ├─ APPROVED → pass to Executor
   │  ├─ REJECTED → record reason, return error
   │  └─ CONDITIONAL → record conditions, await further approval
   └─ Record: governance_approval_id, timestamp
   
6. DECISION LEDGER RECORDING (at approval time)
   ├─ Write entry containing:
   │  ├─ Decision information (id, timestamp, action, rationale)
   │  ├─ Authority information at T_decision (snapshot, immutable)
   │  ├─ Governance approval (id, timestamp, conditions)
   │  └─ Execution status = PENDING (not yet executed)
   └─ Record: decision_id → Ledger persistence mechanism
   
7. EXECUTOR (if governance approved)
   ├─ Receive: approved DecisionResult
   ├─ Capture: T_execution (current time)
   ├─ Revalidate authority:
   │  ├─ Check: authority_state at T_execution (not T_decision)
   │  ├─ Check: temporal validity at T_execution
   │  ├─ Check: revocation state (was authority revoked since T_decision?)
   │  ├─ Check: scope still matches
   │  └─ Result: REVALIDATED_OK / REVOKED / EXPIRED / UNKNOWN
   ├─ Decision:
   │  ├─ REVALIDATED_OK → proceed with execution
   │  └─ NOT OK → HALT, record reason, do NOT execute
   ├─ Execute action (if revalidated)
   └─ Capture: consequence, success/failure
   
8. EXECUTION RECORDING
   ├─ Record: execution_id, T_execution, authority_id
   ├─ Record: revalidation_result (REVALIDATED_OK or reason)
   ├─ Record: action_executed, consequence, success
   └─ Update Ledger: execution_attempted = true, execution_timestamp, consequence
   
9. ACTUAL CONSEQUENCE
   ├─ Side effects of executed action (if any)
   ├─ State changes in external systems
   └─ Resource mutations
   
10. INSTITUTIONAL MEMORY (Decision Ledger)
    ├─ Entry contains complete historical record:
    │  ├─ What decision was made (immutable)
    │  ├─ Authority state when decision was made (immutable)
    │  ├─ Governance approval (immutable)
    │  ├─ Execution outcome (updatable with attempt info)
    │  ├─ Actual consequence (if executed)
    │  └─ Later authority revocation (if applicable, separate record)
    └─ Ready for audit, historical query, compliance verification
```

### Validation Points and Rejection Conditions

| Step | Input | Validation | Rejection Condition | Recorded Evidence |
|------|-------|-----------|---------------------|------------------|
| MCP | authority_context | Structure, authenticity, scope, temporal | INVALID / UNKNOWN / ABSENT | MCP validation record |
| Decision Engine | authority_context | Already validated at MCP | Authority state changed? | authority_binding snapshot |
| Governance | DecisionResult | Risk, priority, conditions | Risk threshold, conditional fail | governance_approval record |
| Executor | approved Decision | Authority state AT T_execution | REVOKED / EXPIRED / UNKNOWN | execution_record (failed) |

### Evidence Immutability Points

```
IMMUTABLE (never changed):
  - Authority state snapshot at T_decision
  - Decision Ledger entry (once written)
  - Governance approval record
  - MCP validation record

MUTABLE (can be updated):
  - Execution record (added after execution attempt)
  - Authority current state (revalidated at each step)
  - Revocation records (added when authority is revoked)
```

---

## STEP 8: EXISTING SYSTEM GAP MAP

### Examined Systems

Based on inspection of actual codebase (Step 1 of Phase2 audit):

#### A. MCP System (mcp/mcp_gateway.py, mcp/mcp_router.py, mcp/adapters/*.py)

| Capability | Status | Evidence |
|---|---|---|
| Accepts requests from multiple sources | EXISTS | HTTPAdapter, GitHubAdapter, etc. |
| Parses request into structured data | EXISTS | adapter.parse() returns {endpoint, method, body} |
| Carries authority_id in request | MISSING | HTTPAdapter doesn't extract authority_id |
| Carries decision_type in request | MISSING | No decision_type in parsed payload |
| Validates authority context | MISSING | No validate_at_mcp_boundary() call in gateway |
| Returns rejection reason | EXISTS | Exception raised, but minimal detail |
| Records MCP validation | MISSING | No validation logging in MCP layer |
| **REQUIRED CHANGE**: Add authority_id/decision_type fields to adapter contracts | CONTRACT CHANGE REQUIRED | All adapters must be updated |

#### B. Decision Engine (decision/decision_engine.py, decision/decision_model.py)

| Capability | Status | Evidence |
|---|---|---|
| Receives request | EXISTS | decide(semantic_result) |
| Generates decision alternatives | EXISTS | Alternative objects with scores |
| Captures authority context | MISSING | DecisionResult has no authority_context field |
| Creates authority binding snapshot | MISSING | No authority_binding in DecisionResult |
| Distinguishes code/auth/evidence states | MISSING | No separate state tracking |
| Records decision with authority | MISSING | Ledger recording not implemented |
| **REQUIRED CHANGE**: Add authority_context and authority_binding to DecisionResult | CONTRACT CHANGE REQUIRED | Decision model must be extended |

#### C. Governance Pipeline (structural/governance_pipeline.py)

| Capability | Status | Evidence |
|---|---|---|
| Governs tool execution | EXISTS | before_tool(), execution_governance |
| Checks authority for tool calls | MISSING | Governance pipeline is tool-focused, not authority-focused |
| Passes authority context through | MISSING | No authority context in GovernanceDecision |
| Blocks unauthorized execution | EXISTS | Can abort based on conditions |
| **STATUS**: Separate from M3 authority validation (tool-level vs decision-level) | ORTHOGONAL | Different governance layer |

#### D. Executor (runtime/executor.py)

| Capability | Status | Evidence |
|---|---|---|
| Receives decision | EXISTS | Loads from runtime/selected_intent.json |
| Extracts authority_id from decision | MISSING | Intent has no authority_id field |
| Revalidates authority at T_execution | MISSING | No revalidation logic |
| Checks temporal validity at T_execution | MISSING | No temporal check |
| Checks revocation state | MISSING | No revocation check |
| Records execution with authority | MISSING | History doesn't include authority evidence |
| **REQUIRED CHANGE**: Add authority_id validation before execution | CONTRACT CHANGE REQUIRED | Executor intake must include authority_id |

#### E. Decision Ledger (runtime/jarvis/record/ledger.py)

| Capability | Status | Evidence |
|---|---|---|
| Stores decision records | EXISTS | JarvisLedger.append(decision_id, status) |
| In-memory storage | EXISTS | self.records list |
| Persistent storage | MISSING | No file I/O, no database |
| Authority state capture | MISSING | Current schema only {decision_id, status, timestamp} |
| Immutable historical snapshot | MISSING | Records can be lost if process restarts |
| Read-back verification | MISSING | No query methods |
| **REQUIRED CHANGE**: Define schema for Authority records + persistence mechanism | GOVERNANCE DECISION REQUIRED | Schema addition requires Human Gate approval |

#### F. M2 System (implicit)

| Capability | Status | Evidence |
|---|---|---|
| Pre-M3 decision flow | EXISTS | M2 decisions lack authority_id |
| Implicit authority (all-human) | EXISTS | M2 uses implicit authorization |
| M3 authority enforcement | MISSING | M3 validation not applied to M2 |
| Backward compatibility | EXISTS | M2 and M3 registries are separate |
| **STATUS**: M2 unchanged, M3 is parallel system | VERIFIED | No M2 modifications required |

### Gap Classification Summary

```
EXISTING SYSTEMS:

MCP System
  ├─ Request parsing: EXISTS
  ├─ Authority context extraction: MISSING
  └─ Authority validation: MISSING → CONTRACT CHANGE REQUIRED

Decision Engine
  ├─ Decision generation: EXISTS
  ├─ Authority binding: MISSING → CONTRACT CHANGE REQUIRED
  └─ State distinction: MISSING

Executor
  ├─ Action execution: EXISTS
  ├─ Authority validation: MISSING → CONTRACT CHANGE REQUIRED
  └─ Revalidation at T_execution: MISSING

Decision Ledger
  ├─ In-memory storage: EXISTS
  ├─ Authority record schema: MISSING → GOVERNANCE DECISION REQUIRED
  ├─ Persistence: MISSING → GOVERNANCE DECISION REQUIRED
  └─ Historical snapshots: MISSING

M2 System
  ├─ Isolation: VERIFIED
  └─ No modification required
```

---

## STEP 9: HUMAN GATE ITEMS (CONSOLIDATED)

### Unresolved Architectural Decisions

These decisions cannot be made by design phase alone. They require Human Gate authorization:

#### HG-ITEM-1: Authority Context Representation

**Question**: How is Authority Context represented and transmitted?

**Alternatives**:
1. **Inline Context**: Authority context embedded directly in request/decision payload
   - Pro: Single object, simpler threading
   - Con: Duplicates authority information across pipeline
   
2. **Reference-Based Context**: Request/decision carries only authority_id, context resolved from registry
   - Pro: Single source of truth
   - Con: Requires registry lookups at each step
   
3. **Hybrid**: Inline context for immutable historical snapshots, references for current state
   - Pro: Immutability + efficiency
   - Con: More complex state management

**Design Recommendation**: Hybrid (inline snapshots at decision/execution points, reference for current validation)

**Requires Human Gate Decision**: Yes

#### HG-ITEM-2: Cryptographic Authority Context Binding

**Question**: How is Authority Context authenticity verified?

**Alternatives**:
1. **HMAC Signature**: Sign context with authority registry key
   - Pro: Detects tampering
   - Con: Key management complexity
   
2. **Time-Bound Token**: Authority context is a time-limited bearer token
   - Pro: Built-in expiration
   - Con: Token management, revocation list
   
3. **Read-Through Verification**: Context authenticity verified by read from canonical Authority Registry
   - Pro: Always fresh, no key management
   - Con: Registry lookup required, scalability?
   
4. **No Cryptographic Binding**: Rely on process integrity + audit trail
   - Pro: Simplest implementation
   - Con: Vulnerable to process compromise

**Design Recommendation**: Read-through verification (Authority Registry is canonical)

**Requires Human Gate Decision**: Yes

#### HG-ITEM-3: Authority State Vocabulary

**Question**: What are the canonical authority states?

**Current (from M3 Phase1)**:
- ACTIVE (authority is valid now)
- REVOKED (authority was revoked, irreversible)
- EXPIRED (authority passed valid_until without being revoked)
- UNDEFINED (not defined in Phase1)

**Question**: Is this vocabulary complete for decision/execution/ledger flow?

**Candidates for addition**:
- VERIFIED (was checked and found valid)
- NOT_VERIFIED (exists but not checked)
- UNKNOWN (cannot determine state)
- STALE (was verified but verification timestamp is old)

**Design Recommendation**: Keep Phase1 states (ACTIVE/REVOKED/EXPIRED). Add separate VERIFICATION_STATUS field (VERIFIED/NOT_VERIFIED/INVALID/UNKNOWN/STALE) to Authority Context, not to Authority Object.

**Requires Human Gate Decision**: Yes

#### HG-ITEM-4: Persistent Decision Ledger Schema

**Question**: What is the canonical persistent storage for Decision Ledger entries?

**Current State**: No persistent ledger implemented. JarvisLedger is in-memory only.

**Alternatives**:
1. **Add to existing Decision Ledger (data/decisions/decision_ledger.jsonl)**
   - Pro: Reuses existing ledger
   - Con: Requires schema evolution of existing file format
   
2. **New Authority Ledger (data/authority/authority_ledger.jsonl)**
   - Pro: Separation of concerns
   - Con: Splits history across multiple files
   
3. **New Decision Ledger v2 Schema**
   - Pro: Opportunity to consolidate
   - Con: Migration required for existing entries
   
4. **Keep in-memory only (sandbox only)**
   - Pro: No persistence complexity
   - Con: No institutional memory across process restarts

**Design Recommendation**: (Cannot recommend without understanding existing ledger intent)

**Requires Human Gate Decision**: Yes (authority to modify existing ledger or create new one)

#### HG-ITEM-5: MCP Boundary Authority Extraction

**Question**: Where does Authority Context come from in MCP requests?

**Current State**: No authority information in HTTP/GitHub/filesystem/browser adapters.

**Alternatives**:
1. **HTTP Header Extraction**: Authorization header → authority_id
   - Pro: Standard HTTP practice
   - Con: Requires adapter changes
   
2. **Request Payload Field**: authority_context as JSON field in request body
   - Pro: Source-agnostic
   - Con: Requires all request sources to include field
   
3. **External Mapping**: Request source + request ID → lookup authority from registry
   - Pro: Decouples request format from authority
   - Con: Requires external context service
   
4. **Implicit Authority by Source**: GitHub source → GitHub admin authority automatically
   - Pro: Convenient
   - Con: Violates "no implicit authority" principle

**Design Recommendation**: Per-adapter implementation (HTTP header for HTTP, GitHub webhook headers for GitHub, etc.)

**Requires Human Gate Decision**: Yes

#### HG-ITEM-6: Decision-to-Execution Authority Revalidation Timing

**Question**: When exactly is authority revalidated at execution time?

**Current Design**: Executor revalidates immediately before execution.

**Question Refinements**:
- If authority changes between Decision approval and Execution start, what happens?
- Is there a maximum staleness allowed for authority verification?
- Who decides if revalidation delay is acceptable?

**Requires Human Gate Decision**: Yes (timing and tolerance policy)

#### HG-ITEM-7: Revocation Cascade and Historical Records

**Question**: When authority is revoked, how are historical decisions affected?

**Principle (from M3 Phase1)**:
- Revocation is prospective, not retroactive
- Historical decisions remain valid
- Revocation does not alter Decision Ledger entries

**Question**: Does this apply to ALL historical decisions, or only those executed before revocation?

**Example**:
- T_decision: Decision made under valid authority
- T_execution: Execution attempted but denied (authority already revoked)
- T_now: Query historical ledger

Should the historical decision record show:
- "Decision was made under valid authority, execution was denied" (current design)
- "Decision was made but authority insufficient at execution" (alternative)

**Design Recommendation**: Former (decision validity is independent of execution outcome)

**Requires Human Gate Decision**: Confirmation needed

#### HG-ITEM-8: Failure Recovery and Partial Execution

**Question**: If Executor revalidation fails, what is the recovery path?

**Scenarios**:
1. Authority verification times out (network issue, not authority problem)
   - Should execution be retried?
   - With how long a delay?
   
2. Authority state is UNKNOWN (registry unreachable)
   - Fail-closed (reject execution) — current design
   - Or allow configurable fail-open?

**Design Recommendation**: Strict fail-closed (no retry, no fail-open)

**Requires Human Gate Decision**: Yes (failure policy)

### Consolidated Decision List

```
HG-ITEM-1: Authority Context Representation (inline vs reference vs hybrid)
HG-ITEM-2: Cryptographic Authority Context Binding (mechanism)
HG-ITEM-3: Authority State Vocabulary (complete vocabulary)
HG-ITEM-4: Persistent Decision Ledger Schema (where, format, migration)
HG-ITEM-5: MCP Boundary Authority Extraction (source mapping)
HG-ITEM-6: Decision-to-Execution Revalidation Timing (policy)
HG-ITEM-7: Revocation Cascade and Historical Records (scope)
HG-ITEM-8: Failure Recovery and Partial Execution (recovery policy)
```

**DO NOT create separate micro-gates for each item. Present consolidated Human Gate decision request in final deliverable.**

---

## STEP 10: FINAL DELIVERABLE CONTENTS

This document contains:

1. ✓ Authority Context Model (Step 1)
   - Minimum required fields
   - Critical distinctions
   - Implicit authority prevention

2. ✓ MCP Boundary Contract (Step 2)
   - Request validation rules
   - Authority state cases (VALID/INVALID/UNKNOWN/ABSENT)
   - Rejection conditions
   - State recording

3. ✓ Decision Engine Contract (Step 3)
   - State separation (code ≠ auth ≠ evidence ≠ decision)
   - Evidence state vocabulary
   - Authority binding snapshot
   - Prevent evidence collapse

4. ✓ Executor Contract (Step 4)
   - Pre-execution revalidation requirement
   - Revalidation cases (still valid, revoked, expired, unknown)
   - Fail-closed behavior
   - Execution consequence recording

5. ✓ Decision Ledger Provenance Model (Step 5)
   - Historical accuracy preservation
   - T_decision ≠ T_now principle
   - Immutable snapshots
   - Revocation history separate from decision records
   - Read-back integrity requirements

6. ✓ Temporal Model (Step 6)
   - Five critical timepoints (T_authorized, T_decision, T_execution, T_revoked, T_now)
   - Authority validity evaluation at each point
   - M3 Phase1 decisions preserved
   - No retroactive authority
   - Prospective revocation
   - Indefinite authority (valid_until=null)

7. ✓ End-to-End Contract Trace (Step 7)
   - Request → MCP → Decision → Governance → Executor → Consequence → Ledger
   - Validation points at each step
   - Rejection conditions
   - Evidence immutability points

8. ✓ Existing System Gap Map (Step 8)
   - MCP System: Authority context MISSING → CONTRACT CHANGE REQUIRED
   - Decision Engine: Authority binding MISSING → CONTRACT CHANGE REQUIRED
   - Executor: Authority validation MISSING → CONTRACT CHANGE REQUIRED
   - Decision Ledger: Authority schema MISSING → GOVERNANCE DECISION REQUIRED
   - M2 System: Verified unchanged

9. ✓ Security and Fail-Closed Conditions
   - REJECT on missing authority (no implicit authority)
   - REJECT on UNKNOWN authority (fail-closed)
   - HALT execution if authority revoked since decision
   - Immutable historical records (no retroactive alteration)
   - No authority inference from code existence

10. ✓ Consolidated Human Gate Decisions (Step 9)
    - HG-ITEM-1: Authority Context Representation
    - HG-ITEM-2: Cryptographic Binding Mechanism
    - HG-ITEM-3: Authority State Vocabulary
    - HG-ITEM-4: Persistent Ledger Schema
    - HG-ITEM-5: MCP Authority Extraction
    - HG-ITEM-6: Revalidation Timing
    - HG-ITEM-7: Revocation Cascade Policy
    - HG-ITEM-8: Failure Recovery Policy

---

## DESIGN COMPLETENESS ASSESSMENT

### What Is Defined

✓ Conceptual Authority Context model  
✓ MCP boundary validation contract  
✓ Decision engine authority binding  
✓ Executor revalidation requirements  
✓ Decision Ledger provenance model  
✓ Temporal model with five critical points  
✓ End-to-end trace with validation/rejection points  
✓ Existing system gap analysis  
✓ Security principles (fail-closed, no implicit authority, immutable history)  
✓ Consolidated Human Gate decision items  

### What Requires Human Gate Decision

✗ Authority Context representation mechanism (inline/reference/hybrid)  
✗ Cryptographic binding mechanism (HMAC/token/read-through/none)  
✗ Extended authority state vocabulary (VERIFIED/NOT_VERIFIED/etc)  
✗ Persistent Decision Ledger schema and location  
✗ MCP boundary authority extraction sources  
✗ Revalidation timing policy  
✗ Revocation cascade policy scope  
✗ Failure recovery policy  

### What Is NOT Defined (Out of Scope)

✗ Implementation code (intentional)  
✗ MCP adapter modifications (requires contract decision)  
✗ Decision model changes (requires contract decision)  
✗ Executor code changes (requires contract decision)  
✗ Persistent storage implementation (requires schema decision)  
✗ Key rotation / token management details (requires mechanism decision)  
✗ Performance/scalability optimization (future phase)  
✗ Multi-tenant authority separation (future phase)  

---

## DESIGN STATUS

**DESIGN PHASE COMPLETE**

All architectural decisions that can be made independently of governance and contract decisions have been documented. The design is ready for Human Gate review.

The design establishes:
1. Authority Context must flow through all decision/execution points
2. Authority must be verified at MCP boundary (reject unknown/absent)
3. Authority must be revalidated at execution boundary
4. Authority state at decision time must be immutable in ledger
5. No implicit authority permitted
6. Fail-closed for unknown authority
7. No retroactive authority alteration

Remaining decisions (8 items) require Human Gate authorization before implementation can proceed.

---

## NEXT STEPS (NOT AUTHORIZED)

1. Human Gate review of 8 consolidated decision items
2. Human Gate authorization for contract changes (if approved)
3. Separate implementation authorization (if contracts approved)
4. MCP adapter modifications (separate implementation)
5. Decision model extension (separate implementation)
6. Executor integration (separate implementation)
7. Decision Ledger schema and persistence (separate implementation)

**NO IMPLEMENTATION IS AUTHORIZED BY THIS DESIGN DOCUMENT.**

---

**Document Created**: 2026-09-19  
**Design Phase**: COMPLETE  
**Status**: AWAITING HUMAN GATE DECISION ON 8 CONSOLIDATED ITEMS  
**Next Authority**: Human Gate Review
