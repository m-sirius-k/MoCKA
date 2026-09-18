# HG-M3 Phase 2: Binding Validation Rules
**Date:** 2026-09-18 | **Authority:** Human Gate | **Status:** DESIGN IN PROGRESS

---

## Binding Validation Framework

A Decision-Evidence binding is established only if 6 mandatory checks pass in sequence.

---

## Check 1: Decision Identity Exists

### Rule
```
IF Decision Object exists in Decision Ledger
   AND decision_id is valid UUID
   AND decision_timestamp is within system time window
THEN return CHECK_PASS
ELSE return CHECK_FAIL(reason: "Decision not found or malformed")
```

### Why This Matters
- Ensures we're binding to a real decision, not phantom entry
- Prevents binding to decisions that don't exist yet (temporal ordering)
- Detects corrupted or truncated decision records

### Validation Logic
```python
def check_decision_exists(decision_id: UUID) -> bool:
    record = decision_ledger.lookup(decision_id)
    if record is None:
        return False
    if not is_valid_uuid(record.decision_id):
        return False
    if not is_plausible_timestamp(record.decision_timestamp):
        return False
    return True
```

### Failure Mode
- `CHECK_FAIL` → Binding blocked, escalate to Human Gate
- Reason: Cannot verify decision exists

---

## Check 2: Authority Reference Exists and Is Valid

### Rule
```
IF Authority Reference object exists
   AND authority_id is in Authority Registry
   AND authority_valid_from <= decision_timestamp <= authority_valid_to
   AND revocation_condition is NOT triggered at decision_timestamp
THEN return CHECK_PASS
ELSE return CHECK_FAIL(reason: "Authority invalid, expired, or revoked")
```

### Why This Matters
- Ensures decision maker had proper authority at time of decision
- Detects retroactive revocation (authority revoked after decision made)
- Prevents expired authority from making new decisions

### Validation Logic
```python
def check_authority_valid(authority_ref: AuthorityReference, decision_timestamp: ISO8601) -> bool:
    authority = authority_registry.lookup(authority_ref.authority_id)
    if authority is None:
        return False
    if not (authority.valid_from <= decision_timestamp <= authority.valid_to):
        return False
    if authority.revocation_condition.triggered_at(decision_timestamp):
        return False
    return True
```

### Failure Mode
- `CHECK_FAIL` → Binding blocked, escalate to Human Gate
- Reason: Authority invalid/expired at decision time

---

## Check 3: Evidence Identity Exists

### Rule
```
FOR EACH evidence_id in Decision.evidence_ids:
  IF Evidence Object exists
     AND evidence_id is valid UUID
     AND evidence is not marked DESTROYED or ARCHIVED_DESTROYED
  THEN check PASS for this evidence
  ELSE check FAIL for this evidence
  
IF ALL evidence checks PASS
THEN return CHECK_PASS
ELSE return CHECK_FAIL(reason: "One or more evidence missing or destroyed")
```

### Why This Matters
- Ensures all referenced evidence actually exists
- Prevents binding to decisions with missing evidence
- Detects evidence destruction (5-year retention violation)

### Validation Logic
```python
def check_evidence_exists(evidence_ids: list[UUID]) -> bool:
    for eid in evidence_ids:
        record = evidence_store.lookup(eid)
        if record is None or record.state == DESTROYED:
            return False
    return True
```

### Failure Mode
- `CHECK_FAIL` → Binding blocked, escalate to Human Gate
- Reason: Evidence missing or destroyed

---

## Check 4: Evidence Integrity Confirmed

### Rule
```
FOR EACH evidence_id in Decision.evidence_ids:
  IF content_hash matches actual payload hash
     AND storage_hash matches verified archive location
     AND signature verifies against source_certificate
  THEN evidence PASS integrity check
  ELSE evidence FAIL integrity check
  
IF ALL evidence integrity checks PASS
THEN return CHECK_PASS
ELSE return CHECK_FAIL(reason: "Evidence integrity compromised")
```

