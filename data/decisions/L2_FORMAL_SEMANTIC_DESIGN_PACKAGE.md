# L2 Formal Semantic Design Package

**Package ID:** L2-FSDP-20260913-001  
**Prepared By:** Claude Haiku 4.5 (くろこ)  
**Prepared For:** Human Gate (nsjp_kimura, Design-time decision scope)  
**Date Prepared:** 2026-09-13  
**Authority Scope:** Layer 2 Formal Semantic Design (Q-L2-01 AUTHORIZE)  
**Status:** DRAFT / PROPOSED

---

## 1. HG Authorization Basis

**Decision:** Q-L2-01 AUTHORIZE (Layer 2 Formal Semantic Design ONLY)

**Authorized Scope:**
- Design and specification of Layer 2 formal semantic definitions
- ActualConsequence, AuthorizedConsequence, CO, Authorization Scope formal definitions
- Semantic Closure Relationship formalization
- Design assumption documentation
- Evidence-bounded specification (no implementation authorization)

**Non-Authorized Scope:**
- Implementation Authorization (remains NOT_GRANTED)
- Production Modification (remains 0)
- Runtime Modification (remains 0)
- Schema Modification (remains 0)
- Code Modification (remains 0)
- Design Approval (deferred to HG Design Review)
- Semantic Closure Achievement (remains NOT_ACHIEVED)

**Locked States (Maintained Throughout):**
```
N14R Necessity               = NOT_PROVEN / LOCKED
M18 Runtime Closure         = NOT_ACHIEVED / LOCKED
Authority → Runtime Binding = BROKEN / LOCKED
C2-b                        = BLOCK / LOCKED
Implementation Authorization = NOT_GRANTED / LOCKED
Production Modification      = 0 / LOCKED
System                       = HOLD / FAIL-CLOSED / LOCKED
Semantic Closure             = NOT_ACHIEVED
```

---

## 2. Executive Summary

This design package formalizes Layer 2 semantic definitions for the MoCKA governance architecture. Layer 2 addresses the gap between conceptual governance frameworks (Layer 1) and implementation representations (Layer 3).

**Primary Objective:**
Define formal semantics for consequence observation and authorization binding, enabling Layer 3 implementation and Layer 4 runtime verification to proceed on explicit semantic foundations.

**Key Findings:**
- Layer 1: Consequential Action concept EXISTS (Paper 3.5ζ, SPP/PHL v1.0)
- Layer 2: Formal definitions NOT_ESTABLISHED for ActualConsequence, AuthorizedConsequence, CO, Authorization Scope
- Layer 3: Implementation representations NOT_FOUND (Consequence capture/binding mechanisms absent)
- Layer 4: Runtime enforcement NOT_PROVEN (GL7 emit exists; consume/enforce not demonstrated)

**Design Approach:**
- Evidence-Bounded: Only what can be derived from existing evidence
- Counterexample-First: Each definition includes semantic boundary violations
- Design-Assumption Explicit: Separates proposed semantics from established facts
- UNKNOWN Preserved: No inference upgrades unresolved states

**Deliverable Status:**
DRAFT / PROPOSED (Design-only; awaiting HG Design Review before implementation authorization)

---

## 3. Scope

### In Scope: Layer 2 Formal Semantic Definitions

1. **ActualConsequence** — Formal type/structure for observed/realized consequences at runtime
2. **AuthorizedConsequence** — Formal type/structure for authorized-to-occur consequences
3. **CO (Consequential Outcome)** — Formal semantics and positioning of CO concept
4. **Authorization Scope** — 3D formalization (WHO/WHEN/WHAT) + extensions
5. **Semantic Closure Relationship** — Formal relationship without achieving closure
6. **Cross-Semantic Model** — Relationships between L2 definitions
7. **UNKNOWN/UNDEFINED/NOT_PROVEN Propagation** — Handling in cascade scenarios
8. **Evidence Contract** — Mapping semantics to supporting evidence
9. **Design Assumption Registry** — Explicit assumptions and verification requirements
10. **Counterexample Analysis** — Semantic boundary violations for each definition
11. **Implementation Preconditions** — What Layer 3 must verify before Layer 2 formalization becomes binding

### Not in Scope: Out-of-Band Activities

- Layer 1 Governance Definition (existing; SPP/PHL v1.0)
- Layer 3 Implementation Representation (deferred to implementation phase)
- Layer 4 Runtime Binding/Enforcement (deferred to verification phase)
- M18 Runtime Closure pursuit (separate evidence collection track)
- 30-route problem resolution (separate SDR-03 track)
- Code/schema/runtime modification of any kind
- Production deployment preparation
- Implementation Authorization (deferred to post-design review)
- Design Approval (deferred to HG Design Review)
- Semantic Closure Achievement (state: NOT_ACHIEVED, maintained)

---

## 4. Non-Scope Clarifications

The following are explicitly NOT objectives of this design phase:

```
Design Approval              ≠ This Package
Implementation Authorization ≠ This Package
Runtime Verification         ≠ This Package
M18 Closure                  ≠ This Package
Code Implementation          ≠ This Package
Schema Implementation        ≠ This Package
Production Modification      ≠ This Package
Semantic Closure Achievement ≠ This Package
```

This package produces DRAFT / PROPOSED semantics for HG review. All state transitions require separate HG decisions.

---

## 5. Evidence Basis

### Existing Evidence Base

**Layer 1 Governance Evidence:**
- Paper 3.5ζ: Consequential Action concept defined
- SPP/PHL v1.0: Foundational rules (5 principles) established
- R01 Investigation: Conceptual framework confirmed to exist

**Layer 1-4 Investigation Evidence (R01):**
- Direct source code inspection: governance_pipeline.py, execution_governance.py, phi_os/event_bus.py, mocka_mcp_server.py, MOCKA_OVERVIEW.json
- Finding: Consequence model NOT_FOUND across Layers 2-4
- Finding: Authorization layer PARTIALLY_IMPLEMENTED (Tool-level READ_ONLY/WRITE gate exists)
- Finding: GL7 event emission exists; GL7 consequence enforce/consume NOT_FOUND

**Governance Validation Evidence (R01):**
- 10 integrity checks (GV-01～GV-10): ALL PASSED
- Evidence state vocabulary: Canonical (NOT_FOUND/NOT_ESTABLISHED/UNKNOWN/NOT_PROVEN) consistently applied
- Locked state preservation: All 8 locked states VERIFIED unchanged through validation cycle
- UNKNOWN/UNDEFINED/NOT_PROVEN preservation: Confirmed

**Evidence Gaps Identified:**
```
Layer 2: ActualConsequence formal type - NOT_ESTABLISHED
Layer 2: AuthorizedConsequence formal type - NOT_ESTABLISHED
Layer 2: CO formal meaning/type - UNKNOWN
Layer 2: Authorization Scope (WHO/WHEN/WHAT) - NOT_FOUND
Layer 3: Consequence capture/binding mechanism - NOT_FOUND
Layer 3: Authorization ↔ Consequence contract - NOT_FOUND
Layer 4: Consequence enforcement observe/verify - NOT_FOUND
Layer 4: Target Invariant proof mechanism - NOT_FOUND
```

### Evidence Discipline Rules (Maintained)

```
OBSERVED        ← Direct empirical finding
NOT_FOUND       ← Evidence searched; artifact not located
NOT_ESTABLISHED ← Formal definition not created/located
UNKNOWN         ← Concept recognized; meaning/type unclear
NOT_PROVEN      ← Mechanism exists but satisfaction not demonstrated
UNRESOLVED      ← Decision question remains open
PARTIAL         ← Partial implementation/evidence exists
PROPOSED        ← Design candidate; not yet decided
```

**Forbidden Conversions:**
```
NOT_FOUND → ABSENT       (PROHIBITED)
NOT_PROVEN → FALSE       (PROHIBITED)
UNKNOWN → FALSE          (PROHIBITED)
UNKNOWN → ABSENT         (PROHIBITED)
PROPOSED → DECIDED       (PROHIBITED)
DRAFT → APPROVED         (PROHIBITED)
UNRESOLVED → RESOLVED    (PROHIBITED without evidence)
```

---

## 6. Semantic Design Principles

### Principle 1: Evidence Boundedness

Each semantic definition is grounded in evidence from Layers 1-4. Where evidence is insufficient, the semantic boundary is explicitly marked as PROPOSED, UNRESOLVED, or UNKNOWN.

**Application:**
- Definitions DO NOT infer from code behavior
- Definitions DO ground in conceptual framework (Paper 3.5ζ)
- Definitions DO acknowledge evidence gaps
- Definitions DO NOT claim proof without evidence

### Principle 2: Semantic Layering

Each concept exists at multiple levels; these must be kept distinct:

```
Concept (naming/reference)
Type (structure/identity)
Semantics (meaning/relationship)
Runtime Observation (evidence channel)
Implementation (code mechanism)
```

**Application:**
- CO-as-concept ≠ CO-as-type ≠ CO-as-runtime-observation
- ActualConsequence-as-proposed ≠ ActualConsequence-as-runtime-proven
- Authorization-as-decision ≠ Authorization-as-runtime-enforced

### Principle 3: Boundary Integrity

Each definition must explicitly distinguish itself from related but different concepts.

**Application:**
- ActualConsequence ≠ Action ≠ Proposal ≠ Authorization ≠ Execution Attempt ≠ Observed Event
- AuthorizedConsequence ≠ ActualConsequence ≠ Possible Consequence
- Authorization Scope ⊆ or ⊇ or ∩ AuthorizedConsequence (relationship PROPOSED, not decided)

### Principle 4: Counterexample First

Each definition must include at least one scenario where:
- Definition appears satisfied
- Semantic condition actually fails

**Application:**
- ActualConsequence: Execution occurs, observation fails → semantic boundary violated
- AuthorizedConsequence: Authorization exists, consequence exceeds scope → boundary violated
- CO: Artifact recorded, semantic provenance insufficient → boundary violated
- Authorization Scope: Permission granted, scope not defined → boundary violated

### Principle 5: UNKNOWN Preservation

UNKNOWN states must be maintained as distinct from FALSE, ABSENT, or UNIMPLEMENTED.

**Application:**
- CO's current meaning: UNKNOWN (not FALSE)
- M18-Scope definition: UNRESOLVED (not DECIDED)
- 30-route relationship to M18: NOT_PROVEN (not DISPROVEN)

---

## 7. L2-01: ActualConsequence — Formal Semantic Design

### 7.1 Definition

**ActualConsequence** is the formal type representing consequences that are realized or observed at runtime following an execution attempt.

```
ActualConsequence
  = Observable state transition / effect / event
    that is empirically detected (via evidence channel)
    after execution of authorized action
    and attributed to that execution
```

**Evidence Basis:** Inferred from GL7 event emission mechanism (ALLOW/DENY events); consequence consume/enforce NOT_FOUND.

### 7.2 Semantic Purpose

ActualConsequence serves as the bridge between:
- **Intention:** What was authorized to happen
- **Reality:** What actually happened at runtime
- **Evidence:** How we know what happened

Without formal ActualConsequence semantics, the authorization → consequence → enforcement chain cannot be closed.

### 7.3 Type / Structure

**Proposed Structure:**

```
ActualConsequence {
  identity        : UUID                    // unique consequence instance
  action          : AuthorizedAction        // action that caused this consequence
  authorization   : Authorization           // authorization under which action occurred
  state_before    : SystemState             // state prior to execution
  state_after     : SystemState             // state after execution attempt
  observation     : ObservationRecord       // how consequence was detected
  timestamp       : ISO8601                 // when observed
  evidence_status : (OBSERVED | NOT_PROVEN) // confidence level
  scope           : ConsequenceScope        // what was affected (subject, resource, etc)
}
```

**Status:** PROPOSED (structure tentative; requires L3 evidence for finalization)

### 7.4 Domain

