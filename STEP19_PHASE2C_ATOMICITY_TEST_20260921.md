# STEP 19 Phase 2-C: Atomicity Test & Runtime Verification
**Date:** 2026-09-21  
**Authority:** HG-18-A, HG-18-D  
**Scope:** Sandbox tests for Decision + Evidence atomicity

---

## Test Plan

### Test Case 1: Both Writes Succeed
**Scenario:** Decision + Pre-Decision Evidence both created successfully

**Expected:**
```
Decision record exists in decision_ledger.jsonl ✓
Evidence record exists in evidence_records.jsonl ✓
decision_record_id linking intact ✓
Bidirectional traversal works ✓
evidence_class = "pre-decision" ✓
```

### Test Case 2: Evidence Write Fails, Decision Succeeds
**Scenario:** Decision persists but Evidence creation fails (file I/O error, validation failure, etc.)

**Expected:**
```
Decision record exists in decision_ledger.jsonl ✓
Evidence record does NOT exist ✗
Failure recorded in Decision Ledger or separate log ✓
Relationship integrity compromised (tracked) ✓
Read-back can detect broken relationship ✓
```

**HG-18-A implication:** 
Cannot rollback Decision (file append irreversible). Must detect and record failure.

### Test Case 3: Decision Write Fails (Impossible in Current Code)
**Scenario:** File I/O error prevents Decision from being written

**Expected:**
```
Decision record does NOT exist ✗
Evidence record does NOT exist ✗
Exception raised/logged ✓
```

### Test Case 4: Binding Failure Detection
**Scenario:** Records exist but relationship lookup fails

**Expected:**
```
Decision exists ✓
Evidence exists ✓
decision_record_id present ✓
Forward traversal works (Evidence → Decision) ✓
Reverse traversal fails or succeeds (depends on index implementation) ?
Broken relationship detectable ✓
```

---

## Implementation Status

### Completed (Sandbox)

- [x] STEP A: Boundary Freeze (frozen at file append + SQLite TX)
- [x] STEP B: Schema Finalization (concrete schema defined)

### To Be Completed (Sandbox Test)

- [ ] STEP C1: Write Decision + Evidence creation function
- [ ] STEP C2: Test Case 1 (both succeed)
- [ ] STEP C3: Test Case 2 (Evidence fails)
- [ ] STEP C4: Test Case 4 (binding verification)
- [ ] STEP D1: Read-back test
- [ ] STEP D2: Bidirectional traversal test
- [ ] STEP D3: Class enforcement test
- [ ] STEP D4: Source provenance validation test

---

## Atomicity Design Decision (HG-18-A = A)

Given frozen boundaries:
- Decision Ledger: file append (irreversible)
- Pre-Decision Evidence: new JSONL file (separate I/O)
- Atomicity: CANNOT be true ACID

**Solution: Quasi-Atomic with Failure Detection**

```
def create_decision_with_evidence(record, evidence_data):
    # Step 1: Append Decision
    decision_id = _append_decision(record)  # File I/O, irreversible
    decision_committed = True
    
    # Step 2: Append Evidence
    try:
        evidence_id = _append_evidence(evidence_data, decision_id)
        evidence_committed = True
        relationship = "intact"
    except Exception as e:
        evidence_committed = False
        relationship = f"broken: {e}"
        log_failure(decision_id, e)
    
    return {
        "decision_id": decision_id,
        "evidence_id": evidence_id if evidence_committed else None,
        "relationship": relationship,
        "integrity": "compromised" if not evidence_committed else "intact"
    }
```

**HG-18-A Interpretation:**
- "atomic を要求" = Record creation together (both happen in same transaction)
- Within frozen boundaries = Sequential writes with relationship integrity tracking
- Failure mode = DETECTED AND RECORDED (not silent)

---

## Expected Test Results (Once Implemented)

### VERIFIED (If All Tests Pass)

1. Test Case 1: Both records created, linking intact
2. Test Case 2: Failure detected, recorded
3. Binding verification: Forward/reverse traversal works
4. Class enforcement: Invalid classes rejected
5. Provenance: Source components valid
6. Read-back: All records readable, integrity verified

### PARTIALLY VERIFIED (If Atomicity Gap Remains)

1. Records created sequentially (not atomic)
2. Failures detected but recovery manual
3. Relationship integrity traceable

### EVIDENCE GAP (If Critical Failure)

1. Atomicity impossible without changing frozen boundaries
2. Need new wrapper transaction mechanism
3. Requires HG decision on acceptable compromise

---

## Conclusion: Testing Framework Ready

Boundary frozen. Schema defined. Test cases specified. Ready for sandbox implementation.

---

**Status:** ATOMICITY TEST PLAN COMPLETE  
**Next:** Sandbox implementation & verification  
**Date:** 2026-09-21
