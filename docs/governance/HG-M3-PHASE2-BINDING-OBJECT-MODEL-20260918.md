# HG-M3 Phase 2: Binding Object Model
**Date:** 2026-09-18 | **Authority:** Human Gate | **Status:** DESIGN IN PROGRESS

---

## Decision Object

### Definition
Formal representation of an institutional decision affecting system state.

### Identity
```
decision_id: UUID (immutable)
decision_timestamp: ISO 8601 (creation time)
decision_type: enum (ADOPT | REJECT | DEFER | ESCALATE)
decision_domain: string (scope of decision: e.g., "authority_role_admin")
```

### Required Attributes
```
Authority Reference:
  authority_id: string (who made decision)
  authority_role: string (role under which decision made)
  authority_scope: string (delegated scope of authority)
  
Decision Content:
  rationale: string (why this decision)
  affected_components: array(string) (what changes as result)
  risk_level: enum (LOW | MEDIUM | HIGH)
  
Approval Chain:
  approver_id: string (if multi-step)
  approval_timestamp: ISO 8601
  approval_signature: hash (non-repudiation proof)
  
Evidence References:
  evidence_ids: array(UUID) (pointers to Evidence Objects)
  evidence_binding_state: enum (VALID | INVALID | UNKNOWN | NOT_VERIFIED)
```

### Relationship Model

```
Decision ─← Authority Reference ─→ Authority Object
   │
   ├─→ Evidence Reference ─→ Evidence Object
   │
   ├─→ Validation Record ─→ Validation State
   │
   └─→ Audit Reference ─→ Audit Memory
```

### Validation State

At creation time:
- `evidence_binding_state: UNKNOWN` (not yet validated)

After validation:
- `evidence_binding_state: VALID` (all evidence intact, authority verified)
- `evidence_binding_state: INVALID` (evidence missing/tampered, authority expired)
- `evidence_binding_state: NOT_VERIFIED` (validation incomplete)

---

## Evidence Object

### Definition
Structured container of decision-supporting material with integrity and source authentication.

### Identity
```
evidence_id: UUID (immutable)
evidence_type: enum (TEST_RESULT | COMPLIANCE_RECORD | RISK_ASSESSMENT | AUDIT_LOG | APPROVAL_FORM)
evidence_timestamp: ISO 8601 (creation time)
evidence_source: string (who created this evidence)
```

### Required Attributes
```
Content:
  payload: binary (evidence data)
  content_hash: SHA256 (integrity proof)
  compression: enum (NONE | GZIP | DEFLATE)
  
Source Authentication:
  source_signature: signature (proof of origin)
  source_certificate: x509 (optional, for formal sources)
  signing_timestamp: ISO 8601
  
Metadata:
  decision_ref: UUID (which decision this supports)
  relevance: enum (PRIMARY | SUPPORTING | CONTEXT)
  validity_period: {start: ISO 8601, end: ISO 8601}
  
Storage:
  storage_location: URI (where evidence is archived)
  storage_hash: SHA256 (proof of correct storage)
  archival_timestamp: ISO 8601
```

### Relationship Model

```
Evidence ─→ Decision Reference (backreference to Decision Object)
   │
   ├─→ Source (who created)
   │
   ├─→ Validation Record (was integrity verified?)
   │
   └─→ Audit Memory (where logged)
```

### Validation State

At creation:
- `integrity_verified: FALSE` (not yet checked)
- `source_authenticated: FALSE` (signature not verified)

After validation:
- `integrity_verified: TRUE` (content hash matches)
- `source_authenticated: TRUE` (signature valid)
- `binding_state: VALID` (ready to link to Decision)

---

## Authority Reference

### Definition
Cryptographic token binding a decision to authority that made it.

### Identity
```
authority_reference_id: UUID (immutable)
authority_id: string (which authority)
authority_role: string (role at time of decision)
authority_timestamp: ISO 8601 (when authority was active)
```

### Required Attributes
```
Authority State Proof:
  valid_from: ISO 8601 (authority became active)
  valid_to: ISO 8601 (authority expires)
  authority_scope: string (what this authority can decide on)
  revocation_condition: string (what triggers revocation)
  
Authority Binding:
  authority_token: hmac (cryptographic binding proof)
  token_signature: signature (proof token not modified)
  
Delegation Chain:
  delegated_by: string (who delegated this authority)
  delegation_timestamp: ISO 8601
  delegation_evidence_ref: UUID (evidence supporting delegation)
```

### Relationship Model

```
Authority Reference ─→ Authority Object (the actual authority being referenced)
   │
   ├─→ Delegation Chain (who delegated it, when)
   │
   ├─→ Decision (which decision this authority made)
   │
   └─→ Validation Record (was authority valid at decision time?)
```

### Validation State

At decision time:
- Check: `now >= valid_from AND now <= valid_to` (is authority still active?)
- Check: `revocation_condition NOT triggered` (was it revoked?)
- Result: `authority_binding_state: VALID | INVALID | UNKNOWN`

