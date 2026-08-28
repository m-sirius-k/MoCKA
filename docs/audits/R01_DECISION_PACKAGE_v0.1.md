# R01 Decision Package
## TIM-MoCKA Comparative Test - Human Gate Review

Status: DECISION REQUIRED
Date: 2026-08-28
Commit: c4756d8
Branch: claude/constitutional-runtime-investigation-jgqkv1
Session: claude/constitutional-runtime-investigation-jgqkv1

---

## A. Evidence Summary

### Implementation Status

| Artifact | Status | Reference |
| -------- | ------ | --------- |
| Re-evaluation gate | COMPLETE | experiments/tim_mocka_comparative/temporal.py |
| Case matrix T01-T10 | COMPLETE | experiments/tim_mocka_comparative/cases.py |
| T50-TIM-REUSE test | COMPLETE | experiments/tim_mocka_comparative/cases.py |
| Test suite | COMPLETE | experiments/tim_mocka_comparative/tests/ |
| Specification document | COMPLETE | docs/tests/TIM_MOCKA_COMPARATIVE_TEST_v0.1.md |
| Results document | COMPLETE | docs/tests/TIM_MOCKA_COMPARATIVE_TEST_RESULTS_v0.1.md |
| Source boundary audit | COMPLETE | docs/audits/TIM_MOCKA_SOURCE_BOUNDARY_v0.1.md |
| T50 causal audit | COMPLETE | docs/audits/T50_MINIMAL_CAUSAL_WITNESS_v0.1.md |
| Sweep boundary audit | COMPLETE | docs/audits/TIM_MOCKA_SWEEP_BOUNDARY_v0.1.md |
| Comparison boundary audit | COMPLETE | docs/audits/TIM_MOCKA_COMPARISON_BOUNDARY_REVIEW_v0.1.md |

### Test Results (Final Verification)

```
42 Comparative Test Invariants    : PASS (42/42)
10 Matrix Cases T01-T10           : PASS (10/10)
T50-TIM-REUSE Critical Test       : PASS (divergence confirmed)
False-Positive Guard              : PASS (10/10 cases match expected findings)
288-Combination Exhaustive Sweep  : PASS (all invariants verified)

Constitutional Runtime Trial      : PASS (117/117 tests unchanged)
Trial Regression Baseline         : INTACT (24 cases unchanged)

UTF-8 Encoding Verification       : PASS
CP932 Contamination Check         : CLEAN
```

### Repository State

- **Branch:** claude/constitutional-runtime-investigation-jgqkv1
- **Latest commit:** c4756d8 (R01 Follow-up: Add comprehensive boundary audits)
- **Main branch:** NOT MODIFIED (verified via git diff)
- **Constitutional Runtime core:** NOT MODIFIED (0 changes to existing code)
- **Trial package:** NOT MODIFIED (117 tests still passing)
- **Isolation:** Complete (experiments/tim_mocka_comparative/ is self-contained)

---

## B. T50-TIM-REUSE Finding

### What T50 Demonstrates

Path A (direct reuse) and Path B (re-evaluation) were compared with identical inputs where all observable premises had changed:

| Premise | Change | Impact |
| ------- | ------ | ------ |
| Evidence digest | Changed | Detected by Path B as EVIDENCE_CHANGED |
| Validity deadline | Expired | Detected by Path B as TEMPORAL_EXPIRED |
| Authority ID | Changed | Detected by Path B as AUTHORITY_CHANGED |
| Context ID | Changed | Detected by Path B as CONTEXT_MISMATCH |
| Context digest | Changed | Would be detected if same context |

**Observed outcome:**
- Path A: Returns ALLOW (stores verdict; present context not inspected)
- Path B: Returns STOP (re-evaluation needed; 4 premise changes detected)
- Result: Divergence exists and is observable

### Reduction Test Results

Single-premise-change reduction tests confirm:

```
Any one premise change alone is sufficient to block execution.
Baseline (no changes): both paths converge to allow-eligible outcome
Single evidence change: Path B returns STOP
Single validity change: Path B returns STOP
Single authority change: Path B returns STOP
Single context ID change: Path B returns STOP
Single context digest change: Path B returns STOP
```

