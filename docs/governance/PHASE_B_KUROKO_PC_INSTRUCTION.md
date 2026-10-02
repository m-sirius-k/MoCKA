# PHASE B KUROKO PC INSTRUCTION
## MoCKA Phase B -- KUROKO PC Implementation and Verification
## Status: ISSUED_TO_PC
## Date: 2026-10-02
## Issued by: くろこWeb (Phase A complete)

---

## PREMISE

Phase A Web_PREPARED artifacts have been received.
However, Web-side artifacts are NOT yet Source of Truth.
Final SoT is:

  C:\Users\sirok\MoCKA

Web-side branch `claude/nifty-keller-dqov84` contains 29 WEB_PREPARED files.
These are PROPOSALS, not IMPLEMENTATIONS, until PC verifies and applies them.

---

## STEP 1: Record initial state BEFORE any action

Run immediately. Save the output.

```powershell
cd C:\Users\sirok\MoCKA

git status
git branch --show-current
git log -1 --oneline
git remote -v
```

If current branch is `main`, that fact is preserved.
Do NOT unconditionally checkout the Web branch.
The current branch state is the SoT baseline.

---

## STEP 2: Confirm Phase A ZIP

Expand the ZIP: MOCKA_PHASE_A_HANDOFF_20261002.zip

Read in this order:
1. PC_HANDOFF.md         <- top-level, read first
2. HANDOFF_MANIFEST.md   <- MUST_COPY / MUST_REVIEW / MUST_EXECUTE classification

Then review:
```
docs/contracts/          <- Contract A through E
docs/governance/         <- AUR_ENFORCEMENT_CONTRACT, plans, reports
implementation/          <- aur/, memory/experience_memory.py
```

---

## STEP 3: Compare Web artifacts to PC SoT

Before copying any file, check for:

- File with same name already exists in C:\Users\sirok\MoCKA
- Canonical contract duplication
- Responsibility overlap with existing implementation
- Import path compatibility (Windows paths vs Linux paths)
- Event Store connection
- Human Gate connection
- GL7 connection
- Memory Pipeline connection
- Decision Pipeline connection

Files to verify before applying:
```
aur/assessment.py
aur/consequence.py
aur/enforcement.py
aur/reassessment.py
memory/experience_memory.py
```

Do NOT copy these unconditionally.
Confirm relationship with existing structure first, then apply.

---

## STEP 4: Maintain WEB_PREPARED / IMPLEMENTED / RUNTIME_VERIFIED separation

| Status | Meaning |
|--------|---------|
| WEB_PREPARED | Web side prepared, not yet on PC SoT |
| IMPLEMENTED | Applied to C:\Users\sirok\MoCKA, tests passing |
| RUNTIME_VERIFIED | Full runtime + Event Store readback confirmed |
| CLOSED_LOOP_VERIFIED | Full Decision->Reassessment loop demonstrated |

Promotion rules:
- WEB_PREPARED -> IMPLEMENTED: requires PC test pass
- IMPLEMENTED -> RUNTIME_VERIFIED: requires V-01 through V-13
- RUNTIME_VERIFIED -> CLOSED_LOOP_VERIFIED: requires Event Store readback

---

## STEP 5: Contract Consistency Check

Verify each of the following contracts for conflicts with existing canonical contracts:

1. Assessment Contract (docs/contracts/assessment_contract_v1.md)
2. Action Execution Contract (docs/contracts/action_execution_contract_v1.md)
3. Actual Consequence Contract (docs/contracts/actual_consequence_contract_v1.md)
4. Experience Memory Contract (docs/contracts/experience_memory_contract_v1.md)
5. Reassessment Contract (docs/contracts/reassessment_contract_v1.md)
6. A-U-R Enforcement Contract (docs/governance/AUR_ENFORCEMENT_CONTRACT.md)

If any new contract overlaps with existing PHASE 5.0-E canonical contract:
- Do NOT create a duplicate
- Declare the existing canonical as the single authority
- Merge any additional content into the canonical

If there is a contradiction between new and existing:
- Do NOT implement
- Record as CONTRACT_CONFLICT and report

---

## STEP 6: Run tests FIRST

```powershell
cd C:\Users\sirok\MoCKA
python -m pytest aur/tests/ -v
```

Expected: 23/23 PASSED
Record actual result. Do NOT adjust results to match expectation.
If any test fails, diagnose before proceeding.

