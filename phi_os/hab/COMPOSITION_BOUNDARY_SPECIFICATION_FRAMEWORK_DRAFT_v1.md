# Composition Boundary Specification Framework — DRAFT

**Date:** 2026-09-20  
**Status:** DRAFT / HUMAN GATE REQUIRED  
**Author:** Claude (Kuroko - Executive Officer)  
**Purpose:** Define what must be specified before Composition Validity can be judged  

---

## Meta-Purpose

This document does NOT define Composition rules.

This document defines **what must be defined** before Composition rules can be created.

Therefore: **Specification of Specification**, not Specification itself.

---

## A. Boundary Definitions

### A.1 Evidence Boundary

**What is the boundary?**
The boundary between "evidence is recorded" and "evidence can be used to prove composition is valid."

**What is the judgment target?**
Whether evidence produced in layer N can be consumed by layer N+1 without degradation, loss, or semantic shift.

**What counts as evidence?**
- Timestamp (ISO 8601)
- Actor identity (exact AI identifier)
- Event content (append-only, no modification)
- Authority trace (who signed, not just who recorded)
- Causality marker (event E caused state S, not just temporal sequence)

**What does it constrain in composition?**
- HAB must produce evidence that JARVIS can read and interpret identically
- Evidence cannot be corrupted or re-interpreted during N→N+1 handoff
- Evidence loss at boundary = composition invalid (not recoverable)

**Network:**
Evidence Boundary constrains → Evidence × Temporal interaction
Evidence Boundary reads from ← Authority Boundary, State Boundary

---

### A.2 State / Semantic Boundary

**What is the boundary?**
The boundary between "state is recorded" and "state carries the same semantic meaning across layers."

**What is the judgment target?**
Whether a state value (STABLE, DRAFT, REVIEW, STASIS, ACTIVE) in layer N means the same thing when layer N+1 observes it.

**What counts as evidence?**
- State definition (semantic mapping)
- State transition rules (valid sequences)
- Semantic invariants (which state combinations are safe)
- State observation timestamp (when was state read)
- State atomicity (was state consistent at read time)

**What does it constrain in composition?**
- FROZEN layer state must be observable by EXTENSION layer without loss
- EXTENSION layer state must remain consistent while JARVIS is reading it
- State changes in layer N during N+1 execution must not violate layer N+1 assumptions

**Network:**
State Boundary constrains → State × Time interaction, State × Authority interaction
State Boundary reads from ← Evidence Boundary, Authority Boundary

---

### A.3 Temporal Boundary

**What is the boundary?**
The boundary between "events have timestamps" and "causality is preserved across layers."

**What is the judgment target?**
Whether event E at time T_N in layer N caused state S at T_N+1 in layer N+1, or whether causality is broken by clock skew, buffering, or ordering issues.

**What counts as evidence?**
- Event timestamp (T_N)
- Decision timestamp (T_N+1)
- Causal dependency (E → S explicitly recorded, not inferred)
- Clock alignment (multi-agent time drift tolerance)
- Ordering guarantee (monotonic or only logical ordering?)

**What does it constrain in composition?**
- If N finishes at T_N, does N+1 definitely see causality?
- If N and N+1 run on different systems, is wall-clock time sufficient or need logical clocks?
- If evidence from N arrives out-of-order at N+1, is composition safe?

**Network:**
Temporal Boundary constrains → Evidence × Time, State × Time, Authority × Time
Temporal Boundary reads from ← Evidence Boundary, State Boundary, Authority Boundary

---

### A.4 Authority Boundary

**What is the boundary?**
The boundary between "authority is recorded" and "authority is correctly delegated/verified across layers."

**What is the judgment target?**
Whether a decision approved by actor A in layer N can be assumed to have the same authority when layer N+1 receives it, or whether re-verification is required.

**What counts as evidence?**
- Actor identity (exact, verifiable)
- Authority level (what can this actor do)
- Approval proof (cryptographic signature or witness, not just a record)
- Authority chain (who approved, who verified approval)
- Authority scope (approved for what purpose, not blank authorization)

**What does it constrain in composition?**
- JARVIS cannot assume HAB's authority; must re-verify or accept delegation explicitly
- HAB authority escalation during execution = composition invalid
- Unknown authority in evidence = composition cannot proceed

**Network:**
Authority Boundary constrains → Authority × Scope, Authority × Readiness
Authority Boundary reads from ← Evidence Boundary, State Boundary

---

