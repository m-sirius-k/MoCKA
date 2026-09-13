# L2 Formal Semantic Design — Human Gate Review Package

**Package ID:** L2-HGRP-20260913-001
**Prepared By:** Claude Haiku 4.5 (くろこ)
**Prepared For:** Human Gate (nsjp_kimura)
**Date Prepared:** 2026-09-13
**Design Submission Point:** Commit c5a07b5 (L2_FORMAL_SEMANTIC_DESIGN_PACKAGE.md)
**Status:** REVIEW_READY / HG_DECISION_PENDING

---

## EXECUTIVE SUMMARY

This package structures the Layer 2 Formal Semantic Design (prepared under Q-L2-01 AUTHORIZE, design-only scope) into explicit Human Gate decision points.

**Key Principle:** This review package does NOT solicit Implementation Authorization. Implementation Authorization remains NOT_GRANTED throughout and after design review.

**Design Authority:** Q-L2-01 AUTHORIZE (Design-only)
**Decision Authority:** Human Gate (nsjp_kimura)
**Decision Scope:** ① Semantic Definition (L2-01～05) | ② M18-Scope is Q7 separate domain | ③ Design Assumptions (DA-01～08) | ④ Evidence Authorization

---

## PART 1: SUBMISSION CONTEXT

### Submission Point

```
Commit:  c5a07b5
Branch:  origin/claude/jolly-gates-du1xaj
File:    data/decisions/L2_FORMAL_SEMANTIC_DESIGN_PACKAGE.md
Size:    91,424 bytes / 2,744 lines
Status:  DRAFT / PROPOSED
```

### Design Approach Applied

1. **Evidence-Bounded:** All definitions grounded in evidence from Layers 1-4 (R01 investigation)
2. **Counterexample-First:** Each definition includes semantic boundary violation scenarios
3. **Design-Assumption Explicit:** DA-01 through DA-08 separate proposed semantics from established facts
4. **UNKNOWN Preserved:** No inference upgrades of unresolved states

### Boundary Maintenance Throughout Design

```
Design Authorization ≠ Implementation Authorization
Design Approval ≠ Design Approval
DRAFT Proposal ≠ Approved Definition
```

---

## PART 2: L2 SEMANTIC CLASSIFICATION

### Evidence-Supported Semantics

These elements have direct evidence basis from Layers 1-4:

1. **Layer 1 Concept Existence:**
   - Consequential Action: OBSERVED (Paper 3.5ζ, SPP/PHL v1.0)
   - Authorization framework: OBSERVED (GL7 tool-level gate exists)

2. **Layer 2 Semantic Status (Pre-Design):**
   - ActualConsequence formal type: NOT_ESTABLISHED
   - AuthorizedConsequence formal type: NOT_ESTABLISHED
   - CO formal type: UNKNOWN
   - Authorization Scope 3D: NOT_FOUND
   - Semantic Closure path: NOT_ACHIEVED

3. **Layer 3/4 Implementation Status:**
   - GL7 event emission: OBSERVED (governance_pipeline.py, execution_governance.py)
   - GL7 consequence consume/enforce: NOT_FOUND
   - State change capture mechanism: NOT_FOUND
   - Consequence binding to authorization: NOT_FOUND

### Proposed Semantics (This Design)

L2-01 through L2-05 formalize the above NOT_ESTABLISHED / UNKNOWN / NOT_FOUND items as PROPOSED designs:

```
L2-01: ActualConsequence = PROPOSED formal type
       (structure, identity, temporal constraints, scope boundaries)

L2-02: AuthorizedConsequence = PROPOSED formal type
       (specification, scope binding, verification criterion)

L2-03: CO (Consequential Outcome) = PROPOSED formal type
       (compliance_status binding, authorization linkage)

L2-04: Authorization Scope = PROPOSED formalization
       (3D WHO/WHEN/WHAT + 6 optional extensions)

L2-05: Semantic Closure Relationship = PROPOSED conditions
       (closure requirements, failure modes, propagation cascade)
```

### Unresolved Elements (For HG Decision)

**Within Semantic Definition Scope (HG-L2-01～07):**
```
CO formal type finalization          (3 candidates; HG selects)
Scope dimension weighting            (WHO vs WHEN vs WHAT priority)
Consequence cardinality              (1 action → 1 or N consequences?)
Evidence temporal tolerance          (GL7 event age threshold)
Revocation timing requirements       (detection SLA)
Cascade consequence attribution      (multi-level authorization chain)
Legacy authorization migration       (existing records retrofit)
Performance targets                  (scope validation latency SLA)
Exception handling policy            (scope validation failure)
```

**Outside Semantic Definition Scope (Q7 / Separate Decision Domain):**
```
M18-Scope definition                 (separate Q7 decision; NOT prerequisite for semantic definition)
```

---

## PART 3: DESIGN ASSUMPTIONS (DA-01～DA-08)

### DA-01: Authorization Semantics are Explicit

**Assumption:** Authorization decisions must be formally recorded with clear WHO/WHEN/WHAT; no inference from code behavior.