---

## STEP 7: Verify Assessment (A)

Confirm AssessmentRecord can hold:

- Evidence (X axis)
- Observation Context
- Interpretation (Y axis)
- UNKNOWN values (where not determinable)
- Validity (admissible flag)
- Uncertainty (confidence score)
- Impact (S axis)
- Assessment Admissibility (admissible = True/False)

Critical check:
  UNKNOWN != FALSE
  An unknown axis does NOT make the assessment inadmissible.
  It reduces confidence. Only confidence < THRESHOLD makes it inadmissible.

---

## STEP 8: Verify Consequence (C)

Confirm the following are treated as DISTINCT:

```
Execution Result  != Actual Outcome  != Actual Consequence
```

The chain must be traceable:
```
Execution
  -> External Effect
  -> Observation
  -> Outcome
  -> Consequence
  -> Verification
```

If verification is not possible: outcome = UNKNOWN (not SUCCESS, not FAILURE).
"execution_success=True" does NOT mean "consequence_verified=True".

---

## STEP 9: Verify Memory (M)

Confirm Experience Memory can hold:

- Decision context
- Authority used
- Authorization state at time of execution
- Execution result
- Outcome classification
- Actual Consequence (or UNKNOWN)
- Learning extracted
- Unknown Conditions at time of assessment

CRITICAL: Do NOT create Memory -> Authorization path.
Correct direction is:

```
Memory
  -> Reassessment Evidence
  -> Assessment (confidence adjustment only)
  -> Human Gate (independent, not auto-triggered by memory)
  -> Authorization
```

---

## STEP 10: Verify A-U-R Enforcement Point

Confirm the single enforcement boundary evaluates:
```
A = Assessment Admissible
U = Authority Valid  (Human Gate APPROVED only)
R = Runtime Conformant  (GL7 clean, no aborts)
```

And:
```
Executable <=> A AND U AND R
```

If any condition is not met: decision = DENY.

---

## STEP 11: Fail-Closed Verification

ALL of the following MUST produce DENY:

| Condition | Expected |
|-----------|----------|
| A = false | DENY |
| A = UNKNOWN (all axes UNKNOWN, confidence < 0.5) | DENY |
| U = false | DENY |
| U = expired | DENY |
| U = revoked / REJECTED | DENY |
| U = scope mismatch | DENY |
| R = false | DENY |
| R = action mismatch | DENY |
| R = target mismatch | DENY |
| R = payload mismatch | DENY |
| R = context mismatch | DENY |
| R = policy mismatch | DENY |
| assessment = None | DENY |
| gate_result = None | DENY |
| gl7_result = None | DENY |
| exception during check | DENY |

---

## STEP 12: GLK Executor STUB Status

Confirm: mocka3/glk_runtime_bridge/executor.py is still STUB.

If STUB: do NOT claim RUNTIME_VERIFIED for the full pipeline.
The stub reports all guards as "satisfied" without real checking.

If upgrading STUB to real implementation, the following MUST be verified:
- action: correct
- target: correct
- payload: correct
- context: correct
- policy version: current
- authorization: Human Gate APPROVED
- scope: within declared scope

If upgrading changes the Human Gate authority boundary:
STOP. Report as Human Gate judgment item. Do not proceed.

---

## STEP 13: Integration Tests (in order)

### Phase 1: Forward path
```
Decision
  -> create_assessment() [A]
  -> Human Gate state check [U]
  -> GL7 pre_execution_check() [R]
  -> EnforcementPoint.check() [A AND U AND R]
```

### Phase 2: Consequence recording
```
[after enforcement ALLOW + execution]
  -> create_consequence()
  -> outcome classification
  -> deviation detection
```

### Phase 3: Memory write
```
  -> create_experience_entry()
  -> write_experience_to_store()
  -> verify memory_store.json no longer empty
```

### Phase 4: Reassessment feedback
```
  -> load_experience_entries()
  -> Reassessment().build_context()
  -> create_assessment(..., reassessment_context=ctx)
  -> verify confidence_adjustment applied
```

---

## STEP 14: Runtime Verification V-01 through V-13

Execute all items in docs/governance/RUNTIME_VERIFICATION_PLAN.md.
Record each as: PASS / FAIL / UNKNOWN / NOT_APPLICABLE.

Do not skip any item. Do not mark PASS without actual execution.