**Applicable Domains:**
- Any action subject to Authorization Scope
- Any system state that can be observed
- Any runtime that provides observation channels (GL7, logs, state snapshots)

**Limits:**
- Consequences outside Authorization Scope (UNKNOWN relationship)
- Unobservable state transitions (NOT_PROVEN)
- Actions not preceded by authorization (BOUNDARY_VIOLATION)

### 7.5 Identity

ActualConsequence instances are identified by:
1. **Primary:** (action_id, authorization_id, timestamp_observed) tuple
2. **Secondary:** UUID assigned by observation mechanism
3. **Tertiary:** State hash (state_before XOR state_after)

**Identity Stability:** Observation timestamp defines ActualConsequence identity; cannot change retroactively without evidence of observation error.

### 7.6 Temporal Semantics

```
Timeline:
  Authorization Issued
           ↓
  Action Executed
           ↓
  State Transition Occurs (may be immediate or delayed)
           ↓
  Observation Detected (evidence channel activated)
           ↓
  ActualConsequence Recorded
```

**Temporal Constraints:**
- observation_timestamp ≥ action_execution_time (never retroactive)
- ActualConsequence cannot precede execution
- Authorization timestamp ≤ action_execution_time

**Unresolved Question:** Can consequence be delayed? (e.g., eventual consistency scenarios)
- **Status:** NOT_PROVEN (no L1 evidence on temporal tolerance)

### 7.7 Preconditions

For ActualConsequence to be valid:

1. Authorization must have been granted (authorization_id must resolve)
2. Action must have been executed (action_id must exist in execution log)
3. Observation channel must have fired (observation_record must exist)
4. State transition must be measurable (state_before ≠ state_after OR permission change detected)

**Precondition Verification:** NOT_ESTABLISHED (Layer 3 implementation phase)

### 7.8 Postconditions

After ActualConsequence is recorded:

1. Authorization's execution scope is updated (consequence attributed)
2. Target Invariant must be evaluated (consequence within authorization scope?)
3. Evidence record is appended (immutable audit trail)
4. M18-Scope must evaluate this consequence (within/outside M18 closure scope?)

**Postcondition Enforcement:** NOT_PROVEN (Layer 4 runtime binding phase)

### 7.9 Evidence Requirements

To claim ActualConsequence with OBSERVED status:

| Evidence Item | Required | Current Status | Verification Method |
|---|---|---|---|
| Authorization record | YES | FOUND (GL7 gate) | Check authorization.issued_timestamp |
| Action execution log | YES | PARTIAL (GL7 emit) | Check execution_governance.log |
| State transition proof | YES | NOT_FOUND | Requires Layer 3 capture mechanism |
| Observation record | YES | PARTIAL (GL7 event) | Check gl7_event_bus.consequences |
| Timestamp consistency | YES | NOT_ESTABLISHED | Requires clock synchronization proof |
| Consequence scope binding | RECOMMENDED | NOT_FOUND | Requires scope definition (L2-04) |

**Overall Status:** PARTIAL (GL7 emit exists; state transition capture NOT_FOUND)

### 7.10 Observation Boundary

**What Counts as Evidence of Consequence:**

1. **Explicit observation:** GL7 event emission (ALLOW/DENY)
2. **State change:** Measurable difference in system state
3. **Permission change:** Verified authorization enforcement
4. **Log entry:** Immutable record in execution log

**What Does NOT Count:**
- Absence of error message (negative evidence)
- Assumption that "nothing broke" (inference)
- Temporal proximity without causal proof (correlation ≠ causation)
- User report of behavior without evidence channel

### 7.11 UNKNOWN Handling

When ActualConsequence attributes are UNKNOWN:

```
identity = KNOWN          (UUID generated at observation time)
action = UNKNOWN          (action_id not found in execution log)
  → Consequence may be spontaneous or recording error
  → Status: UNRESOLVED (requires investigation)

state_before = UNKNOWN    (prior state not captured)
  → Cannot determine state_after significance
  → Status: NOT_PROVEN (consequence magnitude uncertain)

observation = UNKNOWN     (evidence channel malfunction)
  → Cannot verify consequence actually occurred
  → Status: NOT_FOUND (no evidence of observation)

authorization = UNKNOWN   (authorization record missing)
  → Consequence is unsanctioned or authorization lookup failed
  → Status: UNRESOLVED (critical gap)
```

**Handling Rule:** ActualConsequence with UNKNOWN authorization or observation defaults to NOT_PROVEN status.

### 7.12 UNDEFINED Handling

UNDEFINED indicates a concept that was never formalized in Layer 2:

```
scope = UNDEFINED         (ConsequenceScope type never created)
  → Consequences recorded; cannot categorize/filter
  → Status: PROPOSED (design needed in L2-04)

consequence_type = UNDEFINED (no taxonomy of consequence kinds)
  → Permission, state, behavior, data, timing, availability
  → Status: NOT_ESTABLISHED (no formal classification)
```

**Handling Rule:** UNDEFINED attributes do not invalidate ActualConsequence existence; they limit its usability.

### 7.13 NOT_PROVEN Handling

NOT_PROVEN indicates the precondition/postcondition is unverified:

```
Precondition: Authorization issued = NOT_PROVEN
  → Observation exists; authorization lookup failed
  → Consequence recorded; authorization claim unverified
  → Severity: High (breaks authorization-consequence link)

Postcondition: Target Invariant satisfied = NOT_PROVEN
  → Consequence observed; invariant proof absent
  → Cannot confirm execution was legitimate
  → Severity: High (breaks M18 closure)
```

**Handling Rule:** NOT_PROVEN consequences are recorded; cannot propagate to Authorization → Consequence → M18 binding chain until proven.

### 7.14 Scope Boundary

ActualConsequence scope is defined by:

1. **Subject:** Who/what executed the action (actor identity)
2. **Resource:** What was affected (target of action)
3. **Permission:** Which authorization applied (authorization scope)
4. **Temporal:** When the consequence was observed (timestamp window)
5. **Magnitude:** How large was the state change (impact measure)

**Boundary Violations:**

- Consequence affects resource outside authorization subject scope → BOUNDARY_VIOLATION
- Consequence occurs after authorization expiration → BOUNDARY_VIOLATION
- Consequence magnitude exceeds authorization limit (if limit defined) → BOUNDARY_VIOLATION

**Current Status:** Boundary definition NOT_ESTABLISHED (pending L2-04 Authorization Scope formalization)

### 7.15 Examples

**Example 1: Permission Change (GL7 Tool-Level)**

```
Authorization: Grant read access to resource R1
Action: User calls read(R1)
State Before: user.permissions = {read:R1=false}
GL7 Emit: ALLOW (decision: read authorized)
State After: GL7 gate opened; read executed
Observation: Access log entry recorded
ActualConsequence: {
  identity: UUID-001
  action: read(R1)
  authorization: grant-read-R1
  state_before: {permissions: {R1: false}}
  state_after: {read executed; data returned}
  observation: {gl7_event: ALLOW, access_log: ✓}
  timestamp: 2026-09-13T10:00:00Z
  evidence_status: OBSERVED (GL7 + log)
  scope: (actor=user, resource=R1, permission=read)
}
```

**Validity:** Consequence observed; authorization matched; state change proven by GL7 + log.

---

**Example 2: State Change (Unobserved Authorization)**

```
Action: Database write to table T1
State Before: T1.rows = 1000
State After: T1.rows = 1001
Observation: T1 row count changed (source: DB audit log)
GL7 Event: NOT_FOUND (no GL7 gate on DB writes)
Authorization: NOT_FOUND (write not authorized; no record)

ActualConsequence: {
  identity: UUID-002
  action: write(T1)
  authorization: NOT_FOUND
  state_before: {T1.rows: 1000}
  state_after: {T1.rows: 1001}
  observation: {audit_log: ✓, gl7_event: NOT_FOUND}
  timestamp: 2026-09-13T10:05:00Z
  evidence_status: NOT_PROVEN (authorization missing)
  scope: (actor: unknown, resource: T1, permission: UNKNOWN)
}
```

**Validity Issue:** Consequence observed (state change proven); authorization unknown. Record exists but cannot propagate to authorization-consequence chain. Status: NOT_PROVEN.

---

### 7.16 Counterexamples

**Counterexample 1: Execution Appears Successful; Consequence Actually Absent**

```
Scenario:
  Authorization: Grant delete access to record R1
  Action: User calls delete(R1)
  GL7 Gate: ALLOW (decision looks correct)
  User Experience: "Delete successful" message appears
  
  But actually:
    - R1 not found in database
    - Delete operation skipped silently
    - "Success" message is generic (not consequence-specific)
    - State Change: state_after = state_before (no change)
  
  Definition Test:
    Does this count as ActualConsequence?
    - action exists: YES
    - authorization exists: YES
    - GL7 emit exists: YES
    - state_before ≠ state_after: NO
    
  Semantic Boundary Violation:
    GL7 ALLOW + state_before = state_after → BOUNDARY_VIOLATION
    ActualConsequence requires state_after ≠ state_before
    
  Conclusion:
    This is NOT ActualConsequence; it is AUTHORIZATION_WITHOUT_CONSEQUENCE
    (authorization was granted; nothing actually happened)
```

**Lesson:** Mere ALLOW decision is insufficient; actual state change required.

---

**Counterexample 2: Consequence Without Authorization**

```
Scenario:
  Authorization: NOT_FOUND (no authorization record for this action)
  Action: System service performs internal cleanup
  State Before: temp_files = 5000
  State After: temp_files = 0 (cleaned up)
  GL7 Gate: N/A (internal action, no GL7)
  Observation: Log entry: "cleanup completed"
  
  Definition Test:
    Does this count as ActualConsequence?
    - state_before ≠ state_after: YES
    - authorization: NOT_FOUND
    - observation: YES
    - action: YES (system cleanup)
    
  Semantic Boundary Violation:
    ActualConsequence requires authorization precondition
    This is CONSEQUENCE_WITHOUT_AUTHORIZATION
    
  Conclusion:
    Consequence observed; cannot bind to authorization chain
    Record as ActualConsequence with evidence_status = NOT_PROVEN
    Cannot propagate to M18 closure (requires authorization)
```

**Lesson:** Unauthorized consequences cannot propagate up the chain; remain isolated.

---

**Counterexample 3: Observation Error (State Unchanged; Observation Faulty)**

```
Scenario:
  Authorization: Grant write to R1
  Action: user.update(R1)
  GL7: ALLOW
  State Before: R1.value = 10
  State After: R1.value = 10 (unchanged)
  
  But observation system reports:
    "State changed from 10 to 20"
  
  Definition Test:
    Does this count as ActualConsequence?
    - GL7: ALLOW
    - observation reports change
    - actual state: UNCHANGED
    
  Semantic Boundary Violation:
    Observation contradicts reality (false positive)
    ActualConsequence requires state_before ≠ state_after VERIFIED
    Not just reported; must be independently verifiable
    
  Conclusion:
    This is OBSERVATION_ERROR, not ActualConsequence
    Cannot be recorded as consequence
    Must investigate observation channel malfunction
```

**Lesson:** Observation must be verified against independent evidence (state snapshots, multiple sensors).

---

### 7.17 Open Questions

1. **Latency Window:** Can there be delay between action execution and consequence observation? How much delay is acceptable?
   - Status: NOT_PROVEN
   - Required: Evidence on observation latency tolerance

2. **Consequence Magnitude:** Is there a minimum state change that counts as a consequence? (e.g., bit flip vs permission change)
   - Status: UNDEFINED
   - Required: L2-04 Authorization Scope definition

3. **Permission vs Behavior:** Are "permission granted" and "behavior executed" two different consequence types?
   - Status: UNKNOWN
   - Required: Design of consequence taxonomy

4. **Cascading Consequences:** If action A causes consequence C1, which triggers action B, causing consequence C2, are both C1 and C2 attributed to original authorization?
   - Status: NOT_PROVEN
   - Required: Evidence on consequence attribution in cascades