| Aspect | Value |
|--------|-------|
| Rationale | Authorization-consequence chain requires unambiguous starting point; code behavior alone insufficient |
| Evidence | GL7 gate uses formal decision model; authorization lookup required |
| Risk | Code and formal semantics diverge; runtime enforcement based on wrong assumptions |
| If Wrong | Consequences attributed to wrong authorization; M18 closure unverifiable |
| Verification | L3 schema enforces required fields; authorization record must exist before consequence recorded |
| HG Decision | Required if L2 design proceeds |

### DA-02: Consequences are Observable

**Assumption:** Every authorized action produces observable consequences (via GL7, logs, state changes, or audit trail).

| Aspect | Value |
|--------|-------|
| Rationale | ActualConsequence requires evidence channel; unobservable actions cannot be verified |
| Evidence | GL7 framework assumes observation channels (ALLOW/DENY events) |
| Risk | Silent failures; actions execute with no recorded consequence; M18 verification incomplete |
| If Wrong | ActualConsequence cannot be created; compliance proof impossible |
| Verification | GL7 persist mechanism confirmed; audit trail consistency verified |
| HG Decision | No HG decision needed (framework assumption) |

### DA-03: AuthorizedConsequence Specification is Feasible

**Assumption:** For each authorization, formal specification of permitted consequences can be created and maintained.

| Aspect | Value |
|--------|-------|
| Rationale | AuthorizedConsequence binding requires pre-specification; otherwise "anything goes" |
| Evidence | Consequence types enumerated in design (permission, behavior, state, data, timing, availability) |
| Risk | Specification overhead exceeds practical benefit; system becomes unmaintainable |
| If Wrong | Enforcement cannot validate actual vs authorized; scope checking infeasible |
| Verification | L3 creates AuthorizedConsequence for ≥10 representative authorizations |
| HG Decision | Required if L2 design proceeds |

### DA-04: CO Binding Preserves Authorization Link

**Assumption:** CO (Consequential Outcome) artifact always maintains bidirectional link to originating Authorization.

| Aspect | Value |
|--------|-------|
| Rationale | M18 verification requires unbroken chain: Authorization → AuthConsq → ActConsq → CO |
| Evidence | Data integrity principle; system design assumes referential integrity |
| Risk | CO records become orphaned; authorization chain breaks; M18 closure fails |
| If Wrong | Consequence enforcement abandoned; cannot verify which authorization allowed action |
| Verification | Schema enforces foreign key constraints; orphan records trigger alerts |
| HG Decision | No HG decision needed (universal data integrity principle) |

### DA-05: Scope Intersection Logic is Unambiguous

**Assumption:** WHO ∩ WHEN ∩ WHAT validation rules are consistent across all 109 routes (no route-specific exceptions).

| Aspect | Value |
|--------|-------|
| Rationale | Inconsistent logic creates authorization gaps; M18 verification requires uniform rules |
| Evidence | 109 routes form unified system; exception handling complicates semantics |
| Risk | Routes 30 (unverified) or 15 (necessity not proven) may require special logic; uniform rules insufficient |
| If Wrong | Some routes bypass scope validation; authorization scope unverifiable for those routes |
| Verification | Scope validation algorithm tested on all 109 routes |
| HG Decision | Required (M18-Scope decision may force route-specific logic) |

### DA-06: Revocation is Timely

**Assumption:** Revocation signals (authorization cancellation, permission removal, temporary grant expiration) are detected and enforced before consequence permission is granted.

| Aspect | Value |
|--------|-------|
| Rationale | Revoked authorization must block execution; delayed detection allows unauthorized actions |
| Evidence | GL7 gate must check revocation status before ALLOW; cache staleness is risk |
| Risk | Revocation signal delayed; GL7 cache stale; unauthorized consequence recorded |
| If Wrong | Revoked authorization permits execution; compliance proof false |
| Verification | GL7 revocation check tested; cache invalidation verified; latency SLA measured |
| HG Decision | Required (SLA decision: <X ms revocation detection) |

### DA-07: M18-Scope is Decidable

**Assumption:** For each of 109 routes, HG can definitively determine whether execution is within or outside M18 closure scope.

| Aspect | Value |
|--------|-------|
| Rationale | CO.m18_relevance categorization requires explicit scope; UNKNOWN blocks verification |
| Evidence | M18 evidence reconciliation identified 3 blockers; HG must decide if M18-Scope is solvable |
| Risk | M18-Scope remains UNRESOLVED; CO cannot be categorized; M18 closure unverifiable |
| If Wrong | M18 closure unachievable; M18 Runtime Closure remains LOCKED |
| Verification | HG decision recorded; M18-Scope definition formalized; routes categorized |
| HG Decision | CRITICAL BLOCKER (separate from design review) |

### DA-08: 109/30/15 Separation Remains Intact

**Assumption:** L2 design does NOT redefine route categories (109 OBSERVED / 30 PRIOR_ASSERTION / 15 NECESSITY_NOT_PROVEN); categories remain stable.

