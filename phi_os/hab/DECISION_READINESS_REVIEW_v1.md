# Decision Readiness Review — Phase 1A Filter

**Date:** 2026-09-20  
**Status:** REVIEW FILTER (before Human Gate submission)  
**Purpose:** Classify 9 items: which require immediate Human Gate decision vs. which need specification/experiment first  

---

## Core Principle

**Paper 5 avoided premature theory-based decisions.**

This review applies the same discipline: Do not ask Human Gate to decide what should be experimentally verified first.

---

## Decision Readiness Matrix

| Item | Decision Now | Specify More | Experiment First | Defer | Rationale |
|---|---|---|---|---|---|
| **1. Composition Decision Rule** | — | ✓ | ✓ | | AND-logic rejected; but replacement depends on boundary interactions (B category) |
| **2. Current Admissibility Position** | ✓ | | | | Choice between 3 options is governance decision (A category) |
| **3. HAB Handoff Contract** | | ✓ | | | Interface-level spec needed before Human Gate decides execution (B category) |
| **4. JARVIS Execution Contract** | | ✓ | | | Interface-level spec needed before Human Gate decides execution (B category) |
| **5. Boundary Definition Refinement** | | ✓ | | | 6 definitions are candidates; refine via interaction analysis before freezing (B category) |
| **6. Boundary Interaction Rules** | | ✓ | ✓ | | Interactions identified; resolution rules need specification + runtime observation (B/C category) |
| **7. Staleness Policy** | | | ✓ | | Concrete timing requires observing actual evidence/authority/state lifecycles (C category) |
| **8. Re-Validation Triggers** | | | ✓ | | State changes that invalidate composition need runtime observation (C category) |
| **9. Recovery Policy** | | | ✓ | | Failure scenarios must be observed before recovery paths can be designed (C category) |

---

## Classification Details

### A. Decision Now (Human Gate decides immediately)

#### Item 2: Current Admissibility Position

**Decision Frame:**
Current Admissibility (Temporal re-validation at Tn) should be treated as:
- **Option A:** Independent 7th Boundary (requires new definition, evidence requirements, interaction analysis)
- **Option B:** Cross-cutting re-validation condition applied to all 6 boundaries (each boundary defines staleness)
- **Option C:** Deferred to implementation phase (runtime monitoring, not specification)

**Why Decision Now:**
- This is a governance structure choice, not a technical detail
- Decision affects entire specification approach
- No experiment needed to choose governance model

**Human Gate Input Needed:**
- Organizational preference: centralized re-validation (7th boundary) vs. distributed (per-boundary staleness)?
- Timeline tolerance: How quickly must re-validation respond to state changes?

**Recommendation to Human Gate:**
Option B (cross-cutting condition) aligns with Paper 5 principle: Avoid additional boundaries unless independent. Current Admissibility affects all boundaries equally → horizontal condition, not independent boundary.

---

### B. Specify More First (before Human Gate decides)

#### Item 3: HAB Handoff Contract

**Current State:**
Template provided in Framework Draft:
```
HAB_HANDOFF_VALID if:
  - Evidence Boundary: HAB evidence is [readable / verified / ???]
  - State Boundary: HAB state is [consistent / ???]
  - Authority Boundary: HAB authority is [re-verified / delegated / ???]
  - Scope Boundary: JARVIS scope [includes / excludes / ???] HAB scope
  - Readiness Boundary: HAB readiness [re-checked / assumed / ???]
```

**Specification Needed Before Decision:**
1. For each boundary, specify what HAB must prove and what JARVIS must verify
2. Define contract severity: Is one missing boundary blocking, or can violations be waived?
3. Specify handoff evidence: What artifact proves "HAB Handoff Contract satisfied"?

**Why Specify First:**
- Contract details drive implementation of validators
- Without contract spec, Human Gate decision would be "trust HAB" vs. "verify HAB" (too abstract)
- With contract spec, Human Gate decides concrete conditions

**Specification Phase Output:**
```
HAB_HANDOFF_CONTRACT_v1:
  evidence_requirements: [ ... specific evidence for each boundary ... ]
  jarvis_verification: [ ... what JARVIS checks ... ]
  severity_model: [ blocking vs. waivable boundary violations ]
  handoff_proof: [ what artifact certifies handoff valid ]
```