5. **Observation Channel Failure:** If observation channel malfunction is later discovered, can ActualConsequence records be invalidated retroactively?
   - Status: UNRESOLVED
   - Required: Policy decision on evidence integrity vs immutability

---

## 8. L2-02: AuthorizedConsequence — Formal Semantic Design

### 8.1 Definition

**AuthorizedConsequence** is the formal type representing consequences that are explicitly authorized to occur as a result of an authorized action.

```
AuthorizedConsequence
  = Formal specification of:
    - What consequences are permitted (authorization scope)
    - Under what conditions they are permitted (temporal, contextual)
    - By which authorization decision (authorization reference)
    - With what evidence requirements
    - Subject to what constraints/limits
```

**Relationship to ActualConsequence:**
```
Authorization
  ↓ (defines bounds)
AuthorizedConsequence
  ↓ (target for achievement)
ActualConsequence
  ↓ (realized in runtime)
Evidence (GL7 event, state change, log)
```

**Evidence Basis:** SPP/PHL v1.0 framework; no implementation evidence yet (Layer 3 NOT_FOUND).

### 8.2 Semantic Purpose

AuthorizedConsequence serves three functions:

1. **Authorization Specification:** Explicitly states what is permitted (vs implicit or inferred)
2. **Verification Criterion:** Provides target against which actual consequences are measured
3. **Constraint Declaration:** Sets limits on consequence magnitude/scope

Without AuthorizedConsequence, authorization becomes:
- "You may execute action X" (says what you can do)
- But NOT: "Y are the permitted consequences" (leaves consequences ambiguous)

### 8.3 Type / Structure

**Proposed Structure:**

```
AuthorizedConsequence {
  identity            : UUID                  // unique specification
  authorization       : Authorization         // parent authorization
  consequence_type    : ConsequenceType       // PERMISSION | BEHAVIOR | STATE | DATA | TIMING | AVAILABILITY
  scope               : ConsequenceScope      // WHO/WHEN/WHAT/WHERE definitions
  permitted_values    : Set<Value>            // what outcome values are authorized
  constraints         : Constraints           // limits (magnitude, rate, frequency)
  evidence_required   : EvidenceRequirement   // what proof is needed for verification
  temporal_window     : (start, end)          // authorization validity period
  revocation_trigger  : Condition             // condition that nullifies this authorization
  status              : (ACTIVE | REVOKED | EXPIRED | SUPERSEDED)
}
```

**Status:** PROPOSED (structure tentative; depends on L2-04 scope formalization)

### 8.4 Authorization Relation

AuthorizedConsequence is defined BY an Authorization decision.

**Relationship:**
```
Authorization (decision)
  ↓ creates/specifies
AuthorizedConsequence (specification)
  ↓ constrains what
ActualConsequence (runtime)
  can be
```

**Binding Rules:**
- One Authorization can specify multiple AuthorizedConsequences (e.g., read permission allows multiple reads)
- One AuthorizedConsequence is bound to exactly one Authorization
- If Authorization is revoked, all associated AuthorizedConsequences are invalidated

**Status:** PROPOSED (binding mechanics not yet specified in code)

### 8.5 Scope Relation

AuthorizedConsequence scope relates to Authorization Scope (L2-04).

**Relationships to Explore:**

1. **AuthorizedConsequence Scope ⊆ Authorization Scope**
   - Consequence must be within authorization bounds
   - E.g.: "authorized to read file" → consequence is "file data returned" (subset of what auth permits)

2. **AuthorizedConsequence Scope = Authorization Scope**
   - Consequence directly matches authorization
   - E.g.: "permission to execute script" → consequence is "script executes"

3. **AuthorizedConsequence Scope ⊃ Authorization Scope**
   - Consequence exceeds authorization (VIOLATION)
   - E.g.: "read permission" → consequence is "also modify file" (superset violation)

**Status:** UNRESOLVED (Subset/superset relationship requires L2-04 scope definitions)

### 8.6 Evidence Requirements

To claim AuthorizedConsequence is valid:

| Evidence Item | Required | Current Status | Note |
|---|---|---|---|
| Authorization decision record | YES | FOUND (L1) | Must be explicit, not inferred |
| Consequence specification | RECOMMENDED | NOT_ESTABLISHED | What consequences does this authorization permit? |
| Scope definition (WHO/WHEN/WHAT) | RECOMMENDED | NOT_FOUND | Without scope, consequence is undefined |
| Constraint specification | OPTIONAL | NOT_FOUND | If authorization has limits |
| Evidence requirement spec | OPTIONAL | NOT_FOUND | What constitutes proof of consequence? |

**Overall Status:** PARTIAL (Authorization record exists; consequence specification NOT_ESTABLISHED)

### 8.7 UNKNOWN / UNDEFINED / NOT_PROVEN Handling

**UNKNOWN AuthorizedConsequence:**
```
Scenario: Authorization record found; consequence intent unclear
  - Authorization says: "Grant access to R1"
  - Does NOT say: "Therefore, data from R1 must be returned" (inference)
  - Or: "Therefore, R1 access count incremented" (side effect)
  
Handling: AuthorizedConsequence = UNKNOWN
  - Authorization valid; consequences unspecified
  - Cannot measure compliance (ActualConsequence vs AuthorizedConsequence)
  - Status: Design gap (L2-02 not yet formalized for this case)
```

**UNDEFINED AuthorizedConsequence Scope:**
```
Scenario: Authorization given; scope not formalized
  - Authorization: "Read permission"
  - Scope undefined: Does this permit? {read + cache? read + log? read + export?}
  - Each is a consequence type; none explicitly authorized
  
Handling: AuthorizedConsequence.scope = UNDEFINED
  - Consequences observable; cannot categorize as authorized/unauthorized
  - Status: NOT_ESTABLISHED (L2-04 Authorization Scope needed)
```

**NOT_PROVEN AuthorizedConsequence Constraint:**
```
Scenario: Authorization specifies limit; limit verification absent
  - Authorization: "Read up to 1000 records"
  - Evidence: No verification mechanism exists to prove "actually limited to 1000"
  - ActualConsequence: "Read 5000 records"
  
Handling: Constraint NOT_PROVEN
  - Consequence was permitted in principle; limit not enforced
  - Cannot claim constraint violation without verification evidence
  - Status: UNRESOLVED (requires Layer 3/4 implementation)
```

### 8.8 Scope Boundary

AuthorizedConsequence must distinguish:

1. **Authorization Boundary:** What the authorization decision permits
2. **Consequence Boundary:** What consequences can actually occur
3. **Verification Boundary:** What evidence can prove a consequence occurred
4. **Enforcement Boundary:** What mechanisms can prevent unauthorized consequences

**Boundaries Often Misaligned:**
- Authorization permits action X
- But consequences of X are unspecified (boundary gap)
- Consequence-checking code assumes consequences (boundary inference)
- Runtime enforcement misses some consequences (boundary gap)

**Current Status:** All boundaries NOT_ESTABLISHED (L2-02 design phase)

### 8.9 Examples

**Example 1: Simple Read Authorization**

```
Authorization: Grant read access to resource R1

AuthorizedConsequence {
  identity: AC-UUID-001
  authorization: read-R1-auth
  consequence_type: PERMISSION
  scope: {
    WHO: user=alice
    WHEN: 2026-09-13 to 2026-12-13
    WHAT: read R1 (return data from R1)
  }
  permitted_values: {any data from R1}
  constraints: {rate: ≤100 reads/hour}
  evidence_required: {GL7 ALLOW + access log}
  temporal_window: [2026-09-13, 2026-12-13]
  revocation_trigger: {alice.status = REVOKED}
  status: ACTIVE
}
```

**Design Question:** Is "return data from R1" a consequence, or just the mechanism? (Status: UNKNOWN)

---

**Example 2: Delete Authorization with Constraint**

```
Authorization: Grant delete access to archive records, max 100/day

AuthorizedConsequence {
  identity: AC-UUID-002
  authorization: delete-archive-auth
  consequence_type: STATE (data removal)
  scope: {
    WHO: admin=sysadmin
    WHEN: daily, 2026-09-13 onwards
    WHAT: delete record from archive table
  }
  permitted_values: {any archived records}
  constraints: {
    daily_limit: 100
    rate_limit: 10/minute
    allowed_status: (ARCHIVED | EXPIRED)
  }
  evidence_required: {GL7 ALLOW + DB audit log + state change proof}
  temporal_window: [2026-09-13, unbounded]
  revocation_trigger: {admin access revoked OR daily_limit exceeded 3x}
  status: ACTIVE
}
```

**Design Gap:** How is daily_limit verified? No mechanism exists yet. (Status: NOT_PROVEN)

---

### 8.10 Counterexamples

**Counterexample 1: Authorization Exists; AuthorizedConsequence Specification Absent**

```
Scenario:
  Authorization Record: "Grant write permission to file F"
  AuthorizedConsequence: NOT_FOUND (specification never created)
  
  At Runtime:
    Action: user writes 1000 bytes to F
    ActualConsequence: Recorded (state changed, GL7 ALLOW)
    
  Question: Is write authorized?
    - Authorization record: YES (permission exists)
    - AuthorizedConsequence spec: NO (consequence never specified)
    - Cannot measure compliance (no target to measure against)
  
  Semantic Boundary Violation:
    Authorization without AuthorizedConsequence spec = ambiguous
    Cannot determine: Did this consequence exceed permission?
    
  Conclusion:
    Authorization valid; AuthorizedConsequence NOT_ESTABLISHED
    Consequence cannot be verified as compliant
    Status: UNRESOLVED (design gap)
```

**Lesson:** Authorization ≠ AuthorizedConsequence. Both must be explicit.

---

**Counterexample 2: AuthorizedConsequence Constraint Violated; No Enforcement**

```
Scenario:
  Authorization: "Read up to 10 records/request"
  AuthorizedConsequence.constraints: {max_records: 10}
  
  At Runtime:
    Action: user.read(query) → returns 500 records
    GL7: ALLOW (decision looked at authorization; constraint not checked)
    ActualConsequence: State changed (500 records returned)
    
  Question: Is consequence authorized?
    - AuthorizedConsequence spec: YES (exists)
    - Constraints: Specified (max 10)
    - Actual consequence: Exceeds constraint (500 > 10)
    - Enforcement: ABSENT (GL7 did not check constraint)
    
  Semantic Boundary Violation:
    ActualConsequence (500) > AuthorizedConsequence.permitted_values (≤10)
    
  Conclusion:
    Consequence violates authorization scope
    No enforcement mechanism prevented violation
    Status: BOUNDARY_VIOLATION (requires L3/L4 implementation to prevent)
```

**Lesson:** Specification alone is insufficient; enforcement required.

---

**Counterexample 3: Revocation Not Enforced**

```
Scenario:
  AuthorizedConsequence: {status: ACTIVE, revocation_trigger: {admin_access_revoked}}
  
  Timeline:
    T1: admin.access.status = ACTIVE
    T2: admin.access.status = REVOKED (revocation decision made)
    T3: admin attempts action → GL7 ALLOW (cache not updated)
    T4: ActualConsequence: recorded (action executed)
    
  Question: Is consequence authorized?
    - At T1: AuthorizedConsequence valid
    - At T2: revocation_trigger fired (should invalidate)
    - At T3: GL7 did not recheck (stale cache)
    - At T4: Consequence recorded as authorized (but was revoked)
    
  Semantic Boundary Violation:
    AuthorizedConsequence.status changed (ACTIVE → REVOKED)
    But consequence still proceeded
    
  Conclusion:
    AuthorizedConsequence was revoked
    ActualConsequence recorded as valid (faulty)
    Cannot verify compliance retroactively
    Status: ENFORCEMENT_GAP (revocation not checked in time)
```

**Lesson:** Revocation requires runtime enforcement; specification alone insufficient.

---

## 9. L2-03: CO (Consequential Outcome) — Formal Semantic Design

### 9.1 Current Evidence on CO

