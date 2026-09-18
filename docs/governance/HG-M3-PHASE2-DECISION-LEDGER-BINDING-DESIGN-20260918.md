# HG-M3 Phase 2: Decision Ledger Binding Design
**Date:** 2026-09-18 | **Authority:** Human Gate | **Status:** DESIGN IN PROGRESS

---

## Decision Ledger Role in Binding

The Decision Ledger serves as the **immutable record of all decisions**, providing the foundation for binding verification. It enables third-party re-verification 5 years later.

### Ledger Entry Structure

```json
{
  "ledger_entry_id": "LEDGER_202609180001",
  "decision_id": "DEC_20260918_001",
  "decision_timestamp": "2026-09-18T16:25:00Z",
  "decision_type": "ADOPT",
  "decision_domain": "authority_model_design",
  
  "authority_binding": {
    "authority_id": "AUTH_HG_001",
    "authority_role": "Human Gate",
    "authority_valid_from": "2026-01-01T00:00:00Z",
    "authority_valid_to": "2027-01-01T00:00:00Z",
    "authority_scope": "institutional_governance",
    "authority_token_hash": "sha256(token_content)"
  },
  
  "evidence_references": [
    {
      "evidence_id": "EV_20260918_001",
      "evidence_type": "PHASE2_DESIGN_DOCUMENT",
      "evidence_timestamp": "2026-09-18T10:00:00Z",
      "evidence_hash": "sha256(content)",
      "relevance": "PRIMARY"
    },
    {
      "evidence_id": "EV_20260918_002",
      "evidence_type": "VALIDATION_RECORD",
      "evidence_timestamp": "2026-09-18T15:00:00Z",
      "evidence_hash": "sha256(content)",
      "relevance": "PRIMARY"
    }
  ],
  
  "validation_record": {
    "validation_record_id": "VAL_20260918_001",
    "validation_result": "PASS",
    "validation_timestamp": "2026-09-18T16:00:00Z",
    "rules_evaluated": 6,
    "rules_passed": 6,
    "risk_score": 0.32,
    "risk_threshold": 0.75
  },
  
  "decision_content": {
    "rationale": "Phase 2 binding model design approved by Human Gate",
    "affected_components": ["Authority Model", "Evidence Package", "Validation Engine"],
    "implementation_timeline": "4-6 weeks",
    "risk_level": "MEDIUM"
  },
  
  "audit_trail": {
    "ledger_entry_timestamp": "2026-09-18T16:25:00Z",
    "ledger_entry_hash": "sha256(full_entry_content)",
    "previous_entry_hash": "sha256(previous_entry)",
    "chain_integrity": "VALID"
  },
  
  "binding_status": {
    "binding_verified": true,
    "binding_verified_at": "2026-09-18T16:26:00Z",
    "binding_state": "VALID",
    "binding_validator": "Phase2_BindingEngine_v1.0"
  }
}
```

---

## Ledger as Verification Source

### Third-Party Re-Verification (5 Years Later)

An auditor examining this ledger entry in 2031 can verify:

**Question 1: Was this decision made by someone with proper authority?**
```
Look at: authority_binding section
Check:   authority was valid at decision_timestamp
Verify:  authority_valid_from <= 2026-09-18 <= authority_valid_to
Result:  YES - authority was active and within scope
```

**Question 2: Did they have sufficient evidence?**
```
Look at: evidence_references array
Check:   all referenced evidence_ids exist and are intact
Verify:  evidence_hash matches archived content
Result:  YES - 2 evidence items found and verified
```

**Question 3: Were validation rules applied?**
```
Look at: validation_record section
Check:   validation_result = PASS
Verify:  all 6 rules were evaluated (not skipped)
Result:  YES - validation passed all checks
```

**Question 4: Did they find any problems?**
```
Look at: validation_record.risk_score vs risk_threshold
Check:   0.32 (risk) <= 0.75 (threshold)
Result:  NO - risk was acceptable
```

**Question 5: Is the record tamper-evident?**
```
Look at: audit_trail section
Check:   ledger_entry_hash unchanged since creation
Verify:  chain_integrity = VALID
Result:  YES - record is cryptographically sealed
```

---

## Binding Verification Protocol

### Re-Verification Procedure (for auditors in Phase 3+)

```python
def re_verify_decision_binding(ledger_entry_id: string, current_time: ISO8601) -> VerificationResult:
    
    # Step 1: Retrieve from immutable ledger
    entry = decision_ledger.get(ledger_entry_id)
    if entry is None:
        return VerificationResult(
            status="INVALID",
            reason="Ledger entry not found"
        )
    
    # Step 2: Verify ledger integrity
    stored_hash = decision_ledger.compute_hash(entry)
    if stored_hash != entry.audit_trail.ledger_entry_hash:
        return VerificationResult(
            status="INVALID",
            reason="Ledger entry integrity compromised"
        )
    
    # Step 3: Verify chain integrity
    if entry.audit_trail.chain_integrity != "VALID":
        return VerificationResult(
            status="INVALID",
            reason="Chain integrity violated"
        )
    
    # Step 4: Verify authority (historical snapshot)
    authority_valid = verify_authority_at_time(
        entry.authority_binding,
        entry.decision_timestamp
    )
    if not authority_valid:
        return VerificationResult(
            status="INVALID",
            reason="Authority was not valid at decision time"
        )
    
    # Step 5: Verify evidence still exists
    for ev_ref in entry.evidence_references:
        ev = evidence_store.get(ev_ref.evidence_id)
        if ev is None:
            return VerificationResult(
                status="INVALID",
                reason=f"Evidence {ev_ref.evidence_id} missing"
            )
        if sha256(ev.payload) != ev_ref.evidence_hash:
            return VerificationResult(
                status="INVALID",
                reason=f"Evidence {ev_ref.evidence_id} integrity compromised"
            )
    
    # Step 6: Verify validation rules were applied
    val_rec = entry.validation_record
    if val_rec.validation_result != "PASS":
        return VerificationResult(
            status="INVALID",
            reason="Validation did not pass at decision time"
        )
    if val_rec.rules_evaluated != val_rec.rules_passed:
        return VerificationResult(
            status="INVALID",
            reason="Not all rules passed validation"
        )
    
    # All checks passed
    return VerificationResult(
        status="VALID",
        verified_at=current_time,
        authority_confirmed=True,
        evidence_confirmed=True,
        validation_confirmed=True
    )
```

