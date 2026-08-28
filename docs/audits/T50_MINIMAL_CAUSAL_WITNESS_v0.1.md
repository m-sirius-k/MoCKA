# T50-TIM-REUSE Minimal Causal Witness
## v0.1 - Divergence Analysis

Status: AUDIT / ANALYSIS
Date: 2026-08-28
Experiment: TIM-MoCKA Comparative Test
Context: claude/constitutional-runtime-investigation-jgqkv1

---

## 0. Executive Summary

T50-TIM-REUSE compares two execution paths for the same past decision:
- Path A (direct reuse): Returns stored verdict without examining present
- Path B (re-evaluated): Examines all premises and decides re-evaluation necessity

**Divergence:** Path A outputs ALLOW; Path B outputs STOP.

**Minimal Causal Witness:** Any single condition change is sufficient to trigger
divergence. T50 is the maximal case (all 5 observable conditions changed).

---

## 1. Input Difference Table

### Past Decision (Recorded at 2026-08-01T00:00:00Z)

| Field | Value |
| ---- | ----- |
| decision_id | D-T50 |
| decision | ALLOW |
| decided_at | 2026-08-01T00:00:00Z |
| validity_until | 2026-08-10T00:00:00Z |
| evidence_digest | 176fd7845dc02b67 |
| authority_id | AUTH-OPERATOR-01 |
| context_id | CTX-1 |
| context_digest | 3b4021f473d3a90b |

### Present Context (Evaluated at 2026-08-28T12:00:00Z)

| Field | Value |
| ---- | ----- |
| now | 2026-08-28T12:00:00Z |
| evidence_digest | 7ea0f7cf8a13aed6 |
| authority_id | AUTH-OPERATOR-02 |
| authority_state | VALID |
| context_id | CTX-2 |
| context_digest | ce41ea58bdddde70 |

### Premise Changes (Record to Present)

| Premise | Past Value | Present Value | Changed? |
| ------ | ---------- | ------------- | -------- |
| Evidence | 176fd7845dc02b67 | 7ea0f7cf8a13aed6 | YES |
| Validity | 2026-08-10T00:00:00Z | 2026-08-28T12:00:00Z | YES (expired) |
| Authority ID | AUTH-OPERATOR-01 | AUTH-OPERATOR-02 | YES |
| Context ID | CTX-1 | CTX-2 | YES |
| Context Digest | 3b4021f473d3a90b | ce41ea58bdddde70 | YES |

---

## 2. Shared Premises

Both Path A and Path B operate on:
- Identical DecisionRecord input (D-T50)
- Identical PresentContext input
- Same reproducible clock (now = 2026-08-28T12:00:00Z)
- Same evidence digest comparison (digest-only, no content validation)
- Same authority state and ID values
- Same context identification mechanism

No hidden or implicit inputs differ between paths.

---

## 3. Intentional Difference

The only intentional difference is **execution path selection**:

**Path A (Anti-pattern Control):**
- Calls `reuse_directly(record)` 
- Ignores `present` argument completely
- Returns `record.decision` without any comparison

**Path B (Proper Gate):**
- Calls `gate.assess(record, present)`
- Compares all 5 observable premises
- Evaluates eligibility based on premise changes
- Applies reduction rules (HARD_BLOCK, REQUIRE_REEVALUATION, etc.)
- Returns eligibility + execution decision

The implementation differs in **what gets compared**, not in input state.

---

## 4. Execution Trace

### Path A (Direct Reuse)

```
Input: DecisionRecord(decision=ALLOW, ...)
    |
    v
reuse_directly()
    |
    +-- Access record.decision
    +-- (no reference to present context)
    +-- (no temporal validation)
    +-- (no evidence comparison)
    +-- (no authority check)
    +-- (no context check)
    |
    v
Output: PastDecision.ALLOW
Comparisons: 0
```

**Execution Result:**
- Eligibility: (not computed; direct return)
- Execution: EXECUTE (verdict is ALLOW, present never inspected)
- Findings: (none; no comparison performed)
- Legitimacy Assessment: NOT A LEGITIMATE ALLOW

---

### Path B (Re-Evaluated)

```
Input: DecisionRecord + PresentContext
    |
    v
ReEvaluationGate.assess()
    |
    +-- Check evidence_digest
    |   |
    |   v
    |   [176fd78...] != [7ea0f7...] ? YES
    |   -> Finding: EVIDENCE_CHANGED
    |   -> Weight: REQUIRE_REEVALUATION
    |
    +-- Check validity_until
    |   |
    |   v
    |   [2026-08-10] < [2026-08-28] ? YES
    |   -> Finding: TEMPORAL_EXPIRED
    |   -> Weight: REQUIRE_REEVALUATION
    |
    +-- Check authority_id
    |   |
    |   v
    |   [AUTH-OPERATOR-01] != [AUTH-OPERATOR-02] ? YES
    |   -> Finding: AUTHORITY_CHANGED
    |   -> Weight: REQUIRE_REEVALUATION
    |
    +-- Check context_id
    |   |
    |   v
    |   [CTX-1] != [CTX-2] ? YES
    |   -> Finding: CONTEXT_MISMATCH
    |   -> Weight: REQUIRE_REEVALUATION
    |
    +-- Check context_digest (if same context)
    |   |
    |   v
    |   (context_id different, so digest check deferred)
    |
    +-- Apply reduction rules
    |   |
    |   v
    |   REQUIRE_REEVALUATION present ? YES (4 times)
    |   -> Result: RE_EVALUATE
    |
    +-- Apply execution gate
    |   |
    |   v
    |   Eligibility is RE_EVALUATE (not ELIGIBLE)
    |   -> Result: STOP
    |
    v
Output: Eligibility.RE_EVALUATE / Execution.STOP
Comparisons: 4 (evidence, validity, authority, context)
Findings: EVIDENCE_CHANGED, TEMPORAL_EXPIRED, AUTHORITY_CHANGED, CONTEXT_MISMATCH
```