**Existing Evidence:**
- R01 Investigation: CO type/meaning = UNKNOWN
- Searching codebase: "CO" appears in comments but not formally defined
- Paper 3.5ζ reference: Not accessible in current session
- L2 Design Gate Decision Package: Lists "CO formal meaning/type definition needed"

**Evidence Status:**
```
CO exists as: Concept name (referenced in documentation)
CO exists as: Informal usage (in code comments, variable names)
CO exists as: Formal type: NOT_ESTABLISHED
CO exists as: Runtime observation: NOT_FOUND
CO exists as: Semantic relation: UNKNOWN
```

### 9.2 Hypothesis on CO Meaning

**Possible Interpretations (Evidence-Bounded):**

1. **CO as "Consequential Outcome"** (naming convention suggests)
   - Outcome = result of consequence chain
   - Consequential = attributed to authorization/action
   - CO = final observable result after all cascades

2. **CO as "Captured Observation"** (possible technical meaning)
   - Captured = recorded/logged
   - Observation = what was detected
   - CO = evidence artifact for consequence

3. **CO as "Change Order"** (possible process meaning)
   - Change = state modification
   - Order = authorization/request
   - CO = formal record linking authorization to state change

**Status:** All three are PROPOSED. Without evidence, cannot decide.

### 9.3 CO Layering

CO exists at multiple levels; design must separate them:

**Layer 1: CO as Concept**
- Naming: "Consequential Outcome"
- Reference: Used in governance discussions
- Status: KNOWN (named; meaning unclear)

**Layer 2: CO as Formal Type** (L2-03 objective)
- Structure: What fields/properties does CO have?
- Identity: How is one CO instance distinguished from another?
- Semantics: What relationship does CO have to Authorization/ActualConsequence?
- Status: UNKNOWN (requires formalization)

**Layer 3: CO as Implementation**
- Code representation: struct/class/record
- Storage: How is CO persisted?
- Query: How is CO retrieved?
- Status: NOT_FOUND (implementation deferred to Layer 3)

**Layer 4: CO as Runtime Observation**
- Detection: What evidence channel observes CO?
- Recording: How is CO capture verified?
- Verification: How do we know CO was recorded correctly?
- Status: NOT_PROVEN (verification deferred to Layer 4)

### 9.4 CO Relationship to Other L2 Concepts

**Hypothesis: CO as Post-Consequence Record**

```
Action
  ↓
Authorization Decision
  ↓
Execution Attempt
  ↓
ActualConsequence (observed state change)
  ↓
CO (consequential outcome record)
  ↓
Evidence (log entry, audit trail)
```

**Under this model:**
- ActualConsequence = raw observation (state_before → state_after)
- CO = interpreted consequence (what does this state change MEAN?)
- Relationship: CO interprets ActualConsequence

**Evidential Support:** PROPOSED (no evidence yet; plausible)

---

**Alternative: CO as Consequence Artifact**

```
Authorization
  ↓
AuthorizedConsequence (specification)
  ↓
ActualConsequence (runtime observation)
  ↓ (binds to)
CO (the consequential outcome instance)
  ↓ (with metadata)
Evidence Record
```

**Under this model:**
- CO is the conjunction of AuthorizedConsequence + ActualConsequence
- CO = "this actual consequence was authorized"
- Relationship: CO = authorization compliance proof

**Evidential Support:** PROPOSED (aligns with M18 closure needs)

### 9.5 CO Formal Type — Candidate Design

**Without definitive evidence, propose for HG review:**

```
ConsequentialOutcome {
  identity            : UUID
  consequence_id      : ActualConsequence.identity      // what actually happened
  authorization_id    : Authorization.identity          // under which authorization
  authorized_spec_id  : AuthorizedConsequence.identity  // was it in scope?
  
  compliance_status   : (WITHIN | EXCEEDS | VIOLATES | UNKNOWN)
  scope_binding       : Authorization Scope evaluation result
  timestamp           : observation timestamp
  
  evidence_sources    : [EvidenceRecord]                // pointers to GL7 events, logs
  interpretation      : (AUTHORIZED | UNAUTHORIZED | AMBIGUOUS)
  
  m18_relevance       : (RELEVANT | IRRELEVANT | UNKNOWN)  // does this count toward M18?
}
```

**Status:** PROPOSED (candidate for HG design review)

### 9.6 CO and M18 Closure

**Design Hypothesis:**

M18 Runtime Closure requires:
1. ActualConsequence observed (runtime fact)
2. AuthorizedConsequence specification (design fact)
3. CO binding (compliance proof)

**Proposed Semantics:**
- M18 closure scope = all CO instances where compliance_status ≠ UNKNOWN
- M18 verification = aggregate compliance_status across all CO for target invariant

**Status:** PROPOSED (depends on M18-Scope definition; requires HG determination)

### 9.7 Open Questions on CO

1. **Is CO optional or mandatory?** Can we have ActualConsequence without CO?
   - Status: UNRESOLVED

2. **What is the minimal CO?** Must have all fields, or just identity + compliance_status?
   - Status: NOT_ESTABLISHED

3. **Can CO be created retroactively?** Or must CO exist contemporaneously with ActualConsequence?
   - Status: UNDEFINED

4. **Multiple CO per ActualConsequence?** Can one consequence have multiple interpretations/CO records?
   - Status: UNKNOWN

5. **CO lifecycle:** Once created, can CO be modified/revoked?
   - Status: NOT_PROVEN

---

## 10. L2-04: Authorization Scope — Formal Semantic Design

### 10.1 Definition

**Authorization Scope** is the formal specification of the three-dimensional boundaries within which an authorization grants permission.

```
Authorization Scope
  = (WHO × WHEN × WHAT) + optional extensions
    where:
      WHO   = identity of authorized subject (who may act)
      WHEN  = temporal validity (when is authorization active)
      WHAT  = action/consequence permitted (what may be done)
      + optionally: WHERE, CONTEXT, EVIDENCE, EXPIRATION, REVOCATION, SUPERSESSION
```

### 10.2 Core 3D Separation

**WHO Dimension: Subject Identity**

```
WHO = {
  subject_id: (user | service | role | group),
  verification_method: (password | certificate | delegation | inference),
  constraints: (location | device | session | temporal)
}
```

**Examples:**
- WHO = "alice@example.com" (user identity)
- WHO = "backup-service" (service identity)
- WHO = "admin-role" (role-based identity)
- WHO = "alice@example.com FROM 192.168.1.0/24" (identity + constraint)

**Status:** EXISTS in L1 (governance framework); formalization PROPOSED for L2

---

**WHEN Dimension: Temporal Validity**

```
WHEN = {
  issued_at: timestamp,
  expires_at: timestamp | null (null = no expiration),
  valid_from: timestamp,
  valid_until: timestamp,
  window: (continuous | discrete | periodic),
  timezone: string
}
```

**Examples:**
- WHEN = [2026-09-13T00:00:00Z, 2026-09-20T23:59:59Z] (one-week window)
- WHEN = [2026-09-13T00:00:00Z, NULL] (from now, no expiration)
- WHEN = every Monday 09:00-17:00 UTC (periodic access)
- WHEN = session duration (temporary; tied to session lifecycle)

**Status:** EXISTS in L1; formalization PROPOSED for L2

---

**WHAT Dimension: Action / Consequence Permitted**

```
WHAT = {
  action_type: (read | write | execute | admin | custom),
  resource: (file | database | service | api | system),
  resource_scope: (specific | class | wildcard | regex),
  consequence_class: (permission | behavior | state | data | timing),
  constraints: (rate_limit | size_limit | count_limit | custom_predicate)
}
```

**Examples:**
- WHAT = "read file /var/log/app.log" (specific resource, specific action)
- WHAT = "write to database.users.*" (class of resources)
- WHAT = "execute any script in /opt/scripts/" (wildcard; constraint: rate ≤5/hour)
- WHAT = "modify own profile; read public profiles" (multiple actions)

**Status:** PARTIALLY_ESTABLISHED (L1 concept); formalization PROPOSED for L2

### 10.3 Proposed Extended Dimensions

**WHERE Dimension: Spatial / Network Scope** (optional)

```
WHERE = {
  allowed_locations: [location],          // geographic
  allowed_networks: [CIDR],               // network ranges
  allowed_devices: [device_id],           // device identities
  denied_locations: [location],           // exclusions
  vpn_required: boolean
}
```

**Example:** "Grant read access FROM office.example.com OR vpn-gate.example.com; DENY from public_wifi"

**Status:** PROPOSED (not yet in L1; emerging L3 requirement)

---

**CONTEXT Dimension: Situational Constraints** (optional)

```
CONTEXT = {
  required_mfa: boolean,
  required_audit_log: boolean,
  required_approval: (none | peer | manager | hierarchy),
  risk_level: (low | medium | high | critical),
  allowed_risk_contexts: [risk_condition]
}
```

**Example:** "Grant admin access only when audit_log is enabled AND MFA is verified AND manager approval recorded"

**Status:** PROPOSED (policy-level constraint; not yet formalized)

---

**EVIDENCE Dimension: Verification Requirements** (optional)

```
EVIDENCE = {
  required_proof: [ProofType],      // what must be verified
  verification_method: [Method],    // how to verify
  chain_of_custody: (required | optional | forbidden),
  audit_trail: (required | optional),
  independent_verification: (required | optional)
}
```

**Example:** "Grant confidential data access only with: cryptographic proof of identity + independent audit verification + chain-of-custody log"

**Status:** PROPOSED (evidence discipline emerging)

---

**EXPIRATION Dimension: Time-Limited Validity** (optional)

```
EXPIRATION = {
  fixed_expiration: timestamp | null,      // authorization expires at time
  inactivity_expiration: duration,         // expires if unused for duration
  action_count_expiration: integer,        // expires after N uses
  revocation_check_interval: duration      // how often to recheck validity
}
```

**Example:** "Grant temporary access: expires 2026-09-20 OR after 10 uses OR if unused for 24 hours (check every 1 hour)"

**Status:** PROPOSED (partial implementation exists)

---

**REVOCATION Dimension: Invalidation Conditions** (optional)

```
REVOCATION = {
  immediate_revocation: [Condition],      // revoke immediately if true
  deferred_revocation: [Condition],        // revoke after notice period
  revocation_validator: function,          // custom revocation logic
  revocation_timestamp: timestamp          // when revocation occurred
}
```

**Example:** "Revoke immediately if subject.status = SUSPENDED OR subject.org = DISSOLVED; revoke with 7-day notice if subject changes teams"

**Status:** PROPOSED (governance event exists; formal scope not defined)

---

**SUPERSESSION Dimension: Authorization Replacement** (optional)

```
SUPERSESSION = {
  superseded_by: [Authorization.id],       // newer authorizations that replace this
  supersedes: [Authorization.id],          // older authorizations replaced by this
  supersession_date: timestamp,
  compatibility_mode: (strict | lenient)   // how to handle conflicts
}
```

**Example:** "This authorization supersedes auth-2026-001; use lenient mode (both valid until 2026-09-20, then old one invalidated)"

**Status:** PROPOSED (upgrade/versioning concept; not yet formalized)

### 10.4 Authorization Scope Semantics

**Scope Validation Rules:**

1. **Intersection Rule:** Actual consequence must be in ALL dimensions
   ```
   ActualConsequence valid iff:
     (subject ∈ WHO) AND
     (timestamp ∈ WHEN) AND
     (action ∈ WHAT) AND
     (location ∈ WHERE) AND
     (context satisfies CONTEXT) AND
     ...
   ```

2. **Subset Rule:** Narrower scope subsumes broader scope
   ```
   Scope1 ⊆ Scope2 iff:
     Scope1.WHO ⊆ Scope2.WHO AND
     Scope1.WHEN ⊆ Scope2.WHEN AND
     Scope1.WHAT ⊆ Scope2.WHAT
   ```

