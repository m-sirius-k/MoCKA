# HGD-C1: Integration Test Minimum Criterion Decision Package

**Package Type**: Human Gate Decision Draft  
**Status**: PENDING APPROVAL  
**Prepared by**: KUROKO  
**Date**: 2026-10-02  
**Reference**: GAP-3 in PHASE5_1_A_REMEDIATION_DESIGN.md  
**Depends on**: None (Stage 1 is independent)

---

## Decision Question

What is the minimum acceptance criterion for PHASE 5.1-A to be declared
IMPLEMENTATION COMPLETE (removing the current VERIFICATION BLOCKED status)?

Two sub-questions:
1. Is Stage 1 (FAIL_1 test only) sufficient to unblock VERIFICATION BLOCKED?
2. Does the commit message inaccuracy require formal Decision Ledger correction?

---

## Background

PHASE 5.1-A Implementation Verification found:
- 7 unit tests in test_gl8_human_gate_authorization.py are REAL (assertions present)
- 15+ integration tests in test_authorization_pipeline_integration.py are ALL stubs (pass)
- Commit 916bef7 message states "30+ test cases" and "FAIL_1-5 scenarios per
  PHASE 5.0-C investigation" implying full verification, which is inaccurate
- Current status: IMPLEMENTATION COMPLETE / VERIFICATION BLOCKED

GAP-3 remediation options from REMEDIATION_DESIGN.md:
- Option A: Full integration test implementation (requires GAP-2 resolved first)
- Option B: Staged stub replacement (Stage 1 independent, Stage 2+ needs GAP-2)
- Option C: Separate verification script (partial GAP-2 independence)

---

## Stage 1 Scope: GL8 FAIL_1 Blocking Evidence

### What Stage 1 Tests

FAIL_1 scenario: Tool called without decision_id argument.

This is the ONLY integration scenario that can be tested WITHOUT resolving GAP-2,
because the test deliberately omits decision_id to trigger the failure:

```python
# Stage 1 test (no decision_id in args)
args = {"title": "test_event", "description": "no decision_id here"}
decision = pipeline.execute("mocka_write_event", args)

assert decision.allowed == False
assert decision.failure_code == "GL8_FAIL_1_MISSING_DECISION_ID"
assert decision.first_failure.layer == "GL8"
assert len(decision.checkpoints) == 1  # Fast-fail: only GL8 ran
```

### Why Stage 1 Does Not Depend on GAP-2

GAP-2 (propagation contract) is the problem of HOW decision_id is conveyed.
Stage 1 tests the case WHERE decision_id is NOT conveyed.
These are complementary: Stage 1 verifies the absence case.
The absence case works as-is: GL8 correctly detects missing decision_id.

### Why Stage 1 Is Insufficient Alone

Stage 1 only verifies that the pipeline correctly handles missing authorization.
It does NOT verify that authorization WITH a valid decision_id works end-to-end.
FAIL_2-5 remain untested. Happy path (ALLOW) remains untested.

A pipeline that ALWAYS returns DENY (broken) would pass Stage 1.
Therefore, Stage 1 alone cannot confirm the pipeline functions correctly.

---

## GL8 FAIL_1 Blocking Evidence Plan

### Test Implementation Plan (Stage 1)

Target file: `structural/test_authorization_pipeline_integration.py`

Replace `test_fail_1_missing_decision_id` body with:

```python
def test_fail_1_missing_decision_id(self):
    """FAIL_1: Tool called without decision_id -> GL8 denies"""
    pipeline = AuthorizationPipeline()

    result = pipeline.execute(
        tool_name="mocka_write_event",
        args={"title": "test", "description": "no decision_id"}
    )

    assert result.allowed == False, f"Expected DENY, got ALLOW: {result}"
    assert result.failure_code == "GL8_FAIL_1_MISSING_DECISION_ID"
    assert result.first_failure is not None
    assert result.first_failure.layer == "GL8"
    assert len(result.checkpoints) == 1  # Fast-fail: only GL8 checkpoint
```

No fixtures required. No mock Decision Ledger required.
Import: `from structural.authorization_pipeline import AuthorizationPipeline`

### Expected Test Execution Result

```
test_authorization_pipeline_integration.py::TestAuthorizationPipeline::test_fail_1_missing_decision_id
PASSED [assertion verified: allowed=False, failure_code=GL8_FAIL_1_MISSING_DECISION_ID]
```

### Evidence This Constitutes Runtime Enforcement