| Aspect | Value |
|--------|-------|
| Rationale | Route categories are foundational for M18 scope; redefining them changes evidence baseline |
| Evidence | Route categorization from prior investigation; L2 design builds on existing classification |
| Risk | Route categories unknowingly redefined during L2 formalization; verification baseline shifts |
| If Wrong | M18 closure measured against wrong route set; 15-path requirement not satisfied |
| Verification | L2 design review confirms category stability; no routes reclassified |
| HG Decision | No HG decision needed (constraint, not decision) |

---

## PART 4: HGDECISION ITEMS

### HG-L2-01: L2 Formal Semantic Design (Comprehensive)

**Question:** Does HG approve L2-01 through L2-05 formal semantics as designed in L2_FORMAL_SEMANTIC_DESIGN_PACKAGE.md (commit c5a07b5)?

**Options:**
- **ACCEPT** — Design approved as-is; proceed to L3 implementation authorization
- **ACCEPT_WITH_CONDITIONS** — Design approved with specified changes/constraints
- **HOLD** — Design acceptable in principle; defer pending other decisions (e.g., M18-Scope)
- **REJECT** — Design fundamentally flawed; redesign required

**Evidence Provided:**
- Section 7-11: L2-01 through L2-05 detailed design (definitions, types, examples, counterexamples)
- Section 15: Design Assumption Registry (DA-01～08)
- Section 19: Design Risks (5 identified risks with mitigation)
- Section 20-21: Implementation and Verification Preconditions

**If REJECT:**
- Primary concerns (specify)
- Alternative design proposals (if any)
- Redesign scope (which L2-0X definitions need rework)

**If ACCEPT_WITH_CONDITIONS:**
- Required changes (specific section references)
- Constraint(s) on L3 implementation
- Additional verification steps

**Timeline:** Design review phase

---

### HG-L2-02: ActualConsequence Semantic Definition

**Question:** Does HG accept the ActualConsequence formal definition (L2-01: observable state transition, typed structure, temporal semantics, scope boundaries)?

**Design Summary:**
```
ActualConsequence
  = Observable state transition / effect / event
    detected via evidence channel after execution
    and attributed to that execution

Type:  {identity, action, authorization, state_before, state_after,
        observation, timestamp, evidence_status, scope}

Evidence Status: PARTIAL (GL7 emit + log; state capture NOT_FOUND)

Preconditions: Authorization issued, Action executed, Observation fired, State measurable
Postconditions: Authorization scope updated, Target Invariant evaluated, Evidence appended
```

**Open Questions (from Section 7):**
1. Consequence delay tolerance (eventual consistency timing)
2. Consequence magnitude limits (what counts as observable)
3. Distinction: consequence vs side effect
4. Cascade consequences (authorization → permission → downstream permission grant)
5. Observation channel failure retroactivity

**Options:**
- **ACCEPT** — Definition approved; proceed to L3 implementation
- **ACCEPT_WITH_CONDITIONS** — Specify required changes (type field changes, precondition modifications)
- **HOLD** — Definition acceptable; defer pending L2 preconditions (scope boundary formalized in L2-04)
- **REJECT** — Fundamental issues; specify concerns

**Important:** ActualConsequence.scope depends on Authorization Scope formalization (HG-L2-05), NOT on M18-Scope definition. Semantic definition can be approved independently of M18-Scope decision.

**Timeline:** Post-HG-L2-01 decision

---

### HG-L2-03: AuthorizedConsequence Semantic Definition

**Question:** Does HG accept the AuthorizedConsequence formal definition (L2-02: formal specification of permitted consequences, scope binding, verification criterion)?

**Design Summary:**
```
AuthorizedConsequence
  = Formal specification of consequences authorized to occur
    
Relationship to ActualConsequence:
  Authorization → AuthorizedConsequence (defines bounds)
                → [execution]
                → ActualConsequence (realized in runtime)
                → Evidence

Type:  {identity, authorization, consequence_type, scope, permitted_values,
        constraints, evidence_required, temporal_window, status}

Evidence Status: NOT_ESTABLISHED (specification NOT_FOUND; scope NOT_FOUND)

Preconditions: Authorization granted with explicit consequence declaration
Postconditions: Consequence must match specification; violation triggers enforcement
```

**Open Questions (from Section 8):**
1. Scope relationship to Authorization Scope (subset/equal/superset)
2. Consequence type taxonomy (permission, behavior, state, data, timing, availability)
3. Constraint validation timing (pre-execution or post-observation)
4. Multiple AuthorizedConsequences per Authorization (one-to-many cardinality)
5. Revocation behavior (how revocation affects existing AuthorizedConsequence records)

**Options:**
- **ACCEPT**
- **ACCEPT_WITH_CONDITIONS** — Specify type taxonomy, constraint semantics, cardinality rule
- **HOLD** — Depends on L2-04 (Authorization Scope) finalization
- **REJECT** — Specify concerns

**If HOLD:** Dependency chain: L2-04 → L2-02 → L2-03 (backward dependency on scope)

