# TIM-MoCKA Comparison Boundary Review
## v0.1 - Theory, Model, and Implementation Separation

Status: AUDIT / BOUNDARY CLARIFICATION
Date: 2026-08-28
Experiment: TIM-MoCKA Comparative Test
Context: claude/constitutional-runtime-investigation-jgqkv1

---

## Executive Summary

This review separates three distinct layers:
1. **Theory** - What Tim's original thinking may have been (not examined here)
2. **Model** - What this experiment implements (explicitly defined)
3. **Implementation** - How the model is coded (isolated test package)

This experiment does NOT reconstruct Tim's original implementation, does NOT
claim complete alignment with Tim's intent, and does NOT serve as evidence of
Tim's actual position on the problem.

---

## Part 1: Detailed Boundary Definitions

### Q1: What about Tim's work did this experiment model?

**Answer:**

This experiment models the **problem statement and test case structure only**,
as described in the commissioning instruction (§5-7).

**Modeled aspects:**

- The core principle: "past Allow verdict cannot by itself justify present Allow"
- The case matrix structure (10 cases, T01-T10)
- The critical test structure (two paths, full premise change)
- The decision state structure (past decision + premises)
- The premise dimensions (evidence, validity, authority, context)
- The reuse question: "can this past decision be reused now?"

**Source of this model:**

The commissioning instruction (Kimura-sensei's specification), not Tim's
original materials. See docs/audits/TIM_MOCKA_SOURCE_BOUNDARY_v0.1.md §0-1.

### Q2: What about Tim's work did this experiment NOT model?

**Answer:**

Extensive aspects are out of scope.

**Deliberately not modeled:**

- Tim's original implementation (not recovered; stated as NOT RECOVERED)
- Tim's architectural choices (unknown; not provided to session)
- Tim's gate design patterns (not accessible; would require Tim source)
- Tim's evidence validation logic (not replicated; digest-only proxy used)
- Tim's authority validation logic (not replicated; state/ID only)
- Tim's re-evaluation strategy (not tested; gate only flags necessity)
- Tim's context semantics (not implemented; mechanical ID/digest only)
- Tim's temporal handling (not explored; clock fixed to one moment)
- Tim's integration with Constitutional Runtime (not tested; isolated)
- Tim's actual position on the problem (not claimed here; materials not supplied)

**Why these are out of scope:**

1. Source material not provided to this session
2. Scope explicitly limited to "re-evaluation gate" portion
3. Full Constitutional Runtime integration is Phase 2 work
4. Commissioning instruction limits comparison to stated principles

### Q3: Does this experiment claim external theory is completely replicated?

**Answer:**

NO. Explicitly not.

**Claims NOT made:**

- "This is a faithful reconstruction of Tim's thinking"
- "This implementation proves Tim's concepts"
- "Tim would agree with these test results"
- "The original Constitutional Runtime followed this logic"
- "This experiment validates Tim's position"

**What IS claimed:**

- "This experiment implements a re-evaluation gate consistent with the stated principle"
- "The gate correctly enforces premise validation before reuse"
- "The test cases exercise the principle boundaries"
- "The 288-combination sweep covers the defined state space"

### Q4: Is this experiment comparing MoCKA body directly?

**Answer:**

NO. This is not a MoCKA core comparison.

**What it does NOT do:**

- Modify existing MoCKA Constitutional Runtime Trial code (verified; no changes)
- Test MoCKA core behavior directly (isolated test package)
- Compare MoCKA Trial semantics (baseline unchanged: 117 tests / 24 cases)
- Claim MoCKA improvements or validations

**What it IS:**

- An isolated experiment within MoCKA's experiment directory
- A proof-of-concept gate implementation
- A test of a principle (premise-based reuse validation)
- A boundary-setting exercise (defining what "reusable" means)

---

## Part 2: Model vs Theory Boundary

### Layer 1: Theoretical Principle

```
Principle (from instruction §5):
  "Past verdict (ALLOW) by itself must not be grounds for present ALLOW"

Principle (reformulated):
  "Reusable(past) ≠ Executable(past); conditions must be re-validated"
```

**Origin:** Commissioning instruction, understood as response to Tim's concept
**Status:** Established principle; guides test design
**Verification:** Implicit in case matrix structure

### Layer 2: Conceptual Model

```
Model:
  Past_State = DecisionRecord(decision, evidence_digest, validity_until, 
                              authority_id, context_id, context_digest)
  Present_State = PresentContext(evidence_digest, authority_state, 
                                 authority_id, context_id, context_digest)
  
  Re-evaluation Gate: Past_State + Present_State -> Eligibility + Findings
  
  Eligibility ∈ {ELIGIBLE, RE_EVALUATE, BLOCK, UNKNOWN}
  
  Execution Gate: (Eligibility == ELIGIBLE ∧ Decision == ALLOW) -> EXECUTE
                  Otherwise -> STOP
  
  Principle verification: 
    EXECUTE must not occur unless all premises are unchanged
```

**Origin:** Commissioning instruction §2-3, formalized here
**Status:** Tested and verified over 288 combinations
**Scope:** Re-evaluation gate only (not full CR)

### Layer 3: Implementation

```
Implementation (Python):
  experiments/tim_mocka_comparative/temporal.py (351 lines)
  - ReEvaluationGate class with assess(record, present) method
  - Finding enum with 9 judgment categories
  - Reduction rules: HARD_BLOCK -> BLOCK, REQUIRE_REEVALUATION -> RE_EVALUATE
  - gate_execution() with type validation
  
  experiments/tim_mocka_comparative/cases.py (290 lines)
  - Case matrix T01-T10 as class instances
  - T50-TIM-REUSE as critical test data
  - Axis declarations (NOT_TESTED vs PASS/FAIL/UNKNOWN)
  
  experiments/tim_mocka_comparative/run_comparative.py (222 lines)
  - Matrix runner, audit trail, JSON output
  - score_axes() for 5-axis evaluation
```

**Origin:** Authorship unknown to theory or Tim's position
**Status:** Working, tested, verified
**Scope:** Isolated to experiments/ directory

### Theory-Model Relationship

| Layer | Source | Status | Claims |
| ----- | ------ | ------ | ------ |
| Principle | Instruction §5 | ESTABLISHED | "Reusable ≠ Executable" |
| Model | Instruction §2-7 | FORMALIZED | Premise structure + gate logic |
| Implementation | This session | VERIFIED | 288 sweep + 42 invariants pass |

**No reverse causality:** Implementation does not inform principle.
Implementation verifies model consistency with principle.

---

## Part 3: Permitted vs Prohibited Claims

### 3.1 PERMITTED CLAIMS

#### Permitted: About the Gate Itself

- [x] "This gate enforces premise validation before verdict reuse"
- [x] "The gate requires all five premise categories (evidence, validity, 
       authority, context_id, context_digest) to be unchanged for reuse eligibility"