3. **Override Rule:** More specific dimension overrides general
   ```
   Scope = {
     general: (all employees, 2026-09-13 to 2026-09-30, read)
     exception: (alice only, 2026-09-13 to 2026-09-15, read+write)
   }
   => alice has more specific scope during 2026-09-13 to 2026-09-15
   ```

**Status:** PROPOSED (semantics defined; implementation logic NOT_FOUND)

### 10.5 Authorization Scope ↔ AuthorizedConsequence Relationship

**Design Question:** How does Authorization Scope relate to AuthorizedConsequence?

**Hypothesis 1: Scope Defines Consequence Bounds**
```
Authorization Scope (WHO/WHEN/WHAT)
  ↓ (constrains)
AuthorizedConsequence (what consequences are permitted)
  ↓ (must fit within)
Permitted consequences ⊆ Authorization Scope.WHAT
```

**Hypothesis 2: Consequence Determines Scope Applicability**
```
AuthorizedConsequence (consequence specification)
  ↓ (triggers evaluation of)
Authorization Scope (which scope applies to this consequence?)
  ↓ (result)
Is consequence within scope?
```

**Hypothesis 3: Scope and Consequence are Orthogonal**
```
Authorization Scope (identity/temporal bounds)
    ≠
AuthorizedConsequence (what consequences authorized)

Both must be satisfied independently
```

**Status:** UNRESOLVED (relationship requires evidence on how authorizations are actually interpreted)

### 10.6 Current Gaps in Authorization Scope

**Existing Evidence:**
- L1: Authorization Scope concept exists (SPP/PHL framework)
- L2: Formal 3D separation (WHO/WHEN/WHAT) NOT_ESTABLISHED
- L3: Scope checking code (GL7 gate) PARTIAL (Tool-level READ_ONLY/WRITE only)
- L4: Scope enforcement runtime PARTIAL (GL7 emit exists; constraint validation NOT_FOUND)

**Major Gaps:**
```
Gap #1: WHERE dimension not formalized
Gap #2: CONTEXT constraints not specified
Gap #3: Scope intersection validation logic NOT_FOUND
Gap #4: Revocation timing not defined
Gap #5: Supersession rules not established
Gap #6: Scope override precedence not specified
```

**Impact on M18 Closure:**
- M18 verification requires knowing which paths are in scope
- M18-Scope (UNRESOLVED) depends on Authorization Scope formalization
- Cannot close M18 without scope clarity

### 10.7 Examples

**Example 1: Simple 3D Scope**

```
Authorization: Grant read to resource "employees.csv"

AuthorizationScope {
  WHO: {subject_id: "alice", verification: password, constraints: none}
  WHEN: {from: 2026-09-13T00:00Z, to: 2026-09-20T23:59Z}
  WHAT: {action: read, resource: employees.csv, constraints: none}
}

Validation:
  Alice at 2026-09-14 reading employees.csv
  => WHO matches: alice ✓
  => WHEN matches: 2026-09-14 ∈ [2026-09-13, 2026-09-20] ✓
  => WHAT matches: read action on employees.csv ✓
  => Result: AUTHORIZED
```

---

**Example 2: Scoped 3D + CONTEXT Constraint**

```
Authorization: Grant admin access to database, MFA required

AuthorizationScope {
  WHO: {subject_id: "bob", verification: certificate, constraints: none}
  WHEN: {from: 2026-09-13, to: null (no expiration)}
  WHAT: {action: admin, resource: db.*, constraints: admin role required}
  CONTEXT: {required_mfa: true, required_audit_log: true}
}

Scenario 1 - AUTHORIZED:
  Bob, with MFA verified, audit log enabled
  => All dimensions satisfied
  => Result: AUTHORIZED

Scenario 2 - NOT AUTHORIZED:
  Bob, MFA not verified, audit log enabled
  => CONTEXT constraint not satisfied
  => Result: NOT AUTHORIZED (MFA failure)

Scenario 3 - AMBIGUOUS:
  Bob, MFA verified, audit log status unknown
  => CONTEXT.required_audit_log: true (but status unknown)
  => Result: UNKNOWN (cannot verify all constraints)
```

---

### 10.8 Counterexamples

**Counterexample 1: Scope Definition Ambiguous; Actual Consequence Violates Unstated Constraint**

```
Authorization: "Grant read access to sensitive data"

Scope Definition (AMBIGUOUS):
  WHO: alice
  WHEN: 2026-09-13 to 2026-09-20
  WHAT: "read sensitive data" (undefined: which data? all? subset?)
  
At Runtime:
  Action: Alice reads 50,000 sensitive records
  GL7 Gate: ALLOW (scope looks valid)
  ActualConsequence: 50,000 records read + exported to USB drive
  
Question: Is consequence authorized?
  - Scope permits "read": YES
  - Scope permits "export to USB": NOT DEFINED
  - Expected behavior: read in place (no export)
  - Actual behavior: read + export
  
Semantic Boundary Violation:
  ActualConsequence.action (export) NOT in WHAT.action (read only)
  Scope ambiguity allowed unexpected behavior
  
Lesson: WHAT dimension must be unambiguous; undefined actions create gaps
```

---

**Counterexample 2: Scope Intersection Not Checked**

```
Authorization 1: "Grant read to bob on Mon-Fri 09:00-17:00 UTC"
Authorization 2: "Grant write to bob on Sat-Sun 18:00-23:00 UTC"

At Runtime:
  Saturday 10:00 UTC: Bob attempts write
  Auth1 checked: Saturday NOT in Mon-Fri => REJECT
  Auth2 checked: NOT at 18:00-23:00 UTC => REJECT
  GL7 result: REJECT (correct)
  
But what if implementations checked UNION instead of INTERSECTION?
  Auth1 OR Auth2: "Mon-Fri 09-17 OR Sat-Sun 18-23"
  Saturday 10:00: Matches (Sat-Sun range)
  GL7 result: ALLOW (WRONG - outside time window, wrong day)
  
Semantic Boundary Violation:
  Scope intersection rule violated
  Disjunction used instead of conjunction
  
Lesson: Scope must use intersection (AND) not union (OR); mistakes create authorization creep
```

---

**Counterexample 3: Revocation Not Enforced in Time**

```
Authorization: Read permission for alice, revocation_check_interval = 1 hour

Timeline:
  T0: Authorization created; valid
  T30min: Authorization.revocation_trigger fires (alice.status = SUSPENDED)
  T30min+: GL7 cache still has valid auth (next check at T60min)
  T45min: Alice reads sensitive data
  GL7: ALLOW (stale cache; revocation not yet checked)
  ActualConsequence: Data read (unauthorized)
  
Question: Is consequence authorized?
  - At T0: YES
  - At T30min: Revocation condition met
  - At T45min: revocation not yet detected (stale cache)
  - Consequence: Unauthorized read (revocation not yet visible)
  
Semantic Boundary Violation:
  Authorization Scope became invalid (revocation fired)
  But GL7 did not detect (cache staleness)
  
Lesson: Scope validation must include revocation check; cache timing matters
```

---

## 11. L2-05: Semantic Closure Relationship — Formal Semantic Design

### 11.1 Definition

**Semantic Closure** in this context means: achieving confidence that all authorization→consequence pathways are:
1. Formally specified (known)
2. Runtime-observable (verifiable)
3. Verified as compliant (proven)

**Semantic Closure Relationship** is the formal specification of:
- What conditions must be satisfied to achieve closure
- What evidence is required for closure verification
- What constitutes failure to achieve closure
- How unknown or unproven items propagate

**Current State:** NOT_ACHIEVED (and must remain NOT_ACHIEVED during this design phase)

### 11.2 Closure vs Semantic Closure

**Important Distinction:**

```
Closure            = M18 Runtime Closure (architectural goal)
                   = All 109 observed routes verified as authorized/authorized
                   = State: NOT_ACHIEVED / LOCKED

Semantic Closure   = Layer 2 semantic definitions formalized
                   = Authorization→Consequence pathway clear
                   = State: NOT_ACHIEVED (remains unfulfilled after L2 design)
```

**Relationship:**
```
Semantic Closure formalization (L2-05)
  ↓ (prerequisite for)
Verification mechanism design (L3)
  ↓ (prerequisite for)
Runtime verification (L4)
  ↓ (prerequisite for)
M18 Runtime Closure achievement
```

---

### 11.3 Semantic Closure Conditions (Proposed)

**Condition 1: Complete Semantic Definition**

All four core L2 semantics must be formally specified:
```
✓ ActualConsequence formal type (L2-01)
✓ AuthorizedConsequence formal type (L2-02)
✓ CO formal type (L2-03)
✓ Authorization Scope formal definition (L2-04)
```

**Status:** IN_PROGRESS (L2-05 design package currently defining these)

---

**Condition 2: Unambiguous Authorization Chain**

Authorization decision must lead unambiguously to:
```
Authorization
  ↓ (defines)
Authorization Scope
  ↓ (constrains permitted)
AuthorizedConsequence
  ↓ (target for)
ActualConsequence
  ↓ (recorded as)
CO
  ↓ (evidence for)
M18 verification
```

**Ambiguity Tests:**
- Can AuthorizedConsequence be inferred from Authorization Scope alone? (NO → ambiguity)
- Can ActualConsequence be compared to AuthorizedConsequence without CO? (NO → gap)
- Can CO identity be linked to parent Authorization? (YES required; NO → gap)

**Status:** UNRESOLVED (depends on L2-01 through L2-04 formalization)

---

**Condition 3: Evidence Completeness**

For each authorization instance, complete evidence must exist:
```
Evidence Layer 1: Authorization decision recorded
Evidence Layer 2: AuthorizedConsequence specification recorded
Evidence Layer 3: ActualConsequence observation recorded (GL7 event + state change)
Evidence Layer 4: CO instance created (authorization + consequence + compliance proof)
Evidence Layer 5: M18 verification result recorded (within/outside closure scope)
```

**Completeness Test:** All 5 evidence layers present for ≥90% of authorization instances

**Status:** NOT_PROVEN (Layer 3 and 4 implementation absent)

---

**Condition 4: Consistency Across Routes**

All 109 observed routes must follow same semantic model:
```
Route 1: Auth1 → Scope1 → AuthConsq1 → ActConsq1 → CO1 → M18_in_scope
Route 2: Auth2 → Scope2 → AuthConsq2 → ActConsq2 → CO2 → M18_out_of_scope
... 
Route 109: Auth109 → Scope109 → AuthConsq109 → ActConsq109 → CO109 → M18_evaluation
```

**Consistency Test:**
- Can same verification logic apply to all 109 routes? (YES required)
- Do any routes require special-case handling? (if YES → semantic inconsistency)

**Status:** UNKNOWN (109 routes not yet analyzed under L2 semantics)

---

### 11.4 Closure Failure Conditions

Semantic Closure would fail if:

**Failure 1: Ambiguous Authorization Scope**
```
Authorization created without WHO/WHEN/WHAT specification
=> Consequence unverifiable (scope unknown)
=> Cannot achieve closure (authorization meaning ambiguous)
=> Impact: Authorization-consequence link broken
```

**Failure 2: Consequence Not Observable**
```
ActualConsequence occurs; no GL7 event or state change detected
=> Consequence happens; cannot prove it happened
=> Cannot achieve closure (consequence invisible)
=> Impact: Verification impossible
```

**Failure 3: AuthorizedConsequence Exceeds Scope**
```
AuthorizedConsequence.scope > Authorization Scope.WHAT
=> Consequence permission exceeds authorization
=> Counterexample: Permission granted for "read"; consequence permits "read+delete"
=> Cannot achieve closure (inconsistency in authorization bounds)
=> Impact: Authorization-consequence semantic mismatch
```

**Failure 4: CO Creation Fails**
```
ActualConsequence + AuthorizedConsequence recorded
=> GL7 event exists; state change exists
=> But no CO instance created to bind them together
=> Cannot achieve closure (compliance proof missing)
=> Impact: Link in evidence chain broken
```

