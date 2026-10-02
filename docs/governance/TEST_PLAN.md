# Test Plan: A-U-R Closed Loop
## Status: WEB_PREPARED
## Date: 2026-10-02
## Target: C:\Users\sirok\MoCKA (PC)

---

## 1. Unit Tests (already WEB_PREPARED)

File: aur/tests/test_aur_deny.py (13 tests)
File: aur/tests/test_consequence.py (5 tests)
File: aur/tests/test_reassessment.py (5 tests)
Total: 23 tests

Run:
```
python -m pytest aur/tests/ -v
```
Expected: 23/23 PASSED

---

## 2. Deny Condition Matrix (TEST-01 through TEST-13)

| Test | Condition | Expected |
|------|-----------|----------|
| TEST-01 | admissible=False | DENY |
| TEST-02 | confidence < 0.5 | DENY |
| TEST-03 | assessment=None | DENY |
| TEST-04 | all axes UNKNOWN | DENY (confidence penalty) |
| TEST-05 | gate REJECTED | DENY |
| TEST-06 | gate PENDING | DENY |
| TEST-07 | gate EXPIRED | DENY |
| TEST-08 | gate=None (BA04) | DENY |
| TEST-09 | GL7 abort conditions | DENY |
| TEST-10 | gl7=None | DENY |
| TEST-11 | grounding_not_completed | DENY |
| TEST-12 | A=T, U=T, R=T | ALLOW |
| TEST-13 | A+U pass, R fails | DENY |

---

## 3. Additional Contract Tests (to be written on PC)

### TEST-A-01: A=false -> DENY

```python
assessment = create_assessment("action-A", axes={"X":"VIOLATION",...})
# X="VIOLATION" -> inadmissible
assert assessment.admissible == False
```

### TEST-A-02: A=UNKNOWN -> DENY

All axes "UNKNOWN" -> confidence = 1.0 - (6 * 0.15) = 0.1 < 0.5 -> DENY

### TEST-U-01: expired authorization -> DENY

```python
gate_result = {"status": "EXPIRED"}
# enforcement -> DENY
```

### TEST-U-02: revoked authorization -> DENY

```python
gate_result = {"status": "REJECTED"}
# enforcement -> DENY
```

### TEST-R-01: scope mismatch -> DENY

```python
# GL7 with scope ["structural"] but file outside scope changed
# -> deletion_outside_scope abort -> DENY
```

### TEST-R-02: target mismatch -> DENY

```python
# GL7 detects unexpected new directory
# -> new_directory_detected -> DENY
```

### TEST-C-01: execution success + consequence unknown -> NOT VERIFIED

```python
c = create_consequence(..., verification_method="unverified")
assert c.outcome == "UNKNOWN"
assert c.consequence_verified == False
# consequence.outcome != "SUCCESS" even though execution_success=True
```

### TEST-C-02: payload mismatch -> PARTIAL outcome

```python
c = create_consequence(
    actual_changes=["file_a.py", "file_extra.py"],
    expected_changes=["file_a.py"],
    ...
)
assert c.outcome == "PARTIAL"
assert "file_extra.py" in c.deviation
```

### TEST-M-01: memory exists -> authorization NOT automatic

```python
# Inject a SUCCESS experience
r = Reassessment()
r._inject_test_experience({"action_id": "X", "outcome": "SUCCESS", ...})
ctx = r.build_context("X", {})

# Reassessment gives context, but does NOT set gate_result.status="APPROVED"
# The Human Gate is still required independently
assert ctx.has_prior_data == True
# ctx does NOT contain gate_result - it only affects confidence_adjustment
```

### TEST-M-02: actual consequence changed -> reassessment required

```python
# First execution: SUCCESS
# Second execution: same action, PARTIAL outcome with deviation
r = Reassessment()
r._inject_test_experience({"action_id": "X", "outcome": "FAILURE", ...})
ctx = r.build_context("X", {})
assert ctx.confidence_adjustment < 0.0
assert len(ctx.warnings) > 0
# Assessment using this ctx will have reduced confidence
```

### TEST-POLICY-01: Memory -> Authorization direction check

```python
# Memory MUST NOT directly update gate_result or authorization state
# Verify: load_experience_entries() returns data only
# Verify: Reassessment returns ReassessmentContext only
# Verify: create_assessment() accepts context but makes its own admissible decision
# Verify: EnforcementPoint always requires gate_result independently
```

---

## 4. Integration Tests (to be run on PC against real runtime)

### INT-01: Full pipeline trace

```
Context -> Assessment -> GL7 dry run -> EnforcementPoint
-> (DENY or prepare for execution) -> ConsequenceRecord
-> ExperienceMemoryEntry -> write_experience_to_store
-> load_experience_entries -> Reassessment -> new Assessment
```

Verify Event Store captures: CHANGE_START, CHANGE_DONE, enforcement decision

### INT-02: Event Store readback

After INT-01, verify:
```python
# mocka_list_events(limit=20) shows the enforcement events
# mocka_read_event(event_id=...) returns correct data
```

### INT-03: Memory store not empty after full pipeline

```python
entries = load_experience_entries()
assert len(entries) > 0
# Verify memory_store.json is no longer [] (empty)
```

---

## 5. Regression Tests

Verify these production files were NOT modified:
- phi_os/human_gate.py
- structural/execution_governance.py
- memory/memory_model.py
- phi_os/context/control_gate.py

```python
# Check via git diff
# git diff HEAD~2..HEAD -- phi_os/human_gate.py
# Expected: no output (file unchanged)
```

---

## 6. Test Execution Order on PC

1. python -m pytest aur/tests/ -v  (23 unit tests)
2. Manual TEST-A-01 through TEST-POLICY-01 (contract tests)
3. INT-01 through INT-03 (integration tests)
4. Regression verification
5. Record results in RUNTIME_VERIFICATION_PLAN.md
