# HG DECISION SEQUENCE
## First Strike (E13-E22 + A10) — 10-Decision Authorization Path

**Date**: 2026-09-13  
**Package Type**: Sequential HG Decision Framework  
**Authority**: Human Gate (all decisions)  
**System State**: HOLD / FAIL-CLOSED (maintained throughout)  
**Implementation Authorization**: PENDING (decided at HG-D10 only)

---

## PREAMBLE

This package presents **10 sequential decisions** that Human Gate must make before Implementation Authorization can be granted. Each decision is independent and must be made in order. KUROKO presents only evidence, options, and candidate proposals—HG makes all decisions.

**Critical Principle**: Decision ≠ Implementation. Each HG choice is a *decision* about strategy, design, scope, and conditions—NOT an implementation commitment.

---

## DECISION CONTEXT

**Current State** (from 12 audit documents):
- 15 consequential paths total
- E01-E05: 5 protected (M18 guards verified)
- E13-E22: 10 unprotected (authorization bypass vulnerability)
- A10 adversarial test: FAILS (bypass confirmed)
- M18 coverage: 5/15 = 33.3%
- Kernel-Wide Enforcement: NOT ACHIEVED
- Authorization: NOT GRANTED
- System: HOLD / FAIL-CLOSED

**First Strike Objective**: Close authorization gap in E13-E22 + A10

**Prerequisites for Implementation**: HG decisions on strategy, design, scope, conditions, verification, and failure handling.

---

## HG-D1: PERSISTENCE STRATEGY SELECTION

### Context

How should MoCKA persist authorization decisions, enforcement events, and evidence across system restarts?

**Design Candidates**:

| Strategy | Characteristic | Trade-off |
|----------|---|---|
| **A — Event Store** | Append-only log of all authorization events | Full audit trail; queries require replay |
| **B — Decision Ledger Extension** | Structured ledger of decisions + evidence | Query-friendly; requires schema design |
| **C — Relational Store** | SQL tables for decisions, paths, evidence | Query performance; loses append-only guarantee |
| **D — Hybrid** | Event log + relational indices + snapshots | Best of all; highest complexity |

**This Decision Determines**:
- Which persistence layer HG authorizes for First Strike
- Schema design direction for Phase 2+
- Runtime evidence collection method
- Audit trail structure

**THIS IS A DESIGN DECISION, NOT AN IMPLEMENTATION AUTHORIZATION.**

### HG-D1 Options

- [ ] **A — Event Store** — Adopt immutable event log approach
- [ ] **B — Decision Ledger Extension** — Extend existing decision_ledger.jsonl structure
- [ ] **C — Relational Store** — Add SQL schema for decisions/evidence
- [ ] **D — Hybrid** — Combine event log + relational layer
- [ ] **HOLD** — Request additional design clarification before deciding

**HG Decision for HG-D1**: _____________________

---

## HG-D2: ENFORCEMENT DESIGN SELECTION

### Context

How should authorization decisions be enforced at runtime? What is the architectural pattern?

**Design Candidates**:

| Design | Characteristic | Trade-off |
|---|---|---|
| **A — Strict In-Band Enforcement** | Gate checks authorization *before* action executes; blocks immediately if UNKNOWN | Fail-closed; synchronous latency |
| **B — Out-of-Band / Detective Enforcement** | Action executes; audit logs are checked post-hoc; violations detected via monitoring | Non-blocking; detection lag |
| **C — Pluggable Policy Enforcement** | Multiple enforcement policies can be selected per path; extensible | Complexity; requires policy framework |

**This Decision Determines**:
- Whether M18 gates run before or after action
- How UNKNOWN/NOT_PROVEN are handled
- Audit trail timing
- Latency profile

**THIS IS A DESIGN DECISION, NOT AN IMPLEMENTATION AUTHORIZATION.**

### HG-D2 Options