When this test passes, it demonstrates:
1. AuthorizationPipeline.execute() is callable
2. GL8 engine is instantiated and running
3. GL8 correctly detects missing decision_id
4. Pipeline returns DENY with correct failure code
5. Fast-fail behavior: only 1 checkpoint (GL8 ran, GL9-GL12 did not)

This is Runtime Enforcement evidence for the FAIL_1 scenario.

---

## Success Criteria Options

### Option X1: Stage 1 Only (Minimal)

PHASE 5.1-A status changes from VERIFICATION BLOCKED to PARTIALLY VERIFIED when:
- test_fail_1_missing_decision_id passes with real assertions
- pytest output confirms 1 test PASSED (not 0 assertions, not trivially)

Remaining status: FAIL_2-5 and Happy Path still UNVERIFIED
Next milestone: FULLY VERIFIED after GAP-2+5 resolved and all tests implemented

### Option X2: FAIL_1 + Happy Path (Recommended)

PHASE 5.1-A status changes to PARTIALLY VERIFIED when:
- test_fail_1_missing_decision_id passes (Stage 1, as above)
- test_all_layers_pass passes with a mock Decision Ledger and valid inputs

Happy path test requires a mock Decision Ledger (same fixture as GL8 unit test).
This verifies the pipeline can both DENY and ALLOW correctly.

Remaining status: FAIL_2-5 still UNVERIFIED (depends on GAP-2 resolution)

### Option X3: Full Criterion (Comprehensive)

PHASE 5.1-A status changes to IMPLEMENTATION COMPLETE (no qualifier) when:
- ALL test stubs replaced with real assertions
- pytest reports 15+ tests PASSED
- FAIL_1-5 all verified as blocking
- Happy path verified as allowing

This requires GAP-2 and GAP-5 to be resolved first.
Timeline: after HGD-A1 and HGD-B1 decisions and implementation.

---

## Commit Message Inaccuracy

### Facts

Commit 916bef7 message:
> "Tests: 30+ test cases covering: FAIL_1-5 scenarios per PHASE 5.0-C investigation,
>  Happy path authorization flows, E2E scenario testing, Performance validation"

Actual state: 7 real tests (GL8 unit tests) + 15+ stubs = NOT 30+ verified test cases.
The 15+ integration tests do not execute any assertions.

### Policy Reference

Per TODO_384: "診断結果・経過説明・独自語彙をstatusに直接書き込むこと (noteへ書くこと)"
Per TODO_382: "rebase/filter-branch等の履歴書き換え系git操作は禁止"

Rewriting commit history is prohibited. The inaccuracy stands in git history.

### Proposed Handling

Record the discrepancy in Decision Ledger (not in a code commit):

Decision Ledger entry:
```
{
  "decision_id": "DC_20261002_COMMIT_MSG_CORRECTION",
  "title": "Acknowledge commit 916bef7 test coverage inaccuracy",
  "context": "Commit message states 30+ test cases; actual verified tests = 7",
  "decision": "Record inaccuracy. No git history rewrite (TODO_382 prohibition).",
  "status": "Active"
}
```

This makes the discrepancy formally acknowledged without violating TODO_382.

---

## Decision Options Summary

| | Stage 1 Only (X1) | Stage 1 + Happy Path (X2) | Full Criterion (X3) |
|--|--|--|--|
| GAP-2 required | No | No | Yes |
| GAP-5 required | No | No | Partial |
| Achievable now | Yes | Yes | No |
| Verification strength | Weak | Moderate | Strong |
| Unblocks PHASE 5.2 | No | Conditionally | Yes |

**KUROKO Recommendation**: Option X2 as minimum unblocking criterion.
FAIL_1 + Happy Path can be implemented without GAP-2/5 resolution.
This changes status from VERIFICATION BLOCKED to PARTIALLY VERIFIED.
Full criterion (X3) is the target after GAP-2+5 remediation.

---

## Required Approvals

1. きむら博士: Select Success Criterion (X1 / X2 / X3)
2. きむら博士: Approve or reject commit message correction via Decision Ledger
3. Implicit: GAP-3 Stage 1 implementation follows HGD-C1 approval

---

## Next Action After Approval

If X2 approved:
1. Implement test_fail_1_missing_decision_id (non-stub) in integration test file
2. Implement test_all_layers_pass with mock Decision Ledger
3. Run pytest and confirm 2 tests PASS
4. Record CHANGE_DONE with pytest output as evidence
5. Update TODO status to PARTIALLY VERIFIED