**Conclusion:** The minimal causal witness for divergence is the existence of any
single changed premise. T50 exercises the maximal divergence case (all premises
changed simultaneously) for clarity.

### Explicit Boundary: What T50 Does NOT Prove

**This experiment does NOT demonstrate:**
- Tim's original implementation (source code not recovered)
- Tim's intended design for Constitutional Runtime (materials not supplied)
- Tim's agreement with this gate structure
- The correctness of re-evaluation outcomes
- Real-world applicability or safety
- Superiority to alternative designs
- Necessity for Constitutional Runtime adoption

**Source reference:** See docs/audits/TIM_MOCKA_SOURCE_BOUNDARY_v0.1.md §0-1
and docs/audits/TIM_MOCKA_COMPARISON_BOUNDARY_REVIEW_v0.1.md Part 5-7

---

## C. 288-Combination Sweep Boundary

### Exhaustiveness Definition

The 288-combination exhaustive sweep covers all combinations of 7 explicitly
defined dimensions:

```
past_decision         : 3 values (ALLOW, BLOCK, UNKNOWN)
evidence_change       : 2 values (ORIGINAL, CHANGED)
validity_status       : 2 values (FUTURE, PAST)
authority_state       : 3 values (VALID, LOST, REVOKED)
authority_change      : 2 values (ORIGINAL, OTHER)
context_id_change     : 2 values (SAME, DIFFERENT)
context_digest_change : 2 values (ORIGINAL, CHANGED)

Exhaustiveness formula: 3 * 2 * 2 * 3 * 2 * 2 * 2 = 288
```

### What Exhaustiveness Covers

The sweep is **exhaustive within the explicitly defined finite state space** of
the ReEvaluationGate's observable inputs.

- [x] Every combination of the 7 dimensions tested
- [x] All reduction rules verified across 288 cases
- [x] Single execution path identified and confirmed
- [x] Type safety validation checked
- [x] Boundary conditions verified (T06, T07, T08, T09, T10)

### What Exhaustiveness Does NOT Cover

The sweep is **NOT exhaustive** of:
- Evidence content or quality (digest comparison only)
- Authority legitimacy or trustworthiness (state/ID only)
- Re-evaluation correctness (gate only flags necessity)
- Real-world temporal dynamics (clock fixed)
- Context semantics or relationships (mechanical ID only)
- Implementation variants (single gate design tested)
- Complete Constitutional Runtime (gate component only)

**Source reference:** See docs/audits/TIM_MOCKA_SWEEP_BOUNDARY_v0.1.md §3-4

---

## D. Claim Boundary

### Permitted Claims (Can be Made)

The following claims are supported by evidence and do not exceed experimental scope:

- [x] "This gate enforces premise validation before reuse eligibility"
- [x] "All 288 state space combinations have been tested"
- [x] "Only one execution path (past ALLOW + unchanged premises) reaches EXECUTE"
- [x] "Any single premise change prevents execution"
- [x] "Type safety blocks string-enum bypass attacks"
- [x] "The test cases pass all declared expectations"
- [x] "The comparative test passes 42 invariant tests"
- [x] "UNKNOWN verdicts are preserved without auto-conversion"
- [x] "Eligibility and Execution are separable concepts"
- [x] "The gate is exhaustive within its defined state space"

### Prohibited Claims (Cannot be Made)

The following claims exceed experimental scope and must not be made:

- [ ] "This proves Tim's original intent or position"
- [ ] "This implementation matches the original Constitutional Runtime"
- [ ] "This is the only correct approach to decision reuse"
- [ ] "Real-world evidence quality has been validated"
- [ ] "Authority trust has been established"
- [ ] "This is safe for production deployment"
- [ ] "The original CR Trial tested these concepts"
- [ ] "Tim would approve this design"
- [ ] "Other decision reuse systems must follow this pattern"
- [ ] "Complete Constitutional Runtime has been implemented"

**Source reference:** See docs/audits/TIM_MOCKA_COMPARISON_BOUNDARY_REVIEW_v0.1.md §3