- [ ] **A — Strict In-Band Enforcement** — Gate before action (proven working for E01-E05)
- [ ] **B — Out-of-Band / Detective Enforcement** — Action first, audit trail verification later
- [ ] **C — Pluggable Policy Enforcement** — Multiple policies per path
- [ ] **HOLD** — Request enforcement design clarification

**HG Decision for HG-D2**: _____________________

---

## HG-D3: M18 SCOPE & AUTHORIZATION BOUNDARY

### Context

What is the scope of authorization enforcement for First Strike and all future phases?

**Current State**:
- E01-E05 (5 paths): Protected by M18 ✓
- E13-E22 (10 paths): Unprotected (First Strike target)
- M11: Not wired
- Orchestra: Not implemented
- Decision Ledger: Not populated
- GL Engines: Not implemented
- Learning Kernel: Not operational

**Scope Options**:

| Option | First Strike Scope | Phase 2+ Scope |
|---|---|---|
| **APPROVE CURRENT SCOPE** | E13-E22 + A10 | M11 + Orchestra + Decision Ledger + GL + Learning Kernel |
| **MODIFY SCOPE** | (HG specifies) | (HG specifies) |
| **HOLD** | Deferred | Deferred |

**Current Proposal** (if not modified):
- First Strike: E13-E22 + A10 only
- Phase 2: M11 wiring + Decision Ledger + Orchestra
- Phase 3: GL Engines + Learning Kernel

### HG-D3 Options

- [ ] **APPROVE CURRENT SCOPE** — E13-E22 + A10 (First Strike); defer M11/Orchestra/GL/Learning Kernel
- [ ] **MODIFY SCOPE** — (Specify alternative scope and phase assignments)
- [ ] **HOLD** — Request clarification on scope boundaries

**HG Decision for HG-D3**: _____________________

---

## HG-D4: SEMANTIC CLOSURE READINESS

### Context

Given current Evidence, Design Decisions (HG-D2 outcome), and Scope (HG-D3 outcome), is the semantic foundation ready for implementation?

**Assessment Criteria**:

| Factor | Status | Evidence |
|---|---|---|
| Authorization Boundary Definition | Defined | M18 guards + HG chain roles |
| Evidence Lineage Design | Designed | Decision_id tracking + audit logs |
| Fail-Closed Behavior | Specified | UNKNOWN/NOT_PROVEN → BLOCK |
| Runtime Enforcement Chain | Specified (not yet proven) | M18 gate → execution flow |
| Consequence Recording | Designed | Event log / decision ledger |

**Semantic Closure Readiness** means:
- Design is complete and coherent
- No fundamental semantic gaps remain
- Evidence chain is defined (though not yet implemented)
- Authorization model is clear

### HG-D4 Options

- [ ] **READY** — Proceed with implementation confidence
- [ ] **READY WITH CONDITIONS** — Ready, but require specific design clarifications during implementation
- [ ] **NOT READY** — Semantic gaps remain; request design refinement
- [ ] **HOLD** — Additional design work needed before proceeding

**HG Decision for HG-D4**: _____________________

---

## HG-D5: FIRST STRIKE REMEDIATION SCOPE

### Context

Assuming HG-D3 APPROVED CURRENT SCOPE and HG-D4 determined READY, should First Strike implementation scope be:

**Proposed In-Scope**:
- E13: direct subprocess (auto_runner)
- E14: direct subprocess (drift_loop)
- E15: direct subprocess (event_watcher)
- E16: direct subprocess (error_capture)
- E17: subprocess cluster operation
- E18: schema update subprocess
- E19: node discovery subprocess
- E20: state mutation without gate
- E21: API subprocess wrapper
- E22: external system integration
- A10: adversarial test closure

**Proposed Out-of-Scope**:
- M11 in-flight reverification wiring (Phase 2)
- Orchestra multi-audit routing (Phase 2)
- Decision Ledger population (Phase 2)
- GL1/GL2/GL4 governance engines (Phase 3)
- Learning Kernel autonomy (Phase 3)