**Timeline:** Post-HG-L2-01 decision

---

### HG-L2-04: CO (Consequential Outcome) Semantic Definition

**Question:** Does HG accept the CO (Consequential Outcome) formal definition (L2-03: consequence artifact binding ActualConsequence to AuthorizedConsequence)?

**Design Summary:**
```
CO (Consequential Outcome) — Current Evidence: UNKNOWN

Three Candidate Interpretations:
  1. CO as Final Outcome: ActConsq → CO (consolidated result)
  2. CO as Captured Observation: AuthConsq + ActConsq → CO (artifact linking)
  3. CO as Change Order: Authorization → CO (formal record linking auth to outcome)

Proposed Structure (Candidate):
  CO = {identity, consequence_id, authorization_id, authorized_spec_id,
        compliance_status (WITHIN|EXCEEDS|VIOLATES|UNKNOWN),
        scope_binding, timestamp, evidence_sources, interpretation,
        m18_relevance (RELEVANT|IRRELEVANT|UNKNOWN)}

Relationship to M18:
  M18 closure = all CO where compliance_status ≠ UNKNOWN
  Verification = aggregate compliance_status across routes
```

**Open Questions (from Section 9):**
1. CO is mandatory or optional per consequence
2. Minimal CO (what fields required)
3. Retroactive CO creation (can CO be created after-the-fact)
4. Multiple COs per ActualConsequence (cardinality)
5. CO lifecycle (immutable or updatable)

**Options:**
- **ACCEPT** — Candidate structure approved; select interpretation
- **ACCEPT_WITH_CONDITIONS** — Specify: interpretation choice, mandatory fields, lifecycle policy
- **REJECT** — Alternative proposal

**Important Semantic/Scope Separation:**

CO semantic definition (type structure, compliance_status binding, field definitions) is INDEPENDENT of M18-Scope.

The m18_relevance field is designed as a semantic structure WITHOUT requiring M18-Scope decision.
M18-Scope decision (HG-L2-08, Q7) determines WHERE this semantic framework is applied, not WHETHER the semantics are valid.

**Consequence of M18-Scope Decision (handled separately):**
- If HG-L2-08 = DEFINE NOW: m18_relevance populated per scope definition at runtime
- If HG-L2-08 = DEFER: m18_relevance remains UNKNOWN in runtime; CO structure still valid

**Timeline:** Post-HG-L2-01 decision (INDEPENDENT of HG-L2-08 M18-Scope decision)

---

### HG-L2-05: Authorization Scope Semantic Definition

**Question:** Does HG accept the Authorization Scope formal definition (L2-04: 3D formalization WHO/WHEN/WHAT + optional extensions)?

**Design Summary:**
```
Authorization Scope — 3D Core + 6 Optional Extensions

Core 3D (Mandatory):
  WHO:   Subject identity + verification method + constraints (location, device, session, temporal)
  WHEN:  Temporal validity (issued_at, expires_at, valid_from, valid_until, window type, timezone)
  WHAT:  Action/Consequence permitted (action_type, resource, resource_scope,
         consequence_class, constraints)

Optional Extensions (PROPOSED):
  WHERE:       Spatial/network scope (allowed locations, networks, devices)
  CONTEXT:     Situational constraints (MFA, audit log, approval, risk level)
  EVIDENCE:    Verification requirements (proof types, verification methods, chain of custody)
  EXPIRATION:  Time-limited validity (fixed, inactivity, action count, revocation check interval)
  REVOCATION:  Invalidation conditions (immediate, deferred, custom logic, timestamp)
  SUPERSESSION: Replacement rules (superseded_by, date, compatibility mode)

Validation Rules:
  Intersection Rule: ALL dimensions must be satisfied (not UNION)
  Subset Rule: Narrower scope subsumes broader
  Override Rule: More specific overrides general
```

**Open Questions (from Section 10):**
1. Core 3D vs Optional Extensions precedence (if CONTEXT requires MFA but WHO allows all users)
2. Scope dimension weighting (WHO importance vs WHEN vs WHAT)
3. WHERE/CONTEXT feasibility (can all routes enforce these constraints)
4. Intersection validation algorithm formalization (WHO ∩ WHEN ∩ WHAT formal logic)
5. Route-specific scope exceptions (15-path routes may need different scope rules)

**Options:**
- **ACCEPT** — 3D + Extensions approved; proceed to scope validation algorithm formalization
- **ACCEPT_WITH_CONDITIONS** — Specify: mandatory vs optional extensions, intersection algorithm, route exceptions
- **REJECT** — Alternative approach

**Important Note on M18-Scope Relationship:**
Authorization Scope semantic definition (WHO/WHEN/WHAT 3D formalization) is independent of M18-Scope boundary decision.
Scope can be formalized for all authorization types regardless of which routes are within M18 closure scope.

M18-Scope decision (HG-L2-08, Q7) determines which routes require scope enforcement for M18 verification, not whether the semantic definition is valid.