**Failure 5: Revocation Not Detected**
```
Authorization scope includes revocation_trigger
=> Runtime does not check revocation (GL7 cache stale)
=> ActualConsequence recorded under revoked authorization
=> Cannot achieve closure (enforcement failure)
=> Impact: Authorization-consequence binding violated
```

### 11.5 UNKNOWN / NOT_PROVEN / UNRESOLVED Propagation

**How UNKNOWN states propagate in semantic closure:**

```
ActualConsequence.authorization = UNKNOWN
  ↓ propagates to
AuthorizedConsequence = UNKNOWN (cannot verify against spec)
  ↓ propagates to
CO.compliance_status = UNKNOWN
  ↓ propagates to
M18 verification = INCONCLUSIVE (cannot verify target invariant)
  ↓ propagates to
Semantic Closure status = NOT_ACHIEVED
  (one UNKNOWN blocks entire chain)
```

**Handling Rule:** One UNKNOWN anywhere in chain → entire closure chain status becomes UNKNOWN / NOT_PROVEN

---

**How NOT_PROVEN states propagate:**

```
GL7 constraint verification = NOT_PROVEN (no mechanism exists yet)
  ↓ means
Authorization Scope constraint checking = NOT_PROVEN
  ↓ means
ActualConsequence.scope validation = NOT_PROVEN
  ↓ means
CO.compliance_status = NOT_PROVEN (constraint violation undetectable)
  ↓ means
M18 verification = NOT_PROVEN (cannot guarantee authorization compliance)
```

**Handling Rule:** NOT_PROVEN constraints cannot be verified at runtime; must be treated as unverified

---

### 11.6 Semantic Closure Preconditions for Implementation

Before Layer 3 implementation can proceed, L2 design must enable:

**Precondition 1: Unambiguous Authorization Capture**
```
Layer 3 must be able to:
  - Read Authorization record
  - Extract WHO/WHEN/WHAT specification
  - Store as structured data
  - Validate against schema
Status: Requires AUTH-001 through AUTH-004 schema definitions (NOT_ESTABLISHED)
```

**Precondition 2: ActualConsequence Recording**
```
Layer 3 must be able to:
  - Receive GL7 event (from GL7 emit)
  - Capture state change
  - Create ActualConsequence record
  - Link to authorization
Status: Requires GL7-CONSUME mechanism (NOT_FOUND)
```

**Precondition 3: AuthorizedConsequence Specification**
```
Layer 3 must be able to:
  - Parse AuthorizedConsequence structure
  - Store consequence specification
  - Retrieve for comparison with ActualConsequence
Status: Requires AUTHCONSEQ-001 schema (NOT_ESTABLISHED)
```

**Precondition 4: CO Creation & Binding**
```
Layer 3 must be able to:
  - Create CO instance
  - Bind ActualConsequence + AuthorizedConsequence + scope check
  - Record compliance status
  - Persist in audit trail
Status: Requires CO-001 schema + binding logic (NOT_FOUND)
```

**Precondition 5: Scope Validation**
```
Layer 3 must be able to:
  - Evaluate WHO/WHEN/WHAT intersection
  - Check CONTEXT constraints
  - Verify revocation status
  - Determine authorization validity
Status: Requires SCOPE-VALIDATION-001 logic (NOT_FOUND)
```

---

### 11.7 Examples of Semantic Closure (Hypothetical)

**Example 1: Closed Authorization Chain (Hypothetical)**

```
Scenario: Alice reads file.txt under "read" authorization

Authorization Record:
  id: auth-2026-001
  subject: alice
  issued_at: 2026-09-13T09:00:00Z
  expires_at: 2026-09-20T23:59:59Z
  action: read
  resource: file.txt

AuthorizedConsequence Specification:
  id: authconseq-2026-001
  authorization: auth-2026-001
  scope: {WHO: alice, WHEN: [09:00-20:59], WHAT: read file.txt}
  permitted_values: {any data from file.txt}
  constraints: {rate: ≤100 reads/hour}
  evidence_required: {GL7 ALLOW + access log}

Runtime Execution:
  Time: 2026-09-13T10:00:00Z
  Actor: alice
  Action: read file.txt

GL7 Event:
  id: gl7-2026-001
  decision: ALLOW
  reason: Authorization auth-2026-001 valid
  timestamp: 2026-09-13T10:00:00Z

ActualConsequence Record:
  id: actconseq-2026-001
  action: read(file.txt)
  authorization: auth-2026-001
  state_before: {file.txt not in memory}
  state_after: {file.txt data returned to alice}
  observation: {gl7_event: gl7-2026-001, access_log: ✓}
  evidence_status: OBSERVED

CO Record (Compliance Proof):
  id: co-2026-001
  consequence: actconseq-2026-001
  authorized_spec: authconseq-2026-001
  compliance_status: WITHIN (consequence within scope)
  scope_validation: {
    WHO: alice ✓
    WHEN: 2026-09-13T10:00:00Z ∈ [valid window] ✓
    WHAT: read ✓ (rate check: 1/hour ≤ 100/hour) ✓
  }
  m18_relevance: IN_SCOPE (counts toward M18 closure)

M18 Verification (Closure Criterion):
  authorization_chain: complete ✓
  evidence_trail: unbroken ✓
  compliance_status: verified ✓
  => This instance contributes to M18 closure
```

**Closure Status:** CLOSED (for this instance)

---

### 11.8 Counterexamples: Closure Failure

**Counterexample 1: Broken Authorization Chain**

```
ActualConsequence Record:
  id: actconseq-2026-002
  action: write(database.users)
  authorization: NOT_FOUND ← BROKEN LINK
  state_before: {users.count: 1000}
  state_after: {users.count: 1001}
  observation: {db_audit_log: ✓, gl7_event: NOT_FOUND}
  evidence_status: NOT_PROVEN

CO Record:
  id: co-2026-002
  consequence: actconseq-2026-002
  authorized_spec: NOT_FOUND ← CANNOT FIND
  compliance_status: UNKNOWN (cannot verify without spec)
  scope_validation: CANNOT_RUN (no authorization to validate against)
  
Consequence: Consequence recorded; authorization missing
=> Closure BROKEN (authorization chain severed)
=> Cannot verify: Was this action authorized?
=> Impact: M18 closure cannot include this consequence
```

---

**Counterexample 2: Constraint Not Enforced**

```
AuthorizedConsequence Specification:
  scope: {constraints: {rate_limit: 10 reads/hour}}

At Runtime:
  Alice performs 50 reads in 1 minute
  GL7: ALLOW (rate limit check not implemented)
  ActualConsequence: 50 reads recorded
  
CO Record:
  id: co-2026-003
  compliance_status: EXCEEDS ← CONSTRAINT VIOLATED
  scope_validation: {rate_check: 50/min > 10/hour} FAILED
  
Consequence: Constraint violated; no enforcement prevented it
=> Closure FAILED (authorization scope exceeded)
=> Cannot verify: Was authorization compliance maintained?
=> Impact: CO.compliance_status = EXCEEDS (violation recorded)
```

---

## 12. Cross-Semantic Relationship Model

### 12.1 Authorization → Consequence Chain

**Proposed Master Model:**

```
1. Authorization Decision (L1/L2 input)
   ↓ defines
2. Authorization Scope (L2-04)
   ↓ permits
3. AuthorizedConsequence (L2-02)
   ↓ specifies expected outcome
4. Action Execution (L3 input)
   ↓ triggers
5. ActualConsequence (L2-01)
   ↓ what actually occurs
6. CO Instance (L2-03)
   ↓ binds actual to authorized
7. Compliance Proof (L2-05)
   ↓ evidence for
8. M18 Verification (L4)
   ↓ aggregate evaluation
9. Semantic Closure (L2-05)
   ↓ or failure to achieve
```

**Relationships:**

| Step | Input | Output | Status | Verified? |
|---|---|---|---|---|
| 1→2 | Authorization | Scope extracted | FOUND (L1) | YES |
| 2→3 | Scope | AuthConsq inferred | NOT_FOUND | NO |
| 3→4 | AuthConsq | Action permitted | PARTIAL (GL7) | PARTIAL |
| 4→5 | Action | ActConsq observed | PARTIAL (GL7 emit) | NO (consume NOT_FOUND) |
| 5→6 | ActConsq | CO created | NOT_FOUND | NO |
| 6→7 | CO | Compliance check | NOT_FOUND | NO |
| 7→8 | Compliance | M18 aggregate | NOT_FOUND | NO |
| 8→9 | Verification | Closure claimed | NOT_PROVEN | NO |

**Overall Chain Status:** PARTIALLY_COMPLETE (steps 1-2 work; steps 3-9 mostly NOT_FOUND/NOT_PROVEN)

---

### 12.2 Relationship Type: Evidence-Supported, Proposed, Unresolved

**Evidence-Supported Relationships:**

```
Authorization → Authorization Scope (L1 evidence: scope concept exists)
  Confidence: HIGH
  Link: Paper 3.5ζ + SPP/PHL v1.0
  
GL7 Event → ActualConsequence observation (L3 evidence: GL7 emits ALLOW/DENY)
  Confidence: MEDIUM (GL7 emit exists; consume/interpret NOT_FOUND)
  Link: execution_governance.py + GL7 source
```

---

**Proposed Relationships:**

```
Authorization Scope → AuthorizedConsequence (this package proposes)
  Design: Scope specifies what consequences permitted
  Confidence: PROPOSED (no implementation evidence)
  Verification: Requires L3 authconseq-spec storage + retrieval
  
ActualConsequence → CO (this package proposes)
  Design: ActConsq needs CO to bind with AuthConsq
  Confidence: PROPOSED (CO formal type undefined until L2-05)
  Verification: Requires L3 CO binding logic + L4 runtime binding
```

---

**Unresolved Relationships:**

```
AuthorizedConsequence ↔ ActualConsequence matching (not yet defined)
  Question: How do we know actual matches authorized?
  Current: NO formal comparison logic
  Status: UNRESOLVED
  
CO → M18 verification (relationship unclear)
  Question: Which CO instances count toward M18 closure?
  Current: M18-Scope UNRESOLVED
  Status: UNRESOLVED
  
Semantic Closure → M18 Closure (relationship postponed)
  Question: Does L2 semantic closure guarantee M18 closure?
  Current: Design phase does not answer
  Status: DEFERRED (HG decision after L2 design review)
```

---

## 13. UNKNOWN / UNDEFINED / NOT_PROVEN Propagation Rules

### 13.1 Propagation Table

When UNKNOWN appears at any point:

| State | Source | Propagates To | Outcome |
|---|---|---|---|
| ActualConsequence.authorization = UNKNOWN | Observation channel | AuthorizedConsequence = UNKNOWN | Cannot verify against spec |
| AuthorizedConsequence.scope = UNDEFINED | Design gap | CO.compliance_check = CANNOT_RUN | Cannot verify compliance |
| Authorization Scope.WHAT = UNCLEAR | Specification error | Consequence permissions = AMBIGUOUS | Cannot determine if action permitted |
| CO.compliance_status = NOT_PROVEN | Missing enforcement | M18 verification = INCONCLUSIVE | Cannot verify closure |
| Revocation status = UNKNOWN | Check not performed | Authorization validity = UNKNOWN | Cannot trust authorization |

### 13.2 Cascade Rule

```
UNKNOWN at layer N
  ↓ blocks
Verification at layer N+1
  ↓ propagates to
Status at layer N+2 = NOT_PROVEN
```

**Example:**
```
Layer 2: ActualConsequence.authorization = UNKNOWN
  ↓ (cannot find auth record)
Layer 3: AuthorizedConsequence lookup = FAILS
  ↓ (no auth to look up)
Layer 4: M18 verification = CANNOT_VERIFY (authorization unknown)
  ↓ consequence remains unverified
Final Status: Closure INCONCLUSIVE
```

### 13.3 Preservation Rules