- [x] "Only the combination of past ALLOW + unchanged premises reaches execution"
- [x] "The gate implements the stated principle consistently"
- [x] "Type safety is enforced in the execution gate"

#### Permitted: About the Test Results

- [x] "All 10 test cases passed expectation"
- [x] "The 288-combination sweep verified the single-execution-path property"
- [x] "T50 demonstrates Path A (direct reuse) diverges from Path B (re-evaluation)"
- [x] "Any single premise change is sufficient to block execution"
- [x] "42 invariant tests passed"

#### Permitted: About Model Completeness

- [x] "This experiment is exhaustive over the 7 defined dimensions"
- [x] "Eligibility and Execution are separable concepts (T06 proves it)"
- [x] "UNKNOWN verdicts are preserved and never auto-converted to ALLOW"

#### Permitted: About Boundaries

- [x] "This experiment does not model authority legitimacy; state/ID only"
- [x] "Evidence validation is out of scope; digests only are compared"
- [x] "Re-evaluation outcome prediction is out of scope"
- [x] "Constitutional Runtime integration is out of scope (Phase 2)"
- [x] "No production systems were tested"

### 3.2 PROHIBITED CLAIMS

#### Prohibited: About Tim's Intent

- [ ] "This proves what Tim originally intended"
- [ ] "Tim would approve this design"
- [ ] "This is how Tim's Constitutional Runtime worked"
- [ ] "Tim's position on past decisions is now validated"

**Why:** No Tim source material was provided. Commissioning instruction does not
assert Tim agreement. These are conjectures about external parties.