**If ACCEPT_WITH_CONDITIONS:** HG must specify intersection algorithm details (HG-L2-05 precondition for L3)

**Timeline:** Post-HG-L2-01 decision (INDEPENDENT of HG-L2-08 M18-Scope decision)

---

### HG-L2-06: Semantic Closure Relationship Definition

**Question:** Does HG accept the Semantic Closure Relationship formal definition (L2-05: formal conditions for achieving closure confidence, failure conditions, propagation rules)?

**Design Summary:**
```
Semantic Closure Relationship — NOT achieving closure; defining conditions for closure

Closure Conditions (4 proposed):
  1. Complete Semantic Definition: L2-01～05 formalized ✓ (this design)
  2. Unambiguous Authorization Chain: Authorization → Scope → AuthConsq → ActConsq → CO → M18
  3. Evidence Completeness: 5 evidence layers present for ≥90% of authorization instances
  4. Consistency Across Routes: Same verification logic for all 109 routes (no special cases)

Failure Conditions (5 scenarios):
  1. Ambiguous Authorization Scope (scope not specified; consequence unverifiable)
  2. Consequence Not Observable (consequence happens; no GL7 event or state change)
  3. AuthorizedConsequence Exceeds Scope (permission "read"; consequence permits "read+delete")
  4. CO Creation Fails (evidence chain broken; compliance proof missing)
  5. Revocation Not Detected (GL7 cache stale; authorization revoked but not checked)

Propagation Rules (cascade):
  UNKNOWN at layer N → blocks verification at N+1 → NOT_PROVEN at N+2
  NOT_PROVEN constraints unverifiable at runtime
  One UNKNOWN anywhere in chain blocks entire closure

Important Distinction:
  Semantic Closure (L2 formalization) ≠ M18 Runtime Closure (architectural goal)
  Semantic Closure = formal definitions complete
  M18 Runtime Closure = all 109 routes verified compliant
```

**Open Questions (from Section 5):**
1. Closure condition precedence (must all 4 be satisfied simultaneously)
2. Evidence completeness threshold (why ≥90%; what about edge routes)
3. Route consistency exceptions (15 Paths may be impossible to verify uniformly)
4. Temporal closure (point-in-time or continuous verification)
5. Failure detection and recovery (how to handle cascade failures)

**Options:**
- **ACCEPT** — Closure relationship approved; semantics formalized for reference
- **ACCEPT_WITH_CONDITIONS** — Specify: condition precedence, evidence thresholds, route exception handling
- **HOLD** — Closure concept acceptable; defer achievement target (M18 closure decision separate)
- **REJECT** — Closure semantics not workable

**Important:** This decision does NOT achieve closure; it formalizes the relationship for future evaluation.

**Timeline:** Post-HG-L2-01 decision

---

### HG-L2-07: Design Assumptions (DA-01～DA-08)

**Question:** Does HG accept the Design Assumption Registry (DA-01 through DA-08) and their associated risks?

**Summary Table:**

| ID | Assumption | Risk | HG Decision Required |
|----|-----------|------|----------------------|
| DA-01 | Authorization semantics explicit | Divergence from code behavior | YES |
| DA-02 | Consequences observable | Silent failures, incomplete verification | NO* |
| DA-03 | AuthConsq specification feasible | Specification overhead, maintenance burden | YES |
| DA-04 | CO binding preserves auth link | Orphaned CO records, chain breaks | NO* |
| DA-05 | Scope intersection unambiguous | Route-specific logic required | YES |
| DA-06 | Revocation timely | Revocation delay, unauthorized actions | YES |
| DA-07 | M18-Scope decidable | CRITICAL BLOCKER | YES (separate) |
| DA-08 | 109/30/15 separation stable | Route categories redefined unknowingly | NO* |

*NO = framework assumption; system design depends on this; no HG decision needed*

**Options:**
- **ACCEPT** — All assumptions accepted; design proceeds
- **ACCEPT_WITH_CONDITIONS** — Specify which assumptions require additional mitigation
- **CONDITION** — Specify conditions under which each assumption is accepted
- **HOLD** — Assumptions acceptable; defer risk acceptance pending other decisions
- **REJECT** — Assumptions unacceptable; specify which and why

**If REJECT:** Specify alternative assumptions or constraints

**Timeline:** Post-HG-L2-01 decision (concurrent with individual L2-0X decisions)

---

## HG DECISION DEPENDENCY TREE

**CRITICAL CORRECTION: Semantic Definition ≠ M18-Scope Application**

