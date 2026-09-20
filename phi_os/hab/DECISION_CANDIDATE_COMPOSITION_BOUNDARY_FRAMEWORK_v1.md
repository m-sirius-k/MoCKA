# Decision Candidate: Composition Boundary Specification Framework

**Status:** DRAFT / HUMAN GATE REQUIRED  
**Date:** 2026-09-20  
**Source:** Composition Boundary Cross-Check (Paper 5) Phase 1  
**Author:** Claude (Kuroko - Executive Officer)  
**Decision Audience:** きむら博士 (Human Gate Final Authority)

---

## Decision Frame

**Question to Human Gate:**

Shall we adopt the Composition Boundary Specification Framework as defined in `COMPOSITION_BOUNDARY_SPECIFICATION_FRAMEWORK_DRAFT_v1.md`?

Specifically:

1. **Framework Acceptance:** Do you accept the 6-boundary model (Evidence, State/Semantic, Temporal, Authority, Scope, Readiness) as the basis for judging Composition Validity?

2. **Critical Decisions Deferred to You:**
   - What is the actual Composition Decision rule? (Not AND-logic, but what?)
   - Is Current Admissibility a 7th boundary, or a horizontal re-validation condition?
   - What specific conditions must HAB satisfy to hand off to JARVIS?
   - What specific conditions must JARVIS verify before executing?

3. **Evidence Gaps Understood:** Do you accept that runtime verification is missing for all 6 boundaries?

4. **Implementation Halted:** Shall HAB→JARVIS implementation remain halted until these decisions are made?

---

## Options and Alternatives

### Option A: ADOPT (Recommended)

**Decision:**
Accept the Composition Boundary Specification Framework as the structured basis for Composition Validity judgment.

**Implications:**
- Framework provides 6 independent boundaries, each with definition, evidence requirements, and interactions
- Moves from "assume composition is valid" to "explicitly specify composition conditions"
- Defers 9 specific decisions to Human Gate (listed in Specification Draft, Section H)
- Enables disciplined specification of HAB/JARVIS handoff and execution conditions

**Timeline:**
- Phase 1 (now): Framework adopted
- Phase 1A (next): Human Gate specifies 9 decisions
- Phase 2: Implementation of validators based on Phase 1A decisions

---

### Option B: REJECT - Add Additional Boundaries

**Decision:**
Reject framework as incomplete; add Idempotency, Rollback, and/or Consistency as independent boundaries.

**Implications:**
- Increases specification scope by 3+ boundaries
- Requires definition of each new boundary (definition, evidence requirements, interactions)
- Defers adoption until new boundaries are analyzed

**Rationale for rejection (if applicable):**
- [User to provide]

---

### Option C: REJECT - Simplify to AND-Logic

**Decision:**
Reject framework; use simple AND-logic: all 6 boundaries = TRUE → COMPOSITION VALID.

**Implications:**
- Ignores boundary interactions
- Treats UNKNOWN as FALSE (problematic)
- May miss composition failures due to boundary coupling
- **Risk:** Increases probability of undetected composition-invalid states

**Rationale for rejection (if applicable):**
- [User to provide]

---

### Option D: DEFER - Framework as Reference Only

**Decision:**
Use framework as reference documentation but do not formally adopt it.

**Implications:**
- Reduces urgency of specification
- Allows HAB/JARVIS implementation to proceed without explicit composition validation
- May result in composition validity assumed but never verified

**Risk:** Repeats Paper 5 finding: "Local Validity ≠ Composition Validity"

---

## Framework Strengths

1. **Clarity:** Distinguishes VALID (layer), COMPOSITION-VALID (handoff), EXECUTABLE (runtime)
2. **Discipline:** Requires explicit specification, not assumptions
3. **Interaction Awareness:** Maps 6 key boundary interactions
4. **Evidence-Based:** Identifies where evidence exists, where gaps are
5. **Deferral Clarity:** Makes explicit what requires Human Gate decision vs. what can be implementation detail

---

## Framework Weaknesses / Uncertainties