---

## E. Open Questions for Human Gate

This experiment reaches the boundary between verifiable implementation and
architectural decision-making. The following questions require Human Gate
judgment and cannot be answered by the experimental evidence alone.

### Question 1: Gate Design Adoption

**Should this re-evaluation gate design be considered as a candidate design for
MoCKA Constitutional Runtime?**

This question concerns whether the gate's approach to premise-based reuse
eligibility aligns with MoCKA's architectural philosophy and goals.

**Context:**
- Gate is fully implemented and tested
- Isolation from existing code is confirmed
- No breaking changes to core systems
- Decision does not block future alternatives

**Decision required:** YES / NO / DEFER

---

### Question 2: Tim Consultation

**Should Tim (or primary sources of original intent) be consulted to confirm
whether this design aligns with the original Constitutional Runtime concept?**

This question concerns external validation against historical sources that were
not available to this experiment.

**Context:**
- No Tim materials were supplied to this session
- Source boundary is explicitly documented
- Tim alignment cannot be claimed without consultation
- Implementation is complete independent of Tim input

**Decision required:** YES / NO / NOT APPLICABLE (contact unavailable)

---

### Question 3: Phase 2 Integration Timeline

**Should Constitutional Runtime Phase 2 integration work be initiated for this
gate, pending positive responses to Q1 and Q2?**

This question concerns the project timeline and scope for incorporating the gate
into the full Constitutional Runtime pipeline (Evidence -> Validity -> Authority
-> Context -> Re-evaluation -> Decision -> Execution Gate).

**Context:**
- Phase 2 integration is currently out-of-scope (explicitly stated in
  instruction §13)
- Gate implementation is limited to re-evaluation portion only
- Full CR integration requires additional design work
- Current experiment provides design foundation if approved

**Decision required:** YES / NO / DEFER

---

### Question 4: Layer 3 Status Change

**Should Layer 3 (Designed - Constitutional Runtime implementation proposal) be
updated from "未決定" (undecided) status to a formal adoption or defer status?**

This question concerns whether the experimental design proposal becomes a formal
CR design decision or remains exploratory.

**Context:**
- Layer 3 is currently marked "未決定" per instruction §10 final note
- Audit confirms design is bounded and explicit
- Formal adoption requires separate Human Gate decision
- Current status allows future refinement if decision is deferred

**Decision required:** ADOPT / DEFER / REJECT

---

## F. R01 Final Status

### Implementation Status
```
IMPLEMENTATION: COMPLETE
- Re-evaluation gate: Fully implemented and tested
- Test suite: 42 invariant tests, all passing
- Exhaustive verification: 288 combinations verified
- Documentation: Complete with boundaries defined
- Isolation: Confirmed (no core modifications)
```

### Audit Status
```
AUDIT: COMPLETE
- T50 causal independence: Documented and verified
- 288-sweep boundaries: Explicitly defined
- Comparison boundaries: Theory/model/implementation separated
- Encoding verification: UTF-8 verified, CP932-clean
- Regression baseline: CR Trial 117/117 unchanged
```

### Claim Status
```
COMPARATIVE CLAIM: BOUNDED
- Permitted claims enumerated (10 items)
- Prohibited claims enumerated (10 items)
- Scope limits explicitly documented
- External validation requirements identified
```

### Integration Status
```
INTEGRATION: NOT AUTHORIZED
- No merge to main branch
- No production rollout
- No Constitutional Runtime integration
- No feature freeze
- Awaiting Human Gate decision
```

### Lifecycle Status
```
FREEZE: NOT REQUESTED
SEAL: NOT REQUESTED
HUMAN GATE: REQUIRED

Current state: Experiment remains mutable pending decision
Next step: Human Gate review of Decision Package
Timeline: Awaiting decision response
```

---

## G. Decision Package Scope

### What is Included

- [x] Complete test evidence (42 + 117 tests passing)
- [x] T50 findings with explicit boundaries
- [x] 288-sweep exhaustiveness definition
- [x] Permitted vs prohibited claims
- [x] Four open questions for decision-making
- [x] Final R01 status summary
- [x] Repository state verification (read-only)