```
① SEMANTIC DEFINITION APPROVAL
   (HG-L2-01～07: What do the semantics mean?)

   HG-L2-01: L2 Design Acceptance
        │
        ├── HG-L2-02: ActualConsequence (semantic definition)
        ├── HG-L2-03: AuthorizedConsequence (semantic definition)
        ├── HG-L2-04: CO (semantic definition) ← INDEPENDENT of M18-Scope
        ├── HG-L2-05: Authorization Scope (semantic definition) ← INDEPENDENT of M18-Scope
        ├── HG-L2-06: Semantic Closure Relationship (semantic definition)
        │
        └── HG-L2-07: Design Assumptions (DA-01～08 risk acceptance)
               │
               └── All prerequisites for ① COMPLETE


② SCOPE APPLICATION DOMAIN (SEPARATE Q7 DECISION)
   (HG-L2-08: Where does this semantic framework apply?)

   HG-L2-08: M18-Scope Definition ← Q7 DECISION DOMAIN (NOT prerequisite for ①)
        │
        ├── Determines where semantics are applied
        ├── Does NOT validate whether semantics are correct
        ├── Can be DEFER-ed without invalidating ① semantic definitions
        └── Affects implementation detail (m18_relevance population)


③ EVIDENCE AUTHORIZATION (DOWNSTREAM)
   (HG-L2-09: Should we collect next evidence?)

   HG-L2-09: Next Evidence Program ← Depends on ① completion (NOT ②)
        │
        ├── EG-M18-02: M18-Scope Formalization (IF HG-L2-08 = DEFINE NOW)
        ├── EG-M18-04: Historical Evidence (independent)
        └── EG-M18-01: Live Runtime Collection (requires both ① and optional ②)


④ IMPLEMENTATION AUTHORIZATION (FUTURE)
   (NOT part of this review; remains NOT_GRANTED)

   Implementation Authorization ← Requires: ① ACCEPT + (HG choices on ②)
        │
        └── NOT_GRANTED until explicit separate decision
```

**Key Principle:**

```
① ≠ ②

Semantic Definition Approval (①) CAN PROCEED without M18-Scope Definition (②)
Semantic Approval ≠ Scope Definition ≠ Implementation Authorization
```

---

### HG-L2-08: M18-Scope Definition

**Question:** Does HG define M18-Scope boundary now, or defer to implementation phase?

**Context:**
```
Current M18-Scope Status: UNRESOLVED / LOCKED

M18 Evidence Reconciliation (prior session):
  Blocker 1: HG Binding BROKEN (Authority→Runtime connection severed)
  Blocker 2: Consequential Path Coverage UNKNOWN (routes with explicit consequences not identified)
  Blocker 3: Authorization Lineage NOT_PROVEN (auth chain to GL7 not demonstrated)

Relationship to L2 Semantic Design:
  CO semantic definition (HG-L2-04) = INDEPENDENT of M18-Scope
  M18-Scope determines WHERE semantics apply, not WHETHER they are valid
  L3 Implementation CAN proceed with M18_RELEVANCE = UNKNOWN until M18-Scope defined
  L4 Verification depends on M18-Scope boundary (separate decision domain from semantic approval)

Q7 Authority Boundary:
  Q5 = Global Formal Semantic Definition (L2 design approval — HG-L2-01～07)
  Q7 = M18-Scope Boundary (separate decision domain — HG-L2-08)
  These are INDEPENDENT authority domains
```

**Options:**
- **DEFINE NOW** — HG specifies explicit M18-Scope definition (which routes in/out of scope)
- **DEFER** — M18-Scope decision deferred to implementation phase (L3 proceeds with M18 as TBD)
- **HOLD** — M18-Scope remains unresolved; no progress until decided

**If DEFINE NOW:**
- Provide explicit categorization (Route_ID → IN_SCOPE | OUT_OF_SCOPE | UNKNOWN)
- Specify criteria for route categorization
- Clarify how 15-path routes are categorized

**If DEFER:**
- L3 implementation proceeds with M18_RELEVANCE = UNKNOWN for all CO records
- L4 verification cannot begin until M18-Scope defined
- Delivery of M18 closure proof delayed

**Timeline:** Separate from HG-L2-01～07 (can be concurrent or deferred)

**Important:** M18-Scope decision does NOT block HG-L2-04 (CO semantic definition).
Semantic approval and scope definition are independent governance domains (Q5 vs Q7).

**Impact if DEFER:**
- ① Semantic definitions approved (HG-L2-01～07) regardless
- ② M18 verification capability delayed (requires M18-Scope)
- ③ L3 implementation can proceed with runtime constraints (M18_RELEVANCE field populated later)
- ④ Full M18 closure proof deferred (until M18-Scope defined)

---

### HG-L2-09: Next Evidence Program Authorization

**Question:** Does HG authorize the next evidence collection program (Evidence Gaps EG-M18-02, EG-M18-04, EG-M18-01)?

**Context:**
```
Previous M18 Reconciliation Identified Evidence Gaps:
  EG-M18-01: Live Runtime Evidence Collection (HG-L2-01～07 approval → proceed)
  EG-M18-02: M18-Scope Formalization (depends on HG-L2-08, Q7 decision)
  EG-M18-03: Consequence Definition Path (resolved by L2 design approval)
  EG-M18-04: Historical Evidence N-10系 (locate or declare obsolete — independent)

Sequencing:
  ① HG-L2-01～07 APPROVED → EG-M18-01, EG-M18-04 can proceed (design approved)
  ② HG-L2-08 DEFINE NOW → EG-M18-02 can proceed (M18-Scope defined)
  ③ HG-L2-08 DEFER → EG-M18-01 proceeds with M18-Scope TBD; EG-M18-02 deferred

Key Distinction:
  ⚠ Evidence Authorization (HG-L2-09) ≠ Implementation Authorization (remains NOT_GRANTED)
  ✓ Evidence collection is investigation-only; no code/schema/runtime modification
```

