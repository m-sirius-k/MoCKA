# Runtime Verification Plan
## Status: WEB_PREPARED (PC execution required)
## Date: 2026-10-02
## Executor: くろこPC on C:\Users\sirok\MoCKA

---

## IMPORTANT

"Runtime Verified" means くろこPC ran these checks on C:\Users\sirok\MoCKA.
Web-side test results (23/23 on Linux) are WEB_PREPARED only.
Do NOT mark items as verified until PC execution is confirmed.

---

## Verification Checklist

### V-01: Branch Integrity

[ ] git checkout claude/nifty-keller-dqov84
[ ] git log --oneline -3 shows: 0444d98 and 1896cbe
[ ] git diff --name-only origin/main..HEAD shows all 31 expected files
[ ] No uncommitted changes (git status clean)

---

### V-02: Python Environment

[ ] python --version (3.9+)
[ ] pip list | findstr pytest
[ ] All imports succeed:
    - from aur.assessment import create_assessment
    - from aur.consequence import create_consequence
    - from aur.enforcement import EnforcementPoint
    - from aur.reassessment import Reassessment
    - from memory.experience_memory import create_experience_entry

---

### V-03: Unit Test Execution

[ ] python -m pytest aur/tests/ -v
[ ] Result: 23/23 PASSED (no failures, no errors)
[ ] Record actual output here

---

### V-04: Fail-Closed Verification

[ ] gate=None -> DENY confirmed
[ ] assessment=None -> DENY confirmed
[ ] gl7=None -> DENY confirmed
[ ] gate.status="PENDING" -> DENY confirmed
[ ] No exception causes ALLOW (exception -> DENY)

---

### V-05: Assessment Integration

[ ] create_assessment() returns AssessmentRecord
[ ] assessment_id format: ASSESS-{YYYYMMDD}-{hex8}
[ ] axes with all UNKNOWN -> confidence reduced below 0.5 -> inadmissible
[ ] axes with known values -> admissible
[ ] is_assessment_fresh() returns True for new records

---

### V-06: GL7 Integration

[ ] structural/execution_governance.py importable
[ ] ExecutionGovernanceEngine().pre_execution_check({"scope": ["structural"]}) runs
[ ] ApprovalResult.approved is True/False (not None)
[ ] GL7 result can be passed to EnforcementPoint.check()

---

### V-07: Human Gate Integration

[ ] phi_os/human_gate.py importable
[ ] HumanGateEngine (or equivalent) accessible
[ ] gate_result dict format matches EnforcementPoint expectation
[ ] gate_result.status in PENDING/APPROVED/REJECTED/EXPIRED/CANCELED

---

### V-08: Consequence Recording

[ ] create_consequence() returns ConsequenceRecord
[ ] consequence_id format: CONSQ-{YYYYMMDD}-{hex8}
[ ] outcome classification correct: SUCCESS/PARTIAL/FAILURE/UNKNOWN
[ ] deviation correctly computed (symmetric difference)
[ ] "unverified" method -> outcome=UNKNOWN

---

### V-09: Experience Memory Write

[ ] memory/data/ directory exists on C:\Users\sirok\MoCKA
[ ] memory/data/memory_store.json is accessible (create if empty)
[ ] write_experience_to_store() returns True
[ ] Entry appears in load_experience_entries()
[ ] Entry has memory_type="experience"
[ ] Entry content has all ExperienceMemoryContent fields

---

### V-10: Reassessment with Real Data

[ ] After V-09 completes, build_context() returns has_prior_data=True
[ ] Prior outcomes from V-09 appear in ctx.prior_outcomes
[ ] confidence_adjustment is applied correctly
[ ] Confidence clamped to [-0.5, 0.5]

---

### V-11: Event Store Readback

[ ] mocka_write_event was called with CHANGE_START and CHANGE_DONE
[ ] Events appear in mocka_list_events()
[ ] mocka_read_event(event_id="E20261002_981617553cb52") returns CHANGE_START
[ ] mocka_read_event(event_id="E20261002_4298070048d18") returns CHANGE_DONE

---

### V-12: Regression Verification

[ ] git diff HEAD~2..HEAD -- phi_os/human_gate.py: no changes
[ ] git diff HEAD~2..HEAD -- structural/execution_governance.py: no changes
[ ] git diff HEAD~2..HEAD -- memory/memory_model.py: no changes
[ ] git diff HEAD~2..HEAD -- phi_os/context/control_gate.py: no changes
[ ] mocka3/glk_runtime_bridge/executor.py still shows STUB comment

---

### V-13: UTF-8 Verification on Windows

```powershell
# Run mocka_check_utf8 on each new file
mocka_check_utf8("C:\Users\sirok\MoCKA\aur\assessment.py")
mocka_check_utf8("C:\Users\sirok\MoCKA\aur\consequence.py")
mocka_check_utf8("C:\Users\sirok\MoCKA\aur\enforcement.py")
mocka_check_utf8("C:\Users\sirok\MoCKA\aur\reassessment.py")
mocka_check_utf8("C:\Users\sirok\MoCKA\memory\experience_memory.py")
```

[ ] All return {"ok": true}

---

## Completion Criteria

ALL of V-01 through V-13 must be checked before:
- Marking status as RUNTIME_VERIFIED
- Submitting to Human Gate
- Updating MOCKA_OVERVIEW.json canonical paths

---

## Human Gate Submission Checklist

After all verification complete:
[ ] mocka_decision_write() for A-U-R implementation decision
[ ] MOCKA_OVERVIEW.json canonical paths section updated
[ ] GLK executor Phase2 unlocking (separate Human Gate item)
[ ] Pipeline wiring (separate Human Gate item)