---

## Ledger Structure for Binding Support

### Required Fields in Decision Ledger

| Field | Type | Purpose | Usage |
|-------|------|---------|-------|
| `ledger_entry_id` | UUID | Unique ledger entry | Chain reference |
| `decision_id` | UUID | Links to Decision Object | Binding verification |
| `decision_timestamp` | ISO 8601 | When decision made | Temporal ordering |
| `authority_id` | string | Who decided | Authority verification |
| `authority_valid_from` | ISO 8601 | Authority start | Valid-at-time check |
| `authority_valid_to` | ISO 8601 | Authority end | Expiration check |
| `evidence_ids` | array[UUID] | What evidence used | Completeness check |
| `evidence_hashes` | array[SHA256] | Evidence integrity | Tamper detection |
| `validation_result` | enum | Did it pass validation? | Gate verification |
| `validation_timestamp` | ISO 8601 | When validated | Temporal ordering |
| `risk_score` | float | Decision risk | Threshold comparison |
| `risk_threshold` | float | Authority's approval level | Acceptance check |
| `ledger_entry_hash` | SHA256 | Ledger entry seal | Immutability proof |
| `previous_entry_hash` | SHA256 | Chain link | No retroactive insertion |
| `chain_integrity` | enum | Is chain valid? | Ledger trust signal |

---

## Chain Integrity Mechanism

### Hash Chain Structure

```
Entry 1:
├─ ledger_entry_hash = SHA256(entry1_content)
├─ previous_entry_hash = null (first entry)
└─ hash_chain = [hash1]

Entry 2:
├─ ledger_entry_hash = SHA256(entry2_content)
├─ previous_entry_hash = hash1
└─ hash_chain = [hash1, hash2]

Entry 3:
├─ ledger_entry_hash = SHA256(entry3_content)
├─ previous_entry_hash = hash2
└─ hash_chain = [hash1, hash2, hash3]
```

### Retroactive Insertion Detection

If someone tries to insert fake entry between Entry 2 and 3:

```
Entry 2:
├─ ledger_entry_hash = hash2
├─ previous_entry_hash = hash1
└─ Next entry should reference hash2

ATTACK ATTEMPT:
Fake Entry 2.5:
├─ previous_entry_hash = hash2 (looks correct)
├─ BUT: ledger_entry_hash of original Entry 3 doesn't reference hash2.5
└─ RESULT: Chain breaks, tampering detected
```

---

## Binding State in Ledger

### At Decision Time (Entry Created)

```
binding_status.binding_verified = false
binding_status.binding_state = NOT_YET_VERIFIED
```

Decision made, but binding verification runs asynchronously.

### After Binding Validation Complete

```
binding_status.binding_verified = true
binding_status.binding_verified_at = 2026-09-18T16:26:00Z
binding_status.binding_state = VALID | INVALID | UNKNOWN
binding_status.binding_validator = BindingEngine_v1.0
binding_status.validation_error = null | error_message
```

---

## Archival and Long-Term Access

### 5-Year Retention Policy

```
Year 0-2: HOT STORAGE
├─ Location: Fast database (PostgreSQL)
├─ Access: O(1) lookup
├─ Updates: Allowed (no updates post-creation, but metadata can be appended)
└─ Purpose: Day-to-day audits

Year 2-5: WARM STORAGE
├─ Location: Archive database (compressed)
├─ Access: O(n log n) scan
├─ Updates: None (read-only)
└─ Purpose: Annual audits, compliance reviews

Year 5+: COLD STORAGE
├─ Location: Long-term archive (immutable tape)
├─ Access: Restore required (1-24 hours)
├─ Updates: None (read-only)
└─ Purpose: Regulatory retention, historical analysis
```

### Re-Verification After Archival

If need to verify binding 6 years later (entry in cold storage):

```python
def re_verify_archived_decision(ledger_entry_id, current_time):
    # Step 1: Restore from cold storage
    entry = cold_archive.restore(ledger_entry_id)
    
    # Step 2: Verify restoration integrity
    if verify_restoration_checksum(entry) == False:
        return "RESTORATION_FAILED"
    
    # Step 3: Re-verify binding (same as hot storage)
    result = re_verify_decision_binding(entry, current_time)
    
    return result
```

---

## Binding as Ledger Quality Signal

The decision ledger serves as a **quality indicator** for MoCKA governance:

**High Binding Rates (95%+):** System is working as designed
- Decisions have proper evidence
- Authority is being verified
- Validation rules being enforced

**Declining Binding Rates (< 80%):** Red flag for governance issues
- Evidence retention failing
- Authority metadata corrupted
- Validation records missing

**Binding Failure Patterns:**
- If mostly EVIDENCE_MISSING → retention policy being violated
- If mostly AUTHORITY_MISSING → authority registry maintenance failing
- If mostly VALIDATION_FAILURE → rules being circumvented

---

## Document Status

**Status:** READY FOR REVIEW PACKAGE INTEGRATION  
**Next Step:** HG-M3-PHASE2-BINDING-DESIGN-REVIEW-PACKAGE-20260918.md