### HG-D5 Options

- [ ] **APPROVE** — Accept proposed scope (E13-E22 + A10 in First Strike)
- [ ] **APPROVE WITH CONDITIONS** — Approve with modifications (specify)
- [ ] **MODIFY** — Change scope boundaries (specify new scope)
- [ ] **HOLD** — Request scope clarification

**HG Decision for HG-D5**: _____________________

---

## HG-D6: IMPLEMENTATION CONDITIONS

### Context

If implementation is authorized, what conditions must it satisfy?

**Candidate Conditions** (HG to approve/modify/delete):

| Condition | Purpose | Severity |
|---|---|---|
| **Scope Strictly Bounded** | No scope expansion without HG reauthorization | CRITICAL |
| **Fail-Closed Default** | UNKNOWN/NOT_PROVEN/EVIDENCE_GAP → BLOCK (never ALLOW) | CRITICAL |
| **Direct/Internal/Daemon Bypass Verification** | Verify all bypass paths are closed | CRITICAL |
| **Runtime Evidence Required** | Evidence must be collected during execution | HIGH |
| **No Automatic Phase Progression** | Stop after Phase 1; don't auto-proceed to Phase 2 | HIGH |
| **Code Review Mandatory** | All changes require peer review before merge | HIGH |
| **Fail-Closed Verification** | Test that UNKNOWN paths actually block | HIGH |
| **M18 Coverage Reassessment** | After implementation, recalculate coverage | MEDIUM |
| **Critical Failure → Stop** | If critical test fails, stop and reassess (no auto-fix) | HIGH |
| **Evidence Lineage Preserved** | All decisions traced to execution consequences | MEDIUM |

### HG-D6 Options

- [ ] **APPROVE PROPOSED CONDITIONS** — All listed conditions required
- [ ] **APPROVE WITH MODIFICATIONS** — Accept some, modify others (specify)
- [ ] **HOLD** — Request additional conditions or clarifications

**HG Decision for HG-D6**: _____________________

---

## HG-D7: VERIFICATION & COMPLETION CRITERIA

### Context

After implementation, what must be verified before First Strike closure?

**Candidate Verification Criteria** (HG to approve/modify/delete):

| Criteria | Verification Method | Pass Condition |
|---|---|---|
| **E13-E22 Runtime Enforcement** | Execute each path; verify M18 gate called | 10/10 paths verified |
| **A10 Bypass Closure** | Run A10 test; expect BLOCK | A10 test PASSES |
| **Direct Execution Path Closure** | Attempt direct subprocess; verify BLOCKED | Blocked at M18 gate |
| **Internal Dispatch Path Closure** | Verify internal function calls protected | No unprotected dispatch found |
| **Daemon/Background Path Closure** | Verify background processes gated | No unprotected daemon execution |
| **Fail-Closed Behavior Verification** | Attempt UNKNOWN resolution; verify BLOCK | UNKNOWN paths block correctly |
| **Runtime Evidence Acquisition** | Collect execution logs + decision_id linkage | Evidence chain complete |
| **Evidence Lineage Verification** | Trace decision → authorization → execution → consequence | Full lineage documented |
| **Regression Verification** | Run E01-E05 regression tests | 61/61 tests PASS |
| **M18 Coverage Recalculation** | Count protected paths | Coverage = 15/15 = 100% |

### HG-D7 Options

- [ ] **APPROVE PROPOSED CRITERIA** — All listed verifications required
- [ ] **APPROVE WITH MODIFICATIONS** — Accept some, modify others (specify)
- [ ] **HOLD** — Request additional verification criteria

**HG Decision for HG-D7**: _____________________

---

## HG-D8: SCOPE EXPANSION & DISCOVERY RULE

### Context

During implementation, new consequential paths, bypass patterns, authorization boundaries, or runtime dependencies may be discovered. How should they be handled?