**Critical Clarification:**
```
HG-L2-09 AUTHORIZE = Evidence Collection Authorization
                   ≠ Implementation Authorization
                   ≠ M18 Closure Authorization

Evidence collection is investigation-only; no code/schema/runtime modification.
```

**Options:**
- **AUTHORIZE** — Evidence program authorized; EG-M18-02, EG-M18-04, EG-M18-01 can proceed
- **DEFER** — Evidence program deferred pending HG-L2-08 (M18-Scope) or other decisions
- **HOLD** — Evidence program suspended

**If AUTHORIZE:**
- Specify which evidence gaps (EG-M18-01, EG-M18-02, EG-M18-04)
- Specify sequence constraints
- Define success criteria for each gap resolution

**If DEFER:**
- Specify dependencies (what decisions must complete first)
- Specify timeline for reactivation

**Timeline:** Post-HG-L2-01 decision (can be concurrent with M18-Scope decision)

**Important:** Evidence authorization is NOT implementation authorization; system remains HOLD / FAIL-CLOSED throughout.

---

## PART 5: DECISION RECORD TEMPLATE

### For HG Recording Decisions

**Decision Template (one per HG-L2-0X):**

```
HG-L2-XX: [Decision Name]
Date Decided: [YYYY-MM-DD]
Authority: nsjp_kimura (Human Gate)
Scope: [Design-time / Evidence-only / Implementation-time]
Decision: [ACCEPT | ACCEPT_WITH_CONDITIONS | HOLD | REJECT | DEFINE NOW | DEFER | AUTHORIZE]

Rationale:
  [2-3 sentence reasoning]

Conditions (if ACCEPT_WITH_CONDITIONS or CONDITION):
  1. [Condition 1]
  2. [Condition 2]
  ...

Evidence Considered:
  - L2_FORMAL_SEMANTIC_DESIGN_PACKAGE.md (commit c5a07b5)
  - Section [X]: [description]
  - [Other evidence]

Dependencies:
  [If decision depends on other HG decisions, list them]

Next Actions:
  1. [Action 1]
  2. [Action 2]

Recorded By: [nsjp_kimura]
Recorded In: data/decisions/HG_DECISION_RECORD_20260913.md
```

---

## PART 6: SYSTEM STATE AT REVIEW SUBMISSION

**Locked States (Maintained Throughout):**
```
✓ N14R Necessity               = NOT_PROVEN / LOCKED
✓ M18 Runtime Closure         = NOT_ACHIEVED / LOCKED
✓ Authority→Runtime Binding   = BROKEN / LOCKED
✓ C2-b                        = BLOCK / LOCKED
✓ Implementation Authorization = NOT_GRANTED / LOCKED
✓ Production Modification      = 0 / LOCKED
✓ Runtime Modification         = 0 / LOCKED
✓ Schema Modification          = 0 / LOCKED
✓ Code Modification            = 0 / LOCKED
✓ System                       = HOLD / FAIL-CLOSED / LOCKED
```

**Design Status:**
```
✓ L2 Design                   = COMPLETE / DRAFT / PROPOSED
✓ Git Tracking                = COMPLETE
✓ Commit                       = c5a07b5 (SYNCED to remote)
✓ Working Tree                 = CLEAN
```

**Evidence State:**
```
✓ UNKNOWN preserved (not converted to FALSE/ABSENT)
✓ UNDEFINED preserved (not assumed missing)
✓ NOT_PROVEN preserved (not assumed false)
✓ Evidence and inference separated
✓ No implementation authorization inferred
✓ No design approval inferred
```

---

## PART 7: FOUR-LAYER GOVERNANCE SEPARATION

**For Human Gate Review: Clear Distinction Between Authority Domains**

This design package addresses ONLY layer ① below. Layers ②, ③, ④ are separate decisions.