1. **Completeness:** No proof that 6 boundaries are exhaustive (assessment provided but not rigorous)
2. **Interaction Rules:** Boundary interactions identified but resolution rules NOT provided
3. **Current Admissibility:** Position (7th boundary vs. horizontal vs. deferred) not predetermined
4. **Decision Rule:** AND-logic explicitly rejected, but replacement not specified
5. **Recovery:** No specification of what happens if composition becomes invalid at Tn

---

## Decision Dependent Items

If ADOPTED, Human Gate must then decide:

| Item | Current Status | Decision Needed |
|---|---|---|
| Composition Decision Rule | Not specified | "What rule combines 6 boundaries?" (not AND) |
| Current Admissibility Position | 3 options proposed | "7th boundary, horizontal, or deferred?" |
| HAB Handoff Template | Template provided | "What conditions complete the template?" |
| JARVIS Execution Template | Template provided | "What conditions complete the template?" |
| Staleness Policy | Not defined | "How long before re-validation?" |
| Re-Validation Triggers | Candidate triggers listed | "Which trigger which boundaries?" |
| Boundary Weighting | All treated equal | "Are some boundaries more critical?" |
| UNKNOWN Handling | Both types preserved | "How to handle UNDEFINED vs UNDETERMINED?" |
| Recovery Policy | Not defined | "What if composition fails at Tn?" |

---

## Evidence-Based Rationale for ADOPT

1. **Paper 5 Validation:** Cross-Check confirmed Paper 5's finding: Local Validity ≠ Composition Validity
2. **Current State:** 0 composition tests exist; framework enables creation of test plan
3. **Risk Reduction:** Explicit specification reduces assumption-based implementation failures
4. **Timeline:** Framework accelerates handoff to Phase 1A (decision phase) without blocking implementation
5. **Reversibility:** Framework can be updated if Human Gate finds gaps; does not lock in decisions, only structure

---

## Recommendation

**Adopt Option A.**

Rationale:
- Framework is evidence-based (grounded in Paper 5 and Cross-Check)
- Does not pre-decide the 9 items that are Human Gate prerogative
- Enables disciplined specification phase before implementation
- Maintains distinction between specification gaps (EVIDENCE GAP) and policy decisions (HUMAN DECISION REQUIRED)

---

## If ADOPTED, Next Actions (Phase 1A)

1. Human Gate reviews 9 decision items in Section H of Specification Draft
2. Human Gate decides each item:
   - Boundary Definition Refinement
   - Interaction Resolution Rules
   - Composition Decision Semantics
   - Current Admissibility Position
   - HAB Handoff Specifics
   - JARVIS Execution Specifics
   - Staleness Policy
   - Re-Validation Triggers
3. Document Phase 1A decisions (record in Decision Ledger)
4. Proceed to Phase 2: Implementation of validators per Phase 1A decisions

---

## If REJECTED, Next Actions

If Human Gate rejects this framework:

1. Specify alternative composition decision model
2. Or, explicitly accept "composition validity assumed, not verified" (and document risk)
3. Or, propose additional boundaries and repeat framework analysis

---

## Approval Authority

**Human Gate Decision:** きむら博士  
**Approval Status:** AWAITING HUMAN GATE DECISION  
**No AI authority to approve composition specification; awaiting human judgment.**

---

## Appendix: Evidence Trail

This Decision Candidate is based on:

1. Paper 5: "Local Validity Is Not Closed Under Composition"
2. Composition Boundary Cross-Check (E20260920_67397446461cf): 6 boundaries analyzed, 0 composition tests found
3. Composition Boundary Specification Framework Draft (this session): Framework designed per Human Gate Phase 1 instructions

Links:
- `phi_os/hab/COMPOSITION_BOUNDARY_CROSS_CHECK_v1.md` (Analysis)
- `phi_os/hab/COMPOSITION_BOUNDARY_SPECIFICATION_FRAMEWORK_DRAFT_v1.md` (Framework)

---

**AWAITING HUMAN GATE DECISION.**