**Options**:

| Option | Approach |
|---|---|
| **APPROVE** | Any discovery immediately stops implementation; re-submit to HG for scope decision |
| **APPROVE WITH CONDITIONS** | Minor discoveries handled per conditions; major discoveries trigger HG reassessment |
| **MODIFY** | HG specifies discovery handling rule |

**Recommendation** (if HG selects APPROVE):
- Discovery of new Consequential Path → STOP; submit to HG
- Discovery of new bypass vector → STOP; analyze and re-submit
- Discovery of schema incompatibility → STOP; design review with HG
- Minor LOC estimate changes → Continue (within 20% threshold)

### HG-D8 Options

- [ ] **APPROVE** — Auto-stop on major discoveries; re-submit to HG
- [ ] **APPROVE WITH CONDITIONS** — Define discovery threshold (specify)
- [ ] **MODIFY** — Alternative discovery handling rule (specify)
- [ ] **HOLD** — Request discovery rule clarification

**HG Decision for HG-D8**: _____________________

---

## HG-D9: FAILURE, ROLLBACK & CONTAINMENT

### Context

If implementation or verification encounters critical failure, what happens?

**Candidate Failure Conditions** (HG to approve/modify/delete):

| Failure Type | Response |
|---|---|
| **A10 Test Fails** | STOP; containment; root cause analysis; re-design proposal to HG |
| **M18 Guard Implementation Breaks E01-E05** | STOP; rollback; retest; HG reassessment |
| **HG→Execution Chain Not Demonstrated** | STOP; investigation; re-design; HG review |
| **UNKNOWN/NOT_PROVEN Path Produces ALLOW** | STOP; fail-closed enforcement fix; re-test |
| **Evidence Lineage Incomplete** | STOP; implement missing linkage; re-verify |
| **Scope Expansion Beyond HG-D5** | STOP; re-submit to HG per HG-D8 |

**Failure Protocol** (if HG approves):
1. Detect critical failure → STOP implementation immediately
2. Preserve all evidence (logs, code state, execution traces)
3. Implement containment (fail-closed mode active)
4. Analyze root cause
5. Prepare remediation proposal
6. Submit to HG for re-assessment

**NO AUTO-FIX** — Failures must be analyzed and HG-approved before re-attempting.

### HG-D9 Options

- [ ] **APPROVE** — Adopt proposed failure protocol
- [ ] **APPROVE WITH CONDITIONS** — Modify failure definitions or responses (specify)
- [ ] **MODIFY** — Alternative failure handling protocol (specify)
- [ ] **HOLD** — Request failure protocol clarification

**HG Decision for HG-D9**: _____________________

---

## HG-D10: FINAL IMPLEMENTATION AUTHORIZATION

### Context

Given the decisions made in HG-D1 through HG-D9:
- Strategy selected (HG-D1)
- Enforcement design chosen (HG-D2)
- M18 scope approved (HG-D3)
- Semantic readiness assessed (HG-D4)
- Remediation scope approved (HG-D5)
- Implementation conditions defined (HG-D6)
- Verification criteria specified (HG-D7)
- Discovery rule established (HG-D8)
- Failure protocol adopted (HG-D9)

### The Question

**Do you authorize implementation of E13-E22 + A10 First Strike under the above conditions and framework?**

### HG-D10 Options

- [ ] **APPROVE** — Authorize First Strike implementation with stated conditions
- [ ] **APPROVE WITH CONDITIONS** — Authorize with additional conditions (specify)
- [ ] **HOLD** — Request clarification on implementation path before authorizing
- [ ] **REJECT** — Do not authorize; prepare alternative proposal

**HG Decision for HG-D10**: _____________________

---

## AUTHORIZATION EFFECTIVENESS

### Effective Only When HG-D10 Is Decided