---

#### Item 4: JARVIS Execution Contract

**Current State:**
Template provided:
```
JARVIS_EXECUTABLE if:
  - Composition-valid at Tn (re-validated)
  - FROZEN data still accessible
  - EXTENSION state still consistent
  - (+ other conditions)
```

**Specification Needed Before Decision:**
1. Define what "re-validated at Tn" means: Full re-run? Delta check? Selective boundaries?
2. Define accessibility/consistency criteria: How to verify FROZEN is still readable?
3. Define failure detection: What observable signals indicate execution should pause/rollback?

**Why Specify First:**
- Execution safety depends on concrete verification conditions
- Without specifics, Human Gate cannot judge risk of proceeding without re-validation

**Specification Phase Output:**
```
JARVIS_EXECUTION_CONTRACT_v1:
  revalidation_scope: [ which boundaries re-validate, which don't ]
  state_verification: [ how to check FROZEN/EXTENSION consistency ]
  failure_signals: [ observable events that trigger pause/rollback ]
  recovery_trigger: [ when to recover vs. when to escalate ]
```

---

#### Item 5: Boundary Definition Refinement

**Current State:**
6 boundaries defined in Framework Draft with:
- Definition
- Judgment target
- Evidence requirements
- Composition constraints

**Specification Needed Before Decision:**
1. Are definitions sufficient to distinguish boundaries from each other? (Or do some overlap?)
2. For each boundary, what is the minimum evidence to prove validity? (vs. composition validity)
3. How do boundary definitions interact with Current Admissibility (2-hour staleness? 1-minute? None?)?

**Why Specify First:**
- Definitions need internal consistency check before Human Gate ratifies them
- Overlapping boundaries create redundancy in specification

**Specification Phase Output:**
```
6_BOUNDARY_DEFINITIONS_v1:
  evidence_boundary: [ refined definition + evidence requirements ]
  state_semantic_boundary: [ refined definition + evidence requirements ]
  temporal_boundary: [ refined definition + evidence requirements ]
  authority_boundary: [ refined definition + evidence requirements ]
  scope_boundary: [ refined definition + evidence requirements ]
  readiness_boundary: [ refined definition + evidence requirements ]
  (+ proof of non-overlap / mutual distinctness)
```

---

#### Item 6: Boundary Interaction Rules

**Current State:**
6 key interactions identified:
- Evidence × Temporal
- State × Authority
- Authority × Scope
- Authority × Readiness
- Scope × Readiness
- Evidence × State

**Specification Needed Before Decision:**
1. For each interaction, what is the resolution rule?
   - Example: "If Evidence is old (staleness violation) but Authority is fresh, can composition proceed?" → No automatic answer.
2. Do some interactions supersede others?
   - Example: "Authority Boundary blocks composition, so whether State is consistent doesn't matter"? (Unlikely, but should be explicit)
3. How do interactions change with Current Admissibility position?

**Why Specify First:**
- Interaction rules are technical constraints, not governance decisions
- Human Gate cannot decide Composition Decision Rule without knowing interaction constraints

**Specification Phase Output:**
```
BOUNDARY_INTERACTION_RULES_v1:
  evidence_temporal_rule: [ If evidence old, what happens? ]
  state_authority_rule: [ If state inconsistent but authority valid, proceed? ]
  (... 6 rules, each with decision tree or matrix ...)
```

---

### C. Experiment First (before specification or decision)

#### Item 1: Composition Decision Rule

**Current State:**
- AND-logic explicitly rejected
- Replacement not specified
- 3 open questions: How to handle boundary interactions? How to weight boundaries? How to handle UNKNOWN?

**Experiment Needed Before Decision:**
1. **Boundary Interaction Tests:**
   - Run scenarios where one boundary is invalid, others valid
   - Observe: Does composition fail? System behavior?
2. **Weight Observation:**
   - Rank boundaries by criticality: Can Evidence be unverified while Authority is verified? (Probably not)
   - Design experiments to test boundary independence