### A.5 Scope Boundary

**What is the boundary?**
The boundary between "system components are defined" and "scope is consistent across layers during composition."

**What is the judgment target?**
Whether data/components in scope for layer N are the same as in-scope for layer N+1, and if overlapping, how conflicts are resolved.

**What counts as evidence?**
- Scope definition (which data/components are in scope)
- Scope access rules (can N+1 access N's scope?)
- Scope isolation (are scopes disjoint or overlapping)
- Scope changes (did scope change between T_N and T_N+1)
- Scope conflict resolution (if both layers access same data, who wins)

**What does it constrain in composition?**
- If FROZEN is in both N and N+1 scope: how is read consistency maintained?
- If N and N+1 write to overlapping scope: are updates serializable?
- If N's output is outside N+1's scope: how is it accessed?

**Network:**
Scope Boundary constrains → Scope × Time, Scope × Authority, Scope × Readiness
Scope Boundary reads from ← Evidence Boundary, Authority Boundary

---

### A.6 Readiness Boundary

**What is the boundary?**
The boundary between "layer N is in ACTIVE state" and "layer N is truly ready to compose with N+1."

**What is the judgment target?**
Whether all preconditions for safe N→N+1 handoff are met, not just whether N passed its own internal readiness checks.

**What counts as evidence?**
- State verification (N is in ACTIVE, not DRAFT/REVIEW/STASIS)
- Evidence completeness (all required evidence is present)
- Semantic consistency (all state values are consistent with each other)
- Authority verification (all required approvals are in place)
- Time alignment (N and N+1 have synchronized understanding of time)
- Scope readiness (N+1 can access required data)

**What does it constrain in composition?**
- Readiness is not transitive: N ready ≠ N+1 ready
- N's readiness at T_N does not guarantee N's readiness at T_N+1
- N+1 must verify N's readiness, cannot assume it from N's self-report

**Network:**
Readiness Boundary constrains → All other boundaries
Readiness Boundary reads from ← Evidence, State, Temporal, Authority, Scope

---

## B. Boundary Evidence Requirements

For each boundary, what level of evidence is needed to make what claim?

### B.1 Evidence Boundary

| Evidence Level | Claim Possible | Claim Scope |
|---|---|---|
| **DESIGNED** | "Evidence schema is specified" | Individual layer only |
| **IMPLEMENTED** | "Evidence is recorded" | Individual layer only |
| **CONNECTED** | "Evidence from N can be read by N+1" | Composition: one-way connection tested |
| **RUNTIME VERIFIED** | "Evidence flowed through composition without degradation" | Composition: end-to-end claim |
| **NOT AVAILABLE** | No claim | N/A |

**Current Status:** IMPLEMENTED (23 events recorded, schema exists)  
**Missing:** CONNECTED (can JARVIS read HAB evidence?), RUNTIME VERIFIED (tested in composition?)  
**Gap:** Cannot claim "Evidence Boundary is composition-valid" without CONNECTED + RUNTIME VERIFIED

---

### B.2 State / Semantic Boundary

| Evidence Level | Claim Possible | Claim Scope |
|---|---|---|
| **DESIGNED** | "State values are defined" | Individual layer only |
| **IMPLEMENTED** | "State is recorded and transitions enforced" | Individual layer only |
| **CONNECTED** | "N+1 can read and interpret N's state identically" | Composition: semantic consistency tested |
| **RUNTIME VERIFIED** | "State remained consistent during actual composition" | Composition: concurrent access tested |
| **NOT AVAILABLE** | No claim | N/A |

**Current Status:** DESIGNED + IMPLEMENTED (5 states, 344 transitions recorded)  
**Missing:** CONNECTED (semantic mapping defined?), RUNTIME VERIFIED (concurrent state reads tested?)  
**Gap:** Cannot claim "State Boundary is composition-valid" without CONNECTED + RUNTIME VERIFIED

---

### B.3 Temporal Boundary

| Evidence Level | Claim Possible | Claim Scope |
|---|---|---|
| **DESIGNED** | "Timestamp format is specified" | Individual layer only |
| **IMPLEMENTED** | "Timestamps are recorded" | Individual layer only |
| **CONNECTED** | "Causal dependency between T_N and T_N+1 can be verified" | Composition: causality chain tested |
| **RUNTIME VERIFIED** | "Causality was preserved during actual composition" | Composition: multi-agent ordering tested |
| **NOT AVAILABLE** | No claim | N/A |

**Current Status:** DESIGNED + IMPLEMENTED (ISO 8601, 22,887 events with timestamps)  
**Missing:** CONNECTED (causal links defined?), RUNTIME VERIFIED (tested across boundaries?)  
**Gap:** Cannot claim "Temporal Boundary is composition-valid" without clock alignment policy + runtime test

---

### B.4 Authority Boundary

| Evidence Level | Claim Possible | Claim Scope |
|---|---|---|
| **DESIGNED** | "Authority model is specified" | Individual layer only |
| **IMPLEMENTED** | "Authority is recorded and validated" | Individual layer only |
| **CONNECTED** | "Authority from N can be re-verified by N+1" | Composition: re-verification rule tested |
| **RUNTIME VERIFIED** | "Authority was correctly preserved during composition" | Composition: escalation attempt detected? |
| **NOT AVAILABLE** | No claim | N/A |

**Current Status:** DESIGNED + IMPLEMENTED (actor model, authority matrix, 5 test cases)  
**Missing:** CONNECTED (re-verification rule defined?), RUNTIME VERIFIED (tested escalation scenario?)  
**Gap:** Cannot claim "Authority Boundary is composition-valid" without explicit delegation/re-verification policy

---

### B.5 Scope Boundary

| Evidence Level | Claim Possible | Claim Scope |
|---|---|---|
| **DESIGNED** | "Scope definitions exist" | Individual layer only |
| **IMPLEMENTED** | "Access controls are enforced" | Individual layer only |
| **CONNECTED** | "Scope overlap is managed at composition boundary" | Composition: conflict resolution tested |
| **RUNTIME VERIFIED** | "Scope conflicts were detected and resolved safely" | Composition: concurrent access tested |
| **NOT AVAILABLE** | No claim | N/A |

**Current Status:** DESIGNED (FROZEN, Analytical, Extension, Human Gate scopes defined)  
**Missing:** IMPLEMENTED (access controls?), CONNECTED (overlap rules?), RUNTIME VERIFIED  
**Gap:** Cannot claim "Scope Boundary is composition-valid"; scope enforcement not verified

---

### B.6 Readiness Boundary

| Evidence Level | Claim Possible | Claim Scope |
|---|---|---|
| **DESIGNED** | "Readiness criteria are specified" | Individual layer only |
| **IMPLEMENTED** | "Readiness checks run before ACTIVE" | Individual layer only |
| **CONNECTED** | "N's readiness is verified by N+1 before composition" | Composition: mutual readiness check tested |
| **RUNTIME VERIFIED** | "Composition readiness was verified and maintained" | Composition: readiness regression detected? |
| **NOT AVAILABLE** | No claim | N/A |

**Current Status:** DESIGNED (audit checklist exists, state transitions defined)  
**Missing:** IMPLEMENTED (automated readiness validator?), CONNECTED (cross-layer verification?), RUNTIME VERIFIED  
**Gap:** Cannot claim "Readiness Boundary is composition-valid"; automated readiness verification does not exist

---

## C. Boundary Interaction Matrix

Boundaries are NOT independent. Key interactions:

### C.1 Evidence × Temporal

**Interaction:** Evidence timestamp determines causality chain.

| Scenario | What Happens | Gap |
|---|---|---|
| Event E at T_N, State S at T_N+1 | Is E causally responsible for S? | No causal link mechanism defined |
| Evidence arrives out-of-order | Does N+1 detect and reorder? | No ordering guarantee defined |
| Clock skew (T_N+1 < T_N) | Is causality still valid? | Clock sync tolerance undefined |

**Decision Required:** How to handle causal evidence chains across layers?

---

### C.2 State × Temporal

**Interaction:** State changes over time; composition must see consistent state.

| Scenario | What Happens | Gap |
|---|---|---|
| State changes from DRAFT to ACTIVE during N→N+1 | Does N+1 see consistent state? | No atomicity guarantee |
| N+1 reads FROZEN while EXTENSION changes | Are reads isolated? | No isolation level defined |
| State is observed at T1, used at T2 | Is staleness detected? | No staleness checking defined |

**Decision Required:** How to ensure state consistency during composition?

---

### C.3 Authority × Scope

**Interaction:** Authority to access data is scope-dependent.

| Scenario | What Happens | Gap |
|---|---|---|
| N authorized for Scope A, N+1 authorized for Scope B | Can N→N+1 handoff if scopes overlap? | No scope override rules |
| N approved by human, N+1 asks to access Scope X | Does human approval cover Scope X? | No authority-scope binding |
| Authority escalation in N+1's scope | N already approved but scope changed? | No scope change detection during composition |

**Decision Required:** How do authority and scope interact at composition boundary?

---

### C.4 Authority × Readiness

**Interaction:** Readiness includes authority verification.

| Scenario | What Happens | Gap |
|---|---|---|
| N is ACTIVE but authority is unverified | Is it ready to hand off? | Authority re-verification timing undefined |
| N+1 discovers N's authority was revoked | Can composition still proceed? | No recovery path defined |
| Authority changed between T_N and T_N+1 | Does N+1 know? | No authority change notification |

**Decision Required:** When is authority re-verification required before composition?

---

### C.5 Scope × Readiness

**Interaction:** Scope must be stable and accessible before composition.

| Scenario | What Happens | Gap |
|---|---|---|
| N+1 needs data from Scope X, but access rules changed | Is composition blocked or does it proceed? | No scope change detection |
| Scope is marked DRAFT while N tries to hand off | Does N wait for ACTIVE scope? | No scope state monitoring |
| N+1 discovers required data is outside scope | Can it request scope extension? | No dynamic scope adjustment |

**Decision Required:** How to verify scope readiness across layers?

---

### C.6 Evidence × State

**Interaction:** Evidence describes state, but state value and evidence can diverge.

| Scenario | What Happens | Gap |
|---|---|---|
| Evidence says "state is ACTIVE" but actual state is DRAFT | Which is source of truth? | No reconciliation rule |
| State changed after evidence was recorded | Does N+1 see stale evidence? | No evidence-state synchronization |
| Multiple evidence entries for same state | Which one is authoritative? | No evidence ordering rule |

**Decision Required:** How to resolve evidence-state conflicts?

---

## D. Composition Decision Semantics

### D.1 Three Distinct Concepts (NOT interchangeable)

**VALID (Layer N)**
- Layer N meets its own criteria
- Example: HAB produces evidence, records state, verifies authority
- Scope: Individual layer, does not address composition

**COMPOSITION-VALID (N → N+1)**
- Layer N and Layer N+1 can safely exchange control
- Requires: All 6 boundaries evaluated at composition point
- Scope: Composition handoff, not execution

**EXECUTABLE (N+1 at runtime)**
- Layer N+1 can proceed with current state
- Requires: Composition-valid PLUS runtime conditions stable
- Scope: Runtime execution, may require re-validation

### D.2 NOT AND-Logic

**WRONG:**
```
Composition Valid = Evidence VALID 
  AND State VALID 
  AND Temporal VALID 
  AND Authority VALID 
  AND Scope VALID 
  AND Readiness VALID
```

**Why wrong:**
- Different boundaries have different uncertainty levels
- Some boundaries interact (and thus cannot be independently true/false)
- UNKNOWN boundaries cannot be treated as FALSE in AND-logic
- AND-logic assumes symmetry; actually Evidence is more critical than Readiness

### D.3 Composition Decision Semantics (to be determined by Human Gate)

The actual decision rule should:

1. **Weight boundaries by criticality:** Not all are equal
   - (Evidence + Authority) probably mandatory
   - (State + Temporal + Scope) probably conditional on boundary interactions
   - (Readiness) probably gating but possibly recoverable

2. **Handle UNKNOWN explicitly:** Cannot use AND-logic with UNKNOWN values
   - UNKNOWN / UNDEFINED → CANNOT PROCEED (missing spec)
   - UNKNOWN / UNDETERMINED → REVIEW WITH HUMAN (evidence insufficient)

3. **Require explicit re-validation:** Some boundaries may need Tn re-validation
   - Evidence: age matters?
   - State: staleness matters?
   - Temporal: clock drift matters?
   - Authority: revocation matters?
   - Scope: access rule changes matter?
   - Readiness: regression matters?

4. **Define failure modes:** What happens if composition decision changes mid-execution?
   - N composition-valid at T1 but not at T2?
   - N+1 detects composition-invalid state during execution?
   - Recovery path: pause, rollback, or alert only?

---

## E. Current Admissibility (Temporal Re-Validation)

### E.1 Problem Statement

T0 (design time): Layer N is VALID  
T_exec (composition time): Layer N is COMPOSITION-VALID  
Tn (later during N+1 execution): Is N still composition-valid?

### E.2 State Changes That Invalidate Composition

| State Change | Boundary Affected | Re-validation Required? |
|---|---|---|
| New evidence arrives | Evidence Boundary | Maybe (depends on content) |
| State transitions in N | State / Temporal Boundary | Probably |
| Authority revocation | Authority Boundary | Yes |
| Scope access rules change | Scope Boundary | Maybe (depends on overlap) |
| System time jumps | Temporal Boundary | Maybe (depends on magnitude) |
| N enters REVIEW (human challenge) | Readiness Boundary | Yes |

### E.3 Re-Validation Conditions (to be specified)

**Staleness:** How long before composition-valid becomes stale?
- 1 second? 1 minute? No time limit?

**Requalification:** Does re-validation require same proof as initial validation?
- Full audit trail review? Or just delta since last validation?

**Composition Re-Validation:** Do ALL boundaries need re-validation or only changed ones?
- Conservative: re-validate all
- Efficient: re-validate affected ones only (requires dependency map)

**Regression Detection:** Can N+1 detect if N became unready?
- Requires N to report its current state to N+1 during execution?
- Requires N+1 to periodically poll N's state?
- Or only detectable post-failure?

### E.4 Position (to be decided by Human Gate)

**Option A: Current Admissibility as 7th Boundary**
- Treat temporal re-validation as independent boundary
- Requires specification of staleness, requalification, regression detection

**Option B: Current Admissibility as horizontal condition**
- Treat as cross-cutting concern applying to all 6 boundaries
- Each boundary defines its own staleness policy
- Composition decision includes "re-validate at Tn" step

**Option C: Current Admissibility deferred to implementation**
- Design-time composition validity sufficient
- Runtime re-validation is implementation detail, not specification
- Risk: May not detect composition failures at runtime

---

## F. HAB / JARVIS Handoff and Execution Conditions

### F.1 HAB Handoff Condition

"This judgment can be passed to the next decision-maker" = ?

**Not yet defined:**
- What must HAB prove to JARVIS?
- Can HAB hand off DRAFT decisions, or only ACTIVE?
- Does JARVIS re-verify HAB's evidence or trust it?
- Does JARVIS check HAB's authority or accept it as given?

**To be specified by Human Gate:**
```
HAB_HANDOFF_VALID if:
  - [ ] Evidence Boundary: HAB evidence is [readable / verified / ???]
  - [ ] State Boundary: HAB state is [consistent / ???]
  - [ ] Authority Boundary: HAB authority is [re-verified / delegated / ???]
  - [ ] Scope Boundary: JARVIS scope [includes / excludes / ???] HAB scope
  - [ ] Readiness Boundary: HAB readiness [re-checked / assumed / ???]
  - [ ] (+ temporal conditions?)
```

---

### F.2 JARVIS Execution Condition

"This judgment can be executed in the current world" = ?

**Not yet defined:**
- COMPOSITION-VALID ≠ EXECUTABLE
- Even if HAB→JARVIS handoff succeeds, does world state still match JARVIS assumptions?
- Can JARVIS detect if world changed since composition?
- What is JARVIS's recovery if execution fails?

**To be specified by Human Gate:**
```
JARVIS_EXECUTABLE if:
  - [ ] Composition-valid at Tn (all boundaries re-validated)
  - [ ] FROZEN data is still accessible
  - [ ] EXTENSION state is still consistent
  - [ ] Authority chain is still valid
  - [ ] Time has not skewed beyond tolerance
  - [ ] (+ other conditions?)
```

---

## G. Additional Boundary Assessment

**Question:** Are 6 boundaries sufficient and exhaustive?

### G.1 Candidates for Additional Boundaries

**Consistency Boundary**
- Definition: Records for the same decision across N and N+1 refer to the same fact
- Current status: No explicit specification
- Candidate?: Arguably subsumed by Evidence + State (not independent)

**Idempotency Boundary**
- Definition: N→N+1 composition can be safely re-executed
- Current status: No specification
- Candidate?: Probably independent (requires explicit idempotency proof)

**Rollback Boundary**
- Definition: If N+1 fails, can N safely rollback?
- Current status: No recovery mechanism defined
- Candidate?: Could be independent or part of Readiness

**Observer Boundary**
- Definition: Can JARVIS reliably observe what happened in HAB layer?
- Current status: No specification
- Candidate?: Arguably subsumed by Evidence (just a use case)

### G.2 Assessment

**Recommended:** Do not add additional boundaries at this stage.

Reason: The 6 existing boundaries already identified in Paper 5 provide coverage. Candidates above are either:
- Subsumed by existing boundaries (Consistency, Observer)
- Implementation concerns, not specification boundaries (Idempotency, Rollback)

**If Human Gate disagrees:** Additional boundaries must be formally proposed with clear distinction from 6 existing ones.

---

## H. Phase 1 Completion Checklist

Map all 9 required items to one of 4 categories:

| Item | Status | Category | Rationale |
|---|---|---|---|
| **1. Boundary Definitions** | Complete | HUMAN DECISION REQUIRED | 6 boundaries defined above; definitions are candidates, not final |
| **2. Boundary Evidence Requirements** | Complete | HUMAN DECISION REQUIRED + EVIDENCE GAP | Evidence levels mapped; many gaps identified (CONNECTED, RUNTIME VERIFIED missing) |
| **3. Boundary Interactions** | Complete | HUMAN DECISION REQUIRED | 6 key interactions identified; resolution rules NOT defined |
| **4. Composition Decision Semantics** | Complete | HUMAN DECISION REQUIRED | VALID vs COMPOSITION-VALID vs EXECUTABLE distinction made; decision rule NOT defined |
| **5. UNKNOWN Semantics** | Complete | FIXED | UNDEFINED vs UNDETERMINED distinction maintained throughout |
| **6. Temporal / Current Admissibility** | Complete | HUMAN DECISION REQUIRED | 3 positioning options (7th boundary / horizontal / deferred) presented; Human Gate must choose |
| **7. HAB Handoff Condition** | Template | HUMAN DECISION REQUIRED | Template provided; actual conditions NOT specified |
| **8. JARVIS Execution Condition** | Template | HUMAN DECISION REQUIRED | Template provided; actual conditions NOT specified |
| **9. Additional Boundary Assessment** | Complete | FIXED | Assessment complete; recommend NOT adding 7th boundary at this stage |

---

## Summary: What Is FIXED vs. What Requires Decision

### FIXED (No re-decision needed)

- UNDEFINED vs UNDETERMINED distinction is maintained
- 6 boundaries are adopted from Paper 5
- Evidence levels (DESIGNED/IMPLEMENTED/CONNECTED/RUNTIME VERIFIED) framework
- Assessment: Do not add 7th boundary (Consistency, Idempotency, Rollback are not independent)

### HUMAN DECISION REQUIRED

- **Boundary definition refinement:** Are definitions above sufficient, or do they need adjustment?
- **Interaction resolution rules:** How to handle boundary interactions (Evidence × Temporal, State × Authority, etc.)?
- **Composition decision semantics:** What is the actual decision rule? (Not AND-logic, but what?)
- **Current Admissibility position:** 7th boundary vs horizontal vs deferred?
- **HAB Handoff specifics:** What evidence/state/authority does JARVIS require from HAB?
- **JARVIS Execution specifics:** What world conditions must JARVIS verify before executing?
- **Staleness policy:** How long is composition-valid still valid?
- **Re-validation triggers:** What changes force re-validation of which boundaries?

### EVIDENCE GAP (Cannot currently decide, need investigation)

- Can JARVIS read and interpret HAB evidence identically? (CONNECTED evidence level missing)
- Does State/Semantic composition work with concurrent reads? (CONNECTED + RUNTIME VERIFIED missing)
- What causal dependencies are we tracking? (Causal evidence mechanism not implemented)
- How do we detect scope conflicts? (Scope overlap resolution rules missing)
- What is the recovery if readiness regresses? (Recovery mechanism undefined)

### IMPLEMENTATION LATER (After specifications are decided)

- Composition Readiness Validator implementation
- Cross-boundary evidence logger
- State semantic consistency checker
- Temporal causality verifier
- Authority re-validator at composition boundary
- Scope conflict detector
- Current Admissibility monitor (staleness checker)
- Composition re-validation runner at Tn

---

## End of Specification Framework Draft

This document is NOT a final specification.

This is a **structured candidate for Human Gate review**, showing:
- What is understood (Boundary definitions)
- What is decided (UNDEFINED/UNDETERMINED distinction, do NOT add 7th boundary)
- What requires decision (9 items in HUMAN DECISION REQUIRED)
- What is missing evidence for (6 items in EVIDENCE GAP)
- What is deferred to later (8 implementation items)

---

*Next: Convert this into Decision Candidate for Human Gate (Kuroko/博士) approval.*