**Implementation Authorization becomes EFFECTIVE when**:
1. HG-D10 is marked APPROVE or APPROVE WITH CONDITIONS
2. All prior decisions (HG-D1 through HG-D9) are recorded
3. Decision Record is formally confirmed

**Until then**:
- Authorization = NOT GRANTED
- Implementation = NOT AUTHORIZED
- Code changes = ZERO
- System state = HOLD / FAIL-CLOSED

### Post-Authorization Boundary

**After HG-D10 APPROVE/APPROVE WITH CONDITIONS**:
- Implement per HG-D5 scope
- Comply with HG-D6 conditions
- Verify per HG-D7 criteria
- Handle discoveries per HG-D8
- Follow failure protocol per HG-D9

**Scope expansion, unauthorized conditions, or failure bypass = STOP; re-submit to HG**

---

## DECISION RECORD TEMPLATE

### For Human Gate to Complete

```
DECISION RECORD — First Strike (E13-E22 + A10)
Date: _______________
Human Gate Decision Maker: _______________

HG-D1 (Persistence Strategy): _____________________
HG-D2 (Enforcement Design): _____________________
HG-D3 (M18 Scope): _____________________
HG-D4 (Semantic Readiness): _____________________
HG-D5 (Remediation Scope): _____________________
HG-D6 (Implementation Conditions): _____________________
HG-D7 (Verification Criteria): _____________________
HG-D8 (Discovery Rule): _____________________
HG-D9 (Failure Protocol): _____________________
HG-D10 (Implementation Authorization): _____________________

Additional Notes/Modifications:
_______________________________________________________________

Signature: _______________
Date Effective: _______________
```

---

## EVIDENCE BASIS

All decisions grounded in 12 audit documents:
- MOCKA_IMPLEMENTATION_GAP_INVENTORY_20260913.md
- MOCKA_TOP_IMPLEMENTATION_GAPS_20260913.md
- EXECUTIVE_IMPLEMENTATION_GAP_SUMMARY_20260913.md
- KUROKO_AUDIT_COMPLETION_REPORT_20260913.md
- RUNTIME_PATH_CLOSURE_MATRIX_20260913.md
- TRUE_UNIMPLEMENTED_AND_DEAD_CODE_20260913.md
- GROUP_A_B_C_D_E_FINAL_CLASSIFICATION_20260913.md
- PHASE_2_AUDIT_CLOSURE_SUMMARY_20260913.md
- CANONICAL_15_PATH_RECONCILIATION_20260913.md
- PHASE_3_EVIDENCE_VERIFICATION_FINAL_20260913.md
- FINAL_CANONICAL_RECONCILIATION_HG_SUBMISSION_20260913.md
- HG_SUBMISSION_FREEZE_VERIFICATION_20260913.md

**Total Evidence Volume**: ~220 KB

---

## CRITICAL PRINCIPLES

### Preserved Throughout

- ✓ Authorization = NOT GRANTED (until HG-D10 decides)
- ✓ Implementation = NOT AUTHORIZED (no code changes)
- ✓ Production Modification = ZERO
- ✓ System = HOLD / FAIL-CLOSED
- ✓ KUROKO does not recommend HG decisions
- ✓ Design ≠ Implementation
- ✓ Decision ≠ Consequence

### Non-Negotiable

- ❌ NO code implementation before HG-D10 approval
- ❌ NO scope expansion without HG decision
- ❌ NO failure auto-fix without HG approval
- ❌ NO automatic Phase 2 progression
- ❌ KUROKO autonomy in authorization strictly prohibited

---

## PACKAGE STATUS

**Type**: Sequential HG Decision Framework  
**Status**: READY FOR HUMAN GATE DECISION SEQUENCE  
**Next Action**: HG to make HG-D1 through HG-D10 decisions in order  
**System State**: HOLD / FAIL-CLOSED (maintained)  

---

**END OF HG DECISION SEQUENCE PACKAGE**

Awaiting Human Gate decisions on HG-D1 through HG-D10.

