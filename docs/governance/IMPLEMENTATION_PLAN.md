# Implementation Plan: A-U-R Closed Loop
## Status: WEB_PREPARED
## Date: 2026-10-02
## Target: C:\Users\sirok\MoCKA (PC, Source of Truth)

---

## Phase A (Web) Status: COMPLETE

All WEB_PREPARED artifacts are on branch: claude/nifty-keller-dqov84
Commit: 0444d98 (governance reports) + 1896cbe (implementation)

---

## Phase B: PC Implementation Steps

### STEP B-1: Git Setup (PC)

```powershell
cd C:\Users\sirok\MoCKA
git fetch origin claude/nifty-keller-dqov84
git checkout claude/nifty-keller-dqov84
git log --oneline -5
```

Verify these files exist:
  aur/__init__.py
  aur/assessment.py
  aur/consequence.py
  aur/enforcement.py
  aur/reassessment.py
  aur/tests/test_aur_deny.py
  aur/tests/test_consequence.py
  aur/tests/test_reassessment.py
  memory/experience_memory.py
  docs/contracts/assessment_contract_v1.md (and 4 others)
  docs/governance/AUR_ENFORCEMENT_CONTRACT.md (and others)

---

### STEP B-2: Import Verification

```python
# Run from C:\Users\sirok\MoCKA
python -c "
from aur.assessment import create_assessment, AssessmentRecord
from aur.consequence import create_consequence, ConsequenceRecord
from aur.enforcement import EnforcementPoint
from aur.reassessment import Reassessment
from memory.experience_memory import create_experience_entry, write_experience_to_store
print('ALL IMPORTS OK')
"
```

If any import fails, check sys.path and dependencies.

---

### STEP B-3: Unit Tests

```powershell
cd C:\Users\sirok\MoCKA
python -m pytest aur/tests/ -v
```

Expected: 23/23 PASSED

---

### STEP B-4: Integration: Assessment + Human Gate

```python
# Integration test: A condition with real Human Gate
from aur.assessment import create_assessment
from phi_os.human_gate import HumanGateEngine  # canonical

axes = {
    "X": "grounded evidence",
    "Y": "interpretation",
    "Z": "human authority",
    "T": "current",
    "S": "limited scope",
    "K": "structural",
}
assessment = create_assessment(
    action_id="test-integration-001",
    axes=axes,
    assessor="pc_integration_test",
)
print("assessment_id:", assessment.assessment_id)
print("admissible:", assessment.admissible)
print("confidence:", assessment.confidence)
```

---

### STEP B-5: Integration: Enforcement Point

```python
from aur.enforcement import EnforcementPoint
ep = EnforcementPoint()

# Test with real GL7 result
from structural.execution_governance import ExecutionGovernanceEngine
gl7 = ExecutionGovernanceEngine()
gl7_result = gl7.pre_execution_check({"scope": ["structural"]})

# Simulate gate result (do NOT use real gate for test; use stub)
gate_result = {"status": "APPROVED", "authority": "human", "decision_id": "TEST-001"}

result = ep.check(assessment, gate_result, {
    "approved": gl7_result.approved,
    "aborts": gl7_result.dry_run.aborts if gl7_result.dry_run else [],
})
print("enforcement decision:", result["decision"])
```

---

### STEP B-6: Consequence Recording

```python
from aur.consequence import create_consequence

consequence = create_consequence(
    action_id="test-integration-001",
    assessment_id=assessment.assessment_id,
    execution_success=True,
    actual_changes=["structural/test.py"],
    expected_changes=["structural/test.py"],
    verification_method="git_diff",
)
print("outcome:", consequence.outcome)
print("consequence_id:", consequence.consequence_id)
```

---

### STEP B-7: Experience Memory Write + Read

```python
from memory.experience_memory import create_experience_entry, write_experience_to_store, load_experience_entries

entry = create_experience_entry(
    action_id="test-integration-001",
    assessment_id=assessment.assessment_id,
    consequence_id=consequence.consequence_id,
    outcome=consequence.outcome,
    execution_success=consequence.execution_success,
    consequence_verified=consequence.consequence_verified,
    deviation=consequence.deviation,
    axes_snapshot=assessment.axes,
)
ok = write_experience_to_store(entry)
print("write ok:", ok)

entries = load_experience_entries()
print("experience entries count:", len(entries))
```

---

### STEP B-8: Reassessment with Prior Data

```python
from aur.reassessment import Reassessment

r = Reassessment()
ctx = r.build_context(action_id="test-integration-001", axes=axes)
print("has_prior_data:", ctx.has_prior_data)
print("confidence_adjustment:", ctx.confidence_adjustment)
print("prior_outcomes:", ctx.prior_outcomes)
```

---

### STEP B-9: Event Store Verification

```python
# Verify that events were recorded
from mocka_mcp_server import mocka_list_events  # or use MCP tool

# In MCP:
# mocka_list_events(limit=10)
# Confirm CHANGE_START + CHANGE_DONE events are present
```

---

### STEP B-10: Human Gate Submission

After all tests pass, prepare Human Gate submission:
- See docs/governance/RUNTIME_VERIFICATION_PLAN.md for full checklist
- All items must be green before submission

---

## Implementation Order Summary

1. git checkout + import check (STEP B-1, B-2)
2. unit tests 23/23 (STEP B-3)
3. assessment + axes integration (STEP B-4)
4. enforcement point integration (STEP B-5)
5. consequence recording (STEP B-6)
6. experience memory write/read (STEP B-7)
7. reassessment with prior data (STEP B-8)
8. event store readback (STEP B-9)
9. Human Gate submission (STEP B-10)

---

## Prohibitions During PC Implementation

- Do NOT modify phi_os/human_gate.py
- Do NOT modify structural/execution_governance.py
- Do NOT modify memory/memory_model.py (frozen dataclass)
- Do NOT enable the GLK executor (still a STUB, Phase1 design decision)
- Do NOT wire aur/ into production pipeline without Human Gate approval
- Do NOT claim "Runtime Verified" until STEP B-9 is complete