- UNKNOWN MUST be preserved (never converted to FALSE, ABSENT, or UNIMPLEMENTED)
- UNDEFINED MUST be preserved (never assumed to mean "not required")
- NOT_PROVEN MUST be preserved (never assumed to mean "false")

---

## 14. Evidence Contract: L2 Semantics to Evidence Mapping

| L2 Semantic | Required Evidence | Current Status | Data Source | Verification Method |
|---|---|---|---|---|
| ActualConsequence exists | State change + observation record | PARTIAL (GL7 emit + log) | GL7 events, DB audit log, system state | Compare state_before vs state_after + cross-check GL7 |
| ActualConsequence.authorization valid | Authorization record + timestamp proof | FOUND (L1) | Authorization database | Resolve auth ID from ActConsq.authorization |
| AuthorizedConsequence specification | Consequence spec stored + matches auth | NOT_ESTABLISHED | (future) authconseq database | Schema validation + authorization link check |
| Authorization Scope boundaries | WHO/WHEN/WHAT recorded + enforced | PARTIAL (WHO/WHEN exist; WHAT unclear) | Authorization record | Extract and validate scope dimensions |
| CO instance created | CO record links ActConsq + AuthConsq | NOT_FOUND | (future) CO database | CO.consequence_id + CO.authorized_spec_id resolution |
| CO compliance verified | Scope validation logic executed + recorded | NOT_FOUND | (future) CO audit trail | CO.compliance_status field + scope_validation results |
| M18 relevance determined | CO.m18_relevance field populated | NOT_FOUND | (future) CO audit trail | Check if CO counted toward M18 closure |
| Revocation check performed | Authorization.revocation_status current | NOT_PROVEN | Authorization state at execution time | Timestamp(revocation_check) ≥ timestamp(execution) |
| Evidence chain unbroken | Auth→AuthConsq→ActConsq→CO→M18 links all exist | PARTIAL (Auth→ActConsq partial; others NOT_FOUND) | Linked records in audit trail | Follow ID references; all must resolve |

---

## 15. Design Assumption Registry

### DA-01: Authorization Semantics are Explicit

**Assumption:** Authorizations must be formally recorded with clear WHO/WHEN/WHAT specification.

**Rationale:** Implicit or inferred authorization cannot be verified at runtime.

**Evidence:** Authorization must exist as a recorded decision before execution (foundational principle from SPP/PHL v1.0).

**Risk if Wrong:** 
- Consequences occur without clear authorization trace
- Closure verification becomes impossible (authority unknown)

**Verification Required:** 
- Layer 3: Schema enforces required authorization fields
- Layer 4: Runtime verifies all 3 dimensions before consequence permission

**HG Decision Required?** YES (if authorization can be inferred, this changes the entire model)

---

### DA-02: Consequences are Observable

**Assumption:** Every authorized action must have observable consequences (state change or GL7 event).

**Rationale:** Without observation, we cannot verify what actually happened; authorization→consequence chain breaks.

**Evidence:** GL7 event emission exists; state changes measurable (from L3 investigation).

**Risk if Wrong:**
- Actions execute; consequences undetectable
- Closure verification impossible (consequences invisible)

**Verification Required:**
- Layer 3: Observation mechanism (state capture, GL7 consume) implemented
- Layer 4: Observation quality verified (not false positives/negatives)

**HG Decision Required?** NO (GL7 framework already assumes observability)

---

### DA-03: AuthorizedConsequence Specification is Feasible

**Assumption:** For each authorization, we can create a formal specification of permitted consequences.

**Rationale:** Enables comparison: ActualConsequence vs AuthorizedConsequence (compliance check).

**Evidence:** AuthorizedConsequence concept defined in L2-02; structure proposed; Layer 3 capacity sufficient.

**Risk if Wrong:**
- Consequence specification impossible
- Cannot verify compliance (no target to measure against)

**Verification Required:**
- Layer 3: Implement AuthorizedConsequence storage + retrieval for sample authorizations
- Layer 4: Verify sample consequence specs capture authorization intent accurately

**HG Decision Required?** YES (if consequence specifications are infeasible, design strategy changes)

---

### DA-04: CO Binding Preserves Authorization Link

**Assumption:** CO instance creation/query can always identify which Authorization created it.

**Rationale:** Without this link, consequences float free of authorization; closure verification breaks.

**Evidence:** CO structure proposed with authorization_id field; Link preservation assumed feasible.

**Risk if Wrong:**
- CO record created; authorization reference lost
- Consequence unattributable to authorization (orphaned)

**Verification Required:**
- Layer 3: CO schema enforces authorization_id foreign key
- Layer 4: Runtime verifies CO→Authorization link integrity

**HG Decision Required?** NO (data integrity principle; applies universally)

---

### DA-05: Scope Intersection Logic is Unambiguous

**Assumption:** WHO ∩ WHEN ∩ WHAT rules can be implemented consistently across all routes.

**Rationale:** If different routes apply different scope logic, closure verification is unreliable.

**Evidence:** Intersection logic specified in Section 10.4; no known conflicts.

**Risk if Wrong:**
- Different routes use different scope rules
- 109 routes have different semantic models
- Cannot achieve consistent M18 verification

**Verification Required:**
- Layer 3: Same scope logic applied to all 109 routes (automated verification)
- Layer 4: Runtime audit trail confirms consistent application

**HG Decision Required?** YES (if routes require different logic, 109/30/15 separation breaks)

---

### DA-06: Revocation is Timely

**Assumption:** When authorization is revoked, the revocation is detected before consequence permission granted.

**Rationale:** If revocation is delayed, consequences execute under revoked authorization.

**Evidence:** Revocation mechanism exists (GL7 concept); timing not yet proven.

**Risk if Wrong:**
- Revocation delayed (cache staleness, polling latency)
- Consequences execute under revoked auth (security violation)

**Verification Required:**
- Layer 4: revocation_check_interval timing verified against consequence latency
- Layer 4: Audit trail confirms revocation detection occurred before permission grant

**HG Decision Required?** YES (if revocation timing cannot be guaranteed, authorization trust breaks)

---

### DA-07: M18-Scope is Decidable

**Assumption:** For each of the 109 routes, we can definitively decide whether it is within M18 closure scope.

**Rationale:** Without decidability, M18 closure cannot be verified (scope ambiguity).

**Evidence:** M18-Scope currently UNRESOLVED; this is a design assumption, not proven.