---

## STEP 15: Event Store Readback

After runtime verification, read back from Event Store.
Code execution alone does NOT constitute completion.

Confirm actual records exist for:
- Decision (decision_ledger.jsonl)
- Assessment (mocka_write_event with assessment_id)
- Authorization (phi_os/human_gate.py event log)
- Runtime (GL7_EVENT in event_bus)
- Consequence (mocka_write_event with consequence_id)
- Memory (memory_store.json entry)
- Reassessment (mocka_write_event with reassessment_id)

---

## STEP 16: Final Status Judgment

Apply strictly:

| Status | Evidence Required |
|--------|------------------|
| DESIGN_ONLY | Contract exists, no code |
| IMPLEMENTATION_INCOMPLETE | Code exists, tests failing or missing |
| IMPLEMENTATION_READY_FOR_VERIFICATION | 23/23 tests pass, imports work |
| RUNTIME_VERIFIED | V-01 through V-13 all checked |
| CLOSED_LOOP_VERIFIED | Event Store readback confirms full loop |

Promotion criteria:
- Code exists != Runtime Verified
- Event exists != Actual Consequence Verified
- Memory exists != Memory Used

---

## STEP 17: PC-side Output Documents

Create in C:\Users\sirok\MoCKA\docs\governance\:

```
PHASE_B_IMPLEMENTATION_REPORT.md
PHASE_B_TEST_REPORT.md
PHASE_B_RUNTIME_VERIFICATION_REPORT.md
PHASE_B_EVENT_STORE_READBACK.md
PHASE_B_FINAL_GAP_REPORT.md
```

Also document:
- Git status at end
- Git diff (what actually changed on PC vs pre-Phase-B)
- Commit target files (explicit list)

---

## STEP 18: ABSOLUTE PROHIBITIONS

- Do NOT unconditionally merge Web branch into main
- Do NOT copy WEB_PREPARED files to main without verification
- Do NOT bypass Human Gate
- Do NOT create BA04 bypass
- Do NOT create Memory -> Authorization path
- Do NOT expand scope beyond what is specified
- Do NOT activate production connections without Human Gate approval
- Do NOT treat STUB as Verified
- Do NOT treat UNKNOWN as FALSE
- Do NOT treat Execution Success as Consequence Verified
- Do NOT use bash echo/heredoc for file generation (CP932 contamination risk)

---

## STEP 19: Phase B Completion Conditions

Phase B is NOT complete until ALL of the following are confirmed:

[ ] Web artifacts vs PC SoT consistency confirmed
[ ] Contract consistency checked (no CONTRACT_CONFLICT unresolved)
[ ] Assessment tests PASS
[ ] Consequence tests PASS
[ ] Memory tests PASS
[ ] Reassessment tests PASS
[ ] A-U-R tests PASS (13/13 deny conditions)
[ ] Integration Phase 1-4 PASS
[ ] Fail-closed all conditions verified
[ ] Runtime Verification V-01 through V-13 complete
[ ] Event Store readback confirms all 7 record types
[ ] Actual runtime trace documented
[ ] Remaining UNKNOWN conditions identified
[ ] Git diff reviewed and committed
[ ] Final Human Gate judgment materials prepared

---

## Final Goal

The closed loop is considered CLOSED_LOOP_VERIFIED only when:

```
Decision
  -> Assessment
  -> Authorization (Human Gate)
  -> Runtime (GL7)
  -> Actual Consequence
  -> Experience Memory
  -> Reassessment
  -> Assessment  (loop back, with prior data)
```

...is demonstrated with actual Event Store records at every step.

---

## Quick Start for PC

```powershell
# 1. Record current state
cd C:\Users\sirok\MoCKA
git status && git branch --show-current && git log -1 --oneline

# 2. Check Web branch (DO NOT checkout yet)
git fetch origin claude/nifty-keller-dqov84
git diff --name-only origin/main..origin/claude/nifty-keller-dqov84

# 3. Review PC_HANDOFF.md and HANDOFF_MANIFEST.md from ZIP

# 4. Apply WEB_PREPARED files after consistency check
# (follow IMPLEMENTATION_PLAN.md STEP B-1 through B-2)

# 5. Run tests
python -m pytest aur/tests/ -v
```

If 23/23 PASSED, proceed to STEP 13 (Integration Tests).
If any FAILED, diagnose before any further action.