### Why This Matters
- Ensures evidence hasn't been tampered with since decision
- Detects corruption (accidental or malicious)
- Enables non-repudiation (evidence couldn't have been forged)

### Validation Logic
```python
def check_evidence_integrity(evidence: EvidenceObject) -> bool:
    # Hash check
    actual_hash = sha256(evidence.payload)
    if actual_hash != evidence.content_hash:
        return False
    
    # Storage check
    stored_data = archive.retrieve(evidence.storage_location)
    storage_hash = sha256(stored_data)
    if storage_hash != evidence.storage_hash:
        return False
    
    # Signature check
    if not verify_signature(evidence.payload, evidence.source_signature):
        return False
    
    return True
```

### Failure Mode
- `CHECK_FAIL` → Binding blocked, escalate to Human Gate
- Reason: Evidence integrity compromised

---

## Check 5: Timestamp Relationship Valid

### Rule
```
IF evidence_timestamp <= decision_timestamp
   AND decision_timestamp <= validation_timestamp
   AND validation_timestamp <= audit_timestamp
   AND all timestamps are within plausible system clock range
THEN return CHECK_PASS
ELSE return CHECK_FAIL(reason: "Temporal ordering violation")
```

### Why This Matters
- Ensures causal ordering (evidence before decision before validation)
- Detects retroactive binding (evidence created after decision)
- Prevents time-travel attacks
- Ensures audit comes after decision

### Validation Logic
```python
def check_timestamp_ordering(
    evidence_ts: ISO8601,
    decision_ts: ISO8601,
    validation_ts: ISO8601,
    audit_ts: ISO8601
) -> bool:
    # Strict ordering
    if not (evidence_ts <= decision_ts <= validation_ts <= audit_ts):
        return False
    
    # Plausibility check (no jumps >1 year)
    if (decision_ts - evidence_ts).days > 365:
        return False  # unusual delay
    if (validation_ts - decision_ts).days > 30:
        return False  # validation delayed >1 month
    
    return True
```

### Failure Mode
- `CHECK_FAIL` → Binding blocked, escalate to Human Gate
- Reason: Temporal ordering violation

---

## Check 6: Validation Record Exists and Passed

### Rule
```
IF Validation Record exists for this decision
   AND validation_result is PASS (not FAIL or ESCALATE)
   AND all validation rules were evaluated (not SKIPPED)
   AND authority was valid at decision time
   AND risk was within acceptable threshold
THEN return CHECK_PASS
ELSE return CHECK_FAIL(reason: "Validation failed or incomplete")
```

### Why This Matters
- Ensures decision went through required validation gates
- Prevents use of decisions that failed validation
- Confirms risk was acceptable to authority
- Detects incomplete validation (missing rule checks)

### Validation Logic
```python
def check_validation_passed(validation_record: ValidationRecord) -> bool:
    if validation_record is None:
        return False
    if validation_record.validation_result != PASS:
        return False
    
    # All rules must be evaluated (not SKIPPED)
    for rule in validation_record.rule_results:
        if rule.result == SKIPPED:
            return False  # unevaluated rule
    
    # Authority and risk checks
    if not validation_record.authority_valid:
        return False
    if not validation_record.risk_acceptable:
        return False
    
    return True
```

### Failure Mode
- `CHECK_FAIL` → Binding blocked, escalate to Human Gate
- Reason: Validation failed

---

## Binding State Classification

After 6 checks complete, classify binding state:

### State: VALID

**Condition:** All 6 checks PASS

**Meaning:**
- Decision exists and is real
- Authority was valid at time of decision
- All evidence exists and is intact
- Evidence integrity verified (not tampered)
- Temporal ordering is correct
- Validation rules were satisfied

**Action:** Binding is established and can be used for audit/proof

---

### State: INVALID

**Condition:** One or more checks FAIL

**Meaning:** Binding cannot be established due to:
- Decision missing/corrupted
- Authority invalid/expired
- Evidence missing/destroyed/tampered
- Temporal ordering violation
- Validation failed

**Action:** Binding BLOCKED. Escalate to Human Gate for investigation.

---

### State: UNKNOWN

**Condition:** Check result is indeterminate (data incomplete)

**Meaning:**
- Evidence couldn't be retrieved (network error)
- Authority Registry temporarily unavailable
- Decision Ledger query timed out
- Validation Record still being computed

**Action:** Retry binding validation after timeout. If persistent, escalate to Human Gate as system error.

---

### State: NOT_VERIFIED

**Condition:** Validation has not been attempted

**Meaning:**
- Binding validation process hasn't started
- Binding requested before validation check
- Decision created but validation pending

**Action:** Queue for binding validation. Do not use binding until state changes to VALID/INVALID.

---

## Sequential Validation Flow

```
┌─────────────────────────────────────────┐
│ Binding Validation Requested             │
│ (Decision ID + Evidence IDs provided)    │
└──────────────────┬──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Check 1: Decision    │
        │ Exists?              │
        └──────┬───────────────┘
               │
         ┌─────▼─────┐
         │  NO?      │ ─→ INVALID (escalate)
         │ YES       │
         └─────┬─────┘
               │
               ▼
        ┌──────────────────────┐
        │ Check 2: Authority   │
        │ Valid & Active?      │
        └──────┬───────────────┘
               │
         ┌─────▼─────┐
         │  NO?      │ ─→ INVALID (escalate)
         │ YES       │
         └─────┬─────┘
               │
               ▼
        ┌──────────────────────┐
        │ Check 3: All Evidence│
        │ Exists?              │
        └──────┬───────────────┘
               │
         ┌─────▼─────┐
         │  NO?      │ ─→ INVALID (escalate)
         │ YES       │
         └─────┬─────┘
               │
               ▼
        ┌──────────────────────┐
        │ Check 4: Evidence    │
        │ Integrity OK?        │
        └──────┬───────────────┘
               │
         ┌─────▼─────┐
         │  NO?      │ ─→ INVALID (escalate)
         │ YES       │
         └─────┬─────┘
               │
               ▼
        ┌──────────────────────┐
        │ Check 5: Timestamp   │
        │ Order Valid?         │
        └──────┬───────────────┘
               │
         ┌─────▼─────┐
         │  NO?      │ ─→ INVALID (escalate)
         │ YES       │
         └─────┬─────┘
               │
               ▼
        ┌──────────────────────┐
        │ Check 6: Validation  │
        │ Record Passed?       │
        └──────┬───────────────┘
               │
         ┌─────▼─────┐
         │  NO?      │ ─→ INVALID (escalate)
         │ YES       │
         └─────┬─────┘
               │
               ▼
        ┌──────────────────────┐
        │ BINDING STATE:       │
        │ VALID                │
        │ (Ready for use)      │
        └──────────────────────┘
```

---

## Document Status

**Status:** READY FOR FAILURE HANDLING DESIGN  
**Next Step:** HG-M3-PHASE2-BINDING-FAILURE-HANDLING-20260918.md