#### Prohibited: About Original CR

- [ ] "The original Constitutional Runtime contained this gate"
- [ ] "The original CR Trial tested these concepts"
- [ ] "The 50-Test was designed with this gate in mind"

**Why:** Original CR stated as "NOT RECOVERED". Assumption about it is
speculation (documented in SOURCE_BOUNDARY audit).

#### Prohibited: About Empirical Validation

- [ ] "Real-world evidence validation is proven"
- [ ] "Authority trust has been established"
- [ ] "Context boundaries are semantically correct"
- [ ] "This gate is safe for production use"

**Why:** Gate operates on digests and mechanical ID comparison. No real-world
validation is performed.

#### Prohibited: About Complete Implementation

- [ ] "Constitutional Runtime has been implemented"
- [ ] "The full re-evaluation pipeline is in place"
- [ ] "Decision outcomes will be correct after re-evaluation"

**Why:** Gate only determines that re-evaluation is needed. Actual re-evaluation
is outside this scope (per instruction §8.3).

#### Prohibited: About Generalization

- [ ] "All decision-reuse systems must follow this pattern"
- [ ] "This is the only correct approach to premise validation"
- [ ] "Other gate designs are incorrect"

**Why:** This experiment tests one gate design. It does not evaluate
alternatives or claim universality.

---

## Part 4: MoCKA Boundary

### 4.1 MoCKA Core Not Modified

**Verification:**

```
git diff HEAD~1 HEAD --stat (on commit 5abc109):
  experiments/tim_mocka_comparative/...  [new files only]
  docs/audits/TIM_MOCKA_...               [new files only]
  docs/tests/TIM_MOCKA_...                [new files only]
  - Constitutional Runtime Trial: 0 changes
  - MoCKA core behavior: 0 changes
```

**Constitutional Runtime Trial baseline:** 117 tests / 24 cases UNCHANGED

### 4.2 Isolation Verification

```
Import scope: only experiments.tim_mocka_comparative and its test suite
Production imports: 0
Trial imports: 0 (no cross-dependency)
```

**No re-export of types:** Experiment types (Finding enum, etc.) not exposed
to MoCKA core or Trial.

### 4.3 Integration Path (Future)

**Phase 2 will:**
- Evaluate whether gate should be incorporated into CR
- Design integration points (Human Gate decision pending)
- Implement production versions if approved
- Merge to main with explicit lifecycle gate

**This experiment does NOT:**
- Integrate to main (explicit instruction)
- Freeze changes (not requested)
- Seal results (not requested)
- Commit to future design (Layer 3 marked "未決定")

---

## Part 5: Interpretation Boundaries

### 5.1 What We Can Infer

From the gate behavior + test results, we can infer:

1. **Structural principle:** Storing premises alongside verdicts enables
   premise-based re-evaluation eligibility.

2. **Necessity:** Without premise storage, reuse eligibility cannot be determined
   mechanically.

3. **Sufficiency of 5 dimensions:** These five premise categories (evidence,
   validity, authority, context_id, context_digest) are sufficient to determine
   reuse eligibility under this gate design.

4. **Type safety matters:** String enum confusion (section 5.3 of results) can
   cause execution gate failures. Type validation is protective.

### 5.2 What We CANNOT Infer

We cannot infer:

1. **Real-world correctness:** Digests are not real evidence validation. The
   gate does not guarantee actual evidence integrity.

2. **Authority legitimacy:** authority_state is observable, but not verified.
   A VALID authority could still be unauthorized.

3. **Context semantics:** Context mismatch is mechanical (ID comparison). We
   cannot infer whether crossing boundaries is semantically meaningful.

4. **Re-evaluation correctness:** The gate requests RE_EVALUATE but never
   demonstrates that re-evaluation reaches correct outcomes.

5. **Tim agreement:** We cannot claim this matches Tim's thinking.

6. **Original CR compatibility:** We cannot claim this replicates Original CR.

### 5.3 What IS Observable

Observable facts (from 288-sweep + test results):

- **Fact 1:** Only one execution path (ALLOW + ELIGIBLE + type-safe) reaches EXECUTE
- **Fact 2:** Any single premise change blocks execution
- **Fact 3:** Reusable (ELIGIBLE) ≠ Executable (EXECUTE gate required)
- **Fact 4:** UNKNOWN verdicts are preserved (never auto-allowed)
- **Fact 5:** Type safety prevents string-enum bypass