**Risk if Wrong:**
- M18-Scope remains ambiguous
- Cannot verify closure (don't know what "closure" means)

**Verification Required:**
- HG decision on M18-Scope definition (separate governance action)
- Layer 3: M18-Scope specification formalized
- Layer 4: Runtime categorizes each route as IN_SCOPE or OUT_OF_SCOPE

**HG Decision Required?** YES (Critical blocker for M18 verification)

---

### DA-08: 109/30/15 Separation Remains Intact

**Assumption:** Layer 2 semantic formalization does NOT attempt to prove/disprove relationships between 109/30/15 path categories.

**Rationale:** These categories are separate governance concerns; L2 design focuses on authorization-consequence semantics only.

**Evidence:** Design package maintains explicit separation; no mixing of concerns.

**Risk if Wrong:**
- L2 design inadvertently redefines 109/30/15 categories
- Governance scope creep occurs

**Verification Required:**
- Design review confirms no 109/30/15 redefinition attempted
- No inference from L2 semantics to route categorization

**HG Decision Required?** NO (principle; not a decision needed)

---

## 16. Examples: End-to-End Verification (Hypothetical)

### Example: Route verification under complete L2-05 semantics

**Scenario:** Verify that Alice's read of file X was within M18 closure scope

```
Step 1: Authorization Record
  Authorization-1001 {
    subject: alice
    action: read
    resource: file-X
    issued_at: 2026-09-13
    expires_at: 2026-09-20
    scope_validation_required: true
  }

Step 2: Authorization Scope Extraction
  AuthorizationScope-1001 {
    WHO: alice (password-verified)
    WHEN: 2026-09-13 to 2026-09-20
    WHAT: read file-X (rate: ≤100/hour)
  }

Step 3: AuthorizedConsequence Specification
  AuthorizedConsequence-1001 {
    authorization: Authorization-1001
    consequence_type: PERMISSION
    permitted_values: {file-X data}
    constraints: {rate_limit: 100/hour}
    evidence_required: {GL7 ALLOW + access_log}
  }

Step 4: Execution & Observation
  Time: 2026-09-14T10:00:00Z
  Actor: alice
  Action: read(file-X)
  
  GL7 Event:
    decision: ALLOW
    authorization: Authorization-1001
    timestamp: 2026-09-14T10:00:00Z
  
  Access Log:
    actor: alice
    action: read
    resource: file-X
    timestamp: 2026-09-14T10:00:00Z

Step 5: ActualConsequence Recording
  ActualConsequence-1001 {
    action: read(file-X)
    authorization: Authorization-1001
    state_before: {file-X not in memory}
    state_after: {file-X data in memory}
    observation: {gl7: ALLOW, access_log: ✓}
    evidence_status: OBSERVED
  }

Step 6: CO Creation & Compliance Verification
  CO-1001 {
    consequence: ActualConsequence-1001
    authorized_spec: AuthorizedConsequence-1001
    
    compliance_check: {
      WHO: alice ✓
      WHEN: 2026-09-14 ∈ [2026-09-13, 2026-09-20] ✓
      WHAT: read ✓
      constraints: 1 read ≤ 100/hour ✓
    }
    
    compliance_status: WITHIN
    m18_relevance: IN_SCOPE
  }

Step 7: M18 Verification
  Route-Alice-FileX verified:
    - Authorization chain: complete ✓
    - Evidence trail: unbroken ✓
    - Compliance: verified ✓
    => contributes to M18 closure
    
Step 8: Semantic Closure (this route)
  CLOSED (for this instance)
  
Aggregate Verification (across all 109 routes):
  If all 109 routes verify like Route-Alice-FileX
  => M18 Closure = ACHIEVED
  (Semantic Closure prerequisites all met)
```

---

## 17. Counterexamples: Semantic Closure Failure Modes

### Counterexample A: Missing AuthorizedConsequence Spec

```
Scenario: Authorization exists; spec missing

Authorization-2001 { subject: bob, action: write, resource: db-table-Y }
AuthorizedConsequence-2001: NOT_FOUND ← MISSING

At Runtime:
  bob.write(db-table-Y) executed
  GL7: ALLOW
  ActualConsequence-2001 recorded (rows added)
  
CO-2001 creation attempted:
  consequence: ActualConsequence-2001 ✓
  authorized_spec: NOT_FOUND ← CANNOT FIND
  compliance_check: CANNOT_RUN (no spec)
  compliance_status: UNKNOWN
  
Result:
  - Consequence observed
  - Authorization exists
  - Specification missing
  => Cannot verify compliance
  => Closure INCOMPLETE for this route
  => M18 verification: INCONCLUSIVE
```

---

### Counterexample B: Revocation Detection Failure

```
Timeline:
  T0: Authorization-3001 created, valid
  T30s: Revocation condition fires (bob.status = REVOKED)
  T30s+: GL7 cache not yet updated (TTL=60s)
  T45s: bob attempts action
  T45s: GL7 permits (stale cache)
  T45s: ActualConsequence-3001 recorded
  T60s: GL7 cache refreshed; revocation detected (too late)
  
CO-3001 compliance_check:
  revocation_status: REVOKED (detected at T60s)
  BUT action allowed at T45s (revocation not yet known)
  compliance_status: VIOLATED (acted under revoked auth)
  
Result:
  - Consequence recorded under revoked authorization
  - Timing gap (revocation not detected in time)
  => Closure FAILED for this route
  => M18 verification: FAILURE (unauthorized consequence)
```

---

## 18. Open Questions Remaining

1. **Consequence Attribution in Cascades:** If action A triggers B which triggers C, which authorization covers all three consequences?
   - Status: NOT_PROVEN
   - Impact: Affects M18 scope

2. **Consequence Cardinality:** Can one action produce multiple ActualConsequences?
   - Status: UNDEFINED
   - Impact: Changes CO creation logic

3. **Evidence Temporal Tolerance:** How stale can evidence be before it invalidates a consequence claim?
   - Status: NOT_ESTABLISHED
   - Impact: Affects revocation detection timing requirements

4. **Scope Dimension Trade-offs:** If WHO is satisfied but WHAT is unclear, is permission granted?
   - Status: UNRESOLVED
   - Impact: Affects ambiguity handling in scope validation

5. **Consequence Magnitude Limits:** Does "write" permit writing 1 byte or 1 GB?
   - Status: UNDEFINED
   - Impact: Requires constraint specification in WHAT dimension

6. **Superseded Authorization:** When Authorization-A supersedes Authorization-B, what happens to consequences already recorded under B?
   - Status: NOT_DECIDED
   - Impact: Affects historical closure verification

---

## 19. Design Risks

### Risk 1: Complexity Explosion

**Risk:** L2-01 through L2-05 are complex; implementation could become unmaintainable.

**Likelihood:** MEDIUM

**Mitigation:** Start with simplest possible CO binding logic; iterate incrementally from L3 feedback.

---

### Risk 2: Performance Impact

**Risk:** Scope validation (WHO∩WHEN∩WHAT) at runtime could introduce latency.

**Likelihood:** MEDIUM

**Mitigation:** Cache scope validation results; use early-exit logic (fail-fast if any dimension fails).

---

### Risk 3: Backwards Incompatibility

**Risk:** Existing authorization records may not have WHO/WHEN/WHAT explicitly specified; cannot retrofit.

**Likelihood:** HIGH

**Mitigation:** Create migration path; allow LEGACY authorization records with degraded closure status.

---

### Risk 4: Evidence Loss

**Risk:** If GL7 events are not persisted (only cached), evidence is lost after GL7 gate.

**Likelihood:** MEDIUM

**Mitigation:** Implement GL7 consequence persist-to-audit-trail mechanism (Layer 3 requirement).

---

### Risk 5: Circular Dependency

**Risk:** L2 design depends on M18-Scope definition (unresolved); HG decision needed before L2 can be finalized.

**Likelihood:** CONFIRMED (M18-Scope = UNRESOLVED / LOCKED)

**Mitigation:** L2-05 design should proceed assuming M18-Scope is decidable; details deferred to HG decision.

---

## 20. Implementation Preconditions

Before Layer 3 can implement L2-05 semantics, the following preconditions must be satisfied:

### Precondition 1: Formal Approval of L2 Semantics

**Requirement:** Human Gate must approve L2-01 through L2-05 design (or specify changes).

**Current Status:** DRAFT / PROPOSED (awaiting HG Design Review)

**Verification:** HG approval recorded in decision ledger before L3 implementation starts.

---

### Precondition 2: Scope Validation Algorithm Formalized

**Requirement:** WHO ∩ WHEN ∩ WHAT intersection logic must be formally specified (not left to implementation interpretation).

**Current Status:** Proposed in Section 10.4; requires HG review.

**Verification:** Formal algorithm reviewed and approved by HG.

---

### Precondition 3: Authorization Record Schema

**Requirement:** Authorization, AuthorizedConsequence, CO data structures must be formally specified in schema.

**Current Status:** Proposed in L2-01 through L2-03; Layer 3 schema definition pending.

**Verification:** Schema created and validated against L2 design.

---

### Precondition 4: GL7 Consequence Persist Mechanism

**Requirement:** GL7 events must persist to audit trail (not just cache or emit).

**Current Status:** GL7 emit exists; consume/persist NOT_FOUND.

**Verification:** Layer 3 implements GL7 event persistence with audit trail link.

---

### Precondition 5: M18-Scope Formal Definition

**Requirement:** HG must decide M18-Scope boundary (which routes are in scope for M18 closure).

**Current Status:** UNRESOLVED / LOCKED

**Verification:** HG decision recorded; M18-Scope definition formalized.

**Impact:** Critical blocker for full L2-05 implementation; L3 cannot categorize consequences as IN/OUT_OF_SCOPE without this.

---

## 21. Verification Preconditions

Before Layer 4 can verify semantic closure, the following must be satisfied:

### VP-01: L3 Implementation Validation

**Requirement:** Layer 3 implementation must be tested and verified to produce correct L2 semantic records.

**Test Cases:**
- Authorization Scope intersection: all combinations of WHO/WHEN/WHAT
- AuthorizedConsequence matching: consequence within/exceeds/violates scope
- CO creation: correct binding of authorization to consequence
- Revocation detection: revocation flag detected before consequence permission

**Verification Method:** Unit tests + integration tests covering all L2 concepts

---

### VP-02: GL7 Event Integrity

**Requirement:** GL7 events must be verified as complete and non-repudiable.

**Test Cases:**
- GL7 event persisted to audit trail (not lost)
- GL7 event timestamps consistent with execution log
- GL7 event cannot be modified after creation

**Verification Method:** Audit trail integrity checks; timestamp validation

---

### VP-03: State Change Capture Accuracy

**Requirement:** State change capture must be verified as accurate (not false positives/negatives).

**Test Cases:**
- State_before and state_after correctly represent system state
- No state changes missed by capture mechanism
- No phantom state changes recorded

**Verification Method:** State capture tested against known state transitions

---

### VP-04: Evidence Chain Continuity

**Requirement:** Complete link from Authorization → ActualConsequence → CO → Closure must exist.

**Test Cases:**
- All ID references resolvable (no dangling references)
- All required fields populated
- Timestamp consistency across records

**Verification Method:** Record chain walkthrough; referential integrity checks

---

## 22. Canonical State Maintenance

Throughout L2 design and subsequent phases, the following canonical states MUST be maintained unchanged:

```
✓ N14R Necessity               = NOT_PROVEN / LOCKED
✓ M18 Runtime Closure         = NOT_ACHIEVED / LOCKED
✓ Authority → Runtime Binding = BROKEN / LOCKED
✓ C2-b                        = BLOCK / LOCKED
✓ Implementation Authorization = NOT_GRANTED / LOCKED
✓ Production Modification      = 0 / LOCKED
✓ System                       = HOLD / FAIL-CLOSED / LOCKED
✓ Semantic Closure             = NOT_ACHIEVED
✓ 109 routes                  = OBSERVED
✓ 30 routes                   = PRIOR ASSERTION / UNVERIFIED
✓ 15 Paths                    = NECESSITY NOT_PROVEN
✓ M18-Scope                   = UNRESOLVED / LOCKED
✓ ActualConsequence form      = NOT_ESTABLISHED (until now; L2-01 proposes)
✓ AuthorizedConsequence form  = NOT_ESTABLISHED (until now; L2-02 proposes)
✓ CO definition               = UNKNOWN (until now; L2-03 proposes)
✓ Authorization Scope formal  = NOT_ESTABLISHED (until now; L2-04 proposes)
✓ Semantic Closure path       = NOT_ACHIEVED (until now; L2-05 proposes)
```

**Verification:** Each integrity check confirms these states at package completion.

---

## 23. Human Gate Reassessment Package

### What HG Must Decide After Design Review

**Decision Point 1: L2 Design Acceptance**

- Question: Does HG approve L2-01 through L2-05 formal semantics as designed?
- Options: APPROVE | REQUEST_CHANGES | REJECT
- Evidence Provided: This design package + counterexamples + risk analysis
- Timeline: Design review phase (HG design-time decision scope)

**Decision Point 2: M18-Scope Definition**

- Question: Which of the 109 routes are within M18 closure scope?
- Options: HG specifies explicit M18-Scope definition OR defers to implementation phase
- Evidence Provided: M18 evidence reconciliation report (Section: M18 Runtime Closure reconciliation)
- Timeline: Post-design or concurrent (blocks L3 implementation if deferred)
- Impact: Critical blocker for CO.m18_relevance assignment

**Decision Point 3: Design Assumption Risk Acceptance**

- Question: Does HG accept the risks in Design Assumption Registry (DA-01 through DA-08)?
- Options: ACCEPT | REQUEST_MITIGATION | REJECT
- Evidence Provided: Risk analysis in Section 19
- Timeline: Design review phase
- Impact: If any risk is REJECTED, design strategy must change

**Decision Point 4: Implementation Authorization Readiness**

- Question: After L2 design approval, is implementation authorization ready to be requested?
- Options: YES (proceed to L3) | NO (design gaps remain) | DEFER (wait for M18-Scope decision)
- Prerequisites: L2 design APPROVED + M18-Scope resolved + all risks mitigated
- Timeline: After design review
- Impact: Governs when L3 implementation phase begins

---

### Uncertainties Explicitly Not Resolved

The following remain UNRESOLVED / PROPOSED for HG Design Review:

```
[ ] CO formal type finalization (L2-03 structure is CANDIDATE)
[ ] Scope dimension weighting (WHO vs WHEN vs WHAT priority unclear)
[ ] Consequence cardinality (one action → one or multiple ActualConsequences?)
[ ] Evidence temporal tolerance (how old can GL7 event be?)
[ ] Revocation timing requirements (must revocation check happen <X ms after?)
[ ] Cascade consequence attribution (Authorization → consequence cascade → M18?)
[ ] Legacy authorization migration (existing records retrofit feasibility)
[ ] Performance targets (scope validation latency SLA)
[ ] Exception handling (what if scope validation fails?)
```

---

### Next Governance Actions

**Immediate (post-design review):**
1. HG Design Review of L2 package
2. HG decision on M18-Scope definition
3. HG risk acceptance (DA-01 through DA-08)

**Conditional (dependent on HG decisions):**
4. Layer 3 Implementation Authorization request (if L2 approved + M18-Scope resolved)
5. Layer 3 implementation begins (schema, GL7 consume, CO binding)

**Post-implementation:**
6. Layer 4 Verification preconditions satisfaction (VP-01 through VP-04)
7. M18 Runtime Closure verification attempt
8. Semantic Closure achievement (if all evidence chains complete)

---

## FINAL INTEGRITY CHECK

**Before publication, verify all constraints:**

- [ ] Q-L2-01 AUTHORIZE used for design-only scope ✓
- [ ] Implementation Authorization = NOT_GRANTED ✓
- [ ] Production Modification = 0 ✓
- [ ] Runtime Modification = 0 ✓
- [ ] Schema Modification = 0 ✓
- [ ] Code Modification = 0 ✓
- [ ] System = HOLD / FAIL-CLOSED ✓
- [ ] All 24 locked/canonical states preserved ✓
- [ ] N14R = NOT_PROVEN / LOCKED ✓
- [ ] M18 Runtime Closure = NOT_ACHIEVED / LOCKED ✓
- [ ] Authority → Runtime Binding = BROKEN / LOCKED ✓
- [ ] C2-b = BLOCK / LOCKED ✓
- [ ] Semantic Closure = NOT_ACHIEVED ✓
- [ ] 109/30/15 separation maintained ✓
- [ ] M18-Scope = UNRESOLVED ✓
- [ ] UNKNOWN preserved (not converted to FALSE) ✓
- [ ] UNDEFINED preserved (not assumed missing) ✓
- [ ] NOT_PROVEN preserved (not assumed false) ✓
- [ ] Evidence and inference separated ✓
- [ ] Design Proposal ≠ Decision ✓
- [ ] No implementation authorization inferred ✓
- [ ] No design approval inferred ✓
- [ ] No code/schema/runtime modification ✓
- [ ] No production modification ✓

**Status:** DRAFT / PROPOSED (Ready for Human Gate Design Review)

---

**Package Prepared:** 2026-09-13 by Claude Haiku 4.5 (くろこ)  
**Authority:** M18 ADVANCEMENT + Design-time decision scope  
**Submitted For:** Human Gate Review (nsjp_kimura)  
**Next Decision:** HG Design Review → Approval/Changes/Rejection

---

*End of L2 Formal Semantic Design Package*