3. **UNKNOWN Handling:**
   - Test: If boundary status is UNDETERMINED, can composition proceed? (Probably not)
   - Observe: When does UNDETERMINED become determinable without Human Gate?

**Why Experiment First:**
- Composition Decision Rule must be grounded in actual behavior, not theory
- AND-logic was rejected because it's too rigid; replacement needs to reflect boundary coupling

**Experiment Phase Outcomes:**
- Boundary criticality ranking (Evidence > Authority > ? > Scope)
- Interaction matrices (when does boundary A override boundary B?)
- UNKNOWN handling rules (UNDEFINED → STOP vs. UNDETERMINED → WAIT)

---

#### Item 7: Staleness Policy

**Current State:**
- Not defined
- Open questions: 1 second? 1 minute? No limit?

**Experiment Needed Before Decision:**
1. **Evidence Lifecycle Observation:**
   - When is HAB evidence produced?
   - When does JARVIS read it?
   - When is staleness detectable?
2. **Authority Lifecycle Observation:**
   - How often do authority changes occur?
   - How long is authority proof valid?
3. **State Lifecycle Observation:**
   - How often do state changes occur?
   - When does state change invalidate prior composition?

**Why Experiment First:**
- Staleness policy without lifecycle data is arbitrary
- Different boundaries may have different staleness tolerances (Evidence: 1 minute? Authority: 5 minutes? State: 10 seconds?)

**Experiment Phase Outcomes:**
- Evidence staleness tolerance (e.g., "timestamp > 60 seconds old → requires re-verification")
- Authority staleness tolerance (e.g., "approval timestamp > 300 seconds old → requires re-verification")
- State staleness tolerance (e.g., "state observation > 5 seconds old → may be stale")

---

#### Item 8: Re-Validation Triggers

**Current State:**
- Not defined
- Candidate triggers listed (new evidence, state transition, authority revocation, etc.)
- Open question: Which trigger invalidates which boundaries?

**Experiment Needed Before Decision:**
1. **State Change Observation:**
   - Log every state change (DRAFT → ACTIVE, etc.)
   - Observe: Does each state change invalidate prior composition?
2. **Authority Change Observation:**
   - Log every authority change (approval, revocation, escalation)
   - Observe: Which authority changes are blocking?
3. **Scope Change Observation:**
   - Log scope access rule changes
   - Observe: Do overlapping scope changes invalidate composition?

**Why Experiment First:**
- Re-validation is expensive (costs time, resources)
- Without observing actual state changes, triggers will be over- or under-sensitive
- Better to over-trigger in sandbox, then optimize, than to under-trigger in production

**Experiment Phase Outcomes:**
- Trigger matrix: "state change in category X triggers re-validation of boundary Y"
- False positive rate: How often does a trigger fire but composition is still valid?
- False negative rate: How often does composition become invalid without a trigger?

---

#### Item 9: Recovery Policy

**Current State:**
- Not defined
- Options listed (STOP, REVALIDATE, REQUALIFY, ESCALATE)
- Open questions: When does each apply? What are consequences?

**Experiment Needed Before Decision:**
1. **Failure Scenario Observation:**
   - Test: HAB composition-valid, JARVIS starts executing, then HAB evidence becomes invalid
   - Observe: What happens? JARVIS pauses? Continues? Fails?
2. **Authority Escalation Scenario:**
   - Test: During execution, authority changes (approval revoked)
   - Observe: Can execution continue? Must pause? Must rollback?
3. **Scope Conflict Scenario:**
   - Test: During execution, required data becomes inaccessible
   - Observe: Can execution continue with fallback? Must stop?

**Why Experiment First:**
- Recovery policy drives failure mode analysis
- Without observing actual failures, recovery policy is speculative
- Better to design recovery in sandbox after observing failure modes

**Experiment Phase Outcomes:**
- Failure mode taxonomy (Evidence lost, Authority revoked, State diverged, Scope inaccessible, etc.)
- Recovery paths per failure mode (pause + revalidate, rollback + escalate, continue + monitor, etc.)
- Escalation criteria (when to alert Human Gate vs. auto-recover)