These facts do not require external validation. They are internal to this
experiment.

---

## Part 6: Comparison Boundary Summary

### What This Experiment IS

```
[ Isolated Proof-of-Concept ]
    |
    v
[ Principle-Based Gate Design ]
    |
    v
[ Test Matrix (T01-T10 + T50) ]
    |
    v
[ Exhaustive State Space Sweep (288 combinations) ]
    |
    v
[ Verified Behavior (42 invariants pass, regression baseline intact) ]
```

### What This Experiment Is NOT

```
[ Original Tim Implementation ]              [NOT THIS]
[ Complete Constitutional Runtime ]          [NOT THIS]
[ Empirical Real-World Evidence Validation ] [NOT THIS]
[ Authority Trust Establishment ]            [NOT THIS]
[ Production Gate Ready for Deployment ]     [NOT THIS]
[ Proof of Tim's Intent ]                    [NOT THIS]
```

---

## Part 7: Final Boundary Statement

### The Official Statement

> **This experiment evaluates explicitly modeled decision paths under declared
> premises. It does not constitute a complete implementation or empirical
> validation of either external theory or the full MoCKA system.**

### Elaboration

**Explicitly modeled:**
- A re-evaluation gate that checks premise consistency
- A decision data structure storing past verdicts + premises
- A test matrix covering premise variations
- An execution gate separating eligibility from permission

**Not modeled:**
- Tim's original thinking (material not supplied)
- Complete Constitutional Runtime (Phase 2 work)
- Real evidence validation (digest comparison proxy)
- Authority trust (state/ID observation only)
- Context semantics (mechanical boundary only)
- Production safety or correctness

**Declared premises:**
- Fixed clock (2026-08-28T12:00:00Z)
- Reproducible test data
- Isolated implementation (standard library only)
- No trial modification (verified)
- Type-safe execution gate

**Scope:**
- Re-evaluation gate design only
- Test case matrix structure only
- Principle verification only
- Boundary definition only

**Not in scope:**
- Formal proof of correctness (mathematical rigor absent)
- Empirical validation (no real systems tested)
- Production readiness (isolated experiment only)
- Tim alignment claim (material not available)
- Original CR reconstruction (source not recovered)

---

## Part 8: Approval and Escalation

### Current Status

- [x] Model explicitly defined
- [x] Theory-implementation boundary clarified
- [x] Permitted vs prohibited claims enumerated
- [x] MoCKA core isolation verified
- [x] Interpretation limits documented
- [x] Comparison boundary stated

### Decision Required

This experiment reaches the boundary of what can be verified in isolation.

**Next steps require:**

1. **Human Gate Review** (not yet performed)
   - Should this gate design be considered for adoption?
   - Does the principle match Constitutional Runtime intent?
   - Should Phase 2 (integration) be approved?

2. **Tim Consultation** (if possible)
   - Does this design align with original intent?
   - Are the premise dimensions sufficient?
   - Should other dimensions be added?

3. **Formal Decision** (to follow)
   - Adopt / Defer / Reject for Constitutional Runtime integration
   - Update Layer 3 status in results (currently "未決定")
   - Determine Phase 2 scope (if approved)

### This Audit's Scope

This audit establishes **where the experiment ends** and **where external
judgment begins**. The boundaries are now explicit.

The experiment itself is complete and verified. The decision to integrate or
adopt is outside this experiment's scope and requires Human Gate approval.

---

## 9. Verification Checklist

- [x] Theory layer identified (principle from instruction)
- [x] Model layer defined (re-evaluation gate structure)
- [x] Implementation layer isolated (experiments/ only)
- [x] Tim modeling scope clarified (problem structure, not intent)
- [x] Tim non-modeling scope enumerated (everything about his thinking)
- [x] External theory replication claim denied
- [x] MoCKA core comparison boundary confirmed
- [x] Permitted claims enumerated
- [x] Prohibited claims enumerated
- [x] Observable facts distinguished from inference
- [x] Interpretation limits documented
- [x] Comparison boundary statement formulated
- [x] Decision escalation path identified