---

## Validation Record

### Definition
Formal proof that validation rules were applied and decision passed required gates.

### Identity
```
validation_record_id: UUID (immutable)
validation_timestamp: ISO 8601 (when validation occurred)
decision_id: UUID (which decision validated)
```

### Required Attributes
```
Validation Rules Applied:
  rule_set: array(string) (which rules were checked)
  rule_results: object {
    rule_id: string,
    rule_name: string,
    rule_condition: string,
    evaluated: boolean,
    result: enum (PASS | FAIL | SKIPPED),
    failure_reason: string (if FAIL)
  }
  
Authority Validation:
  authority_valid: boolean
  authority_expiration_check: PASS | FAIL
  authority_scope_check: PASS | FAIL
  
Evidence Validation:
  evidence_integrity: PASS | FAIL
  evidence_source_authenticated: PASS | FAIL
  evidence_completeness: PASS | FAIL
  
Risk Assessment:
  risk_score: float (0.0-1.0)
  risk_threshold: float (authority's approval threshold)
  risk_acceptable: boolean (risk_score <= threshold)
  
Overall Result:
  validation_result: enum (PASS | FAIL | ESCALATE)
  escalation_reason: string (if ESCALATE)
  escalation_to: string (Human Gate, if ESCALATE)
```

### Relationship Model

```
Validation Record ─→ Decision (validates this decision)
   │
   ├─→ Rule Set (which rules applied)
   │
   ├─→ Evidence Set (which evidence validated)
   │
   └─→ Authority (which authority's validation)
```

### Validation Result Meaning

- `PASS`: All rules satisfied, decision can proceed
- `FAIL`: One or more rules violated, decision BLOCKED
- `ESCALATE`: Ambiguity or special condition, refer to Human Gate
- `NOT_VERIFIED`: Validation incomplete (data missing)

---

## Audit Reference

### Definition
Pointer to audit trail enabling third-party re-verification of decision and binding.

### Identity
```
audit_reference_id: UUID (immutable)
audit_timestamp: ISO 8601 (when audit record created)
decision_id: UUID (which decision audited)
```

### Required Attributes
```
Audit Location:
  audit_path: URI (where full audit trail stored)
  audit_entry_hash: SHA256 (proof of audit record integrity)
  
Audit Contents:
  decision_ledger_entry: UUID (reference to Decision Ledger)
  evidence_package_ref: UUID (reference to Evidence Package)
  authority_reference_snapshot: object (copy of authority state at decision time)
  validation_record_snapshot: object (copy of validation result)
  
Re-verification Instructions:
  re_verification_steps: array(string) (how to re-verify this decision)
  required_evidence: array(UUID) (which evidence needed)
  required_authority: string (which authority to query)
  
Access Control:
  audit_access_level: enum (PUBLIC | INTERNAL | RESTRICTED)
  audit_read_authorization: array(string) (who can read audit)
```

### Relationship Model

```
Audit Reference ─→ Decision Ledger (entry to verify against)
   │
   ├─→ Evidence Package (snapshots to verify)
   │
   ├─→ Authority (to validate authority was real)
   │
   └─→ Validation Record (to verify rules were applied)
```

### Purpose

Enable **third-party audit** 5 years later:
- "Was this decision made by someone with proper authority?"
- "Did they have sufficient evidence?"
- "Were validation rules applied?"
- "Did they find any problems?"

---

## Binding Relationship Summary

```
            DECISION OBJECT
               (UUID)
                 │
        ┌────────┼────────┬─────────────┐
        │        │        │             │
        ▼        ▼        ▼             ▼
   AUTHORITY  EVIDENCE  VALIDATION   AUDIT
   REFERENCE  OBJECTS   RECORDS      REFERENCE
      │        (N)        │             │
      │        │          │             │
      └────────┼──────────┴─────────────┘
               │
         ┌─────▼─────┐
         │   VALID   │ ←── Binding State
         └───────────┘
```

---

## Binding Completeness Checklist

| Component | Identity | Attributes | Relationship | Validation | Status |
|-----------|----------|-----------|--------------|-----------|--------|
| Decision | ✓ UUID | ✓ 8 fields | ✓ defined | ✓ state model | COMPLETE |
| Evidence | ✓ UUID | ✓ 10 fields | ✓ defined | ✓ state model | COMPLETE |
| Authority Ref | ✓ UUID | ✓ 8 fields | ✓ defined | ✓ state model | COMPLETE |
| Validation Rec | ✓ UUID | ✓ 12 fields | ✓ defined | ✓ results | COMPLETE |
| Audit Ref | ✓ UUID | ✓ 9 fields | ✓ defined | ✓ re-verify | COMPLETE |

---

## Document Status

**Status:** READY FOR VALIDATION RULES DESIGN  
**Next Step:** HG-M3-PHASE2-BINDING-VALIDATION-RULES-20260918.md