**Execution Result:**
- Eligibility: RE_EVALUATE
- Execution: STOP
- Findings: 4 detected premises changes
- Legitimacy Assessment: (not applicable; re-evaluation requested)

---

## 5. Minimal Causal Witness

### Single-Condition Reduction Tests

Holding all other premises constant, changing one condition at a time:

| Condition Changed | Eligibility | Execution | Finding(s) | Execution Blocked? |
| --------------- | ----------- | --------- | ---------- | ------------------ |
| Evidence only | RE_EVALUATE | STOP | EVIDENCE_CHANGED | YES |
| Validity only | RE_EVALUATE | STOP | TEMPORAL_EXPIRED | YES |
| Authority only | RE_EVALUATE | STOP | AUTHORITY_CHANGED | YES |
| Context ID only | RE_EVALUATE | STOP | CONTEXT_MISMATCH | YES |
| Context Digest only | RE_EVALUATE | STOP | CONTEXT_CHANGED | YES |
| None (baseline) | ELIGIBLE | EXECUTE | PREMISES_UNCHANGED | NO |

### Conclusion

The minimal necessary condition for T50 divergence is **any single premise change**.

When no premises change:
- Path A: ALLOW (unchanged)
- Path B: ELIGIBLE -> EXECUTE (unchanged)
- Result: Paths converge

When exactly one premise changes:
- Path A: ALLOW (unchanged; ignores present)
- Path B: RE_EVALUATE -> STOP
- Result: Divergence appears

When multiple premises change (as in T50):
- Path A: ALLOW (unchanged)
- Path B: RE_EVALUATE -> STOP (same as single-condition case)
- Result: Divergence persists (no additive interaction)

### Sufficiency Statement

> The divergence between Path A and Path B is **caused by** the presence of at
> least one changed premise (evidence, validity, authority, or context).
>
> The divergence is **sufficient to require** the distinction between "reusable"
> (Eligibility) and "executable" (Execution) as separate evaluation stages.
>
> T50 uses the maximal set of condition changes to make the divergence clearly
> observable, but this maximal set is not necessary for divergence itself.

---

## 6. Causality Chain

**Root cause of divergence:**

1. Path A design: Direct reuse ignores present state
2. Path B design: Gate checks all premises against present
3. Input state: At least one premise differs (fact in T50)
4. Gate logic: Premise difference triggers RE_EVALUATE
5. Reduction rules: RE_EVALUATE never executes
6. Result: Paths diverge

**Removal of any step breaks divergence:**
- If all premises were unchanged: both paths execute (converge)
- If Path A had a gate: both would re-evaluate (converge)
- If reduction rule allowed RE_EVALUATE to execute: paths converge
- If execution gate permitted non-ELIGIBLE states: divergence unclear

---

## 7. Temporal Continuity Witness

**Time domain:**
- Decision made at: 2026-08-01T00:00:00Z
- Validity window: [2026-08-01, 2026-08-10]
- Present moment: 2026-08-28T12:00:00Z
- Status: **Beyond validity boundary** (18+ days past expiry)

Path A's return of ALLOW at 2026-08-28T12:00:00Z is temporally unjustified.
It represents a verdict from 27+ days in the past, without temporal validation.

Path B correctly identifies this via TEMPORAL_EXPIRED finding.

---

## 8. Assessment of Legitimacy

### Path A Output

**Claim:** "I returned ALLOW"
**Basis:** Stored decision.decision field
**Validation:** None performed

**Verdict:** Output is mechanically correct (field value matches storage),
but not a legitimate authorization. No present-state justification exists.

### Path B Output

**Claim:** "Re-evaluation required"
**Basis:** 4 independent premise changes detected
**Validation:** Each premise checked before finding raised

**Verdict:** Output is justified. Any single finding would justify the claim.

---

## 9. Final Causal Statement

**T50-TIM-REUSE demonstrates that:**

The divergence between direct reuse (Path A) and re-evaluated (Path B) is
minimally caused by the execution of different code paths on the same input.

The gate-based re-evaluation (Path B) is triggered by observable premise changes.

Any one of the five premise categories (evidence, validity, authority,
context_id, context_digest) is sufficient to require re-evaluation.

The verdict "it was allowed before" carries no inherent authority in the present
moment without validation against changed premises.

---

## 10. Verification Status

- [x] Input state documented
- [x] Shared premises enumerated
- [x] Path difference isolated
- [x] Execution traces reconstructed
- [x] Single-condition reduction tests performed
- [x] Sufficiency statement confirmed
- [x] Minimal witness identified
- [x] Causality chain verified