### What is NOT Included

- [ ] New implementation changes (prohibited)
- [ ] Additional testing beyond verification (prohibited)
- [ ] Layer 3 status changes (prohibited)
- [ ] Design decisions (deferred to Human Gate)
- [ ] Tim intent conjecture (prohibited)
- [ ] Main branch merge recommendations (prohibited)
- [ ] Production deployment guidance (out of scope)

### What Remains Unchanged

```
experiments/tim_mocka_comparative/
  - temporal.py
  - cases.py
  - run_comparative.py
  - tests/
    - test_tim_mocka_comparative.py
[NO CHANGES]

docs/tests/
  - TIM_MOCKA_COMPARATIVE_TEST_v0.1.md
  - TIM_MOCKA_COMPARATIVE_TEST_RESULTS_v0.1.md
[NO CHANGES]

docs/audits/
  - TIM_MOCKA_SOURCE_BOUNDARY_v0.1.md (existing)
  - T50_MINIMAL_CAUSAL_WITNESS_v0.1.md (R01)
  - TIM_MOCKA_SWEEP_BOUNDARY_v0.1.md (R01)
  - TIM_MOCKA_COMPARISON_BOUNDARY_REVIEW_v0.1.md (R01)
  - R01_DECISION_PACKAGE_v0.1.md (this document)

Constitutional Runtime Trial
  - tests/ (117 tests)
  - cases/ (24 cases)
[NO CHANGES - baseline intact]

main branch
[NOT MODIFIED]
```

---

## H. Next Actions

### For Human Gate

1. **Review this Decision Package** in its entirety
2. **Make decisions on the four open questions** (§E)
3. **Document the decision** in decision_ledger.json (per TODO_361)
4. **Communicate decision** to the working session

### For Working Session

**Upon Human Gate decision:**

If Q1 = YES (adopt gate design):
- Proceed to architectural integration planning
- Coordinate with Phase 2 timeline (Q3)
- Update design documentation

If Q1 = NO (reject gate design):
- Archive experiment (transition to read-only)
- Document decision rationale
- Proceed with alternative designs if needed

If Q1 = DEFER (suspend decision):
- Experiment remains mutable
- No architectural commitment
- May revisit in future phase

---

## I. Verification Checklist

All items below are READ-ONLY (no changes made during package preparation):

- [x] Commit c4756d8 verified in git log
- [x] Branch claude/constitutional-runtime-investigation-jgqkv1 verified
- [x] 42 tests passing (pytest experiments/tim_mocka_comparative/tests/)
- [x] 117 baseline tests passing (pytest experiments/constitutional_runtime_trial/tests/)
- [x] No modifications to existing code (git diff main..HEAD)
- [x] Audit documents complete and UTF-8 verified
- [x] CP932 contamination check: CLEAN
- [x] All audit findings documented
- [x] Permitted/prohibited claims separated
- [x] Scope boundaries explicit
- [x] Decision questions clearly stated

---

## J. Summary Statement

The TIM-MoCKA Comparative Test has been completed with full implementation,
comprehensive auditing, and explicit boundary documentation.

**What has been verified:**
- A re-evaluation gate that separates reusability from executability
- Premise-based approach to decision reuse eligibility
- Type safety and boundary condition handling
- Exhaustive testing within defined state space
- Isolation from existing Constitutional Runtime core

**What has been left to Human Gate judgment:**
- Whether this design should be adopted for Constitutional Runtime
- Whether external validation (Tim consultation) is necessary
- Whether Phase 2 integration should proceed
- Whether design status should be formalized

**The experiment is complete. The decision is required.**

---

## Document Metadata

- **Status:** AWAITING HUMAN GATE DECISION
- **Commit:** c4756d8
- **Branch:** claude/constitutional-runtime-investigation-jgqkv1
- **Date:** 2026-08-28
- **Session:** claude/constitutional-runtime-investigation-jgqkv1
- **Instruction:** R01 Decision Package Preparation
- **Scope:** Decision Package only (no implementation changes)
- **Next:** Human Gate review and decision response

