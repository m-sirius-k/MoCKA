# Decision Candidate: Current Admissibility Position

**Status:** HUMAN GATE DECISION REQUIRED  
**Date:** 2026-09-20  
**Decision Authority:** きむら博士  
**Phase:** 1A (Governance structure choice)  

---

## Decision Frame

**Question:**

How should we treat **Current Admissibility** (temporal re-validation at Tn)?

Is composition validity at T0 still valid at Tn, when state/authority/evidence may have changed?

Three options:

---

## Option A: Independent 7th Boundary

### Definition
Create "Current Admissibility Boundary" as independent boundary, parallel to the 6 existing.

### Specification Required
- Evidence requirements (how to measure staleness?)
- Judgment target (is Tn composition still valid?)
- Composition constraint (what state changes invalidate prior composition?)

### Implementation Required
- Central staleness monitor (tracks age of all evidence/authority/state)
- Re-validation orchestrator (decides when to re-check)
- Fallback if re-validation fails

### Advantages
- Explicit boundary makes staleness visible
- Single point of control for re-validation policy

### Disadvantages
- Adds complexity (7th boundary must interact with existing 6)
- May be redundant (staleness could be per-boundary)
- Specification overhead

### Risk Level
**MEDIUM** - Additional boundary adds specification and implementation burden. If poorly specified, becomes blocker for all composition.

---

## Option B: Horizontal Re-Validation Condition (RECOMMENDED)

### Definition
Current Admissibility is not an independent boundary, but a **cross-cutting condition** that applies to all 6 boundaries.

Each boundary defines its own re-validation requirement:
- Evidence Boundary: How old can evidence be before re-verification?
- State Boundary: How long until state observation becomes stale?
- Temporal Boundary: How large can clock skew be before re-sync?
- Authority Boundary: How old can approval be before re-check?
- Scope Boundary: How often do access rules change?
- Readiness Boundary: How quickly can readiness regress?

### Implementation Required
- Per-boundary staleness checker (each boundary monitors its own age)
- Composition decision includes staleness check for affected boundaries
- Re-validation triggered when any boundary exceeds its tolerance

### Advantages
- Aligns with boundary-agnostic design
- Staleness policy can vary per boundary (Authority critical, State less critical)
- Simpler conceptually (condition, not new boundary)

### Disadvantages
- Requires per-boundary staleness specifications
- Risk of inconsistent staleness policies across boundaries

### Risk Level
**LOW** - Leverages existing boundary structure. Staleness becomes implementation detail, not new governance boundary.

### Recommendation Rationale
Aligns with Paper 5 principle: "Add new boundary only if independent." Current Admissibility affects all 6 equally → horizontal condition, not independent boundary.

---

## Option C: Deferred to Implementation

### Definition
Composition validity is judged at T0. Runtime re-validation is implementation detail, not specification.

JARVIS proceeds with composition-valid judgment from T0; if state changes invalidate composition, JARVIS detects failure at execution time.

### Implementation Required
- None (specification phase)
- Runtime monitoring to detect composition failure (implementation phase)
- Recovery policy for detected failures

### Advantages
- Simplest specification
- Defers complexity to implementation

### Disadvantages
- **HIGH RISK:** Composition becomes invalid but JARVIS continues → silent failure
- No proactive re-validation → reactive failure detection only
- Recovery is post-failure, not preventive

### Risk Level
**HIGH** - Repeats Paper 5 anti-pattern: "assume composition stays valid without verification."

---

## Comparison Matrix

| Criterion | Option A | Option B | Option C |
|---|---|---|---|
| **Specification Complexity** | High | Medium | Low |
| **Implementation Complexity** | High | Medium | Low |
| **Preventive Re-validation** | Yes | Yes | No |
| **Risk of Silent Failure** | Low | Low | **High** |
| **Alignment with Paper 5** | Medium | **High** | Low |
| **Timeline Impact** | +2 phases | +1 phase | None |

---

## Recommendation

**Adopt Option B: Horizontal Re-Validation Condition**

### Rationale

1. **Governance Choice:** This is a governance decision (structure), not a technical detail
2. **Paper 5 Alignment:** Current Admissibility affects all boundaries equally → cross-cutting condition, not independent boundary
3. **Risk Balance:** Preventive re-validation (vs. Option C) with reasonable complexity (vs. Option A)
4. **Future Extensibility:** If future boundaries are added, re-validation applies uniformly
5. **Specification Clarity:** Staleness policy becomes per-boundary decision (implementable)

### Implementation Path (if adopted)

1. **Phase 1B:** Each boundary defines its own staleness tolerance
2. **Phase 3:** Experiments observe actual evidence/authority/state lifecycles to inform tolerances
3. **Phase 4:** Human Gate decides concrete staleness values per boundary
4. **Phase 5:** Sandbox implementation of per-boundary staleness monitors

---

## Decision Alternatives

**If Human Gate disagrees with recommendation:**

1. **Prefer Option A?** Additional 7th boundary specification needed before implementation can proceed. Extend Phase 1B for boundary definition work.

2. **Prefer Option C?** Explicit acceptance that composition failures are detected post-failure, not prevented. Document risk acceptance in Decision Record.

---

## What This Decision Enables

If adopted (Option B):

- Phase 1A complete
- Phase 1B can proceed with 4 items (HAB Handoff, JARVIS Execution, Boundary Refinement, Interaction Rules)
- Phase 2 sandbox can implement without waiting for staleness specification
- Phase 3 experiments can validate staleness assumptions

---

## What This Decision Does NOT Decide

This decision is **governance structure only.** It does NOT decide:

- Specific staleness values (1 second? 1 hour? → Phase 4, after experiments)
- Which state changes invalidate composition (→ Phase 3 experiments)
- How to detect re-validation failure (→ Phase 2 implementation)
- Recovery actions if re-validation fails (→ Phase 4)

Those are decided after specification and experimental observation.

---

## Next Steps (after decision)

If **adopted (Option B):**
1. Record decision in Decision Ledger (DC_YYYYMMDD_NNN)
2. Proceed to Phase 1B: Specification of 4 remaining items
3. Begin sandbox implementation planning

If **rejected:**
1. Specify alternative governance structure
2. Document rationale
3. Adjust Phase timeline accordingly

---

## Summary

| Aspect | Detail |
|---|---|
| **Decision Type** | Governance structure (not technical) |
| **Decision Scope** | How to treat temporal re-validation |
| **Options** | 3 (7th boundary / horizontal condition / deferred) |
| **Recommendation** | Option B (horizontal condition) |
| **Timeline Impact** | Medium complexity, enables Phase 1B |
| **Risk Impact** | Prevents silent composition failures (vs. Option C) with reasonable overhead (vs. Option A) |
| **Next Decision Gate** | Human Gate approval required |

---

**AWAITING HUMAN GATE DECISION ON CURRENT ADMISSIBILITY POSITION.**
