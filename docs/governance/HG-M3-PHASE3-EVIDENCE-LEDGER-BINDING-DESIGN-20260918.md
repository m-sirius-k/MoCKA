# HG-M3 Phase 3: Evidence Ledger Binding Design
**Date:** 2026-09-18 | **Authority:** Conditional Authorization (Option B) | **Status:** PREPARATION

---

## PURPOSE

Define how Phase 3 captures and records evidence that decisions are properly bound to their supporting evidence and authority.

---

## EVIDENCE BINDING FLOW

```
Action (Phase 3 Code Execution)
     ↓
Evidence Captured (What happened)
     ↓
Ledger Entry Created (Immutable record)
     ↓
Verification Performed (Binding validated)
     ↓
Human Gate Review (Evidence examined)
```

---

## LEDGER ENTRY STRUCTURE

Each Phase 3 action must create a ledger entry:

```json
{
  "action_id": "ACT_20260918_001",
  "action_type": "decision_binding_test",
  "timestamp": "2026-09-18T17:14:56Z",
  "phase": "PHASE3",
  "environment": "sandbox",
  
  "decision_binding": {
    "decision_id": "TEST_DEC_001",
    "q_decisions": ["Q1:B", "Q2:A", "Q3:B", "Q4:B", "Q5:C", "Q6:B"],
    "binding_result": "VALID"
  },
  
  "evidence_references": [
    {
      "evidence_id": "EVD_001",
      "type": "synthetic_evidence",
      "sha256_hash": "abc123...",
      "status": "verified"
    }
  ],
  
  "authority_snapshot": {
    "authority_id": "AUTH_TEST_001",
    "snapshot_timestamp": "2026-09-18T17:14:00Z",
    "status": "registered"
  },
  
  "validation_record": {
    "check_1_decision_identity": "PASS",
    "check_2_authority_validity": "PASS",
    "check_3_evidence_existence": "PASS",
    "check_4_evidence_integrity": "PASS",
    "check_5_timestamp_ordering": "PASS",
    "check_6_validation_record": "PASS",
    "overall_result": "VALID"
  },
  
  "audit_reference": {
    "audit_trail_id": "AUD_001",
    "retention_policy": "5_year_sandbox_only",
    "searchable": true
  },
  
  "metadata": {
    "created_by": "phase3_binding_test",
    "environment": "sandbox",
    "data_classification": "test_only",
    "human_reviewed": false
  }
}
```

---

## BINDING ACTION TYPES

### Binding Action B1: Q Decision Implementation
**What:** Translating Q1-Q6 decisions into code

**Evidence Captured:**
- Decision option selected (A/B/C)
- Code implementation (Git commit hash)
- Test result (PASS/FAIL)
- Rationale documentation

**Ledger Entry:** decision_binding_test
**Verification:** Q decision reflected accurately in code

---

### Binding Action B2: Evidence Validation Test
**What:** Testing evidence binding against synthetic evidence

**Evidence Captured:**
- Evidence ID created
- SHA256 hash calculated
- Validation checks performed (6 checks)
- Binding result (VALID/INVALID/UNKNOWN)

**Ledger Entry:** evidence_validation_test
**Verification:** All 6 checks completed

---

### Binding Action B3: Authority Registration
**What:** Creating authority snapshots for binding

**Evidence Captured:**
- Authority ID registered
- Registration timestamp
- Q2 decision (retroactive registration rule)
- Authority snapshot state

**Ledger Entry:** authority_registration
**Verification:** Authority snapshot created correctly per Q2 policy

---

### Binding Action B4: Failure Scenario Test
**What:** Testing failure handling for 5 patterns

**Evidence Captured:**
- Failure pattern (Evidence Missing / Conflict / Authority Missing / Validation Failure / Timestamp Conflict)
- Failure trigger
- Escalation result
- Human Gate notification sent

**Ledger Entry:** failure_scenario_test
**Verification:** Escalation reached Human Gate

---

### Binding Action B5: Rollback Test
**What:** Testing rollback mechanism

**Evidence Captured:**
- Checkpoint created
- Action executed
- Database restored
- Integrity verified

**Ledger Entry:** rollback_test
**Verification:** Database returned to clean state

---

## LEDGER STORAGE (Sandbox Only)

### Storage Location
```
/home/user/MoCKA/data/sandbox/
├── sb_phase3_ledger.jsonl (immutable append-only)
└── sb_phase3_ledger.backup (weekly backup)
```

### Immutability Guarantee
- Append-only: New entries only, no overwrites
- Hash chain: Each entry references previous entry
- Tamper detection: Retroactive insertion will break hash chain
- Verification: Can be verified by third party

### Hash Chain Structure
```
Entry 1: { ..., previous_hash: null, current_hash: HASH1 }
Entry 2: { ..., previous_hash: HASH1, current_hash: HASH2 }
Entry 3: { ..., previous_hash: HASH2, current_hash: HASH3 }
```

---

## VERIFICATION PROCEDURES

### Procedure V1: Ledger Integrity Check
**Command:**
```python
def verify_ledger_hash_chain(ledger_file):
    previous_hash = None
    for entry in read_jsonl(ledger_file):
        if entry['previous_hash'] != previous_hash:
            return FAIL("Hash chain broken at entry")
        previous_hash = entry['current_hash']
    return PASS("Hash chain intact")
```

### Procedure V2: Binding Completeness Check
**Verification:**
- All 6 Q decisions have at least 1 ledger entry
- Each entry shows decision → code → test flow
- All test results recorded
- All evidence collected

### Procedure V3: Evidence Authenticity Check
**Verification:**
- All SHA256 hashes recalculated and match
- All evidence marked as synthetic (test-only)
- No production data references
- Data provenance traceable to fixtures

---

## LEDGER QUERIES

### Query Q1: Find all bindings for decision Q1
```
SELECT * FROM sb_phase3_ledger 
WHERE decision_binding.q_decisions CONTAINS "Q1"
```

### Query Q2: Find all failures with escalation
```
SELECT * FROM sb_phase3_ledger 
WHERE action_type = "failure_scenario_test"
```

### Query Q3: Verify authority snapshot completeness
```
SELECT * FROM sb_phase3_ledger 
WHERE action_type = "authority_registration"
```

### Query Q4: Timeline of all binding actions
```
SELECT timestamp, action_id, action_type 
FROM sb_phase3_ledger 
ORDER BY timestamp ASC
```

---

## HUMAN GATE REVIEW EVIDENCE

After Phase 3 completes, Human Gate receives:

1. **Ledger Export:** Complete sb_phase3_ledger.jsonl
2. **Hash Verification:** Integrity check report
3. **Binding Summary:** 
   - 6 Q decisions → code implementations
   - All test results (PASS/FAIL)
   - Evidence validation completeness
4. **Failure Scenarios:** All 5 patterns tested + escalation verified
5. **Authority Snapshots:** All authority registrations per Q2 policy
6. **Timeline:** Chronological proof of all actions

---

## LEDGER READINESS CHECKLIST

- [ ] Ledger schema defined
- [ ] Storage location prepared (sandbox)
- [ ] Hash chain algorithm implemented
- [ ] Append-only guarantee enforced
- [ ] Verification procedures automated
- [ ] Query interface ready
- [ ] Human Gate review format prepared
- [ ] Audit trail generation configured

---

**EVIDENCE LEDGER BINDING DESIGN READY**