---

## Summary Table

| Item | Category | Status | Next Step |
|---|---|---|---|
| 1. Composition Decision Rule | C | Deferred to experiment | Observe boundary interactions |
| 2. Current Admissibility Position | A | Decision Now | Human Gate chooses governance model |
| 3. HAB Handoff Contract | B | Specify More | Interface-level specification |
| 4. JARVIS Execution Contract | B | Specify More | Interface-level specification |
| 5. Boundary Definition Refinement | B | Specify More | Consistency check + overlap analysis |
| 6. Boundary Interaction Rules | B | Specify More | Decision tree per interaction |
| 7. Staleness Policy | C | Experiment First | Observe evidence/authority/state lifecycles |
| 8. Re-Validation Triggers | C | Experiment First | Log state/authority/scope changes |
| 9. Recovery Policy | C | Experiment First | Sandbox failure scenario tests |

---

## What Goes to Human Gate NOW

**Only Item 2: Current Admissibility Position**

Decision Candidate should focus on:
- Option A (7th Boundary) vs. Option B (Horizontal Condition) vs. Option C (Deferred)
- Rationale for each option
- Recommendation (Option B)
- Human Gate to decide governance structure

**Other items deferred** until:
- Items 3, 4, 5, 6: Specification completed (Phase 1B)
- Items 1, 7, 8, 9: Sandbox experiments completed (Phase 2)

---

## Phase 2 Structure (after Phase 1A decision)

### Phase 1A: Human Gate Decision (1 item)
- Decision: Current Admissibility position (7th boundary vs. horizontal vs. deferred)
- Output: Decision record in Decision Ledger

### Phase 1B: Specification Refinement (4 items)
- Refine 6 boundary definitions for internal consistency
- Specify HAB Handoff Contract (interface-level)
- Specify JARVIS Execution Contract (interface-level)
- Specify Boundary Interaction Rules (decision matrices)
- **Output:** Specification Freeze document

### Phase 2: Sandbox Implementation (1 item)
- Implement HAB/JARVIS validator framework (NO production changes)
- **Execution Scope:** tech_lab/ sandbox only

### Phase 3: Experimental Verification (3 items)
- Test 1: Boundary interactions (for Composition Decision Rule)
- Test 2: Evidence/Authority/State lifecycles (for Staleness Policy)
- Test 3: State/Authority/Scope changes (for Re-Validation Triggers)
- Test 4: Failure scenarios (for Recovery Policy)
- **Output:** Experimental results + observed patterns

### Phase 4: Decision on Remaining Items (4 items)
- Based on Phase 3 experiments, Human Gate decides:
  - Composition Decision Rule
  - Staleness Policy
  - Re-Validation Triggers
  - Recovery Policy
- **Output:** 4 additional Decision records

### Phase 5: Implementation Hardening
- Implement validators based on Phase 4 decisions
- Monitor for Composition Validity in sandbox
- **NO production activation yet**

---

## Critical Constraint

**Production HAB/JARVIS Activation is deferred** until:
- Phase 1A decision completed
- Phase 1B specification freeze completed
- Phase 3 experimental results analyzed
- Phase 4 remaining decisions made
- Phase 5 sandbox verification complete

Earliest possible production activation: After Phase 5 (NOT before).

---

## Why This Approach

1. **Avoids Paper 5 anti-pattern:** Specification now based on experiment, not theory
2. **Reduces decision load on Human Gate:** Only governance choice (Item 2) now; technical constraints (Items 1, 7, 8, 9) informed by data
3. **Grounds decisions in reality:** Boundary interactions, staleness, triggers observed before committing to rules
4. **Preserves revision capability:** If experiments reveal unsound assumptions, specifications can be revised before Human Gate decision

---

## Next: Simplified Decision Candidate

Revise Decision Candidate to focus on Item 2 only:

**Current Admissibility: 7th Boundary vs. Horizontal vs. Deferred?**

With recommendation: **Horizontal Condition** (cross-cutting re-validation applying to all 6 boundaries, not independent boundary).

---

*This review filter ensures Human Gate decides governance, not implementation details.*