```
① SEMANTIC DEFINITION
   "What do the concepts mean?"
   
   Scope: Formal types, structures, relationships, preconditions, postconditions
   Authority: Q5 (HG-L2-01～07 decision)
   Status: DESIGN / DRAFT / PROPOSED (ready for HG review)
   Decision Options: ACCEPT | ACCEPT_WITH_CONDITIONS | REJECT
   ✓ HG CAN decide layer ① based on this package alone


② SCOPE APPLICATION DOMAIN
   "Where do these semantics apply?"
   
   Scope: Which routes/authorizations subject to M18 closure verification
   Authority: Q7 (HG-L2-08 decision) — SEPARATE from Q5
   Status: UNRESOLVED / LOCKED (requires separate HG decision)
   Decision Options: DEFINE NOW | DEFER | HOLD
   ✗ Layer ① approval does NOT require layer ② decision
   ✓ Layer ① and ② are INDEPENDENT authority domains


③ RUNTIME EVIDENCE
   "Do the semantics actually hold at runtime?"
   
   Scope: Evidence collection, verification, proof generation
   Authority: Future investigation authorization (HG-L2-09 conditional)
   Status: NOT_AUTHORIZED (investigation phase only)
   Decision Options: AUTHORIZE | DEFER | HOLD
   ✗ Layer ③ requires both ① AND optional ②


④ IMPLEMENTATION AUTHORIZATION
   "Are we authorized to modify code/schema/runtime?"
   
   Scope: Production deployment, code changes, runtime modification
   Authority: Future implementation authorization decision
   Status: NOT_GRANTED / LOCKED
   Decision Options: AUTHORIZE | DEFER | HOLD
   ✗ Layer ④ requires ①, optional ②, and confirmation


**Critical Separation:**

```
① Semantic Approval (HG-L2-01～07) 
                    ≠ 
② Scope Definition (HG-L2-08, Q7)
                    ≠ 
③ Evidence Authorization (HG-L2-09)
                    ≠ 
④ Implementation Authorization (Future)
```

**HG Authority Boundary:**

This review package requests approval only for ①.

- ① YES: Semantics approved; proceed to implementation planning
- ① NO: Redesign required before implementation
- ② DECISION: Separate governance domain (Q7); proceed independently
- ③ DECISION: Conditional on ① approval; investigation-only scope
- ④ DECISION: Future; requires ① + ② confirmation

**Translation to HG Decisions:**

```
HG REVIEW: ① Semantic Definition
           ├── HG-L2-01 Comprehensive Approval
           ├── HG-L2-02～06 Individual Definitions
           ├── HG-L2-07 Assumptions/Risks
           └── Result: DESIGN APPROVED | CONDITIONS | REJECTED

SEPARATE: ② M18-Scope Definition
           └── HG-L2-08 (Q7)
               Result: DEFINE NOW | DEFER | HOLD
               (Independent of ① outcome)

DOWNSTREAM: ③ Evidence Program
             └── HG-L2-09
                 Result: AUTHORIZE | DEFER | HOLD
                 (Depends on ① approval, optional ②)

FUTURE: ④ Implementation Authorization
        └── (Requires ① + ② confirmation)
            Result: AUTHORIZED | DENIED
```

---

## PART 8: NEXT GOVERNANCE SEQUENCE

**After All HG Decisions Recorded:**

1. **Immediate:**
   - Formalize HG decisions in data/decisions/HG_DECISION_RECORD_20260913.md
   - Update system state (M18-Scope status, Implementation Authorization status)
   - Assess whether L3 Implementation Authorization can be requested

2. **Conditional (if HG-L2-01 = ACCEPT):**
   - Request Implementation Authorization for Layer 3 (separate decision)
   - Layer 3 implementation phase begins (schema, GL7 consume, CO binding)

3. **Conditional (if HG-L2-08 = DEFINE NOW):**
   - Proceed with EG-M18-02 formalization (M18-Scope to formal definition)
   - Categorize all 109 routes per M18-Scope decision

4. **Conditional (if HG-L2-09 = AUTHORIZE):**
   - Proceed with evidence gaps EG-M18-02, EG-M18-04, EG-M18-01
   - Investigation-only; no implementation

5. **Post-Implementation (conditional):**
   - Layer 4 Verification preconditions satisfaction (VP-01～04)
   - M18 Runtime Closure verification attempt
   - Semantic Closure achievement (if all evidence chains complete)

---

## PART 9: SUMMARY FOR HG

**What This Package Asks:**

1. **Approve** L2-01～L2-05 formal semantic designs (HG-L2-01 through HG-L2-06)
2. **Accept** design assumptions and their risks (HG-L2-07)
3. **Define** M18-Scope boundary (HG-L2-08) — CRITICAL BLOCKER
4. **Authorize** next evidence program (HG-L2-09)

**What This Package Does NOT Ask:**

- ❌ Implementation Authorization (remains NOT_GRANTED)
- ❌ Production Modification (remains 0)
- ❌ Code Changes (remains 0)
- ❌ Schema Changes (remains 0)
- ❌ Runtime Changes (remains 0)
- ❌ Semantic Closure Achievement (remains NOT_ACHIEVED)
- ❌ M18 Runtime Closure (remains LOCKED until all blockers resolved)

**Critical Principle:**

```
Design Review Approval ≠ Implementation Authorization
Evidence Authorization ≠ Implementation Authorization
M18-Scope Definition ≠ M18 Runtime Closure Achievement
```

All remains locked until explicitly authorized by subsequent decisions.

---

**Package Status:** REVIEW_READY / HG_DECISION_PENDING
**Submission Point:** Commit c5a07b5
**Prepared By:** Claude Haiku 4.5 (くろこ)
**Date:** 2026-09-13

---

*End of HG Review Package*
